#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import unit_test_utility
import os
import urllib
import manage_proxy
import json
import ast
import time
from tools import sysinfo_ops


class TestProxy(unittest.TestCase):
    """ manage_proxy test case
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

    def test_proxy_file(self):
        """ Test get_proxy_config and set_proxy_config
        """

        # record the current session's ones
        value_http = os.getenv('http_proxy', 'not_there')
        value_https = os.getenv('https_proxy', 'not_there')
        value_ftp = os.getenv('ftp_proxy', 'not_there')
        value_socks = os.getenv('socks_proxy', 'not_there')
        value_no = os.getenv('no_proxy', 'not_there')

        u = manage_proxy.get_proxy_config_in_worker_process()
        js_data = json.loads(u)
        print ""  # better print format
        print "Running test_proxy_file: proxy settings: %s" % str(u)
        self.assertTrue("http_url" in js_data, "http_url field not in returned result for get_proxy_config!")
        self.assertTrue("http_port" in js_data, "http_port field not in returned result for get_proxy_config!")
        self.assertTrue("https_url" in js_data, "https_url field not in returned result for get_proxy_config!")
        self.assertTrue("https_port" in js_data, "https_port field not in returned result for get_proxy_config!")
        self.assertTrue("ftp_url" in js_data, "ftp_url field not in returned result for get_proxy_config!")
        self.assertTrue("ftp_port" in js_data, "ftp_port field not in returned result for get_proxy_config!")
        self.assertTrue("socks_url" in js_data, "socks_url field not in returned result for get_proxy_config!")
        self.assertTrue("socks_port" in js_data, "socks_port field not in returned result for get_proxy_config!")
        self.assertTrue("no_proxy" in js_data, "no_proxy field not in returned result for get_proxy_config!")
        u2 = manage_proxy.set_proxy_config_in_worker_process(js_data['http_url'], js_data['http_port'],
                                                             js_data['https_url'],
                                                             js_data['https_port'], js_data['ftp_url'],
                                                             js_data['ftp_port'],
                                                             js_data['socks_url'], js_data['socks_port'],
                                                             js_data['no_proxy'])
        js_data2 = json.loads(u2)
        self.assertEqual(js_data2['status'], 'success', "set_proxy_config does not return status = success!")

        # compare
        u3 = manage_proxy.get_proxy_config_in_worker_process()
        js_data3 = json.loads(u3)
        self.assertEqual(js_data, js_data3, "new proxy data is not the same as the original proxy data!")

        # set it back
        if value_http == 'not_there':
            os.unsetenv('http_proxy')
        elif not value_http:
            os.unsetenv('http_proxy')
        else:
            os.environ['http_proxy'] = value_http

        if value_https == 'not_there':
            os.unsetenv('https_proxy')
        elif not value_https:
            os.unsetenv('https_proxy')
        else:
            os.environ['https_proxy'] = value_https

        if value_ftp == 'not_there':
            os.unsetenv('ftp_proxy')
        elif not value_ftp:
            os.unsetenv('ftp_proxy')
        else:
            os.environ['ftp_proxy'] = value_ftp

        if value_socks == 'not_there':
            os.unsetenv('socks_proxy')
        elif not value_socks:
            os.unsetenv('socks_proxy')
        else:
            os.environ['socks_proxy'] = value_socks

        if value_no == 'not_there':
            os.unsetenv('no_proxy')
        elif not value_no:
            os.unsetenv('no_proxy')
        else:
            os.environ['no_proxy'] = value_no

    def test_split_proxy_info(self):
        """ Test split_proxy_info
        """
        u = manage_proxy.split_proxy_info("http_proxy=proxy-chain.intel.com:911")
        print ""  # better print format
        print "Running test_split_proxy_info with http_proxy=proxy-chain.intel.com:911: %s" % str(u)
        self.assertEqual(len(u), 2, "Return does not have 2 items!")
        self.assertEqual(u[0], "proxy-chain.intel.com", "URL is not splitted correctly!")
        self.assertEqual(u[1], "911", "Port is not splitted correctly!")


class TestCherryPyAPIProxy(unittest.TestCase):
    """ manage_proxy Proxy test case
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

    def test_proxy_get_list(self):
        """ Test Proxy::GET list
        """
        print ""  # better print format
        print "Running test_proxy_get_list"
        self.assertTrue(self._connection_handler._auth, '/api/auth POST failed!')

        # GET, request = list
        connection_result = self._connection_handler.send_request(command='GET',
                                                                  path='/api/proxy?id=12345_1&is_checking=False&request=list')
        self.assertEqual(connection_result[0], 200,
                         '/api/proxy?id=12345&is_checking=False&request=list GET: failed with status ' + str(connection_result[0]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'success', 'The status should be success. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], False, 'The in_progress should be False. ' + str(js_data))
        while True:
            connection_result = self._connection_handler.send_request(command='GET',
                                                                      path='/api/proxy?id=12345_1&is_checking=True&request=list')
            self.assertEqual(connection_result[0], 200,
                             '/api/proxy?id=12345&is_checking=True&request=list GET: failed with status ' + str(connection_result[0]))

            js_data = json.loads(connection_result[1])
            if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(js_data['status'], 'success', 'The status should be success. ' + str(js_data))
                self.assertTrue('https_url' in js_data, 'https_url is not in result ' + str(js_data))
                break

    def test_proxy_get_test(self):
        """ Test Proxy::GET test
        """
        print ""  # better print format
        print "Running test_proxy_get_test"
        self.assertTrue(self._connection_handler._auth, '/api/auth POST failed!')

        ####################################
        # Get environment variables
        ###################################
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

        ##################################
        # set the proxy to be a wrong one
        #################################
        js_data = {'id': '12345_2', 'is_checking': 'False', 'http_url': value_http_url, 'http_port': value_http_port,
                   'https_url': 'www.gog.com', 'https_port': value_https_port,
                   'ftp_url': value_ftp_url, 'ftp_port': value_ftp_port,
                   'socks_url': value_socks_url, 'socks_port': value_socks_port,
                   'no_proxy': value_no_proxy}
        params = urllib.urlencode(js_data)
        connection_result = self._connection_handler.send_request(command='POST', path='/api/proxy', body=params)
        self.assertEqual(connection_result[0], 200,
                         '/api/proxy POST: failed with status ' + str(connection_result[0]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'success', 'The status should be success. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], False, 'The in_progress should be False. ' + str(js_data))
        # GET, request = test
        connection_result = self._connection_handler.send_request(command='GET',
                                                                  path='/api/proxy?request=test')
        self.assertEqual(connection_result[0], 200,
                         '/api/proxy?request=test GET: failed with status ' + str(connection_result[0]))
        dic_data = ast.literal_eval(connection_result[1])
        self.assertTrue('https_conn' in dic_data, '/api/proxy?request=test GET: failed with result ' + str(dic_data))
        # Check when the "set proxy" is done
        while True:
            js_data = {'id': '12345_2', 'is_checking': 'True'}
            params = urllib.urlencode(js_data)
            connection_result = self._connection_handler.send_request(command='POST', path='/api/proxy', body=params)
            self.assertEqual(connection_result[0], 200,
                             '/api/proxy POST: failed with status ' + str(connection_result[0]))

            js_data = json.loads(connection_result[1])
            if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(js_data['status'], 'success', 'The status should be success. ' + str(js_data))
                print js_data
                break

        # GET, request = test
        connection_result = self._connection_handler.send_request(command='GET',
                                                                  path='/api/proxy?request=test')
        self.assertEqual(connection_result[0], 200,
                         '/api/proxy?request=test GET: failed with status ' + str(connection_result[0]))
        dic_data = ast.literal_eval(connection_result[1])
        self.assertTrue('https_conn' in dic_data, '/api/proxy?request=test GET: failed with result ' + str(dic_data))
        self.assertEqual(dic_data['https_conn'], 'False', 'https connection should not work!')

        ##################################
        # set the proxy to be a good one... Note: we use the testing sessions's environment variables
        ##################################
        js_data = {'id': '12345_3', 'is_checking': 'False', 'http_url': value_http_url, 'http_port': value_http_port,
                   'https_url': value_https_url, 'https_port': value_https_port,
                   'ftp_url': value_ftp_url, 'ftp_port': value_ftp_port,
                   'socks_url': value_socks_url, 'socks_port': value_socks_port,
                   'no_proxy': value_no_proxy}
        params = urllib.urlencode(js_data)
        connection_result = self._connection_handler.send_request(command='POST', path='/api/proxy', body=params)
        self.assertEqual(connection_result[0], 200,
                         '/api/proxy POST: failed with status ' + str(connection_result[0]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'success', 'The status should be success. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], False, 'The in_progress should be False. ' + str(js_data))
        # GET, request = test
        # This will not trigger an internal work.
        connection_result = self._connection_handler.send_request(command='GET',
                                                                  path='/api/proxy?request=test')
        self.assertEqual(connection_result[0], 200,
                         '/api/proxy?request=test GET: failed with status ' + str(connection_result[0]))
        dic_data = ast.literal_eval(connection_result[1])
        self.assertTrue('https_conn' in dic_data, '/api/proxy?request=test GET: failed with result ' + str(dic_data))
        self.assertEqual(dic_data['https_conn'], 'True', 'https connection should work!')
        # GET, request = list
        connection_result = self._connection_handler.send_request(command='GET',
                                                                  path='/api/proxy?id=12345&is_checking=False&request=list')
        self.assertEqual(connection_result[0], 200,
                         '/api/proxy?id=12345&is_checking=False&request=list GET: failed with status ' + str(connection_result[0]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'failure', 'The status should be failure. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], True, 'The in_progress should be True. ' + str(js_data))
        # Check when the "set proxy" is done
        while True:
            js_data = {'id': '12345_3', 'is_checking': 'True'}
            params = urllib.urlencode(js_data)
            connection_result = self._connection_handler.send_request(command='POST', path='/api/proxy', body=params)
            self.assertEqual(connection_result[0], 200,
                             '/api/proxy POST: failed with status ' + str(connection_result[0]))

            js_data = json.loads(connection_result[1])
            if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(js_data['status'], 'success', 'The status should be success. ' + str(js_data))
                print js_data
                break

    def test_proxy_post(self):
        """ Test Proxy::GET test
        """
        print ""  # better print format
        print "Running test_proxy_post"
        self.assertTrue(self._connection_handler._auth, '/api/auth POST failed!')

        ####################################
        # Get environment variables
        ###################################
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

        ####################################
        # Set
        ###################################
        js_data = {'id': '12345', 'is_checking': 'False', 'http_url': value_http_url, 'http_port': value_http_port,
                   'https_url': value_https_url, 'https_port': value_https_port,
                   'ftp_url': value_ftp_url, 'ftp_port': value_ftp_port,
                   'socks_url': value_socks_url, 'socks_port': value_socks_port,
                   'no_proxy': value_no_proxy}
        params = urllib.urlencode(js_data)
        connection_result = self._connection_handler.send_request(command='POST', path='/api/proxy', body=params)
        self.assertEqual(connection_result[0], 200,
                         '/api/proxy POST: failed with status ' + str(connection_result[0]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'success', 'The status should be success. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], False, 'The in_progress should be False. ' + str(js_data))
        while True:
            js_data = {'id': '12345', 'is_checking': 'True'}
            params = urllib.urlencode(js_data)
            connection_result = self._connection_handler.send_request(command='POST', path='/api/proxy', body=params)
            self.assertEqual(connection_result[0], 200,
                             '/api/proxy POST: failed with status ' + str(connection_result[0]))

            js_data = json.loads(connection_result[1])
            if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(js_data['status'], 'success', 'The status should be success. ' + str(js_data))
                #print js_data
                break


