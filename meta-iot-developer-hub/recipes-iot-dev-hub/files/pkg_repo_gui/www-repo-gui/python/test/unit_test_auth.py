#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import manage_auth
import unit_test_utility
import json
import ast


class TestAuth(unittest.TestCase):
    """ manage_auth test case

    We ignore all testing for cherrypy part since we are not running these testings along with cherrypy flow.
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

    def test_authenticate_user(self):
        """ Test authenticate_user

        We ignore all testing for cherrypy part since we are not running these testings along with cherrypy flow.
        """
        print ""  # better print format
        print "Running test_authenticate_user."

        authenticate_error = False
        try:
            u = manage_auth.authenticate_user(self._utility_helper._un, self._utility_helper._pw)
            if u['status'] == 'failure':
                authenticate_error = True
        except Exception as e:
            if isinstance(e, AttributeError):
                # ignore this since this is due to cherrypy error.
                # we are not using a complete cherrypy flow, so we don't have any session.
                pass
            else:
                self.assertTrue(False, 'test_authenticate_user failed with exception ' + str(e))

        self.assertFalse(authenticate_error,
                         'Authenticate failed with ' + self._utility_helper._un + ', ' + self._utility_helper._pw)


class TestCherryPyAPIAuth(unittest.TestCase):
    """ manage_auth Auth test case
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

    def test_auth_put(self):
        """ Test Auth::PUT
        """
        print ""  # better print format
        print "Running test_auth_put"
        self.assertTrue(self._connection_handler._auth, '/api/auth POST failed!')

        # change
        data = json.dumps({'username': self._connection_handler._un,
                           'password': self._connection_handler._pw,
                           'newpassword': 'testtemp'})
        connection_result = self._connection_handler.send_request(command='PUT',
                                                                  path='/api/auth',
                                                                  body=data,
                                                                  json_type=True)
        self.assertEqual(connection_result[0], 200,
                         '/api/auth PUT: failed with status ' + str(connection_result[0]))
        dic_data = ast.literal_eval(connection_result[1])
        self.assertEqual(dic_data['status'], 'success',
                         '/api/auth PUT: failed with result ' + str(dic_data))

        # change it back
        data = json.dumps({'username': self._connection_handler._un,
                           'password': 'testtemp',
                           'newpassword': self._connection_handler._pw})
        connection_result = self._connection_handler.send_request(command='PUT',
                                                                  path='/api/auth',
                                                                  body=data,
                                                                  json_type=True)
        self.assertEqual(connection_result[0], 200,
                         '2nd /api/auth PUT: failed with status ' + str(connection_result[0]))
        self.assertEqual(dic_data['status'], 'success',
                         '2nd /api/auth PUT: failed with result ' + str(dic_data))

    def test_auth_get(self):
        """ Test Auth::GET
        """
        print ""  # better print format
        print "Running test_auth_get"
        self.assertTrue(self._connection_handler._auth, '/api/auth POST failed!')

        connection_result = self._connection_handler.send_request(command='GET',
                                                                  path='/api/auth')
        self.assertEqual(connection_result[0], 200,
                         '/api/auth GET: failed with status ' + str(connection_result[0]))
        dic_data = ast.literal_eval(connection_result[1])
        self.assertEqual(dic_data['status'], 'success',
                         '/api/auth GET: failed with result ' + str(dic_data))
