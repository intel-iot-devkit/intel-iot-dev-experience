#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import unit_test_utility
import time
import ast
import manage_worker


class TestWorkerProcess(unittest.TestCase):
    """ worker_process
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

    def test_worker_process(self):
        """ Test test_worker_process
        """
        from tools import logging_helper
        import logging
        self.__log_helper = logging_helper.logging_helper.Logger(logger_name='backend_general')
        self.__log_helper.logger.level = logging.INFO

        manage_worker.start()

        type_dict = {'type': '', 'id': '1232'}
        u = manage_worker.submit_work(work_type=type_dict)
        self.assertEqual(u['status'], 'success', 'This should work...' + str(u))
        time.sleep(3)
        u = manage_worker.retrieve_work_result(work_type=type_dict)
        self.assertEqual(u['status'], 'failure', 'This should result in failure...' + str(u))

        type_dict = {'type': manage_worker.worker_process_message_test, 'id': '1232'}
        type_dict_2 = {'type': manage_worker.worker_process_message_test, 'id': '1232893'}
        print 'submit some idle work'
        u = manage_worker.submit_work(work_type=type_dict)
        self.assertEqual(u['status'], 'success', 'This should work...' + str(u))
        print 'try retrieving result'
        u = manage_worker.retrieve_work_result(work_type=type_dict)
        self.assertEqual(u['status'], 'failure', 'This should fail...' + str(u))
        self.assertEqual(u['in_progress'], True, 'This should be in progress...' + str(u))
        print 'try submitting another work'
        u = manage_worker.submit_work(work_type=type_dict_2)
        self.assertEqual(u['status'], 'failure', 'This should fail...' + str(u))
        self.assertEqual(u['in_progress'], True, 'This should be in progress...' + str(u))
        self.assertEqual(u['work_type'], manage_worker.worker_process_message_test, 'The work type is not correct.' + str(u))
        time.sleep(manage_worker.worker_process_test_sleep_time * 2)
        print 'try retrieving result again after waiting for enough time.'
        u = manage_worker.retrieve_work_result(work_type=type_dict)
        self.assertEqual(u['status'], 'success', 'This should work...' + str(u))
        self.assertEqual(u['in_progress'], False, 'This should no be in progress...' + str(u))

        type_dict = {'type': manage_worker.worker_process_message_test_2, 'id': '1232'}
        type_dict_2 = {'type': manage_worker.worker_process_message_test, 'id': '1232893'}
        print 'submit intensive work'
        u = manage_worker.submit_work(work_type=type_dict)
        self.assertEqual(u['status'], 'success', 'This should work...' + str(u))
        time.sleep(2)
        print 'try retrieving result'
        u = manage_worker.retrieve_work_result(work_type=type_dict)
        self.assertEqual(u['status'], 'failure', 'This should fail...' + str(u))
        self.assertEqual(u['in_progress'], True, 'This should be in progress...' + str(u))
        time.sleep(1)
        print 'try submitting another work'
        u = manage_worker.submit_work(work_type=type_dict_2)
        self.assertEqual(u['status'], 'failure', 'This should fail...' + str(u))
        self.assertEqual(u['in_progress'], True, 'This should be in progress...' + str(u))
        self.assertEqual(u['work_type'], manage_worker.worker_process_message_test_2, 'The work type is not correct.' + str(u))
        time.sleep(manage_worker.worker_process_test_2_sleep_time * 1.5)
        print 'try retrieving result again after waiting for enough time.'
        u = manage_worker.retrieve_work_result(work_type=type_dict)
        self.assertEqual(u['status'], 'success', 'This should work...' + str(u))
        self.assertEqual(u['in_progress'], False, 'This should not be in progress...' + str(u))

        # check state and finish
        while True:
            u = manage_worker.get_worker_process_state()
            if u == manage_worker.worker_process_state_idle:
                break
            time.sleep(5)
        manage_worker.finish()
        time.sleep(4)

    def test_force_stop(self):
        """ Test test_force_stop
        """
        from tools import logging_helper
        import logging
        self.__log_helper = logging_helper.logging_helper.Logger(logger_name='backend_general')
        self.__log_helper.logger.level = logging.INFO

        manage_worker.start()

        type_dict = {'type': manage_worker.worker_process_message_test_2, 'id': '1232'}
        u = manage_worker.submit_work(work_type=type_dict)
        self.assertEqual(u['status'], 'success', 'This should work...' + str(u))

        time.sleep(2)

        print 'trying to stop'
        manage_worker.finish()
        time.sleep(4)
        print 'stopped.'
