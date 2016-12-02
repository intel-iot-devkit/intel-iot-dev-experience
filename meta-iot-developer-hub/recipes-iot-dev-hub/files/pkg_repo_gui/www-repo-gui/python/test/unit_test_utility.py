#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import logging
import os
import time
import httplib
import json
import socket
import errno
from tools import logging_helper, shell_ops
import manage_proxy


class HttpConnectionHelper:
    """ The helper to manage connection to Dev Hub and establish authenticated session.
    """
    def __init__(self, service_name, status_running, status_dead, username, password):
        self._sn = service_name
        self._sc_running = status_running
        self._sc_dead = status_dead
        self._un = username
        self._pw = password
        self._h = None
        self._cookies = None
        self._auth = False

        # make sure that the server is started!
        result = shell_ops.run_command('systemctl status ' + self._sn)
        if not (self._sc_running in result):
            shell_ops.run_command('systemctl start ' + self._sn)
            time.sleep(5)

        while True:
            try:
                self._h = httplib.HTTPConnection('localhost:80')
                data = json.dumps({'username': self._un, 'password': self._pw})
                headers = {"Content-type": "application/json"}
                self._h.request('POST', '/api/auth', data, headers)
                r = self._h.getresponse()
                self._cookies = r.getheader('set-cookie', 'no value')
                js_data = json.loads(r.read())
                if js_data['status'] == 'success':
                    self._auth = True
                r.close()
                break
            except socket.error as e:
                if e.errno == errno.ECONNREFUSED:
                    # continue
                    print 'Connection refused... wait for 5 seconds and try again....'
                    time.sleep(5)
                else:
                    print 'Connection failed: ' + str(e)
                    break
            except Exception as e:
                print 'Connection failed: ' + str(e)
                break

    def send_request(self, command='GET', path='/', body=None, json_type=False, content_length_zero=False):
        """ Send REST request to Dev Hub.

        Args:
            command (str): REST commands. GET, POST, PUT, DELETE
            path (str): REST path.
            body (dict):
            json_type (bool):
            content_length_zero (bool): True to add 'content-length': 0 to header.

        Returns:
            tuple: tuple[0] is int for response status code. tuple[1] is str for the response.
        """
        if body is None:
            headers = {'cookie': self._cookies}
        else:
            if json_type:
                headers = {'cookie': self._cookies, "Content-type": "application/json"}
            else:
                headers = {'cookie': self._cookies, "Content-type": "application/x-www-form-urlencoded",
                           "Accept": "text/plain"}
        if content_length_zero:
            headers['content-length'] = 0

        self._h.request(command, path, body, headers=headers)
        r = self._h.getresponse()
        result_status = r.status
        result_str = r.read()
        r.close()
        return result_status, result_str


class UtilityHelper(object):
    """ Helper class to handle common unit test ops
    """

    def __init__(self):
        # We want to hide all the detailed debug messages during unit testing.
        # If there is an error/failure in unit testing, you can reenable the debug logging to see more details.
        self.__log_helper = logging_helper.logging_helper.Logger(logger_name='backend_general')
        self.__log_helper.logger.level = logging.ERROR
        # self.__log_helper.logger.level = logging.DEBUG

        # do not change the following order

        self._un = 'root'
        self._pw = 'root'
        self._un_pro = 'root'
        self._pw_pro = 'root'
        self._un_pro_correct = 'Intel_internal_IDP3XT'
        self._pw_pro_correct = 'WbEtJDYNqp'

        self.__fn_config = "developer_hub_config"
        self.__fn_logging_config = 'logging.conf'
        self.__fn_pro_package_list = "pro_files"
        self.__fn_harden_package_list = "harden_image_packages"
        self.__fn_harden_updater_list = "harden_image_updater"
        self.__fn_harden_stig_list = "harden_image_stig_selected"
        self.__fn_harden_stig_all = "harden_image_stig.json"
        self._fn_to_be_compressed = "file_to_be_compressed.txt"
        self._fn_compressed = "file_compressed.zip"
        self._fn_uncompressed = "file_uncompressed.txt"

        self._sn = 'iot-dev-hub.service'
        self._sn_target = "node-red-experience.service"
        self._sc_running = 'active (running)'
        self._sc_dead = 'inactive (dead)'

        self._pn_info = 'python-nose'
        self._pn_test_target = 'p7zip'

        self._url_repo = 'http://jfslabigs.jf.intel.com/iotgateway/nicks_test/'
        self._name_repo = 'TestRepo'

        self._value_http = os.getenv('http_proxy', 'not_there')
        self._value_https = os.getenv('https_proxy', 'not_there')
        self._value_ftp = os.getenv('ftp_proxy', 'not_there')
        self._value_socks = os.getenv('socks_proxy', 'not_there')
        self._value_no = os.getenv('no_proxy', 'not_there')

        if not self._value_http:
            self._value_http = 'not_there'

        if not self._value_https:
            self._value_https = 'not_there'

        if not self._value_ftp:
            self._value_ftp = 'not_there'

        if not self._value_socks:
            self._value_socks = 'not_there'

        if not self._value_no:
            self._value_no = 'not_there'

        self.__cleanup_test_files()
        self.__prepare_config_file()

    def __prepare_config_file(self):
        """ Prepare for config file

        If the target (to be tested) codes use os.path.dirname(__file__),
        it will return empty if launched by our unit testing scripts.
        To work around this, we copy the config file to root / folder.
        """
        # Clean up file first
        try:
            os.remove('/' + self.__fn_config)
        except OSError:
            pass

        try:
            os.remove('/' + self.__fn_pro_package_list)
        except OSError:
            pass

        try:
            os.remove('/' + self.__fn_harden_package_list)
        except OSError:
            pass

        try:
            os.remove('/' + self.__fn_harden_updater_list)
        except OSError:
            pass

        try:
            os.remove('/' + self.__fn_harden_stig_all)
        except OSError:
            pass

        try:
            os.remove('/' + self.__fn_harden_stig_list)
        except OSError:
            pass

        try:
            os.remove('/' + self.__fn_logging_config)
        except OSError:
            pass

        try:
            if os.path.exists(self.__fn_config):
                # The way testing is launched (based on README.md) will use python folder as our base directory for
                # our unit testing scripts codes.
                with open(self.__fn_config) as f_in:
                    data_in = f_in.read()
                    with open('/' + self.__fn_config, 'w') as f_out:
                        f_out.write(data_in)
            else:
                return False
        except:
            return False

        try:
            if os.path.exists(self.__fn_pro_package_list):
                # The way testing is launched (based on README.md) will use python folder as our base directory for
                # our unit testing scripts codes.
                with open(self.__fn_pro_package_list) as f_in:
                    data_in = f_in.read()
                    with open('/' + self.__fn_pro_package_list, 'w') as f_out:
                        f_out.write(data_in)
            else:
                return False
        except:
            return False

        try:
            if os.path.exists(self.__fn_harden_package_list):
                # The way testing is launched (based on README.md) will use python folder as our base directory for
                # our unit testing scripts codes.
                with open(self.__fn_harden_package_list) as f_in:
                    data_in = f_in.read()
                    with open('/' + self.__fn_harden_package_list, 'w') as f_out:
                        f_out.write(data_in)
            else:
                return False
        except:
            return False

        try:
            if os.path.exists(self.__fn_harden_updater_list):
                # The way testing is launched (based on README.md) will use python folder as our base directory for
                # our unit testing scripts codes.
                with open(self.__fn_harden_updater_list) as f_in:
                    data_in = f_in.read()
                    with open('/' + self.__fn_harden_updater_list, 'w') as f_out:
                        f_out.write(data_in)
            else:
                return False
        except:
            return False

        try:
            if os.path.exists(self.__fn_harden_stig_all):
                # The way testing is launched (based on README.md) will use python folder as our base directory for
                # our unit testing scripts codes.
                with open(self.__fn_harden_stig_all) as f_in:
                    data_in = f_in.read()
                    with open('/' + self.__fn_harden_stig_all, 'w') as f_out:
                        f_out.write(data_in)
            else:
                return False
        except:
            return False

        try:
            if os.path.exists(self.__fn_harden_stig_list):
                # The way testing is launched (based on README.md) will use python folder as our base directory for
                # our unit testing scripts codes.
                with open(self.__fn_harden_stig_list) as f_in:
                    data_in = f_in.read()
                    with open('/' + self.__fn_harden_stig_list, 'w') as f_out:
                        f_out.write(data_in)
            else:
                return False
        except:
            return False

        try:
            if os.path.exists(os.getcwd() + '/tools/logging_helper/' + self.__fn_logging_config):
                # The way testing is launched (based on README.md) will use python folder as our base directory for
                # our unit testing scripts codes.
                with open(self.__fn_config) as f_in:
                    data_in = f_in.read()
                    with open('/' + self.__fn_config, 'w') as f_out:
                        f_out.write(data_in)
            else:
                return False
        except:
            return False

        return True

    def __cleanup_config_file(self):
        """ Cleanup temp config file

        If the target (to be tested) codes use os.path.dirname(__file__),
        it will return empty if launched by our unit testing scripts.
        To work around this, we copy the config file to root / folder.

        We need to remove this temp file after we are done testing.
        """
        try:
            os.remove('/' + self.__fn_config)
        except OSError:
            pass

        try:
            os.remove('/' + self.__fn_pro_package_list)
        except OSError:
            pass

        try:
            os.remove('/' + self.__fn_harden_package_list)
        except OSError:
            pass

        try:
            os.remove('/' + self.__fn_harden_updater_list)
        except OSError:
            pass

        try:
            os.remove('/' + self.__fn_harden_stig_list)
        except OSError:
            pass

        try:
            os.remove('/' + self.__fn_harden_stig_all)
        except OSError:
            pass

        try:
            os.remove('/' + self.__fn_logging_config)
        except OSError:
            pass

    def __cleanup_test_files(self):
        try:
            os.remove(self._fn_to_be_compressed)
        except OSError:
            pass
        try:
            os.remove(self._fn_compressed)
        except OSError:
            pass
        try:
            os.remove(self._fn_uncompressed)
        except OSError:
            pass

    def wrap_up(self):
        """ Wrap up and clean up
        """
        self.__cleanup_test_files()
        self.__cleanup_config_file()

    def set_proxy_file(self):
        """ Get environment variables and save them to proxy_env file.

        Returns:
            bool:  True if succeeded. False if failed
        """

        if self._value_http == 'not_there':
            value_http_url = ''
            value_http_port = ''
        else:
            result = manage_proxy.split_proxy_info('http_proxy=' + self._value_http)
            if len(result) == 2:
                value_http_url = result[0]
                value_http_port = result[1]
            else:
                print str(result)
                return False

        if self._value_https == 'not_there':
            value_https_url = ''
            value_https_port = ''
        else:
            result = manage_proxy.split_proxy_info('https_proxy=' + self._value_https)
            if len(result) == 2:
                value_https_url = result[0]
                value_https_port = result[1]
            else:
                print str(result)
                return False

        if self._value_ftp == 'not_there':
            value_ftp_url = ''
            value_ftp_port = ''
        else:
            result = manage_proxy.split_proxy_info('ftp_proxy=' + self._value_ftp)
            if len(result) == 2:
                value_ftp_url = result[0]
                value_ftp_port = result[1]
            else:
                print str(result)
                return False

        if self._value_socks == 'not_there':
            value_socks_url = ''
            value_socks_port = ''
        else:
            result = manage_proxy.split_proxy_info('socks_proxy=' + self._value_socks)
            if len(result) == 2:
                value_socks_url = result[0]
                value_socks_port = result[1]
            else:
                print str(result)
                return False

        if self._value_no == 'not_there':
            value_no_proxy = ''
        else:
            value_no_proxy = self._value_no

        u = manage_proxy.set_proxy_config_in_worker_process(http_url=value_http_url, http_port=value_http_port,
                                                            https_url=value_https_url, https_port=value_https_port,
                                                            ftp_url=value_ftp_url, ftp_port=value_ftp_port,
                                                            socks_url=value_socks_url, socks_port=value_socks_port,
                                                            no_proxy=value_no_proxy)
        js_data = json.loads(u)
        if js_data['status'] == 'success':
            return True
        else:
            return False
