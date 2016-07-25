#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import unit_test_utility
import manage_hac


class TestHACGenerateReg(unittest.TestCase):
    """ manage_hac test case
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

    def test_isDeviceRegistered(self):
        """ Test isDeviceRegistered
        """
        print ""  # better print format
        print "Running test_isDeviceRegistered"

        u = manage_hac.isDeviceRegistered()
        self.assertIsInstance(u, bool, 'test_isDeviceRegistered failed. Return type is ' + str(type(u)))

    def test_getHTTPSProxy(self):
        """ Test getHTTPSProxy
        """
        print ""  # better print format
        print "Running test_getHTTPSProxy"

        # set environment variable to proxy file
        self._utility_helper.set_proxy_file()

        manage_hac.getHTTPSProxy()
        self.assertTrue(True, 'No Ops!')

    def test_getHacServerName(self):
        """ Test getHacServerName
        """
        print ""  # better print format
        print "Running test_getHacServerName"

        u = manage_hac.getHacServerName()
        self.assertTrue(u, 'getHacServerName returns empty string!')

    def test_getNonExpiredPreexistingCode(self):
        """ Test getNonExpiredPreexistingCode
        """

        print ""  # better print format
        print "Running test_getNonExpiredPreexistingCode"

        manage_hac.getNonExpiredPreexistingCode()
        self.assertTrue(True, 'No Ops!')

    def test_getNewCodeFromAppCloud(self):
        """ Test getNewCodeFromAppCloud
        """

        print ""  # better print format
        print "Running test_getNewCodeFromAppCloud"

        manage_hac.getNewCodeFromAppCloud("")
        self.assertTrue(True, 'No Ops!')


class TestCherryPyAPIHAC(unittest.TestCase):
    """ manage_hac HAC test case
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

    def test_hac_get(self):
        """ Test HAC::GET
        """
        print ""  # better print format
        print "Running test_hac_get"
        self.assertTrue(self._connection_handler._auth, '/api/auth POST failed!')

        connection_result = self._connection_handler.send_request(command='GET',
                                                                  path='/api/hac')
        self.assertEqual(connection_result[0], 200,
                         '/api/hac GET: failed with status ' + str(connection_result[0]))
