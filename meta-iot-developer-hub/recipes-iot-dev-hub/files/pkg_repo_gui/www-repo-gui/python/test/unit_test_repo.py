#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import urllib
import json
import ast
import time
import unit_test_utility
import manage_repo
import manage_proxy
from tools import shell_ops


class TestRepo(unittest.TestCase):
    """ manage_repo test case
    """
    # prepare to test
    def setUp(self):
        """ Initial setup
        """
        self._utility_helper = unit_test_utility.UtilityHelper()

    # wrap up test
    def tearDown(self):
        """ Wrap up
        """
        self._utility_helper.wrap_up()

    def test_update_channels(self):
        """ Test update_channels
        """
        u = manage_repo.update_channels()
        js_data = json.loads(u)
        print ""  # better print format
        print "Running test_update_channels: %s" % str(u)
        self.assertEqual(js_data['status'], 'success', "status is not success!")

    def test_repos(self):
        """ Test add_repo, list_repos, remove_repo
        """
        print ""  # better print format
        print "Running test_repos."

        # clean up first
        manage_repo.RepoTracking.reset()
        # add
        u = manage_repo.add_repo(url=self._utility_helper._url_repo,
                                 user_name='None', password='None',
                                 name=self._utility_helper._name_repo)
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'add_repo failed with ' + str(u))
        # list
        u = manage_repo.list_repos()
        self.assertTrue(self._utility_helper._name_repo in u,
                        'list_repos failed! ' + self._utility_helper._name_repo + ' not in list: ' + str(u))
        # read
        u = manage_repo.RepoTracking.read_from_tracking()
        self.assertEqual(len(u), 0, 'read_from_tracking failed. The length should be 0. The return is ' + str(u))
        # remove
        u = manage_repo.remove_repo(name=self._utility_helper._name_repo)
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'remove_repo failed with ' + str(u))
        # add
        u = manage_repo.add_repo(url=self._utility_helper._url_repo,
                                 user_name='None', password='None',
                                 name=self._utility_helper._name_repo, from_GUI=True)
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'add_repo failed with ' + str(u))
        # read
        u = manage_repo.RepoTracking.read_from_tracking()
        self.assertEqual(len(u), 1, 'read_from_tracking failed. The length should be 1. The return is ' + str(u))
        self.assertEqual(u[0], self._utility_helper._name_repo, 'read_from_tracking failed. The return is ' + str(u))
        # remove
        u = manage_repo.remove_repo(name=self._utility_helper._name_repo, from_GUI=True)
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'remove_repo failed with ' + str(u))
        # read
        u = manage_repo.RepoTracking.read_from_tracking()
        self.assertEqual(len(u), 0, 'read_from_tracking failed. The length should be 0. The return is ' + str(u))
        # clean up at the end
        manage_repo.RepoTracking.reset()

    def test_repos_filter(self):
        """ Test add_repo, list_repos, remove_repo
        """
        print ""  # better print format
        print "Running test_repos_filter."

        # clean up first
        manage_repo.RepoTracking.reset()

        # add
        u = manage_repo.add_repo(url=self._utility_helper._url_repo,
                                 user_name='None', password='None',
                                 name='OS 1')
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'add_repo failed with ' + str(u))
        u = manage_repo.add_repo(url=self._utility_helper._url_repo,
                                 user_name='None', password='None',
                                 name='OS 2')
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'add_repo failed with ' + str(u))
        u = manage_repo.add_repo(url=self._utility_helper._url_repo,
                                 user_name='None', password='None',
                                 name='GUI 1', from_GUI=True)
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'add_repo failed with ' + str(u))
        u = manage_repo.add_repo(url=self._utility_helper._url_repo,
                                 user_name='None', password='None',
                                 name='GUI 2', from_GUI=True)
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'add_repo failed with ' + str(u))

        # list
        u1 = manage_repo.list_repos(do_filter=True, keep_tracking=True)
        self.assertEqual(len(u1), 2, 'There should be only 2 repos in tracking file. ' + str(u1))
        print str(u1)
        u1 = manage_repo.list_repos_non_os_only()
        self.assertEqual(len(u1), 3, 'There should be only 3 nonOS repos. ' + str(u1))
        print str(u1)

        # remove
        u = manage_repo.remove_repo(name='OS 1')
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'remove_repo failed with ' + str(u))
        u = manage_repo.remove_repo(name='OS 2')
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'remove_repo failed with ' + str(u))
        u = manage_repo.remove_repo(name='GUI 1', from_GUI=True)
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'remove_repo failed with ' + str(u))
        u = manage_repo.remove_repo(name='GUI 2', from_GUI=True)
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'remove_repo failed with ' + str(u))

        # clean up at the end
        manage_repo.RepoTracking.reset()

    def test_repo_tracking(self):
        """ Test repo_tracking
        """
        print ""  # better print format
        print "Running test_repo_tracking."

        # clean up first
        manage_repo.RepoTracking.reset()

        # add 1
        u = manage_repo.RepoTracking.add_to_tracking("Test 1")
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'add_to_tracking failed with ' + str(u))

        # read
        u = manage_repo.RepoTracking.read_from_tracking()
        self.assertEqual(len(u), 1, 'read_from_tracking failed. The length should be 1. The return is ' + str(u))
        self.assertEqual(u[0], "Test 1", 'read_from_tracking failed. It should equal to Test 1. The return is ' + str(u))
        # print str(u)

        # remove 1
        u = manage_repo.RepoTracking.remove_from_tracking("Test 1")
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'remove_from_tracking failed with ' + str(u))

        # add 3
        u = manage_repo.RepoTracking.add_to_tracking("Test 2")
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'add_to_tracking failed with ' + str(u))
        u = manage_repo.RepoTracking.add_to_tracking("Test 3")
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'add_to_tracking failed with ' + str(u))
        u = manage_repo.RepoTracking.add_to_tracking("Test 4")
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'add_to_tracking failed with ' + str(u))

        # read
        u = manage_repo.RepoTracking.read_from_tracking()
        self.assertEqual(len(u), 3, 'read_from_tracking failed. The length should be 3. The return is ' + str(u))
        self.assertEqual(u[0], "Test 2", 'read_from_tracking failed. It should equal to Test 2. The return is ' + str(u))
        self.assertEqual(u[1], "Test 3", 'read_from_tracking failed. It should equal to Test 3. The return is ' + str(u))
        self.assertEqual(u[2], "Test 4", 'read_from_tracking failed. It should equal to Test 4. The return is ' + str(u))
        # print str(u)

        # check
        u = manage_repo.RepoTracking.check_in_tracking("Test 2")
        self.assertTrue(u, "check_in_tracking failed.  Test 2 should be in tracking file.")
        u = manage_repo.RepoTracking.check_in_tracking("Test 4")
        self.assertTrue(u, "check_in_tracking failed.  Test 4 should be in tracking file.")
        u = manage_repo.RepoTracking.check_in_tracking("Test 1")
        self.assertFalse(u, "check_in_tracking failed.  Test 1 should not be in tracking file.")

        # remove 1
        u = manage_repo.RepoTracking.remove_from_tracking("Test 3")
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'remove_from_tracking failed with ' + str(u))

        # read
        u = manage_repo.RepoTracking.read_from_tracking()
        self.assertEqual(len(u), 2, 'read_from_tracking failed. The length should be 2. The return is ' + str(u))
        self.assertEqual(u[0], "Test 2", 'read_from_tracking failed. It should equal to Test 2. The return is ' + str(u))
        self.assertEqual(u[1], "Test 4", 'read_from_tracking failed. It should equal to Test 4. The return is ' + str(u))
        # print str(u)

        # clean up at the end
        manage_repo.RepoTracking.reset()

    def test_os_repo_ops(self):
        """ Test operations for os repos
        """
        print ""  # better print format
        print "Running test_os_repo_ops."

        # clean up first
        manage_repo.RepoTracking.reset()

        # add
        manage_repo.add_repo(url=self._utility_helper._url_repo,
                                 user_name='None', password='None',
                                 name="OS 1")
        manage_repo.add_repo(url=self._utility_helper._url_repo,
                                 user_name='None', password='None',
                                 name="GUI 1", from_GUI=True)

        result = manage_repo.enable_only_os_repos()
        self.assertTrue(result['status'], 'enable_only_os_repos failed.')
        cmd_result = shell_ops.run_cmd_chk("smart channel --show")
        print "enable_only_os_repos results: " + str(cmd_result)

        result = manage_repo.enable_repo(result['disabled_repos'])
        self.assertTrue(result['status'], 'enable_repo failed.')
        cmd_result = shell_ops.run_cmd_chk("smart channel --show")
        print "enable_repo results: " + str(cmd_result)

        # filter
        result = manage_repo.RepoTracking.filter_repo_list(['OS 1', 'GUI 1', 'Test 1'], keep_tracking=True)
        self.assertEqual(len(result), 1, 'The result should return only 1 item. The actual result is ' + str(result))
        self.assertEqual(result[0], 'GUI 1', 'The item is not GUI 1. The actual result is ' + str(result))
        result = manage_repo.RepoTracking.filter_repo_list(['OS 1', 'GUI 1', 'Test 1'], keep_tracking=False)
        self.assertEqual(len(result), 2, 'The result should return only 2 items. The actual result is ' + str(result))
        self.assertEqual(result[0], 'OS 1', 'The item is not OS 1. The actual result is ' + str(result))
        self.assertEqual(result[1], 'Test 1', 'The item is not Test 1. The actual result is ' + str(result))

        # remove
        manage_repo.remove_repo(name="GUI 1", from_GUI=True)
        manage_repo.remove_repo(name="OS 1")

        # clean up at the end
        manage_repo.RepoTracking.reset()


class TestCherryPyAPIRepo(unittest.TestCase):
    """ manage_repo Repository test case
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

    def test_repository(self):
        """ Test Repository::GET, POST, PUT, DELETE
        """
        print ""  # better print format
        print "Running test_repository"
        self.assertTrue(self._connection_handler._auth, '/api/auth POST failed!')

        # set up proxy file.
        self.assertTrue(self.__set_proxy_file(), 'Set up proxy /api/proxy POST failed!')

        # POST, add_repo
        js_data = {'id': '12345_addrepo', 'is_checking': 'False',
                   'name': self._utility_helper._name_repo, 'url': self._utility_helper._url_repo,
                   'username': '', 'password': ''}
        params = urllib.urlencode(js_data)
        connection_result = self._connection_handler.send_request(command='POST',
                                                                  path='/api/repository', body=params)
        self.assertEqual(connection_result[0], 200,
                         '/api/repository POST: failed with status ' + str(connection_result[0]) + str(connection_result[1]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'success', 'Add: The status should be success. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], False, 'Add: The in_progress should be False. ' + str(js_data))
        while True:
            js_data = {'id': '12345_addrepo', 'is_checking': 'True'}
            params = urllib.urlencode(js_data)
            connection_result = self._connection_handler.send_request(command='POST',
                                                                      path='/api/repository', body=params)
            self.assertEqual(connection_result[0], 200,
                             '/api/repository POST: failed with status ' + str(connection_result[0]))

            js_data = json.loads(connection_result[1])
            if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(js_data['status'], 'success', 'Add: The status should be success. ' + str(js_data))
                print js_data
                break

        # GET, list_repos
        connection_result = self._connection_handler.send_request(command='GET',
                                                                  path='/api/repository?id=12345_getrepo&is_checking=False')
        self.assertEqual(connection_result[0], 200,
                         '/api/repository GET: failed with status ' + str(connection_result[0]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'success', 'List: The status should be success. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], False, 'List: The in_progress should be False. ' + str(js_data))
        while True:
            connection_result = self._connection_handler.send_request(command='GET',
                                                                      path='/api/repository?id=12345_getrepo&is_checking=True')
            self.assertEqual(connection_result[0], 200,
                             '/api/repository GET: failed with status ' + str(connection_result[0]))

            js_data = json.loads(connection_result[1])
            if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(js_data['status'], 'success', 'List: The status should be success. ' + str(js_data))
                print js_data
                self.assertTrue(self._utility_helper._name_repo in js_data['list'], '/api/repository GET: failed with result ' + str(js_data))
                break

        # DELETE, remove_repo
        connection_result = self._connection_handler.send_request(command='DELETE',
                                                                  path=('/api/repository?id=12345_removerepo&is_checking=False&name=' + self._utility_helper._name_repo))
        self.assertEqual(connection_result[0], 200,
                         '/api/repository DELETE: failed with status ' + str(connection_result[0]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'success', 'Remove: The status should be success. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], False, 'Remove: The in_progress should be False. ' + str(js_data))
        while True:
            connection_result = self._connection_handler.send_request(command='DELETE',
                                                                      path='/api/repository?id=12345_removerepo&is_checking=True')
            self.assertEqual(connection_result[0], 200,
                             '/api/repository DELETE: failed with status ' + str(connection_result[0]))

            js_data = json.loads(connection_result[1])
            if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(js_data['status'], 'success', 'Remove: The status should be success. ' + str(js_data))
                print js_data
                break

        # PUT, update_channels
        connection_result = self._connection_handler.send_request(command='PUT',
                                                                  path='/api/repository?id=12345_update&is_checking=False',
                                                                  content_length_zero=True)
        self.assertEqual(connection_result[0], 200,
                         '/api/repository PUT: failed with status ' + str(connection_result[0]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'success', 'Update: The status should be success. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], False, 'Update: The in_progress should be False. ' + str(js_data))
        while True:
            connection_result = self._connection_handler.send_request(command='PUT',
                                                                      path='/api/repository?id=12345_update&is_checking=True',
                                                                      content_length_zero=True)
            self.assertEqual(connection_result[0], 200,
                             '/api/repository PUT: failed with status ' + str(connection_result[0]))

            js_data = json.loads(connection_result[1])
            if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(js_data['status'], 'success', 'Update: The status should be success. ' + str(js_data))
                print js_data
                break
