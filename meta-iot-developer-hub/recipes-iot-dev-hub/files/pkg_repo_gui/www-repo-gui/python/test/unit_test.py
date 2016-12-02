#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import unit_test_network_ops
import unit_test_data_ops
import unit_test_shell_ops
import unit_test_config
import unit_test_usb
import unit_test_service
import unit_test_sysinfo_ops
import unit_test_proxy
import unit_test_repo
import unit_test_package
import unit_test_auth
import unit_test_hac
import unit_test_os_controls
import unit_test_pro_upgrade
import unit_test_os_update
import unit_test_security
import unit_test_self_update
# Import new test cases here

# Add new test cases in the following list
testCaseList = [unit_test_network_ops.TestNetworkOps,
                unit_test_data_ops.TestDataOps,
                unit_test_shell_ops.TestShellOps,
                unit_test_config.TestConfig,
                unit_test_usb.TestUsb,
                unit_test_service.TestService,
                unit_test_sysinfo_ops.TestDataCollect,
                unit_test_proxy.TestProxy,
                unit_test_proxy.TestCherryPyAPIProxy,
                unit_test_repo.TestRepo,
                unit_test_repo.TestCherryPyAPIRepo,
                unit_test_package.TestPackage,
                unit_test_package.TestCherryPyAPIPackage,
                unit_test_auth.TestAuth,
                unit_test_auth.TestCherryPyAPIAuth,
                unit_test_os_controls.TestCherryPyAPIOSControls,
                unit_test_os_update.TestOSUpdate,
                unit_test_os_update.TestCherryPyAPIOSUpdate,
                unit_test_security.TestSecurity,
                unit_test_hac.TestCherryPyAPIHAC,
                unit_test_pro_upgrade.TestCherryPyAPIPro,
                unit_test_pro_upgrade.TestProUpgrade,
                unit_test_hac.TestHACGenerateReg]

testLoader = unittest.TestLoader()
caseList = []
for testCase in testCaseList:
    testSuite = testLoader.loadTestsFromTestCase(testCase)
    caseList.append(testSuite)

mySuite1 = unittest.TestSuite(caseList)
myRunner1 = unittest.TextTestRunner()
myRunner1.run(mySuite1)
