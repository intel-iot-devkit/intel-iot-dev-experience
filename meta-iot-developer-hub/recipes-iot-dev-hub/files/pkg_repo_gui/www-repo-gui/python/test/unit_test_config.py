#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import unit_test_utility
import manage_config
import manage_proxy
from tools import shell_ops


class TestConfig(unittest.TestCase):
    """ manage_config test case
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

    def test_read_config_file(self):
        """ Test read_config_file
        """
        config = manage_config.read_config_file()
        u = config.sections()
        print ""  # better print format
        print "Running test_read_config_file"
        self.assertTrue('DefaultRepo' in u, "DefaultRepo not int returned config section list!")
        self.assertTrue('HDC' in u, "HDC not int returned config section list!")
        self.assertTrue('ProRepo' in u, "ProRepo not int returned config section list!")
        self.assertTrue('BaseRepo' in u, "BaseRepo not int returned config section list!")
        self.assertTrue('SecurityAutomation' in u, "SecurityAutomation not int returned config section list!")

    def test_add_secure_http_to_config_file(self):
        """ Test add_secure_http_to_config_file
        """
        print ""  # better print format
        print "Running test_add_secure_http_to_config_file."

        manage_config.add_secure_http_to_config_file('true')
        config = manage_config.read_config_file()
        result = config.get('SecurityAutomation', 'secure_http')
        self.assertEqual(result, 'true', 'Config result is not true, but ' + result)

        manage_config.add_secure_http_to_config_file('false')
        config = manage_config.read_config_file()
        result = config.get('SecurityAutomation', 'secure_http')
        self.assertEqual(result, 'false', 'Config result is not false, but ' + result)

    def test_configure_node_red_https(self):
        """ Test configure_node_red_https
        """
        print ""  # better print format
        print "Running test_configure_node_red_https. Set to https and then set to http."
        manage_config.configure_node_red_https('true')
        # check status of node red service
        result = shell_ops.run_command('systemctl status ' + self._utility_helper._sn_target)
        self.assertTrue(self._utility_helper._sc_running in result,
                        self._utility_helper._sn_target + ' is not started at the 1st test try!')

        manage_config.configure_node_red_https('false')
        # check status of node red service
        result = shell_ops.run_command('systemctl status ' + self._utility_helper._sn_target)
        self.assertTrue(self._utility_helper._sc_running in result,
                        self._utility_helper._sn_target + ' is not started at the 2nd test try!')

    def test_set_proxy_settings_for_HDC(self):
        """ Test set_proxy_settings_for_HDC
        """
        print ""  # better print format
        print "Running test_set_proxy_settings_for_HDC"

        if self._utility_helper._value_http == 'not_there':
            value_http_url = ''
            value_http_port = ''
        else:
            result = manage_proxy.split_proxy_info('http_proxy=' + self._utility_helper._value_http)
            if len(result) == 2:
                value_http_url = result[0]
                value_http_port = result[1]
            else:
                value_http_url = ''
                value_http_port = ''

        if value_http_url != '':
            manage_config.HDCSettings.set_proxy_settings_for_HDC("http", value_http_url, value_http_port)
        else:
            manage_config.HDCSettings.set_proxy_settings_for_HDC("none", "proxy.windriver.com", "3128")

        self.assertTrue(True, 'No Ops!')

    def test_set_hdc_server_details(self):
        """ Test set_hdc_server_details
        """
        print ""  # better print format
        print "Running test_set_hdc_server_details"

        manage_config.HDCSettings.set_hdc_server_details()
        self.assertTrue(True, 'No Ops!')
