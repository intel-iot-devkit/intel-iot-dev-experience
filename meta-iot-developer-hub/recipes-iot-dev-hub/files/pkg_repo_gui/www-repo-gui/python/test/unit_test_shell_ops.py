#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import unit_test_utility
from tools import shell_ops


class TestShellOps(unittest.TestCase):
    """ tools . shell_ops test case
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

    def test_run_command(self):
        """ Test run_command
        """
        u = shell_ops.run_command("ls")
        print ""  # better print format
        print "Running test_run_command with ls."
        self.assertIsInstance(u, str, "Return is not str type!")
