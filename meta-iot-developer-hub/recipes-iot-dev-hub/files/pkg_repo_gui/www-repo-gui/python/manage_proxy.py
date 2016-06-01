#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

from tools import logging_helper, shell_ops, network_ops, sysinfo_ops
import json
import ast
import os
import manage_config
import manage_repo
import manage_pro_upgrade
import manage_os_update
import manage_proxy
import manage_package
import manage_worker
from manage_auth import require


def set_proxy_config_in_main_process(http_url, http_port, https_url, https_port, ftp_url,
                                     ftp_port, socks_url, socks_port, no_proxy):
    """ Writes the new proxy configuration to the /etc/environment file without overriding other environment configurations.
        This has to be done in the main process...

    Args:
        http_url (str):
        http_port (str):
        https_url (str):
        https_port (str):
        ftp_url (str):
        ftp_port (str):
        socks_url (str):
        socks_port (str):
        no_proxy (str): comma separated

    Returns:
        str: Json response with key 'status' and value 'success' if no error was encountered.
    """
    log_helper = logging_helper.logging_helper.Logger()
    network_checker = network_ops.NetworkCheck()

    proxy_mass = ''
    if http_url != '' and http_port != '':
        http_proxy = http_url + ':' + http_port
        proxy_mass += 'http_proxy=' + http_proxy + '\n'
        os.environ["http_proxy"] = http_proxy
    else:
        os.environ["http_proxy"] = ''

    if https_url != '' and https_port != '':
        https_proxy = https_url + ':' + https_port
        proxy_mass += 'https_proxy=' + https_proxy + '\n'
        os.environ["https_proxy"] = https_proxy
    else:
        os.environ["https_proxy"] = ''

    if ftp_url != '' and ftp_port != '':
        ftp_proxy = ftp_url + ':' + ftp_port
        proxy_mass += 'ftp_proxy=' + ftp_proxy + '\n'
        os.environ["ftp_proxy"] = ftp_proxy
    else:
        os.environ["ftp_proxy"] = ''

    if socks_url != '' and socks_port != '':
        socks_proxy = socks_url + ':' + socks_port
        proxy_mass += 'socks_proxy=' + socks_proxy + '\n'
        os.environ["socks_proxy"] = socks_proxy
    else:
        os.environ["socks_proxy"] = ''

    if no_proxy != '':
        no_proxy = no_proxy
        proxy_mass += 'no_proxy=' + no_proxy + '\n'
        os.environ["no_proxy"] = no_proxy
    else:
        os.environ["no_proxy"] = ''

    # Check network connections
    response = {'status': 'success', 'https_conn': 'False'}
    net_conn, net_resp = network_checker.test_network_connection(check_http=manage_config.network_check_http,
                                                                 no_rest_period=True)
    if net_conn['https_conn'] == "False" or net_conn['http_conn'] == 'False':
        log_helper.logger.debug("Proxy setting invalid: '%s'" % proxy_mass)
        manage_config.network_status['https_conn'] = net_conn['https_conn']
        manage_config.network_status['http_conn'] = net_conn['http_conn']
        return json.dumps(response)
    else:
        manage_config.network_status['https_conn'] = net_conn['https_conn']
        manage_config.network_status['http_conn'] = net_conn['http_conn']
        response['https_conn'] = 'True'
        return json.dumps(response)


def set_proxy_config_in_worker_process(http_url, http_port, https_url, https_port, ftp_url,
                                       ftp_port, socks_url, socks_port, no_proxy):
    """ Writes the new proxy configuration to the /etc/environment file without overriding other environment configurations.
        This also has to be done in the worker process...

    Args:
        http_url (str):
        http_port (str):
        https_url (str):
        https_port (str):
        ftp_url (str):
        ftp_port (str):
        socks_url (str):
        socks_port (str):
        no_proxy (str): comma separated

    Returns:
        str: Json response with key 'status' and value 'success' if no error was encountered.
    """
    log_helper = logging_helper.logging_helper.Logger()
    network_checker = network_ops.NetworkCheck()

    proxy_mass = ''
    http_proxy = ''
    https_proxy = ''
    if http_url != '' and http_port != '':
        http_proxy = http_url + ':' + http_port
        proxy_mass += 'http_proxy=' + http_proxy + '\n'
        os.environ["http_proxy"] = http_proxy
    else:
        os.environ["http_proxy"] = ''

    if https_url != '' and https_port != '':
        https_proxy = https_url + ':' + https_port
        proxy_mass += 'https_proxy=' + https_proxy + '\n'
        os.environ["https_proxy"] = https_proxy
    else:
        os.environ["https_proxy"] = ''

    if ftp_url != '' and ftp_port != '':
        ftp_proxy = ftp_url + ':' + ftp_port
        proxy_mass += 'ftp_proxy=' + ftp_proxy + '\n'
        os.environ["ftp_proxy"] = ftp_proxy
    else:
        os.environ["ftp_proxy"] = ''

    if socks_url != '' and socks_port != '':
        socks_proxy = socks_url + ':' + socks_port
        proxy_mass += 'socks_proxy=' + socks_proxy + '\n'
        os.environ["socks_proxy"] = socks_proxy
    else:
        os.environ["socks_proxy"] = ''

    if no_proxy != '':
        no_proxy = no_proxy
        proxy_mass += 'no_proxy=' + no_proxy + '\n'
        os.environ["no_proxy"] = no_proxy
    else:
        os.environ["no_proxy"] = ''

    # Add Java proxy support
    java_proxy = "_JAVA_OPTIONS='-Dhttp.proxyHost=%s -Dhttp.proxyPort=%s -Dhttps.proxyHost=%s -Dhttps.proxyPort=%s'" % (http_url, http_port, https_url, https_port)
    proxy_mass += java_proxy

    # Update proxy environment file
    update = open('/var/www/www-repo-gui/proxy_env', 'w+')
    update.write(proxy_mass)
    update.close()
    log_helper.logger.debug("New environment file: '%s'" % proxy_mass)

    # Confirm if NPM is installed and update proxy
    npm_check = os.path.isfile('/usr/bin/npm')
    if npm_check:
        if http_proxy != '':
            if '://' not in http_proxy:
                http_proxy = 'http://' + http_proxy
            shell_ops.run_command('npm config set proxy ' + http_proxy)
        else:
            shell_ops.run_command('npm config rm proxy')
        if https_proxy != '':
            if '://' not in https_proxy:
                https_proxy = 'https://' + https_proxy
            shell_ops.run_command('npm config set https-proxy ' + https_proxy)
        else:
            shell_ops.run_command('npm config rm https-proxy')

    # Set proxy for HDC
    if '://' in http_url:
        split_url = http_url.split('://')
        http_url = split_url[1]
    if http_url != '':
        manage_config.HDCSettings.set_proxy_settings_for_HDC("http", http_url, http_port)
    else:
        manage_config.HDCSettings.set_proxy_settings_for_HDC("none", "proxy.windriver.com", "3128")

    # Check network connections
    response = {'status': 'success', 'https_conn': 'False'}
    net_conn, net_resp = network_checker.test_network_connection(check_http=manage_config.network_check_http,
                                                                 no_rest_period=True)
    if net_conn['https_conn'] == "False" or net_conn['http_conn'] == 'False':
        log_helper.logger.debug("Proxy setting invalid: '%s'" % proxy_mass)
        manage_config.network_status['https_conn'] = net_conn['https_conn']
        manage_config.network_status['http_conn'] = net_conn['http_conn']
        return json.dumps(response)
    else:
        manage_config.network_status['https_conn'] = net_conn['https_conn']
        manage_config.network_status['http_conn'] = net_conn['http_conn']
        response['https_conn'] = 'True'

    # Add Flex repos if we are in flex.
    # And we do not need to check network again since we checked it already.
    pro_status = manage_pro_upgrade.ProStatus()
    if pro_status.enabled_state()['result'] == 'False':
        log_helper.logger.debug('Has network and in flex... so add flex repos.')
        # add flex repos
        os_updater = manage_os_update.OS_UPDATER(sysinfo_ops.rcpl_version, sysinfo_ops.arch)
        add_result = os_updater.add_os_repos()
        if add_result['status'] == 'fail':
            log_helper.logger.error('Failed to add flex repos.. ' + add_result['error'])

    # Update package list after proxy settings
    # And we do not need to check network again since we checked it already.
    manage_repo.update_channels(CheckNetworkAgain=False)

    # We do this at the end so that we don't run too many processes.
    # Restart Node-Red and WR-IOT-Agent for Proxy settings to take effect
    try:
        shell_ops.run_command('systemctl --no-block restart node-red-experience')
    except:
        log_helper.logger.debug("Unable to restart node-red service. Package may not be installed.")
        pass

    try:
        shell_ops.run_command('systemctl --no-block restart wr-iot-agent')
    except:
        log_helper.logger.debug("Unable to restart wr-iot-agent service. Package may not be installed.")
        pass

    return json.dumps(response)


def get_proxy_config_in_worker_process():
    """ Reads the proxy configuration from the /etc/environment location
    This should be done in Worker Process, since Worker Process should be the only process touching proxy_env file.

    Returns:
        str: String with all proxy information separated by line
    """
    log_helper = logging_helper.logging_helper.Logger()
    log_helper.logger.debug("Fetching proxy configuration...")
    http_url = http_port = https_url = https_port = ftp_url = ftp_port = socks_url = socks_port = no_proxy = ""
    with open("/var/www/www-repo-gui/proxy_env", "r") as my_file:
        content = my_file.read()
        for line in content.split("\n"):

            # Catch lines without content
            if len(line) < 13 or "#" in line:
                continue

            # no_proxy has no (url, port) pair to split
            if "no_proxy" in line:
                noproxy_split = line.split('=')
                no_proxy = noproxy_split[1]
                continue

            # Parse through sections for proxy types
            if '__JAVA_OPTIONS' not in line:
                sections = split_proxy_info(line)

            if "http_proxy" in line:
                http_url = sections[0]
                http_port = sections[1]
            if "https_proxy" in line:
                https_url = sections[0]
                https_port = sections[1]
            if "ftp_proxy" in line:
                ftp_url = sections[0]
                ftp_port = sections[1]
            if "socks_proxy" in line:
                socks_url = sections[0]
                socks_port = sections[1]

        response = ({
            'http_url': http_url,
            'http_port': http_port,
            'https_url': https_url,
            'https_port': https_port,
            'ftp_url': ftp_url,
            'ftp_port': ftp_port,
            'socks_url': socks_url,
            'socks_port': socks_port,
            'no_proxy': no_proxy
        })
        response = json.dumps(response)
        log_helper.logger.debug("Finished retrieving proxy configuration: '%s'" % response)
        return response


def split_proxy_info(string):
    """ Splits the proxy definition into 'url' and 'port'

    Args:
        string (str): String type with one line of proxy info

    Returns:
        tuple: url and port
    """
    pair = string.split('=')
    pair = pair[1].split(':')
    if len(pair) == 2:
        url = pair[0].strip('"')
        port = pair[1].strip('"')
        return url, port
    elif len(pair) == 3:
        url = pair[0].strip('"') + ':' + pair[1]
        port = pair[2].strip('"')
        return url, port


@require()
class Proxy(object):
    exposed = True

    def __init__(self):
        self.__network_checker = network_ops.NetworkCheck()
        self.__log_helper = logging_helper.logging_helper.Logger()

    def GET(self, **kwargs):
        if kwargs['request'] == "list":
            # This should be in worker process, since we want to only let worker process to touch proxy setting file.
            retrieving_work, worker_result = manage_worker.do_work(manage_worker.worker_process_message_type_get_proxy,
                                                                   kwargs)
            try:
                if retrieving_work:
                    if worker_result['status'] == 'success':
                        # {u'status': u'success',
                        #  u'message': u'{
                        #    'http_url': '',
                        #    'http_port': '',
                        #    'https_url': '',
                        #    'https_port': '',
                        #    'ftp_url': '',
                        #    'ftp_port': '',
                        #    'socks_url': '',
                        #    'socks_port': '',
                        #    'no_proxy': ''
                        #     }',
                        #  u'in_progress': False,
                        #  u'work_type': ''}
                        # move the key work result to the 1st dictionary item
                        result_dict = ast.literal_eval(worker_result['message'])
                        worker_result['http_url'] = result_dict['http_url']
                        worker_result['http_port'] = result_dict['http_port']
                        worker_result['https_url'] = result_dict['https_url']
                        worker_result['https_port'] = result_dict['https_port']
                        worker_result['ftp_url'] = result_dict['ftp_url']
                        worker_result['ftp_port'] = result_dict['ftp_port']
                        worker_result['socks_url'] = result_dict['socks_url']
                        worker_result['socks_port'] = result_dict['socks_port']
                        worker_result['no_proxy'] = result_dict['no_proxy']
            except Exception as e:
                worker_result['status'] = 'failure'
                worker_result['message'] = str(e)
            return json.dumps(worker_result)
        elif kwargs['request'] == "test":
            # read the previous result
            connection_good = False
            if self.__network_checker.get_stored_https_status() and self.__network_checker.get_stored_http_status():
                connection_good = True
            # test network
            test_result1, test_result2 = self.__network_checker.test_network_connection(check_http=manage_config.network_check_http)
            # read the current result
            connection_good_new = False
            if self.__network_checker.get_stored_https_status() and self.__network_checker.get_stored_http_status():
                connection_good_new = True

            # If the connection status changes, submit the work to worker process.
            # However, this work is an internal work and is not exposed to Front-end.
            if connection_good != connection_good_new:
                type_dict = {'type': manage_worker.worker_process_message_type_test_proxy,
                             'id': manage_worker.worker_process_internal_work_id}
                s_result = manage_worker.submit_work(work_type=type_dict, internal_work=True)
                if s_result['status'] == 'failure':
                    self.__log_helper.logger.error('Failed to submit work: ' + str(s_result))

            # Check if we need other information or not
            need_refresh = manage_worker.check_gui_refresh()
            test_result1['pro_status'] = {'result': 'NA'}
            test_result1['package_list'] = 'NA'
            test_result1['repo_list'] = 'NA'
            if need_refresh:
                # Grab the pro status
                config = manage_pro_upgrade.ProStatus()
                pro_status = config.enabled_state()
                test_result1['pro_status'] = pro_status
                # Get the new package list
                test_result1['package_list'] = manage_package.get_data()
                # Get the new repos list
                test_result1['repo_list'] = manage_repo.list_repos_non_os_only()
            return json.dumps(test_result1)

    def POST(self, **kwargs):
        str_work_type = manage_worker.worker_process_message_type_save_proxy
        worker_result = {'status': 'failure', 'message': '', 'in_progress': False,
                         'work_type': str_work_type}
        try:

            if kwargs['is_checking'] == 'True':  # checking to see if result is returned by worker process
                type_dict = {'type': str_work_type, 'id': kwargs['id']}
                worker_result = manage_worker.retrieve_work_result(work_type=type_dict)
                if worker_result['status'] == 'success':
                    # {u'status': u'success', u'message': u'{"status": "success", "https_conn": "True"}',
                    #    u'in_progress': False}
                    # move the key work result to the 1st dictionary item
                    result_dict = ast.literal_eval(worker_result['message'])
                    worker_result['work_type'] = str_work_type
                    worker_result['https_conn'] = result_dict['https_conn']

                    # check if the network test result is the same for main process and worker process
                    network_checker = network_ops.NetworkCheck()
                    if str(network_checker.get_stored_https_status()) != worker_result['https_conn']:
                        self.__log_helper.logger.error("Worker Process and Main Process have different https results.")
                        worker_result['status'] = 'failure'
                        worker_result['message'] = 'Worker Process and Main Process have different https results.'

                    # For testing purpose
                    # self.__log_helper.logger.info('https_proxy: ' + os.getenv('https_proxy', 'Not Set') + ', no_proxy:' + os.getenv('no_proxy', 'Not Set'))
                    # self.__log_helper.logger.info('npm https-proxy: ' + str(shell_ops.run_command('npm config get https-proxy')))
            else:  # Submit work to worker process
                # save proxy settings for os environment variables and
                # test network to update global network flag on the worker process
                type_dict = {'type': str_work_type, 'id': kwargs['id'],
                             'http_url': kwargs['http_url'], 'http_port': kwargs['http_port'],
                             'https_url': kwargs['https_url'], 'https_port': kwargs['https_port'],
                             'ftp_url': kwargs['ftp_url'], 'ftp_port': kwargs['ftp_port'],
                             'socks_url': kwargs['socks_url'], 'socks_port': kwargs['socks_port'],
                             'no_proxy': kwargs['no_proxy']
                             }
                worker_result = manage_worker.submit_work(work_type=type_dict)

                # If the "submit work" does not work, we should not set it in main process
                if worker_result['status'] == 'success':
                    # save proxy settings for os environment variables and
                    # test network to update global network flag on the main process
                    manage_proxy.set_proxy_config_in_main_process(http_url=kwargs['http_url'],
                                                                  http_port=kwargs['http_port'],
                                                                  https_url=kwargs['https_url'],
                                                                  https_port=kwargs['https_port'],
                                                                  ftp_url=kwargs['ftp_url'],
                                                                  ftp_port=kwargs['ftp_port'],
                                                                  socks_url=kwargs['socks_url'],
                                                                  socks_port=kwargs['socks_port'],
                                                                  no_proxy=kwargs['no_proxy'])
        except Exception as e:
            worker_result['message'] = str(e)
        return json.dumps(worker_result)
