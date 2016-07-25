#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import manage_service
import json
import unit_test_utility
import time
from tools import shell_ops


class TestService(unittest.TestCase):
    """ manage_service test case
    """
    # prepare to test
    def setUp(self):
        """ Initial setup
        """
        self._utility_helper = unit_test_utility.UtilityHelper()
        self._service = manage_service.ServiceControl()

    # wrap up test
    def tearDown(self):
        """ Wrap up
        """
        self._utility_helper.wrap_up()

    def test_service_control_get(self):
        """ Test Service_control::GET
        """
        u = self._service.GET(service='mosquitto.service')
        js_data = json.loads(u)
        print ""  # better print format
        print "Running test_service_control_get: %s" % u
        self.assertEqual(len(js_data), 1, "Return does not have 7 items!")
        self.assertTrue(('mosquitto.service' in js_data), "mosquitto.service not in result!")
        print js_data
