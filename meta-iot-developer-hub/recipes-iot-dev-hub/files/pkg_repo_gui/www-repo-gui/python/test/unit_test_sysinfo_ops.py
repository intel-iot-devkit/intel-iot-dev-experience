#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import unit_test_utility
from tools import sysinfo_ops


class TestDataCollect(unittest.TestCase):
    """ tools . sysinfo_ops test case
    """
    # prepare to test
    def setUp(self):
        """ Initial setup
        """
        self._utility_helper = unit_test_utility.UtilityHelper()
        self._collector = sysinfo_ops.DataCollect()

    # wrap up test
    def tearDown(self):
        """ Wrap up
        """
        self._utility_helper.wrap_up()

    def test_get_hostname(self):
        """ Test DataCollect::getHostname
        """
        u = self._collector.getHostname()
        print ""  # better print format
        print "Running test_get_hostname: %s" % str(u)
        self.assertIsInstance(u, str, "Return is not str type!")
        if not u:  # empty string
            self.assertTrue(False, "Empty string!")

    def test_get_model(self):
        """ Test DataCollect::getModel
        """
        u = self._collector.getModel()
        print ""  # better print format
        print "Running test_get_model: %s" % str(u)
        self.assertIsInstance(u, str, "Return is not str type!")
        if not u:  # empty string
            self.assertTrue(False, "Empty string!")

    def test_get_lanip(self):
        """ Test DataCollect::getLanIPAddr
        """
        u = self._collector.getLanIPAddr()
        print ""  # better print format
        print "Running test_get_lanip: %s" % str(u)
        self.assertTrue(True, "Noop!")

    def test_get_wifi_ssid(self):
        """ Test DataCollect::getWifiSSID
        """
        u = self._collector.getWifiSSID()
        print ""  # better print format
        print "Running test_get_wifi_ssid: %s" % str(u)
        self.assertIsInstance(u, str, "Return is not str type!")

    def test_get_datetime(self):
        """ Test DataCollect::getDateTime
        """
        u = self._collector.getDateTime()
        print ""  # better print format
        print "Running test_get_datetime: %s" % str(u)
        self.assertIsInstance(u, str, "Return is not str type!")
        if not u:  # empty string
            self.assertTrue(False, "Empty string!")

    def test_get_up_time(self):
        """ Test DataCollect::getUpTime
        """
        u = self._collector.getUpTime()
        print ""  # better print format
        print "Running test_get_up_time: %s" % str(u)
        self.assertIsInstance(u, str, "Return is not str type!")
        if not u:  # empty string
            self.assertTrue(False, "Empty string!")

    def test_get_system_version(self):
        """ Test DataCollect::getSystemVersion
        """
        u = self._collector.getSystemVersion()
        print ""  # better print format
        print "Running test_get_system_version: %s" % str(u)
        self.assertIsInstance(u, str, "Return is not str type!")
        if not u:  # empty string
            self.assertTrue(False, "Empty string!")

    def test_get_cpu_type(self):
        """ Test DataCollect::getCPUType
        """
        u = self._collector.getCPUType()
        print ""  # better print format
        print "Running test_get_cpu_type: %s" % str(u)
        self.assertIsInstance(u, str, "Return is not str type!")
        if not u:  # empty string
            self.assertTrue(False, "Empty string!")

    def test_get_disk_usage(self):
        """ Test DataCollect::getDiskUsage
        """
        u = self._collector.getDiskUsage("/")
        print ""  # better print format
        print "Running test_get_disk_usage: %s" % str(u)
        self.assertIsInstance(u, dict, "Return is not dict type!")
        self.assertEqual(len(u), 3, "Returned dict does not have 3 items!")

    def test_get_data_set(self):
        """ Test DataCollect::getDataSet
        """
        u = self._collector.getDataSet()
        print ""  # better print format
        print "Running test_get_data_set: %s" % str(u)
        self.assertIsInstance(u, dict, "Return is not dict type!")
        self.assertEqual(len(u), 8, "Returned dict does not have 8 items!")

    def test_platform_details(self):
        """ Test platform_details
        """
        u = self._collector.platform_details()
        print ""  # better print format
        print "Running test_platform_details: %s" % str(u)
        self.assertEqual(len(u), 2, "Return does not have 2 items!")


