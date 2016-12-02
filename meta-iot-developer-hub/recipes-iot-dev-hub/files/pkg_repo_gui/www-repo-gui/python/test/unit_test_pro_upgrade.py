#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import unit_test_utility
import urllib
import json
import ast
import time
import manage_pro_upgrade
import manage_proxy
from tools import sysinfo_ops
from multiprocessing import Process


class TestProUpgrade(unittest.TestCase):
    """ manage_pro_upgrade test case
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

    def test_pro_status_enabled_state(self):
        """ Test Pro_Status::enabled_state
        """
        print ""  # better print format
        print "Running test_pro_status_enabled_state"

        u = manage_pro_upgrade.ProStatus().enabled_state()
        self.assertTrue('result' in u, 'test_pro_status_enabled_state failed with result ' + str(u))

    def test_pro_status_multiprocess(self):
        def f(work_type, p_name):
            if work_type == 'read':
                for i in range(10):
                    u = manage_pro_upgrade.ProStatus().enabled_state()
                    print p_name + 'read process: ' + str(u)
                    # time.sleep(1)
            else:
                for i in range(10):
                    if i % 2 == 0:
                        manage_pro_upgrade.ProStatus().upgrade_status('True')
                        print p_name + 'write process: True'
                    else:
                        manage_pro_upgrade.ProStatus().upgrade_status('False')
                        print p_name + 'write process: False'
                    # time.sleep(1)

        p1 = Process(target=f, args=('read', 'p1', ))
        p2 = Process(target=f, args=('write', 'p2', ))
        p3 = Process(target=f, args=('read', 'p3', ))
        p1.start()
        p2.start()
        p3.start()
        p1.join()
        p2.join()
        p3.join()

    def test_propackagelist_getpackages(self):
        """ Test ProPackageList::get_packages
        """
        print ""  # better print format
        print "Running test_propackagelist_getpackages"

        u = manage_pro_upgrade.ProPackageList.get_packages()
        print str(len(u))
        print u
        self.assertTrue(True, 'NoOps!')


class TestCherryPyAPIPro(unittest.TestCase):
    """ manage_pro_upgrade EnablePro test case
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

    def test_enable_pro_get(self):
        """ Test EnablePro::GET
        """
        print ""  # better print format
        print "Running test_enable_pro_get"
        self.assertTrue(self._connection_handler._auth, '/api/auth POST failed!')

        connection_result = self._connection_handler.send_request(command='GET',
                                                                  path='/api/pro')
        self.assertEqual(connection_result[0], 200,
                         '/api/pro GET: failed with status ' + str(connection_result[0]) + str(connection_result[1]))
        dic_data = ast.literal_eval(connection_result[1])
        self.assertTrue('result' in dic_data,
                        '/api/pro GET: failed with result ' + str(dic_data))

    def test_enable_pro_post(self):
        """ Test EnablePro::POST
        """
        print ""  # better print format
        print "Running test_enable_pro_post"
        self.assertTrue(self._connection_handler._auth, '/api/auth POST failed!')

        # set up proxy file.
        self.assertTrue(self.__set_proxy_file(), 'Set up proxy /api/proxy POST failed!')

        # get os data to set the arch value. otherwise, /api/pro POST will fail
        connection_result = self._connection_handler.send_request(command='GET',
                                                                  path='/api/osc')
        self.assertEqual(connection_result[0], 200,
                         '/api/osc GET: failed with status ' + str(connection_result[0]) + str(connection_result[1]))

        js_data = {'id': '12345_5', 'is_checking': 'False',
                   'username': self._utility_helper._un_pro,
                   'password': self._utility_helper._pw_pro}
        data = json.dumps(js_data)
        connection_result = self._connection_handler.send_request(command='POST',
                                                                  path='/api/pro',
                                                                  body=data,
                                                                  json_type=True)
        self.assertEqual(connection_result[0], 200,
                         '/api/pro POST: failed with status ' + str(connection_result[0]) + str(connection_result[1]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'success', 'The status should be success. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], False, 'The in_progress should be False. ' + str(js_data))
        while True:
            js_data = {'id': '12345_5', 'is_checking': 'True'}
            data = json.dumps(js_data)
            connection_result = self._connection_handler.send_request(command='POST',
                                                                      path='/api/pro',
                                                                      body=data,
                                                                      json_type=True)
            self.assertEqual(connection_result[0], 200,
                             '/api/pro POST: failed with status ' + str(connection_result[0]))

            js_data = json.loads(connection_result[1])
            if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(js_data['status'], 'failure', 'The status should be failiure. ' + str(js_data))
                self.assertTrue('401' in js_data['error'],
                                'The result should be 401 for auth failure, but it is not. ' + str(js_data))
                print js_data
                break
