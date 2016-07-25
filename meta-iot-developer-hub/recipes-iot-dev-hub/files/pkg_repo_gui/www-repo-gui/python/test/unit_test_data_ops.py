#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import unit_test_utility
from tools import data_ops
import gzip
import filecmp


class TestDataOps(unittest.TestCase):
    """ tools . data_ops test case
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

    def test_uncompress(self):
        """ Test uncompress
        """
        # Compress the test data
        with open(self._utility_helper._fn_to_be_compressed, "w") as f:
            f.write("test file")
        with open(self._utility_helper._fn_to_be_compressed) as f_input, gzip.open(self._utility_helper._fn_compressed, 'wb') as f_output:
            f_output.writelines(f_input)

        # Uncompress
        data_ops.uncompress(self._utility_helper._fn_compressed, self._utility_helper._fn_uncompressed)

        # Compare files
        u = filecmp.cmp(self._utility_helper._fn_to_be_compressed, self._utility_helper._fn_uncompressed, shallow=False)

        print ""  # better print format
        print "Running test_uncompress: %s" % str(u)
        self.assertTrue(u, "Uncompressed data different from the original data!")

    def test_byteify(self):
        """ Test byteify
        """
        data = {'Name': 'testdata', 'Value': 25, 'Details': {'Value1': 1, 'Value2': 2}}
        u = data_ops.byteify(data)
        print ""  # better print format
        print "Running test_byteify: %s" % str(u)
        self.assertEqual(u['Name'], 'testdata', "Name = testdata fails!")
        self.assertEqual(u['Value'], 25, "Value = 25 fails!")
        self.assertEqual(u['Details']['Value1'], 1, "Value1 = 1 fails!")
        self.assertEqual(u['Details']['Value2'], 2, "Value2 = 2 fails!")
