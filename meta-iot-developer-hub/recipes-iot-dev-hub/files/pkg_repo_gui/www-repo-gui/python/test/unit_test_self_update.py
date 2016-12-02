#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import unit_test_utility
import json
import urllib
import time
import manage_proxy


class TestCherryPyAPISelfUpdate(unittest.TestCase):
    """ manage_self_update test case
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

    def test_self_update_put(self):
        """ Test SelfUpgrade::PUT
        """
        print ""  # better print format
        print "Running test_self_update_put"
        self.assertTrue(self._connection_handler._auth, '/api/auth POST failed!')

        # set up proxy file.
        self.assertTrue(self.__set_proxy_file(), 'Set up proxy /api/proxy POST failed!')

        connection_result = self._connection_handler.send_request(command='PUT',
                                                                  path='/api/selfupgrade?id=12345_selfupgrade&is_checking=False', content_length_zero=True)
        self.assertEqual(connection_result[0], 200,
                         '/api/selfupgrade PUT: failed with status ' + str(connection_result[0]) + str(connection_result[1]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'success', 'The status should be success. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], False, 'The in_progress should be False. ' + str(js_data))
        while True:
            connection_result = self._connection_handler.send_request(command='PUT',
                                                                      path='/api/selfupgrade?id=12345_selfupgrade&is_checking=True', content_length_zero=True)
            self.assertEqual(connection_result[0], 200,
                             '/api/selfupgrade PUT: failed with status ' + str(connection_result[0]))

            js_data = json.loads(connection_result[1])
            if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(js_data['status'], 'success', 'The status should be success. ' + str(js_data))
                break
