#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import unit_test_utility
import time
import manage_package
import manage_repo
import json
import manage_proxy
import urllib


class TestPackage(unittest.TestCase):
    """ manage_package test case
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

    def test_update_package_list(self):
        """ Test update_package_list and build_package_database
        """
        u = manage_package.update_package_list()
        js_data = json.loads(u)
        print ""  # better print format
        print "Running test_update_package_list: %s" % str(u)
        self.assertTrue(js_data['status'] == 'success', "status is not success!")

    def test_get_is_installed(self):
        """ Test get_is_installed and get_installed_packages
        """
        u = manage_package.get_is_installed(None, self._utility_helper._pn_info)
        print ""  # better print format
        print "Running test_get_is_installed: %s" % str(u)
        self.assertEqual(u[1]['package'],
                         self._utility_helper._pn_info,
                         "The returned result shows a different package name! " + str(u))

    def test_get_package_info(self):
        """ Test get_package_info
        """
        u = manage_package.get_package_info(self._utility_helper._pn_info)
        js_data = json.loads(u)
        print ""  # better print format
        print "Running test_get_package_info: %s" % str(u)
        self.assertEqual(len(js_data), 7, "Return does not have 7 items!")
        self.assertTrue('url' in js_data, "url not in returned data!")
        self.assertTrue('license' in js_data, "license not in returned data!")
        self.assertTrue('size' in js_data, "size not in returned data!")
        self.assertTrue('description' in js_data, "description not in returned data!")
        self.assertTrue('summary' in js_data, "summary not in returned data!")
        self.assertTrue('group' in js_data, "group not in returned data!")
        self.assertTrue('version' in js_data, "version not in returned data!")

    def test_get_data(self):
        """ Test get_data
        """
        u = manage_package.get_data()
        print ""  # better print format
        print "Running test_get_data."
        if u is None:
            self.assertTrue(True, 'no package file yet! ')
        else:
            self.assertIsInstance(u, str, 'get_data fails with result ' + str(u))

    def test_package(self):
        """ Test package_transaction
        """
        print ""  # better print format
        print "Running test_package for target package %s" % self._utility_helper._pn_test_target

        # check if installed
        u = manage_package.get_is_installed(None, self._utility_helper._pn_test_target)
        self.assertEqual(u[1]['installed'], 'False', self._utility_helper._pn_test_target +
                         ' is already installed! Please modify the test scripts to use another package.')

        # test install
        u = manage_package.package_transaction('install', {'package': self._utility_helper._pn_test_target})
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', self._utility_helper._pn_test_target +
                         ' installation failed with result: ' + str(u))

        # check if installed
        u = manage_package.get_is_installed(None, self._utility_helper._pn_test_target)
        self.assertEqual(u[1]['installed'], 'True', self._utility_helper._pn_test_target + ' is not installed!')

        # test upgrade
        u = manage_package.package_transaction('upgrade', {'package': self._utility_helper._pn_test_target})
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', self._utility_helper._pn_test_target +
                         ' upgrade failed with result: ' + str(u))

        # test remove
        u = manage_package.package_transaction('remove', {'package': self._utility_helper._pn_test_target})
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', self._utility_helper._pn_test_target +
                         ' remove failed with result: ' + str(u))

        # check if uninstalled
        u = manage_package.get_is_installed(None, self._utility_helper._pn_test_target)
        self.assertEqual(u[1]['installed'], 'False', self._utility_helper._pn_test_target + ' is still installed!')

    def test_get_updates_for_os_packages(self):
        """ Test get_updates_for_os_packages
        """
        print ""  # better print format
        print "Running test_get_updates_for_os_packages."

        # clean up first
        manage_repo.RepoTracking.reset()

        # add
        manage_repo.add_repo(url=self._utility_helper._url_repo,
                                 user_name='None', password='None',
                                 name="OS 1")
        manage_repo.add_repo(url=self._utility_helper._url_repo,
                                 user_name='None', password='None',
                                 name="GUI 1", from_GUI=True)

        # check
        result = manage_package.get_updates_for_os_packages()
        print str(result)

        # remove
        manage_repo.remove_repo(name="GUI 1", from_GUI=True)
        manage_repo.remove_repo(name="OS 1")

        # clean up at the end
        manage_repo.RepoTracking.reset()


class TestCherryPyAPIPackage(unittest.TestCase):
    """ manage_package Package test case
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

    def test_package_info_get(self):
        """ Test PackageInfo::GET
        """
        print ""  # better print format
        print "Running test_package_info_get"

        self.assertTrue(self._connection_handler._auth, '/api/auth POST failed!')

        connection_result = self._connection_handler.send_request(command='GET',
                                                                  path=('/api/packageinfo?id=12345_info&is_checking=False&name=' + self._utility_helper._pn_info))
        # print connection_result
        self.assertEqual(connection_result[0], 200,
                         '/api/packageinfo?name= GET: failed with status ' + str(connection_result[0]) + str(connection_result[1]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'success', 'Info: The status should be success. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], False, 'Info: The in_progress should be False. ' + str(js_data))
        while True:
            connection_result = self._connection_handler.send_request(command='GET',
                                                                      path='/api/packageinfo?id=12345_info&is_checking=True')
            self.assertEqual(connection_result[0], 200,
                             '/api/packageinfo?name= GET: failed with status ' + str(connection_result[0]))

            js_data = json.loads(connection_result[1])
            if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(js_data['status'], 'success', 'Info: The status should be success. ' + str(js_data))
                print js_data
                break

    def test_packages(self):
        """ Test Packages::GET/POST/PUT/DELETE and Proxy::POST
        """
        print ""  # better print format
        print "Running test_packages"
        self.assertTrue(self._connection_handler._auth, '/api/auth POST failed!')

        # GET
        connection_result = self._connection_handler.send_request(command='GET',
                                                                  path='/api/packages')
        self.assertEqual(connection_result[0], 200,
                         '/api/packages GET: failed with status ' + str(connection_result[0]))
        js_data = json.loads(connection_result[1])
        self.assertTrue(len(js_data) > 0, '/api/packages GET: It is impossible to have zero packages installed!')
        self.assertTrue('group' in js_data[0], '/api/packages GET: group is not in the 1st result set!')
        self.assertTrue('curated' in js_data[0], '/api/packages GET: curated is not in the 1st result set!')
        self.assertTrue('name' in js_data[0], '/api/packages GET: name is not in the 1st result set!')
        self.assertTrue('version' in js_data[0], '/api/packages GET: version is not in the 1st result set!')

        # set up proxy file.
        self.assertTrue(self.__set_proxy_file(), 'Set up proxy /api/proxy POST failed!')

        # INSTALL - False
        params = urllib.urlencode({'package': 'HaHaWrongOne',
                                   'id': '12345_installpackage',
                                   'is_checking': 'False'})
        connection_result = self._connection_handler.send_request(command='POST',
                                                                  path='/api/packages', body=params)
        self.assertEqual(connection_result[0], 200,
                         '/api/packages POST: failed with status ' + str(connection_result[0]) + str(connection_result[1]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'success', 'Install: The status should be success. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], False, 'Install: The in_progress should be False. ' + str(js_data))
        while True:
            params = urllib.urlencode({'id': '12345_installpackage',
                                       'is_checking': 'True'})
            connection_result = self._connection_handler.send_request(command='POST',
                                                                      path='/api/packages', body=params)
            self.assertEqual(connection_result[0], 200,
                             '/api/packages POST: failed with status ' + str(connection_result[0]))

            js_data = json.loads(connection_result[1])
            if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(js_data['status'], 'failure', 'Install: The status should be failure. ' + str(js_data))
                print js_data
                break

        # INSTALL
        params = urllib.urlencode({'package': self._utility_helper._pn_test_target,
                                   'id': '12345_installpackage',
                                   'is_checking': 'False'})
        connection_result = self._connection_handler.send_request(command='POST',
                                                                  path='/api/packages', body=params)
        self.assertEqual(connection_result[0], 200,
                         '/api/packages POST: failed with status ' + str(connection_result[0]) + str(connection_result[1]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'success', 'Install: The status should be success. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], False, 'Install: The in_progress should be False. ' + str(js_data))
        while True:
            params = urllib.urlencode({'id': '12345_installpackage',
                                       'is_checking': 'True'})
            connection_result = self._connection_handler.send_request(command='POST',
                                                                      path='/api/packages', body=params)
            self.assertEqual(connection_result[0], 200,
                             '/api/packages POST: failed with status ' + str(connection_result[0]))

            js_data = json.loads(connection_result[1])
            if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(js_data['status'], 'success', 'Install: The status should be success. ' + str(js_data))
                print js_data
                break

        # UPGRADE
        params = urllib.urlencode({'package': self._utility_helper._pn_test_target,
                                   'id': '12345_upgradepackage',
                                   'is_checking': 'False'})
        connection_result = self._connection_handler.send_request(command='PUT',
                                                                  path='/api/packages', body=params)
        self.assertEqual(connection_result[0], 200,
                         '/api/packages PUT: failed with status ' + str(connection_result[0]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'success', 'Upgrade: The status should be success. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], False, 'Upgrade: The in_progress should be False. ' + str(js_data))
        while True:
            params = urllib.urlencode({'id': '12345_upgradepackage',
                                       'is_checking': 'True'})
            connection_result = self._connection_handler.send_request(command='PUT',
                                                                      path='/api/packages', body=params)
            self.assertEqual(connection_result[0], 200,
                             '/api/packages PUT: failed with status ' + str(connection_result[0]))

            js_data = json.loads(connection_result[1])
            if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(js_data['status'], 'success', 'Upgrade: The status should be success. ' + str(js_data))
                print js_data
                break

        # REMOVE
        connection_result = self._connection_handler.send_request(command='DELETE',
                                                                  path=('/api/packages?id=12345_deletepackage&is_checking=False&package=' + self._utility_helper._pn_test_target))
        self.assertEqual(connection_result[0], 200,
                         '/api/packages DELETE: failed with status ' + str(connection_result[0]))
        js_data = json.loads(connection_result[1])
        self.assertEqual(js_data['status'], 'success', 'Delete: The status should be success. ' + str(js_data))
        self.assertEqual(js_data['in_progress'], False, 'Delete: The in_progress should be False. ' + str(js_data))
        while True:
            connection_result = self._connection_handler.send_request(command='DELETE',
                                                                      path='/api/packages?id=12345_deletepackage&is_checking=True')
            self.assertEqual(connection_result[0], 200,
                             '/api/packages DELETE: failed with status ' + str(connection_result[0]))

            js_data = json.loads(connection_result[1])
            if (js_data['status'] == 'failure') and (js_data['in_progress'] == True):
                time.sleep(5)
            else:
                self.assertEqual(js_data['status'], 'success', 'Delete: The status should be success. ' + str(js_data))
                print js_data
                break
