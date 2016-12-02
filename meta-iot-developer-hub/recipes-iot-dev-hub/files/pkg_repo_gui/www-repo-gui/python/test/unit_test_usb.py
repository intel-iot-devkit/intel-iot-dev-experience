#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import manage_usb
import unit_test_utility


class TestUsb(unittest.TestCase):
    """ manage_usb test case
    """
    # prepare to test
    def setUp(self):
        """ Initial setup
        """
        self._utility_helper = unit_test_utility.UtilityHelper()
        self._usb = manage_usb.UsbSupport()
        self._api = manage_usb.USB_API()

    # wrap up test
    def tearDown(self):
        """ Wrap up
        """
        self._utility_helper.wrap_up()

    def test_usb_support(self):
        """ Test UsbSupport::list_usbs
        """
        u = self._usb.list_usbs()
        print ""  # better print format
        print "Running test_usb_support: %s" % str(u)
        self.assertIsInstance(u, str, "Not a str type!")

    def test_usb_api_get(self):
        """ Test USB_API::GET
        """
        u = self._api.GET()
        print ""  # better print format
        print "Running test_usb_api_get: %s" % str(u)
        self.assertIsInstance(u, str, "Not a str type!")
