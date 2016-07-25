#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import unittest
import unit_test_utility
import time
import json
import subprocess
import manage_repo
import manage_config
import manage_package
import manage_proxy
from tools import network_ops, shell_ops


class TestProfile(unittest.TestCase):
    """ Profile test case
    """
    # prepare to test
    def setUp(self):
        """ Initial setup
        """
        self._utility_helper = unit_test_utility.UtilityHelper()
        self.__start_time = time.time()

    # wrap up test
    def tearDown(self):
        """ Wrap up
        """
        self._utility_helper.wrap_up()
        run_time = time.time() - self.__start_time
        print ''
        print str(self.id) + " time = " + str(run_time)

    def test_1_read_config_file(self):
        """ Test manage_config.read_config_file
        """
        config = manage_config.read_config_file()
        u = config.sections()
        self.assertTrue('DefaultRepo' in u, "DefaultRepo not int returned config section list!")
        self.assertTrue('HDC' in u, "HDC not int returned config section list!")
        self.assertTrue('ProRepo' in u, "ProRepo not int returned config section list!")
        self.assertTrue('BaseRepo' in u, "BaseRepo not int returned config section list!")
        self.assertTrue('SecurityAutomation' in u, "SecurityAutomation not int returned config section list!")

    def test_2_list_repos(self):
        """ Test manage_repo.list_repos
        """
        manage_repo.list_repos()

    def test_3_configure_default_repo(self):
        """ Test manage_repo.configure_default_repo
        """
        manage_repo.configure_default_repo()

    def test_4_network_connection(self):
        """ Test tools.network_ops.NetworkCheck
        """
        self._network_handler = network_ops.NetworkCheck()
        u = self._network_handler.test_network_connection()
        self.assertEqual(len(u), 2, "Return does not have 2 items!")
        self.assertTrue('https_conn' in u[0], "https_conn not in the first returned item!")
        self.assertTrue('https_conn' in u[1], "https_conn not in the second returned item!")

    def test_5_build_package_database(self):
        """ Test manage_package.build_package_database
        """
        manage_package.build_package_database()

    def test_6_update_package_list(self):
        """ Test manage_package.update_package_list
        """
        manage_package.update_package_list()

    def test_7_update_channels(self):
        """ Test manage_repo.update_channels
        """
        u = manage_repo.update_channels()
        js_data = json.loads(u)
        self.assertEqual(js_data['status'], 'success', 'update_channels failed with ' + str(u))

    def test_8_set_proxy_config(self):
        """ Test manage_proxy.set_proxy_config
        """
        self._utility_helper.set_proxy_file()
        u = manage_proxy.get_proxy_config_in_worker_process()
        js_data = json.loads(u)

        u2 = manage_proxy.set_proxy_config_in_worker_process(js_data['http_url'], js_data['http_port'],
                                                             js_data['https_url'],
                                                             js_data['https_port'], js_data['ftp_url'],
                                                             js_data['ftp_port'],
                                                             js_data['socks_url'], js_data['socks_port'],
                                                             js_data['no_proxy'])
        js_data2 = json.loads(u2)
        self.assertEqual(js_data2['status'], 'success', "set_proxy_config does not return status = success!")

    def test_all(self):
        """ Test all
        """

        run_num = 5
        str_message = 'Smart channel --list, '
        stop_node_red = True

        # smart channel --list
        index = 0
        average_time = 0
        while True:
            start_time = time.time()
            shell_ops.run_command('smart channel --list')
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        average_time /= run_num
        str_average_time = "{:.5f}".format(average_time)
        str_message = str_message + 'average, ' + str_average_time
        print str_message
        str_message += '\n'

        # smart update
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'smart update, '
        while True:
            start_time = time.time()
            try:
                shell_ops.run_command("smart update")
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        # systemctl --no-block restart node-red-experience
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'systemctl --no-block restart node-red-experience, '
        if stop_node_red:
            str_message += 'skip'
        else:
            while True:
                start_time = time.time()
                try:
                    shell_ops.run_command('systemctl --no-block restart node-red-experience')
                except Exception as e:
                    run_failed = True
                    fail_message = str(e)
                    break
                elapse_time = time.time() - start_time
                average_time += elapse_time
                str_elapse_time = "{:.5f}".format(elapse_time)
                str_message = str_message + str_elapse_time + ', '
                time.sleep(2)

                index += 1
                if index == run_num:
                    break

            if run_failed:
                str_message += fail_message
            else:
                average_time /= run_num
                str_average_time = "{:.5f}".format(average_time)
                str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        # systemctl --no-block restart wr-iot-agent
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'systemctl --no-block restart wr-iot-agent, '
        while True:
            start_time = time.time()
            try:
                shell_ops.run_command('systemctl --no-block restart wr-iot-agent')
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        # read_config_file
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'read_config_file, '
        while True:
            start_time = time.time()
            try:
                manage_config.read_config_file()
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        # list_repos
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'list_repos, '
        while True:
            start_time = time.time()
            try:
                manage_repo.list_repos()
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        # configure_default_repo
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'configure_default_repo, '
        while True:
            start_time = time.time()
            try:
                manage_repo.configure_default_repo()
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        # test_network_connection
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'test_network_connection, '
        self._network_handler = network_ops.NetworkCheck()
        while True:
            start_time = time.time()
            try:
                self._network_handler.test_network_connection()
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        # build_package_database
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'build_package_database, '
        while True:
            start_time = time.time()
            try:
                manage_package.build_package_database()
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        # update_package_list
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'update_package_list, '
        while True:
            start_time = time.time()
            try:
                manage_package.update_package_list()
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        # set_proxy_config
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'set_proxy_config, '
        self._utility_helper.set_proxy_file()
        u = manage_proxy.get_proxy_config_in_worker_process()
        js_data = json.loads(u)
        while True:
            start_time = time.time()
            try:
                manage_proxy.set_proxy_config_in_worker_process(js_data['http_url'], js_data['http_port'],
                                                                js_data['https_url'],
                                                                js_data['https_port'], js_data['ftp_url'],
                                                                js_data['ftp_port'],
                                                                js_data['socks_url'], js_data['socks_port'],
                                                                js_data['no_proxy'])
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        with open("profile_output.txt", "w") as text_file:
            text_file.write(str_message)

    def test_set_proxy_config(self):
        """ Test set_proxy_config
        """

        run_num = 5
        str_message = 'Smart channel --list, '

        # set_proxy_config
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'set_proxy_config, '
        self._utility_helper.set_proxy_file()
        u = manage_proxy.get_proxy_config_in_worker_process()
        js_data = json.loads(u)
        while True:
            start_time = time.time()
            try:
                manage_proxy.set_proxy_config_in_worker_process(js_data['http_url'], js_data['http_port'],
                                                                js_data['https_url'],
                                                                js_data['https_port'], js_data['ftp_url'],
                                                                js_data['ftp_port'],
                                                                js_data['socks_url'], js_data['socks_port'],
                                                                js_data['no_proxy'])
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        with open("profile_output.txt", "w") as text_file:
            text_file.write(str_message)

    def test_list_repos_new(self):
        """ Test list_repos_new
        """
        for i in range(2):
            if i == 0:
                print 'add 1 repo'
                result = subprocess.check_output(["smart", "channel", "--add",
                                                  self._utility_helper._name_repo,
                                                  "type=rpm-md",
                                                  'baseurl=' + self._utility_helper._url_repo, "-y"])
                self.assertFalse('error' in result, 'add repo failed!')
                subprocess.check_output(['smart', 'update'])
            elif i == 1:
                print 'remove the added repo'
                result = subprocess.check_output(["smart", "channel", "--remove",
                                                  self._utility_helper._name_repo, "-y"])
                self.assertFalse('error' in result, 'remove repo failed!')
                subprocess.check_output(['smart', 'update'])

            original_config = manage_config.use_new_list_repos
            manage_config.use_new_list_repos = True
            result = manage_repo.list_repos()
            print result
            manage_config.use_new_list_repos = False
            result = manage_repo.list_repos()
            print result
            manage_config.use_new_list_repos = original_config

    def test_time_list_repos_new(self):
        """ Test time for list_repos_new
        """

        run_num = 5
        str_message = ''
        original_config = manage_config.use_new_list_repos

        # list_repos_new
        manage_config.use_new_list_repos = True
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'list_repos_new, '
        while True:
            start_time = time.time()
            try:
                manage_repo.list_repos()
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        # list_repos
        manage_config.use_new_list_repos = False
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'list_repos, '
        while True:
            start_time = time.time()
            try:
                manage_repo.list_repos()
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        manage_config.use_new_list_repos = original_config

        with open("profile_output.txt", "w") as text_file:
            text_file.write(str_message)

    def test_build_package_database_new(self):
        """ Test build_package_database_new
        """

        for i in range(2):
            if i == 0:
                print 'add 1 repo'
                result = subprocess.check_output(["smart", "channel", "--add",
                                                  self._utility_helper._name_repo,
                                                  "type=rpm-md",
                                                  'baseurl=' + self._utility_helper._url_repo, "-y"])
                self.assertFalse('error' in result, 'add repo failed!')
                subprocess.check_output(['smart', 'update'])
            elif i == 1:
                print 'remove the added repo'
                result = subprocess.check_output(["smart", "channel", "--remove",
                                                  self._utility_helper._name_repo, "-y"])
                self.assertFalse('error' in result, 'remove repo failed!')
                subprocess.check_output(['smart', 'update'])

            original_config = manage_config.use_new_build_package_database
            manage_config.use_new_build_package_database = True
            manage_package.build_package_database()
            manage_config.use_new_build_package_database = False
            manage_package.build_package_database()
            manage_config.use_new_build_package_database = original_config
            print 'old/new: ' + str(len(manage_package.constructed_packages_list)) + ' v.s. ' + str(len(manage_package.constructed_packages_list_new))

            for pc_new in manage_package.constructed_packages_list_new:
                got_match = False
                for pc in manage_package.constructed_packages_list:
                    if pc_new['name'] == pc['name']:
                        got_match = True
                        check_ok = True
                        check_list = ['version', 'summary', 'group', 'image', 'title', 'installed',
                                      'upgrade_version', 'curated', 'depends', 'bundle', 'vertical',
                                      'service', 'launch']
                        for str_check in check_list:
                            existed_in_new = (str_check in pc_new)
                            existed_in_original = (str_check in pc)
                            if not (existed_in_new == existed_in_original):
                                print 'For ' + pc_new['name'] + ', ' + str_check + ' in 1 but not the other.'
                                check_ok = False
                            if existed_in_original and existed_in_new:
                                if not (pc_new[str_check] == pc[str_check]):
                                    print 'For ' + pc_new['name'] + ', ' + str_check + ' value not same: ' + str(pc_new[str_check]) + ' v.s. ' + str(pc[str_check])
                                    check_ok = False
                        if check_ok:
                            break
                self.assertTrue(got_match,
                                pc_new['name'] + ' is not in the original list!')

    def test_time_build_package_database_new(self):
        """ Test time for build_package_database_new
        """

        run_num = 5
        str_message = ''
        original_config = manage_config.use_new_build_package_database

        # build_package_database_new
        manage_config.use_new_build_package_database = True
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'build_package_database_new, '
        while True:
            start_time = time.time()
            try:
                manage_package.build_package_database()
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        # build_package_database
        manage_config.use_new_build_package_database = False
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'build_package_database, '
        while True:
            start_time = time.time()
            try:
                manage_package.build_package_database()
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        manage_config.use_new_build_package_database = original_config

        with open("profile_output.txt", "w") as text_file:
            text_file.write(str_message)

    def test_add_remove_repo(self):
        """ Test build_package_database_new with add repo and remove repo
        """

        original_config = manage_config.use_new_build_package_database

        for i in range(2):
            if i == 0:
                manage_config.use_new_build_package_database = True

                print 'add 1 repo'
                manage_repo.add_repo(url=self._utility_helper._url_repo,
                                     user_name='None', password='None',
                                     name=self._utility_helper._name_repo)
                print 'new number: ' + str(len(manage_package.constructed_packages_list_new))

                print 'remove the added repo'
                manage_repo.remove_repo(name=self._utility_helper._name_repo, UpdateCache=True)
                print 'new number: ' + str(len(manage_package.constructed_packages_list_new))

            elif i == 1:
                manage_config.use_new_build_package_database = False

                print 'add 1 repo'
                manage_repo.add_repo(url=self._utility_helper._url_repo,
                                     user_name='None', password='None',
                                     name=self._utility_helper._name_repo)
                print 'old number: ' + str(len(manage_package.constructed_packages_list))

                print 'remove the added repo'
                manage_repo.remove_repo(name=self._utility_helper._name_repo, UpdateCache=True)
                print 'old number: ' + str(len(manage_package.constructed_packages_list))

        manage_config.use_new_build_package_database = original_config

    def test_time_test_network_connection(self):
        """ Test time for test_network_connection
        """

        run_num = 1
        str_message = ''
        network_helper = network_ops.NetworkCheck()

        # test_network_connection no http
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'test_network_connection no http, '
        while True:
            start_time = time.time()
            try:
                result = network_helper.test_network_connection(check_http=False)
                print str(result)
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        # sleep some so that network check will run
        time.sleep(70)

        # test_network_connection yes http
        index = 0
        average_time = 0
        run_failed = False
        fail_message = ''
        str_message += 'test_network_connection yes http, '
        while True:
            start_time = time.time()
            try:
                result = network_helper.test_network_connection(check_http=True)
                print str(result)
            except Exception as e:
                run_failed = True
                fail_message = str(e)
                break
            elapse_time = time.time() - start_time
            average_time += elapse_time
            str_elapse_time = "{:.5f}".format(elapse_time)
            str_message = str_message + str_elapse_time + ', '
            time.sleep(2)

            index += 1
            if index == run_num:
                break

        if run_failed:
            str_message += fail_message
        else:
            average_time /= run_num
            str_average_time = "{:.5f}".format(average_time)
            str_message = str_message + 'average, ' + str_average_time

        print str_message
        str_message += '\n'

        with open("profile_output.txt", "w") as text_file:
            text_file.write(str_message)
