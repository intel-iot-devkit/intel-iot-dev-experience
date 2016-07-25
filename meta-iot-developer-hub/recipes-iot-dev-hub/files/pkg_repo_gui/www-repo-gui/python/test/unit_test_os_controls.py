#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import unit_test_utility
import ast


class TestCherryPyAPIOSControls(unittest.TestCase):
    """ manage_os_controls test case
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

    def test_os_controls_get(self):
        """ Test OSControls::GET
        """
        print ""  # better print format
        print "Running test_os_controls_get"
        self.assertTrue(self._connection_handler._auth, '/api/auth POST failed!')

        connection_result = self._connection_handler.send_request(command='GET',
                                                                  path='/api/osc')
        self.assertEqual(connection_result[0], 200,
                         '/api/osc GET: failed with status ' + str(connection_result[0]))
        dic_data = ast.literal_eval(connection_result[1])
        self.assertEqual(len(dic_data), 9,
                         '/api/osc GET: failed with result ' + str(dic_data))
