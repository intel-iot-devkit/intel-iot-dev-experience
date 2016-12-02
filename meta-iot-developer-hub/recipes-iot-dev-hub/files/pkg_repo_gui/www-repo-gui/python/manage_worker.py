#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import cherrypy
import time
import ast
import os
import copy
import json
from multiprocessing import Process, Lock, Queue
from cherrypy.process import wspbus
from Queue import Empty, Full
from tools import logging_helper, data_ops, sysinfo_ops, shell_ops, network_ops
import manage_proxy
import manage_config
import manage_pro_upgrade
import manage_os_update
import manage_repo
import manage_package
import manage_security
import manage_self_update
import manage_service

# global variables across multiple modules
worker_process_state_starting = 'Starting'
worker_process_state_idle = 'Idling'
worker_process_state_working = 'Working'
worker_process_state_finishing = 'Finishing'
worker_process_state = worker_process_state_starting
worker_process_result = {}  # key is a string, value is a dictionary: {'status': 'failure', 'result': ''}
worker_process_work_to_be_done = None
worker_process_queue_to_worker = None
worker_process_queue_from_worker = None
worker_process_process = None
worker_process_lock = None
worker_process_message_stop = "stop"
worker_process_message_test = "test"
worker_process_message_test_2 = "test2"
worker_process_message_type_initialization = "Initial Set-up"
worker_process_message_type_save_proxy = "Set Proxy Settings"
worker_process_message_type_get_proxy = "Get Proxy Settings"
worker_process_message_type_test_proxy = "Adjust Worker Process Proxy Settings"
worker_process_message_type_pro_upgrade = "Upgrade To Pro"
worker_process_message_type_save_image = "Save OS Image"
worker_process_message_type_toggle_https = "Toggle HTTPS Connection"
worker_process_message_type_get_repo = "Get Repositories List"
worker_process_message_type_update_repo = "Update Repositories and Packages"
worker_process_message_type_add_repo = "Add Repository"
worker_process_message_type_remove_repo = "Remove Repository"
worker_process_message_type_upgrade_package = "Upgrade Package"
worker_process_message_type_install_package = "Install Package"
worker_process_message_type_remove_package = "Remove Package"
worker_process_message_type_get_package_info = "Get Package Information"
worker_process_message_type_self_upgrade = "Upgrade Developer Hub"
worker_process_message_type_control_service = "Control Service"
worker_process_message_type_check_rcpl_update = "Check RCPL OS Update"
worker_process_message_type_check_os_packages_update = "Check OS Packages Update"
worker_process_message_type_do_rcpl_update = "Perform RCPL OS Update"
worker_process_message_type_do_os_packages_update = "Perform OS Packages Update"
worker_process_work_type = worker_process_message_test
worker_process_join_timeout = 5  # unit is second
worker_process_check_message_interval = 2  # unit is second
worker_process_test_sleep_time = 5  # unit is seconds
worker_process_test_2_sleep_time = 10  # unit is seconds
worker_process_internal_work_id = 'internal'
worker_process_internal_init_work_id = 'internal init'
worker_process_GUI_refresh_time = time.time() - 1000  # make this a long time (1000 seconds) ago


class WorkerProcess(Process):
    def __init__(self, queue_to_worker, queue_from_worker):
        """ Constructor

        Args:
            queue_to_worker (Queue): The Queue used to get stuff from CherryPy process.
            queue_from_worker (Queue): The Queue used to send stuff to the CherryPy process.

        Returns:

        """
        self.__log_helper = logging_helper.logging_helper.Logger()
        self.__network_checker = network_ops.NetworkCheck()

        # Construct the parent class object
        Process.__init__(self)
        # For communication with other process
        self.__queue_to_worker = queue_to_worker
        self.__queue_from_worker = queue_from_worker
        # wspbus
        self.__bus = wspbus.Bus()
        self.__bus.subscribe("main", self.check_and_run)

        # gather system info
        data_collector = sysinfo_ops.DataCollect()
        sys_info_dict = data_collector.getDataSet()

    def handler_default(self, message, str_work_id, work_result):
        """ Handler function for not supported type
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_result['result'] = 'Do not support this work type'
        return False, False

    def handler_stop(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_stop
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        self.__bus.unsubscribe("main", self.check_and_run)
        self.__bus.exit()
        # send message to queue to indicate entering finishing state
        self.__queue_from_worker.put({'state': worker_process_state_finishing,
                                      'result': {},
                                      'id': str_work_id})
        self.__log_helper.logger.info("Worker Process ends!")
        return True, False

    def handler_test_1(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_test
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_test
        self.__log_helper.logger.debug("Doing work: " + work_type)
        time.sleep(worker_process_test_sleep_time)
        self.__log_helper.logger.debug("Finishing work: " + work_type)
        work_result['result'] = 'Test done.'
        work_result['status'] = 'success'
        return False, False

    def handler_test_2(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_test_2
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_test_2
        self.__log_helper.logger.debug("Doing work: " + work_type)
        start_time = time.time()
        index = 0
        while True:
            index += 1
            if (time.time() - start_time) > worker_process_test_2_sleep_time:
                # run for several seconds and then break
                break
        self.__log_helper.logger.debug("Finishing work: " + work_type)
        work_result['result'] = 'Test done.'
        work_result['status'] = 'success'
        return False, False

    def handler_initialization(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_initialization
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_initialization
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            # Let's not remove the old file, so that the user can see the old packages list even if conection does not work.
            # Remove old package data file.
            # manage_package.remove_data_file()

            # Add Flex repos if we are in flex and we have network.
            # Remove Flex repos (if any) if we are in pro.
            pro_status = manage_pro_upgrade.ProStatus()
            # Check network
            network_checker = network_ops.NetworkCheck()
            network_checker.test_network_connection(check_http=manage_config.network_check_http)
            if network_checker.get_stored_https_status() and network_checker.get_stored_http_status():  # yes network
                if pro_status.enabled_state()['result'] == 'False':  # flex
                    add_flex_repo = True
                    remove_flex_repo = False
                else:  # pro.
                    add_flex_repo = False
                    remove_flex_repo = True
            else:  # no network
                if pro_status.enabled_state()['result'] == 'False':  # fex
                    add_flex_repo = False
                    remove_flex_repo = False
                else:  # pro.
                    add_flex_repo = False
                    remove_flex_repo = True

            if add_flex_repo:
                self.__log_helper.logger.debug('Has network and in flex... so add flex repos.')
                os_updater = manage_os_update.OS_UPDATER(sysinfo_ops.rcpl_version, sysinfo_ops.arch)
                add_result = os_updater.add_os_repos()
                if add_result['status'] == 'fail':
                    self.__log_helper.logger.error('Failed to add flex repos.. ' + add_result['error'])
                else:
                    pass

            if remove_flex_repo:
                self.__log_helper.logger.debug('Removing Flex repos since we are in pro.')
                os_updater = manage_os_update.OS_UPDATER(sysinfo_ops.rcpl_version, sysinfo_ops.arch, no_network_ops=True)
                remove_result = os_updater.remove_os_repos(do_update=False, do_pro=False)
                if remove_result['status'] == 'fail':
                    self.__log_helper.logger.error('Failed to remove flex repos.. ' + remove_result['error'])
                else:
                    pass

            # Add default repo and build packages list
            manage_repo.configure_default_repo(check_network_again=False)

            manage_package.set_signature_verification_status(True)

            work_result['result'] = ''
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, False

    def handler_save_proxy(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_save_proxy
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_save_proxy
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            p_result = manage_proxy.set_proxy_config_in_worker_process(message.get('http_url', ''),
                                                                       message.get('http_port', ''),
                                                                       message.get('https_url', ''),
                                                                       message.get('https_port', ''),
                                                                       message.get('ftp_url', ''),
                                                                       message.get('ftp_port', ''),
                                                                       message.get('socks_url', ''),
                                                                       message.get('socks_port', ''),
                                                                       message.get('no_proxy', ''))
            work_result['result'] = p_result
            work_result['status'] = 'success'

            # For test purpose
            # self.__log_helper.logger.info('https_proxy: ' + os.getenv('https_proxy', 'Not Set') + ', no_proxy:' + os.getenv('no_proxy', 'Not Set'))
            # self.__log_helper.logger.info('npm https-proxy: ' + str(shell_ops.run_command('npm config get https-proxy')))
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, True

    def handler_get_proxy(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_get_proxy
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_get_proxy
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            p_result = manage_proxy.get_proxy_config_in_worker_process()
            work_result['result'] = p_result
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, False

    def handler_test_proxy(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_test_proxy
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_test_proxy
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
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

            # if the result is from False to True,
            #     then if we are in Flex, then if Flex repos are not added, add them.
            #     then if we are in Pro, then rebuild the package list
            if (not connection_good) and connection_good_new:
                pro_status = manage_pro_upgrade.ProStatus()
                self.__log_helper.logger.info("Update info for Flex or Pro due to network changes!")
                if pro_status.enabled_state()['result'] == 'False':  # flex
                    os_updater = manage_os_update.OS_UPDATER(sysinfo_ops.rcpl_version, sysinfo_ops.arch)
                    add_result = os_updater.add_os_repos()
                    if add_result['status'] == 'fail':
                        self.__log_helper.logger.error('Failed to add flex repos.. ' + add_result['error'])
                    else:
                        # Update package list
                        # And we do not need to check network again since we checked it already.
                        manage_repo.update_channels(CheckNetworkAgain=False)
                else:  # pro
                    # Update package list
                    # And we do not need to check network again since we checked it already.
                    manage_repo.update_channels(CheckNetworkAgain=False)
            work_result['result'] = ''
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, True

    def handler_upgrade_to_pro(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_pro_upgrade
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_pro_upgrade
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            flex_to_pro = manage_pro_upgrade.ProRepo()
            u_result = flex_to_pro.os_upgrade(message.get('username', ''), message.get('password', ''))
            work_result['result'] = u_result
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, True

    def handler_save_harden_image(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_save_image
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_save_image
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            # message = {
            #        'harden_type'                : 'standard'/'custom',
            #        'usb_device'                 : _usb_device,
            #        'packages_removed'           : ['node', 'node-red-experience', .....],
            #        'updaters'                   : ['/usr/bin/wr-iot-watchdog', '/usr/bin/wr-iot-agent', .......],
            #        'users'                      : [{'name': '', 'pw': ''}, {'name': '', 'pw': ''}, ......],
            #        'stig'                       : ['V-50549', 'V-50551', ....],
            #        'admin_password'             : '',
            #        'mec_password'               : ''
            #    };
            harden_type = message.get('harden_type', 'standard')
            if harden_type == 'standard':
                sa = manage_security.SecurityAutomationWorker()
                sa.standard_harden_image(message.get('usb_device', ''),
                                       message.get('admin_password', ''),
                                       message.get('mec_password', ''))
                s_result = sa.create_harden_image()
            else:
                sa = manage_security.SecurityAutomationWorker()
                sa.custom_harden_image(message.get('usb_device', ''),
                                       message.get('packages_removed', []),
                                       message.get('updaters', []),
                                       message.get('users', []))
                s_result = sa.create_harden_image()

                # replace the default config data with the new input
                manage_security.save_default_custom_harden_data(message.get('packages_removed', []),
                                                                message.get('updaters', []))

            work_result['result'] = s_result
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, False

    def handler_toggle_https(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_toggle_https
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_toggle_https
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            manage_config.configure_nginx_https(message.get('enable', ''))
            manage_config.add_secure_http_to_config_file(message.get('enable', ''))
            work_result['result'] = ''
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, True

    def handler_get_repo(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_get_repo
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_get_repo
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            l_result = manage_repo.list_repos_non_os_only()
            if l_result is None:
                work_result['result'] = 'Cannot access repositories tracking file!'
                work_result['status'] = 'failure'
            else:
                work_result['result'] = json.dumps(l_result)
                work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, False

    def handler_update_repo(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_update_repo
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_update_repo
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            u_result = manage_repo.update_channels()
            work_result['result'] = u_result
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, False

    def handler_add_repo(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_add_repo
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_add_repo
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            a_result = manage_repo.add_repo(message.get('url', ''),
                                            message.get('username', ''),
                                            message.get('password', ''),
                                            message.get('name', ''), from_GUI=True)
            work_result['result'] = a_result
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, True

    def handler_remove_repo(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_remove_repo
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_remove_repo
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            r_result = manage_repo.remove_repo(message.get('name', ''), UpdateCache=True, from_GUI=True)
            work_result['result'] = r_result
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, True

    def handler_upgrade_package(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_upgrade_package
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_upgrade_package
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            p_result = manage_package.package_transaction("upgrade", message)

            # If this upgraded 1 package successfully, grab the latest info
            if 'package' in message:
                if message['package'] != 'all':
                    temp_data = json.loads(p_result)
                    if temp_data['status'] == 'success':
                        # get package information
                        p_info = manage_package.get_package_info(message['package'])
                        p_data = json.loads(p_info)
                        temp_data['p_info'] = p_data
                        p_result = json.dumps(temp_data)

            work_result['result'] = p_result
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, True

    def handler_install_package(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_install_package
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_install_package
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            p_result = manage_package.package_transaction("install", message)
            work_result['result'] = p_result
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, True

    def handler_remove_package(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_remove_package
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_remove_package
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            p_result = manage_package.package_transaction("remove", message)
            work_result['result'] = p_result
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, True

    def handler_get_package_info(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_get_package_info
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_get_package_info
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            p_result = manage_package.get_package_info(message.get('name', ''))
            work_result['result'] = p_result
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, False

    def handler_upgrade_dev_hub(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_self_upgrade
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_self_upgrade
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            devhub = manage_self_update.DevHubUpdate()
            u_result = devhub.update()
            work_result['result'] = json.dumps(u_result)
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, True

    def handler_control_service(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_control_service
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_control_service
        self.__log_helper.logger.info("Doing work: " + work_type)
        try:
            s_result = manage_service.ServiceSupport.control_service(message)
            work_result['result'] = s_result
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, True

    def handler_check_rcpl_update(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_check_rcpl_update
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_check_rcpl_update
        self.__log_helper.logger.info("Doing work: " + work_type)
        c_result = {'status': 'failure', 'message': '', 'update': False}
        try:
            updater = manage_os_update.OS_UPDATER(sysinfo_ops.rcpl_version, sysinfo_ops.arch,
                                                  user_name=message.get('username', ''),
                                                  password=message.get('password', ''))
            error_message = updater.get_error()
            if error_message is None:
                c_result['update'] = updater.higher_version
                c_result['status'] = 'success'
            else:
                c_result['message'] = str(error_message)
            work_result['result'] = json.dumps(c_result)
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, False

    def handler_check_os_packages_update(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_check_os_packages_update
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_check_os_packages_update
        self.__log_helper.logger.info("Doing work: " + work_type)
        c_result = {'status': 'failure', 'packages': [], 'package_update': False, 'message': ''}
        try:
            get_result = manage_package.get_updates_for_os_packages()
            c_result['package_update'] = get_result['package_update']
            c_result['packages'] = get_result['packages']
            # Check for error
            if get_result['message']:
                c_result['status'] = 'failure'
                c_result['message'] = get_result['message']
                self.__log_helper.logger.error(get_result['message'])
            else:
                c_result['status'] = 'success'
            work_result['result'] = json.dumps(c_result)
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, False

    def handler_do_rcpl_update(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_do_rcpl_update
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_do_rcpl_update
        self.__log_helper.logger.info("Doing work: " + work_type)
        c_result = {'status': 'failure', 'message': ''}
        try:
            # get node-red-experience status, stop node-red-experience service
            status_node_red = manage_service.ServiceSupport.stop_node_red_experience()

            updater = manage_os_update.OS_UPDATER(sysinfo_ops.rcpl_version, sysinfo_ops.arch,
                                                  user_name=message.get('username', ''),
                                                  password=message.get('password', ''))
            error_message = updater.get_error()
            if error_message is None:
                # osUpdate needs to return the same dict as this function.
                c_result = updater.osUpdate(user_name=message.get('username', ''),
                                            password=message.get('password', ''))
                # Do not do system reboot here..... Let's wait for GUI to tell us to reboot.
                # If osUpdate succeeded, schedule a system reboot
                # if c_result['status'] == 'success':
                #    process = subprocess.Popen('sleep 5s; sudo shutdown -r now', shell=True)
                #    pass
            else:
                c_result['message'] = str(error_message)

            # If failure, start node-red-experience service if it was started before.
            # If success, the gateway will be rebooted by Dev Hub, so do nothing.
            if c_result['status'] == 'failure':
                if status_node_red['status'] == 'success':
                    if status_node_red['is_active']:
                        manage_service.ServiceSupport.start_node_red_experience()

            work_result['result'] = json.dumps(c_result)
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, False

    def handler_do_os_packages_update(self, message, str_work_id, work_result):
        """ Handler function for worker_process_message_type_do_os_packages_update
        Args:
            message (dict): the parameters related to this work
            str_work_id (str): the work id
            work_result (dict): mutable, this is our output result

        Returns:
            tuple:
                1st: bool: True to for the calling function to return immediately
                2nd: bool: True if this operation should trigger a GUI refresh for other Dev HUB GUI user.
        """
        work_type = worker_process_message_type_do_os_packages_update
        self.__log_helper.logger.info("Doing work: " + work_type)
        c_result = {'status': 'failure', 'message': '', 'p_list': []}
        try:
            # get node-red-experience status, stop node-red-experience service
            status_node_red = manage_service.ServiceSupport.stop_node_red_experience()

            # do_updates_for_os_packages needs to return the same dict as this function.
            c_result = manage_package.do_updates_for_os_packages()

            # If failure, start node-red-experience service if it was started before.
            # If success, the gateway will be rebooted by Dev Hub, so do nothing.
            if c_result['status'] == 'failure':
                if status_node_red['status'] == 'success':
                    if status_node_red['is_active']:
                        manage_service.ServiceSupport.start_node_red_experience()

            work_result['result'] = json.dumps(c_result)
            work_result['status'] = 'success'
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            work_result['result'] = str(e)
        self.__log_helper.logger.info("Finishing work: " + work_type)
        return False, True

    def dict_mapping_for_handler(self, work_type):
        """ Return the target handler for the work_type
        Args:
            work_type (str): work type

        Returns:
            function: the mapped function
        """
        mapper = {
            worker_process_message_stop: self.handler_stop,
            worker_process_message_test: self.handler_test_1,
            worker_process_message_test_2: self.handler_test_2,
            worker_process_message_type_initialization: self.handler_initialization,
            worker_process_message_type_save_proxy: self.handler_save_proxy,
            worker_process_message_type_get_proxy: self.handler_get_proxy,
            worker_process_message_type_test_proxy: self.handler_test_proxy,
            worker_process_message_type_pro_upgrade: self.handler_upgrade_to_pro,
            worker_process_message_type_save_image: self.handler_save_harden_image,
            worker_process_message_type_toggle_https: self.handler_toggle_https,
            worker_process_message_type_get_repo: self.handler_get_repo,
            worker_process_message_type_update_repo: self.handler_update_repo,
            worker_process_message_type_add_repo: self.handler_add_repo,
            worker_process_message_type_remove_repo: self.handler_remove_repo,
            worker_process_message_type_upgrade_package: self.handler_upgrade_package,
            worker_process_message_type_install_package: self.handler_install_package,
            worker_process_message_type_remove_package: self.handler_remove_package,
            worker_process_message_type_get_package_info: self.handler_get_package_info,
            worker_process_message_type_self_upgrade: self.handler_upgrade_dev_hub,
            worker_process_message_type_control_service: self.handler_control_service,
            worker_process_message_type_check_rcpl_update: self.handler_check_rcpl_update,
            worker_process_message_type_check_os_packages_update: self.handler_check_os_packages_update,
            worker_process_message_type_do_rcpl_update: self.handler_do_rcpl_update,
            worker_process_message_type_do_os_packages_update: self.handler_do_os_packages_update
        }
        handler_func = mapper.get(work_type, self.handler_default)
        return handler_func

    def check_and_run(self):
        """ Check Queue and process message from other process.

        The queue message (received) is a dictionary:
            {'type': '', 'id': '', .....}

        The queue message (sent out) is a dictionary:
            {'result': {}, 'id': '', 'GUI_refresh': True/False}

        Returns:

        """
        try:
            message = self.__queue_to_worker.get_nowait()
        except Empty:
            # no communication from other process
            # self.__log_helper.logger.info('no communicate yet.')
            return

        # There is communication from other process
        # 'status' is to indicate if we successfully parsed the message.
        # 'result' has the real result of the target work.
        work_result = {'status': 'failure', 'result': ''}
        str_work_id = ''
        h_result2 = False
        try:
            if type(message) is dict:
                if ('type' in message) and ('id' in message):
                    work_type = message['type']
                    str_work_id = message['id']

                    target_handler = self.dict_mapping_for_handler(work_type=work_type)
                    h_result1, h_result2 = target_handler(message=message, str_work_id=str_work_id, work_result=work_result)
                    if h_result1:
                        return
                else:
                    # no id, do not need to send message to queue
                    self.__log_helper.logger.error('Did not specify the type or the id in message: ' + str(message))
                    return
            else:
                # no id, do not need to send message to queue
                self.__log_helper.logger.error('The message is not a dictionary. ' + str(message))
                return
        except Exception as e:
            # no id, do not need to send message to queue
            self.__log_helper.logger.error(str(e))
            return

        # send message to queue
        # block indefinitely, until we can put it on the queue.
        self.__queue_from_worker.put({'result': work_result,
                                      'id': str_work_id,
                                      'GUI_refresh': h_result2})

    def run(self):
        """ Overwrite the Process's run method.

        Returns:

        """
        # This Process is always running until the following condition is true.
        #         After waiting for the EXITING state, it also waits for all threads
        #         to terminate, and then calls os.execv if self.execv is True. This
        #         design allows another thread to call bus.restart, yet have the main
        #         thread perform the actual execv call (required on some platforms).

        # Use wspbus's block to trigger main channel signal every interval seconds.
        self.__bus.start()
        self.__bus.block(interval=worker_process_check_message_interval)  # internal unit is second


def start():
    """ Start the singleton worker process

    Returns:

    """
    global worker_process_queue_to_worker
    global worker_process_queue_from_worker
    global worker_process_process
    global worker_process_state
    global worker_process_work_to_be_done
    global worker_process_lock
    log_helper = logging_helper.logging_helper.Logger()
    if worker_process_process is None:
        log_helper.logger.info("Staring worker process.")
        worker_process_lock = Lock()
        worker_process_queue_to_worker = Queue()
        worker_process_queue_from_worker = Queue()
        worker_process_work_to_be_done = set()
        worker_process_process = WorkerProcess(queue_to_worker=worker_process_queue_to_worker,
                                               queue_from_worker=worker_process_queue_from_worker)
        worker_process_process.start()

        # update state
        worker_process_lock.acquire()
        worker_process_state = worker_process_state_idle
        worker_process_lock.release()
    else:
        log_helper.logger.info("Do not start worker process since it is already started.")


def finish():
    """ Finish the singleton worker process

    Returns:

    """
    global worker_process_queue_to_worker
    global worker_process_process
    global worker_process_state
    global worker_process_lock
    global worker_process_join_timeout
    log_helper = logging_helper.logging_helper.Logger()
    if not (worker_process_process is None):
        log_helper.logger.info("Finishing worker process.")
        work_type = {'type': worker_process_message_stop, 'id': ''}
        worker_process_queue_to_worker.put(work_type)

        # update state
        worker_process_lock.acquire()
        worker_process_state = worker_process_state_finishing
        worker_process_lock.release()

        worker_process_process.join(worker_process_join_timeout)
        worker_process_process.terminate()
        worker_process_process = None  # This will trigger re-construct other objects.

        log_helper.logger.info("Finished worker process.")
    else:
        log_helper.logger.info("No worker process to finish.")


def read_process_queue_message():
    """ Read and process queue messages sent by the singleton worker process.
    Returns:

    """
    global worker_process_queue_from_worker
    global worker_process_process
    global worker_process_state
    global worker_process_lock
    global worker_process_result
    global worker_process_work_to_be_done
    global worker_process_GUI_refresh_time
    log_helper = logging_helper.logging_helper.Logger()

    # read until there is none.
    while True:
        # read queue message
        try:
            message_dict = worker_process_queue_from_worker.get_nowait()
            if type(message_dict) is dict:
                # update the state and result based on message
                worker_process_lock.acquire()

                if ('id' in message_dict) and ('result' in message_dict) and ('GUI_refresh' in message_dict):
                    if message_dict['id'] != '':
                        # log_helper.logger.info("got result for work id " + message_dict['id'])
                        # remove the entry from to-be-done set
                        worker_process_work_to_be_done.discard(message_dict['id'])
                        # if to-be-done set is empty, update state to idle
                        if len(worker_process_work_to_be_done) == 0:
                            worker_process_state = worker_process_state_idle
                        # add to results dictionary
                        worker_process_result[message_dict['id']] = message_dict['result']
                        # if needed, update the GUI refresh request time
                        if message_dict['GUI_refresh']:
                            worker_process_GUI_refresh_time = time.time()

                worker_process_lock.release()
                log_helper.logger.debug('Update state and result, based on queue message. ' + str(message_dict))

            else:
                log_helper.logger.error('The message from worker process is not dict type: ' + str(message_dict))
        except Empty:
            # no communication from other process, so no change
            break


def submit_work(work_type, internal_work=False):
    """ Submit the work to Worker Process

    The queue message has the format [work type],,[work id].

    If this is internal work, we will submit the work to queue no matter what.
    If this is not internal work, we will not submit if worker process is already working.

    Args:
        work_type (dict): {'type': '', 'id': '', .....}
        internal_work (bool): False if this is not internal work.

    Returns:
        dict: {'status': 'failure', 'message': '', 'in_progress': False, 'work_type': ''} or
              {'status': 'success', 'message': '', 'in_progress': False, 'work_type': ''}
    """
    global worker_process_queue_to_worker
    global worker_process_process
    global worker_process_state
    global worker_process_lock
    global worker_process_work_type
    global worker_process_work_to_be_done
    result = {'status': 'failure', 'message': '', 'in_progress': False, 'work_type': ''}
    log_helper = logging_helper.logging_helper.Logger()

    # extend the session expiration time,  reset the expiration time
    # this will take effect from the next request
    cherrypy.config.update({'tools.sessions.timeout': manage_config.cherrypy_session_timeout_chosen})

    if not (worker_process_process is None):
        if not ('type' in work_type):
            result['message'] = 'Did not specify work type!!'
            return result

        # read and process queue message
        read_process_queue_message()

        worker_process_lock.acquire()

        first_check_ok = False
        is_busy = False
        if internal_work:
            first_check_ok = True
            if worker_process_state != worker_process_state_idle:
                is_busy = True
        else:
            # get worker process state
            if worker_process_state == worker_process_state_idle:
                first_check_ok = True
            else:
                # return the work type.
                first_check_ok = False
                is_busy = True
                result['message'] = "Another important work " + worker_process_work_type + " is in progress! Please wait and try again later!"
                result['in_progress'] = True
                result['work_type'] = worker_process_work_type

        if first_check_ok:
            if 'type' in work_type and 'id' in work_type:
                if work_type['id'] != '':
                    if not (work_type['id'] in worker_process_work_to_be_done):
                        try:
                            # submit work
                            if internal_work:
                                worker_process_queue_to_worker.put(work_type)  # wait when queue is full
                            else:
                                worker_process_queue_to_worker.put_nowait(work_type)  # do not wiat
                            # Update state
                            worker_process_state = worker_process_state_working
                            # Add entry to to be done set
                            worker_process_work_to_be_done.add(work_type['id'])
                            # Record the work type.
                            # If this is internal work and some other work is already running,
                            #   do not change work type
                            if internal_work and is_busy:
                                log_helper.logger.debug("This is internal work and an earlier work is still running, so do not change work type.")
                            else:
                                worker_process_work_type = work_type['type']
                            result['status'] = 'success'
                        except Full:
                            result['message'] = "Communicate queue to worker process is full. Try again later."
                            result['in_progress'] = False
                            result['work_type'] = worker_process_work_type
                    else:
                        # If the id is internal work for network change, change the message.
                        if work_type['id'] == worker_process_internal_work_id:
                            result['message'] = "The internal work is already queued. Discard this one. This is not an error."
                        else:
                            result['message'] = "The passed-in work_type has duplicate id."
                        result['in_progress'] = False
                        result['work_type'] = worker_process_work_type
                else:
                    result['message'] = "The passed-in work_type has empty id."
                    result['in_progress'] = False
                    result['work_type'] = worker_process_work_type
            else:
                result['message'] = "The passed-in work_type does not have type and id."
                result['in_progress'] = False
                result['work_type'] = worker_process_work_type

        worker_process_lock.release()
    else:
        result['message'] = 'No Worker Process was created!!'
    return result


def retrieve_work_result(work_type):
    """ Retrieve the work results done by Worker Process

    Args:
        work_type (dict): {'type': '', 'id': ''}

    Returns:
        dict: {'status': 'failure', 'message': 'error messsage', 'in_progress': False/True} or
              {'status': 'success', 'message': 'dict of the direct work result in str', 'in_progress': False}
    """
    global worker_process_process
    global worker_process_state
    global worker_process_lock
    global worker_process_work_type
    log_helper = logging_helper.logging_helper.Logger()
    result = {'status': 'failure', 'message': '', 'in_progress': False}
    if not (worker_process_process is None):
        if ('type' in work_type) and ('id' in work_type):
            work_id = work_type['id']
            type_value = work_type['type']

            # read and process queue message
            read_process_queue_message()

            worker_process_lock.acquire()
            if work_id in worker_process_result:  # if the result with the work_id is in
                result['status'] = 'success'
                result['message'] = str(worker_process_result[work_id])
                worker_process_result.pop(work_id, None)  # delete the result dictionary
                log_helper.logger.debug("The result dictionary has length: " + str(len(worker_process_result)))
            else:
                if worker_process_state == worker_process_state_idle:
                    result['status'] = 'failure'
                    result['in_progress'] = False
                    result['message'] = 'Worker Process (in idle) does not have the target result!'
                else:
                    if worker_process_work_type == type_value:  # The work is still running.
                        result['status'] = 'failure'
                        result['in_progress'] = True
                    else:
                        result['status'] = 'failure'
                        result['in_progress'] = False
                        result['message'] = 'Worker Process (working on another work) does not have the target result!'
            worker_process_lock.release()
        else:
            result['message'] = 'Input dictionary does not have type and id!! ' + str(work_type)
    else:
        result['message'] = 'No Worker Process was created!!'

    if result['status'] == 'success':  # If result['status'] is 'success',
        #  {u'status': u'success',
        #   u'message': u'{\'status\': \'success\', \'result\': \'{"status": "success", "https_conn": "True"}\'}',
        #   u'in_progress': False}
        # Clean them out to bring the real work result to 1st level.
        # The result back to the Front End should have only one layer dictionary.
        result_2 = {'status': 'failure', 'message': '', 'in_progress': False}
        try:
            result_dict = ast.literal_eval(result['message'])
            # copy Worker Process Queue message results
            result_2['status'] = result_dict['status']
            result_2['message'] = result_dict['result']
        except Exception as e:
            log_helper.logger.error(str(e))
            result_2['status'] = 'failure'
            result_2['message'] = str(e)
        return result_2
    else:
        return result


def get_worker_process_state():
    global worker_process_process
    global worker_process_state
    global worker_process_lock

    # read and process queue message
    read_process_queue_message()

    if not (worker_process_process is None):
        worker_process_lock.acquire()
        state = worker_process_state
        worker_process_lock.release()
        return state
    else:
        return worker_process_state_starting


def get_worker_process_state_and_type():
    global worker_process_process
    global worker_process_state
    global worker_process_work_type
    global worker_process_lock

    if not (worker_process_process is None):
        worker_process_lock.acquire()
        state = worker_process_state
        work_type = worker_process_work_type
        worker_process_lock.release()
        return state, work_type
    else:
        return worker_process_state_starting, worker_process_message_test


def check_gui_refresh():
    """ Read and process queue messages sent by the singleton worker process.
    Returns:
        bool: True if GUI needs a refresh.
    """
    global worker_process_lock
    global worker_process_GUI_refresh_time

    try:
        elapsed_time = 0
        worker_process_lock.acquire()
        elapsed_time = time.time() - worker_process_GUI_refresh_time
        worker_process_lock.release()

        # The periodic network checking is 60 seconds (defined at front end).
        # We give it larger value to include some delay.
        if 0 < elapsed_time < 70:
            return True
        else:
            return False
    except:
        # no communication from other process, so no change
        return False


def do_work(work_type, parameters):
    """ Helper function to do submit work or retrieve work

    Args:
        work_type (str): work type string
        parameters (dict): input data

    Returns:
        tuple:  1st item bool: True if this is retrieving work.
                2nd item dict: {'status': 'failure', 'message': '', 'in_progress': True/False, 'work_type': ''}
    """

    str_work_type = work_type
    retrieving_work = False
    worker_result = {'status': 'failure', 'message': '', 'in_progress': False,
                     'work_type': str_work_type}
    try:
        if parameters['is_checking'] == 'True':   # checking to see if result is returned by worker process
            type_dict = {'type': str_work_type, 'id': parameters['id']}
            worker_result = retrieve_work_result(work_type=type_dict)
            worker_result['work_type'] = str_work_type
            retrieving_work = True
        else:  # Submit work to worker process
            type_dict = copy.deepcopy(parameters)
            type_dict['type'] = str_work_type
            worker_result = submit_work(work_type=type_dict)

    except Exception as e:
        worker_result['message'] = str(e)

    return retrieving_work, worker_result

