#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import time
import os
import ConfigParser
import json
import shutil
from tools import logging_helper, shell_ops

# global variables across multiple modules
default_repo_name = 'Intel_Repository'
cherrypy_session_timeout_other = 180  # (min) default is 60 minutes. This is 3 hours.
cherrypy_session_timeout_quark = 720  # (min) This is 12 hours.
cherrypy_session_timeout_chosen = 180
network_status = {'https_conn': 'False', 'http_conn': 'NA'}
network_time = time.time()
network_check_http = False
smart_cache_path = '/var/lib/smart/channels'
smart_cache_file = '/var/lib/smart/cache'
package_data_file = '/tmp/json_packages.txt'
package_installed_data_file = '/tmp/json_packages_installed.txt'
harden_image_packages_config_file = os.path.dirname(__file__) + '/' + 'harden_image_packages'  # note: we are assuming that the directory exists already!!!!
harden_image_updater_config_file = os.path.dirname(__file__) + '/' + 'harden_image_updater'  # note: we are assuming that the directory exists already!!!!
harden_image_stig_config_file = os.path.dirname(__file__) + '/' + 'harden_image_stig_selected'  # note: we are assuming that the directory exists already!!!!
harden_image_stig_all_file = os.path.dirname(__file__) + '/' + 'harden_image_stig.json'  # note: we are assuming that the directory exists already!!!!
repo_tracking_file = os.path.dirname(__file__) + '/' + 'repo_tracking'  # note: we are assuming that the directory exists already!!!!
pro_packages_file = os.path.dirname(__file__) + '/' + 'pro_files'  # note: we are assuming that the directory exists already!!!!
os_update_log_file = os.path.dirname(__file__) + '/' + 'os_update_log'  # note: we are assuming that the directory exists already!!!!
flex_repo_name = 'WR_Repo_'
pro_repo_name = 'Pro_Repo_'
use_new_build_package_database = True
use_new_get_installed_packages = True
use_new_list_repos = False  # Do not use new approach since Smart and its cache will be out-of-sync in some way.
oem_branding_config = {'logo_file': '', 'eula_files': [], 'eula_files_datetime': []}
node_red_experience_service = 'node-red-experience.service'


def read_config_file():
    """ Read the configuration file for the corresponding architecture URL

    Returns:
        ConfigParser
    """
    log_helper = logging_helper.logging_helper.Logger()
    config = ConfigParser.ConfigParser()
    config_file = os.path.dirname(__file__) + '/' + 'developer_hub_config'
    config.read(config_file)
    log_helper.logger.debug("Configuration file: '%s'" % config_file)
    return config


def add_secure_http_to_config_file(state):
    """ Update config file to enable/disable https connections.

    Args:
            state (str): 'true' or 'false'
    """
    log_helper = logging_helper.logging_helper.Logger()
    config = read_config_file()
    try:
        config.set('SecurityAutomation', 'secure_http', state)
        config_file = os.path.dirname(__file__) + '/' + 'developer_hub_config'
        set_config = open(config_file, 'w')
        config.write(set_config)
    except ConfigParser.DuplicateSectionError:
        log_helper.logger.debug('Security Automation section is configured; no need to add again')


def configure_node_red_https(state):
    """ Configure node red to use http or https.
    Args:
        state (str): 'true' or 'false'

    Returns:

    """
    settings = '/home/gwuser/.node-red/settings.js'
    https_settings = settings + ".https"
    http_settings = settings + ".http"
    shell_ops.run_command('systemctl stop node-red-experience.service')
    if state == 'true':
        if os.path.isfile(https_settings):
            try:
                os.rename(settings, http_settings)
                os.rename(https_settings, settings)
            except:
                pass
    else:
        if os.path.isfile(http_settings):
            try:
                os.rename(settings, https_settings)
                os.rename(http_settings, settings)
            except:
                pass
    shell_ops.run_command('systemctl start node-red-experience.service')


def configure_nginx_https(state):
    log_helper = logging_helper.logging_helper.Logger()
    node_cloudcmd_conf_file = "/home/gwuser/.node-cloudcmd/node-cloudcmd_nginx_http.conf"
    node_red_conf_file = "/home/gwuser/.node-red/node-red_nginx_http.conf" 
    if state == 'true':
        node_cloudcmd_conf_file = node_cloudcmd_conf_file.replace("http", "https")
        node_red_conf_file = node_red_conf_file.replace("http", "https")
    try:
        shutil.copyfile(node_cloudcmd_conf_file, '/etc/nginx/conf.d/node-cloudcmd.conf')
        shutil.copyfile(node_red_conf_file, '/etc/nginx/conf.d/node-red.conf')
        log_helper.logger.debug('node-red and cloud commander nginx https configured')
        log_helper.logger.debug('Restarting ngnix')
        shell_ops.run_command('systemctl restart nginx.service') 
    except Exception as e:
        log_helper.logger.error(str(e))
        log_helper.logger.error("Failed to configure https settings for node-red and cloudcmd")       


class HDCSettings(object):
    """ Class to configure HDC
    """
    #    "proxy_config": [
    #               {
    #                     "proxy_protocol": "none",
    #                     "proxy_address": "",
    #                     "proxy_port": 3128,
    #                     "proxy_username": "",
    #                    "proxy_password": ""
    #               }
    #			],

    @staticmethod
    def set_proxy_settings_for_HDC(protocol, proxy_address, proxy_port):
        log_helper = logging_helper.logging_helper.Logger()
        try:
            f = open('/var/wra/files/default/default_settings', 'r+')
            data = json.load(f)
            data['proxy_config'][0]['proxy_protocol'] = protocol
            data['proxy_config'][0]['proxy_port'] = proxy_port
            data['proxy_config'][0]['proxy_address'] = proxy_address
            f.seek(0)
            f.truncate()
            f.write(json.dumps(data, indent=5, sort_keys=True))
            log_helper.logger.debug('updated HDC proxy settings')
        except IOError:
            log_helper.logger.error("HDC settings file doesn't exist. No need to set HDC proxy settings")

    @staticmethod
    def upgrade_status():
        config = ConfigParser.ConfigParser()
        config_file = os.path.dirname(__file__) + '/' + 'developer_hub_config'
        config.read(config_file)
        config.set('HDC', 'config', 'True')
        set_config = open(config_file, 'w')
        config.write(set_config)

    @staticmethod
    def set_hdc_server_details():
        log_helper = logging_helper.logging_helper.Logger()
        try:
            f = open('/var/wra/files/default/default_settings', 'r+')
            data = json.load(f)
            data['device_config'][0]['model_number'] = "MI-IDP-IOT-GW-EVAL"
            data['ems_server_config'][0]['server_address'] = "wrpoc6.axeda.com"
            f.seek(0)
            f.write(json.dumps(data, indent=5, sort_keys=True))
            f.truncate()
            try:
                shell_ops.run_command('systemctl --no-block restart wr-iot-agent')
            except:
                log_helper.logger.debug("Unable to restart wr-iot-agent service. Package may not be installed.")
                pass
            HDCSettings.upgrade_status()
            log_helper.logger.debug('updated HDC server settings')
        except IOError:
            log_helper.logger.error("HDC settings file doesn't exist. No need to set HDC server settings")         
