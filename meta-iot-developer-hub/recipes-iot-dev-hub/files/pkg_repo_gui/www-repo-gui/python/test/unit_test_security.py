#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import unit_test_utility
import json
import manage_security
import manage_mec
from tools import shell_ops


class TestSecurity(unittest.TestCase):
    """ manage_security and manage_mec test case
    """
    # prepare to test
    def setUp(self):
        """ Initial setup
        """
        self._utility_helper = unit_test_utility.UtilityHelper()
        self._security_auto_handler = manage_security.SecurityAutomationWorker()
        self._mec_handler = manage_mec.MEC()
        self._rest_handler = manage_security.SecurityAutomation()

    # wrap up test
    def tearDown(self):
        """ Wrap up
        """
        self._utility_helper.wrap_up()

    def test_is_mec_installed(self):
        """ Test IsMecInstalled
        """
        print ""  # better print format
        print "Running test_is_mec_installed"

        self._mec_handler.IsMecInstalled()
        self.assertTrue(True, 'No Ops!')

    def test_get_default_custom_harden_data(self):
        """ Test get_default_custom_harden_data
        """
        print ""  # better print format
        print "Running test_get_default_custom_harden_data"

        u = manage_security.get_default_custom_harden_data()
        print str(type(u))
        print u
        self.assertTrue(True, 'NoOps!')

    def test_security_automation_put(self):
        """ Test SecurityAutomation::PUT
        """
        print ""  # better print format
        print "Running test_security_automation_put"

        self._rest_handler.PUT(enable='true')
        # check status of node red service
        result = shell_ops.run_command('systemctl status ' + self._utility_helper._sn_target)
        self.assertTrue(self._utility_helper._sc_running in result,
                        self._utility_helper._sn_target + ' is not started at the 1st test try!')

        self._rest_handler.PUT(enable='false')
        # check status of node red service
        result = shell_ops.run_command('systemctl status ' + self._utility_helper._sn_target)
        self.assertTrue(self._utility_helper._sc_running in result,
                        self._utility_helper._sn_target + ' is not started at the 2nd test try!')
