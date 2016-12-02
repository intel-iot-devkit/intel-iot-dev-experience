#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import json
import urllib
import ast
import time
import unit_test_utility
from tools import sysinfo_ops
import manage_proxy
import manage_os_update
import manage_repo
import manage_pro_upgrade


class TestOSUpdate(unittest.TestCase):
    """ OS_UPDATER test case
    """
    # prepare to test
    def setUp(self):
        """ Initial setup
        """
        self._utility_helper = unit_test_utility.UtilityHelper()

        self._data_collector = sysinfo_ops.DataCollect()
        self._data_collector.getDataSet()

    # wrap up test
    def tearDown(self):
        """ Wrap up
        """
        self._utility_helper.wrap_up()

    def test_os_update(self):
        """ Test OS_UPDATER::getIndex, processInfo, findNext, osUpdate
        """
        print ""  # better print format
        print "Running test_os_update"
        # from tools import logging_helper
        # import logging
        # self.__log_helper = logging_helper.logging_helper.Logger(logger_name='backend_general')
        # self.__log_helper.logger.level = logging.DEBUG

        update_handler = manage_os_update.OS_UPDATER(sysinfo_ops.rcpl_version, sysinfo_ops.arch)

        result = update_handler.osUpdate()
        self.assertTrue('status' in result, 'status key is not in result ' + str(result))

        u = update_handler.remove_os_repos(do_update=True, do_pro=False)
        self.assertEqual(u['status'], 'success', 'remove_os_repos failed: ' + str(u['error']))

    def test_repos(self):
        """ Test remove_os_repos and add_os_repos
        """
        print ""  # better print format
        print "Running test_repos"
        # from tools import logging_helper
        # import logging
        # self.__log_helper = logging_helper.logging_helper.Logger(logger_name='backend_general')
        # self.__log_helper.logger.level = logging.DEBUG

        update_handler = manage_os_update.OS_UPDATER(sysinfo_ops.rcpl_version, sysinfo_ops.arch)
        # remove first
        u = update_handler.remove_os_repos(do_update=True, do_pro=False)
        self.assertEqual(u['status'], 'success', 'remove_os_repos failed: ' + str(u['error']))
        print str(manage_repo.list_repos())
        # check
        u = update_handler.check_os_repos_existed(check_pro=False)
        self.assertFalse(u, 'There should not be any flex repos.')
        # add
        u = update_handler.add_os_repos()
        self.assertEqual(u['status'], 'success', 'add_os_repos failed: ' + str(u['error']))
        print str(manage_repo.list_repos())
        # check
        u = update_handler.check_os_repos_existed(check_pro=False)
        self.assertTrue(u, 'There should be flex repos.')
        # remove
        u = update_handler.remove_os_repos(do_update=True, do_pro=False)
        self.assertEqual(u['status'], 'success', 'remove_os_repos failed: ' + str(u['error']))
        print str(manage_repo.list_repos())
        # check
        u = update_handler.check_os_repos_existed(check_pro=False)
        self.assertFalse(u, 'There should not be any flex repos.')


class TestCherryPyAPIOSUpdate(unittest.TestCase):
    """ manage_os_update test case
    """
    # prepare to test
    def setUp(self):
        """ Initial setup
        """
        self._utility_helper = unit_test_utility.UtilityHelper()
        self._connection_handler = unit_test_utility.HttpConnectionHelper(service_name=self._utility_helper._sn,
                                                                          status_running=self._utility_helper._sc_running,
                                                                          status_dead=self._utility_helper._sc_dead,
                                                                          username=self._utility_helper._un,
                                                                          password=self._utility_helper._pw)

    # wrap up test
    def tearDown(self):
        """ Wrap up
        """
        self._utility_helper.wrap_up()

    def __set_proxy_file(self):
        """ Get environment variables and save them to proxy_env file.

        Returns:
            bool:  True if succeeded. False if failed
        """

        if self._utility_helper._value_http == 'not_there':
            value_http_url = ''
            value_http_port = ''
        else:
            result = manage_proxy.split_proxy_info('http_proxy=' + self._utility_helper._value_http)
            if len(result) == 2:
                value_http_url = result[0]
                value_http_port = result[1]
            else:
                print str(result)
                return False

        if self._utility_helper._value_https == 'not_there':
            value_https_url = ''
            value_https_port = ''
        else:
            result = manage_proxy.split_proxy_info('https_proxy=' + self._utility_helper._value_https)
            if len(result) == 2:
                value_https_url = result[0]
                value_https_port = result[1]
            else:
                print str(result)
                return False

        if self._utility_helper._value_ftp == 'not_there':
            value_ftp_url = ''
            value_ftp_port = ''
        else:
            result = manage_proxy.split_proxy_info('ftp_proxy=' + self._utility_helper._value_ftp)
            if len(result) == 2:
                value_ftp_url = result[0]
                value_ftp_port = result[1]
            else:
                print str(result)
                return False

        if self._utility_helper._value_socks == 'not_there':
            value_socks_url = ''
            value_socks_port = ''
        else:
            result = manage_proxy.split_proxy_info('socks_proxy=' + self._utility_helper._value_socks)
            if len(result) == 2:
                value_socks_url = result[0]
                value_socks_port = result[1]
            else:
                print str(result)
                return False

        if self._utility_helper._value_no == 'not_there':
            value_no_proxy = ''
        else:
            value_no_proxy = self._utility_helper._value_no

        js_data = {'id': '12345_proxy', 'is_checking': 'False',
                   'http_url': value_http_url, 'http_port': value_http_port,
                   'https_url': value_https_url, 'https_port': value_https_port,
                   'ftp_url': value_ftp_url, 'ftp_port': value_ftp_port,
                   'socks_url': value_socks_url, 'socks_port': value_socks_port,
                   'no_proxy': value_no_proxy}
        params = urllib.urlencode(js_data)
        connection_result = self._connection_handler.send_request(command='POST', path='/api/proxy', body=params)
        result = True
        if connection_result[0] == 200:
            js_data = json.loads(connection_result[1])
            if not (js_data['status'] == 'success'):
                result = False
            else:
                while True:
                    js_data = {'id': '12345_proxy', 'is_checking': 'True'}
                    params = urllib.urlencode(js_data)
                    connection_result = self._connection_handler.send_request(command='POST', path='/api/proxy', body=params)
                    js_data = json.loads(connection_result[1])
                    if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                        time.sleep(5)
                    else:
                        break
        else:
            result = False
        return result

    def test_os_update_post_check(self):
        """ Test OSUpdate::POST
        """
        print ""  # better print format
        print "Running test_os_update_post_check"
        self.assertTrue(self._connection_handler._auth, '/api/auth POST failed!')

        # set up proxy file.
        self.assertTrue(self.__set_proxy_file(), 'Set up proxy /api/proxy POST failed!')

        # get os data to set the arch value. otherwise, /api/osup POST will fail
        connection_result = self._connection_handler.send_request(command='GET',
                                                                  path='/api/osc')
        self.assertEqual(connection_result[0], 200,
                         '/api/osc GET: failed with status ' + str(connection_result[0]) + str(connection_result[1]))

        # make the call
        data = json.dumps({'id': '12345_rcpl_check', 'is_checking': 'False',
                           'type': 'check',
                           'request': 'rcpl',
                           'username': self._utility_helper._un_pro_correct,
                           'password': self._utility_helper._pw_pro_correct})
        connection_result = self._connection_handler.send_request(command='POST',
                                                                  path='/api/osup',
                                                                  body=data,
                                                                  json_type=True)
        self.assertEqual(connection_result[0], 200,
                         '/api/osup POST check, rcpl: failed with status ' + str(connection_result[0]) + str(connection_result[1]))
        dic_data = json.loads(connection_result[1])
        self.assertEqual(dic_data['status'], 'success', 'RCPL Check: The status should be success. ' + str(dic_data))
        self.assertEqual(dic_data['in_progress'], False, 'RCPL Check: The in_progress should be False. ' + str(dic_data))
        while True:
            data = json.dumps({'id': '12345_rcpl_check', 'is_checking': 'True',
                               'type': 'check',
                               'request': 'rcpl',
                               'username': self._utility_helper._un_pro_correct,
                               'password': self._utility_helper._pw_pro_correct})
            connection_result = self._connection_handler.send_request(command='POST',
                                                                      path='/api/osup',
                                                                      body=data,
                                                                      json_type=True)
            self.assertEqual(connection_result[0], 200,
                             '/api/osup POST check, rcpl: failed with status ' + str(connection_result[0]) + str(connection_result[1]))
            dic_data = json.loads(connection_result[1])
            if (dic_data['status'] == 'failure') and (dic_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(dic_data['status'], 'success', 'RCPL Check: The status should be success. ' + str(dic_data))
                print dic_data
                break

        # make the call
        data = json.dumps({'id': '12345_packages_check', 'is_checking': 'False',
                           'type': 'check',
                           'request': 'package'})
        connection_result = self._connection_handler.send_request(command='POST',
                                                                  path='/api/osup',
                                                                  body=data,
                                                                  json_type=True)
        self.assertEqual(connection_result[0], 200,
                         '/api/osup POST check, package: failed with status ' + str(connection_result[0]) + str(connection_result[1]))
        print connection_result[1]
        dic_data = json.loads(connection_result[1])
        self.assertEqual(dic_data['status'], 'success', 'Packages Check: The status should be success. ' + str(dic_data))
        self.assertEqual(dic_data['in_progress'], False, 'Packages Check: The in_progress should be False. ' + str(dic_data))
        while True:
            data = json.dumps({'id': '12345_packages_check', 'is_checking': 'True',
                               'type': 'check',
                               'request': 'package'})
            connection_result = self._connection_handler.send_request(command='POST',
                                                                      path='/api/osup',
                                                                      body=data,
                                                                      json_type=True)
            self.assertEqual(connection_result[0], 200,
                             '/api/osup POST check, rcpl: failed with status ' + str(connection_result[0]) + str(connection_result[1]))
            dic_data = json.loads(connection_result[1])
            if (dic_data['status'] == 'failure') and (dic_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(dic_data['status'], 'success', 'Packages Check: The status should be success. ' + str(dic_data))
                print dic_data
                break

    def test_os_update_post_update(self):
        """ Test OSUpdate::POST
        """
        print ""  # better print format
        print "Running test_os_update_post_update"
        self.assertTrue(self._connection_handler._auth, '/api/auth POST failed!')

        # set up proxy file.
        self.assertTrue(self.__set_proxy_file(), 'Set up proxy /api/proxy POST failed!')

        # get os data to set the arch value. otherwise, /api/osup POST will fail
        connection_result = self._connection_handler.send_request(command='GET',
                                                                  path='/api/osc')
        self.assertEqual(connection_result[0], 200,
                         '/api/osc GET: failed with status ' + str(connection_result[0]) + str(connection_result[1]))

        # make the call
        data = json.dumps({'id': '12345_do_os_packages', 'is_checking': 'False',
                           'type': 'update_packages'})
        connection_result = self._connection_handler.send_request(command='POST',
                                                                  path='/api/osup',
                                                                  body=data,
                                                                  json_type=True)
        self.assertEqual(connection_result[0], 200,
                         '/api/osup POST update_packages: failed with status ' + str(connection_result[0]) + str(connection_result[1]))
        print connection_result[1]
        dic_data = json.loads(connection_result[1])
        self.assertEqual(dic_data['status'], 'success', 'Do OS Packages: The status should be success. ' + str(dic_data))
        self.assertEqual(dic_data['in_progress'], False, 'Do OS Packages: The in_progress should be False. ' + str(dic_data))
        while True:
            data = json.dumps({'id': '12345_do_os_packages', 'is_checking': 'True',
                               'type': 'update_packages'})
            connection_result = self._connection_handler.send_request(command='POST',
                                                                      path='/api/osup',
                                                                      body=data,
                                                                      json_type=True)
            self.assertEqual(connection_result[0], 200,
                             '/api/osup POST update_packages: failed with status ' + str(connection_result[0]) + str(connection_result[1]))
            dic_data = json.loads(connection_result[1])
            if (dic_data['status'] == 'failure') and (dic_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(dic_data['status'], 'success', 'Do OS Packages: The status should be success. ' + str(dic_data))
                print dic_data
                break

        # make the call
        data = json.dumps({'id': '12345_do_rcpl', 'is_checking': 'False',
                           'type': 'update_rcpl',
                           'username': self._utility_helper._un_pro_correct,
                           'password': self._utility_helper._pw_pro_correct})
        connection_result = self._connection_handler.send_request(command='POST',
                                                                  path='/api/osup',
                                                                  body=data,
                                                                  json_type=True)
        self.assertEqual(connection_result[0], 200,
                         '/api/osup POST update_rcpl: failed with status ' + str(connection_result[0]) + str(connection_result[1]))
        print connection_result[1]
        dic_data = json.loads(connection_result[1])
        self.assertEqual(dic_data['status'], 'success', 'Do RCPL: The status should be success. ' + str(dic_data))
        self.assertEqual(dic_data['in_progress'], False, 'Do RCPL: The in_progress should be False. ' + str(dic_data))
        while True:
            data = json.dumps({'id': '12345_do_rcpl', 'is_checking': 'True',
                               'type': 'update_rcpl',
                               'username': self._utility_helper._un_pro,
                               'password': self._utility_helper._pw_pro})
            connection_result = self._connection_handler.send_request(command='POST',
                                                                      path='/api/osup',
                                                                      body=data,
                                                                      json_type=True)
            self.assertEqual(connection_result[0], 200,
                             '/api/osup POST update_rcpl: failed with status ' + str(connection_result[0]) + str(connection_result[1]))
            dic_data = json.loads(connection_result[1])
            if (dic_data['status'] == 'failure') and (dic_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(dic_data['status'], 'failure', 'Do RCPL: The status should be failure, as we have wrong credential. ' + str(dic_data))
                print dic_data
                break
