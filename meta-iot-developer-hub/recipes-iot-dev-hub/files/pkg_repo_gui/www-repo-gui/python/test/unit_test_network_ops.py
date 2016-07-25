#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import unit_test_utility
from tools import network_ops
import os


class TestNetworkOps(unittest.TestCase):
    """ tools . network_ops test case
    """
    # prepare to test
    def setUp(self):
        """ Initial setup
        """
        self._utility_helper = unit_test_utility.UtilityHelper()
        self._network_handler = network_ops.NetworkCheck()
        self._timeout_value = 10

    # wrap up test
    def tearDown(self):
        """ Wrap up
        """
        self._utility_helper.wrap_up()

    def test_is_network_connected_url_header_http(self):
        """ Test is_network_connected_url_header http
        """
        print ""  # better print format
        print "Running test_is_network_connected_url_header_http: %s" % os.getenv("http_proxy", "no_proxy")
        result = self._network_handler.is_network_connected_url_header(secure=False, timeout_value=self._timeout_value)
        str_message = "Not successful with result: " + str(result)
        self.assertEqual(result, 0, str_message)

    def test_is_network_connected_url_header_https(self):
        """ Test is_network_connected_url_header https
        """
        print ""  # better print format
        print "Running test_is_network_connected_url_header_https: %s" % os.getenv("https_proxy", "no_proxy")
        result = self._network_handler.is_network_connected_url_header(secure=True, timeout_value=self._timeout_value)
        str_message = "Not successful with result: " + str(result)
        self.assertEqual(result, 0, str_message)

    def test_is_network_connected_https(self):
        """ Test is_network_connected https
        """
        print ""  # better print format
        print "Running test_is_network_connected_https: %s" % os.getenv("https_proxy", "no_proxy")
        result = self._network_handler.is_network_connected(secure=True, factor_value=3)
        str_message = "Not successful with result: " + str(result)
        self.assertEqual(result, "True", str_message)

    def test_network_connection(self):
        """ Test test_network_connection
        """
        u = self._network_handler.test_network_connection()
        print ""  # better print format
        print "Running test_network_connection: %s" % str(u)
        self.assertEqual(len(u), 2, "Return does not have 2 items!")
        self.assertTrue('https_conn' in u[0], "https_conn not in the first returned item!")
        self.assertTrue('https_conn' in u[1], "https_conn not in the second returned item!")

        https_status = self._network_handler.get_stored_https_status()
        http_status = self._network_handler.get_stored_http_status()
        print "https, http: " + str(https_status) + ", " + str(http_status)
