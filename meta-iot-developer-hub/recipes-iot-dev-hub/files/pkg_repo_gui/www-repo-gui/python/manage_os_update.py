# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import urllib2
from platform import platform, release
import json
import manage_repo
import manage_config
import manage_package
import manage_pro_upgrade
import os
import ast
import subprocess
import cherrypy
from manage_auth import require
from tools import logging_helper, sysinfo_ops, network_ops, shell_ops, rcpl
import manage_worker


class OS_UPDATER(object):
    def __init__(self, m_current_rcpl, m_arch, user_name='', password='', no_network_ops=False):
        """

        Args:
            m_current_rcpl:
            m_arch:
            user_name (str): For Pro.
            password (str): For Pro.
            no_network_ops (bool):  True if not doing network-related ops.

        Returns:

        """
        self.__log_helper = logging_helper.logging_helper.Logger()
        self.__error = None
        self.__available_rcpls = dict()
        self.__handler = None
        self.__rcplindex_fname = str("NOT SET")
        self.__current_rcpl = int(m_current_rcpl)
        self.__arch = m_arch
        self.__platform = platform()
        self.__release = release()
        self.__index_file_loc = str("NOT SET")
        self.__repoUrls = []
        self.__repoUrls_highest = []
        self.__result = {'status': 'failure', 'message': ''}
        self.highest_rcpl = int(m_current_rcpl)
        self.higher_version = False

        pro_status = manage_pro_upgrade.ProStatus()
        if pro_status.enabled_state()['result'] == 'False':
            self.__pro_enabled = False
        else:
            self.__pro_enabled = True

        if no_network_ops:
            return

        # get index
        config = manage_config.read_config_file()
        try:
            download_dir = "downloads"
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
            self.__rcplindex_fname = 'downloads/rcplindex.xml'
            # remove old one
            try:
                os.remove(self.__rcplindex_fname)
            except:
                pass
            # get new index file
            if self.__pro_enabled:
                self.__log_helper.logger.debug('Get Pro rcplindex')
                self.__index_file_loc = config.get('ProRepo', sysinfo_ops.arch)
                # Do not need to escape username and password .
                # It is passed in "-u" flag as a string, run via "subprocess".
                # Subprocess's check_output takes care of escaping already.
                str_cred = str(user_name) + ":" + str(password)
                curl_out = subprocess.check_output(["curl",
                                                    "-u",
                                                    str_cred,
                                                    "%s" % self.__index_file_loc])
                if 'Username or password does not match' in curl_out:
                    self.__error = 'Error 401 - Unauthorized: Access is denied due to invalid credentials.'
                    self.__log_helper.logger.error(str(self.__error))
                else:
                    # write to the local index file
                    xml_file = open(self.__rcplindex_fname, "w")
                    xml_file.write(curl_out)
                    xml_file.close()
            else:
                self.__log_helper.logger.debug('Get Flex rcplindex')
                self.__index_file_loc = config.get('BaseRepo', sysinfo_ops.arch)
                index_file = urllib2.urlopen(self.__index_file_loc)
                # write to the local index file
                with open(self.__rcplindex_fname, 'wb') as index_out:
                    index_out.write(index_file.read())
        except Exception as err:
            self.__error = err
            self.__log_helper.logger.error(str(self.__error))

        # process info
        if self.__error is None:  # no error yet
            try:
                self.__handler = rcpl.file_io.handler.RCPLINDEX_READER(self.__rcplindex_fname, False, False, None)
                self.__handler.load_index()
                self.__available_rcpls = self.__handler.getData()
                # self.__log_helper.logger.error(str(self.__available_rcpls))
                if len(self.__available_rcpls) == 1:
                    for key in self.__available_rcpls:
                        if key is None:
                            self.__error = "The directory.xml file of your Pro account does not have valid RCPL information. Please check with your Wind River support!"
                            self.__log_helper.logger.error(str(self.__error))
            except Exception as err:
                self.__error = err
                self.__log_helper.logger.error(str(self.__error))

        # get current repo URLs
        self.__repoUrls = []
        if self.__error is None:  # no error yet
            try:
                if self.__pro_enabled:
                    # note: the Pro and Flex directory.xml has different meaning for file
                    self.__repoUrls = self.__available_rcpls[str(self.__current_rcpl)]['files']
                else:
                    rcpl_file_locs = self.__available_rcpls[str(self.__current_rcpl)]["files"]
                    for file_loc in rcpl_file_locs:
                        rcpl_file = urllib2.urlopen(file_loc)
                        for url in rcpl_file:
                            url = url.strip('\r\n')
                            self.__repoUrls.append(url)
                self.__log_helper.logger.info("Current Flex or Pro repos: " + str(self.__repoUrls))
            except Exception as err:
                self.__error = err
                self.__log_helper.logger.error(str(self.__error))

        # find the next rcpl version
        if self.__error is None:  # no error yet
            try:
                for version, data in self.__available_rcpls.iteritems():
                    if int(version) > self.__current_rcpl and data["arch"] == self.__arch and version > self.highest_rcpl:
                        self.higher_version = True
                        self.highest_rcpl = version
            except Exception as err:
                self.__error = err
                self.__log_helper.logger.error(str(self.__error))

        # find the highest rcpl repos
        if self.__error is None:  # no error yet
            try:
                if self.higher_version:
                    if self.__pro_enabled:
                        # note: the Pro and Flex directory.xml has different meaning for file
                        self.__repoUrls_highest = self.__available_rcpls[str(self.highest_rcpl)]['files']
                    else:
                        rcpl_file_locs = self.__available_rcpls[str(self.highest_rcpl)]["files"]
                        for file_loc in rcpl_file_locs:
                            rcpl_file = urllib2.urlopen(file_loc)
                            for url in rcpl_file:
                                url = url.strip('\r\n')
                                self.__repoUrls_highest.append(url)
                    self.__log_helper.logger.info("Highest Flex or Pro repos: " + str(self.__repoUrls_highest))
            except Exception as err:
                self.__error = err
                self.__log_helper.logger.error(str(self.__error))

        self.__log_helper.logger.debug("RCPL current, highest: " + str(self.__current_rcpl) + ", " + str(self.highest_rcpl))
        # print str(self.__current_rcpl)
        # print str(self.highest_rcpl)

    def get_error(self):
        """

        Returns:
            None if there is no error. Error string if there is error.
        """
        if self.__error is None:
            return None
        else:
            return str(self.__error)

    def check_os_repos_existed(self, check_pro=False):
        """ Check if OS repos exist already or not
        Args:
            check_pro (bool): True if checking Pro repos. False if checking Flex repos.
        Returns:
            bool: True if at least one flex repo exists.
        """
        try:
            if check_pro:
                cmd = "smart channel --show | grep " + manage_config.pro_repo_name
            else:
                cmd = "smart channel --show | grep " + manage_config.flex_repo_name
            u = subprocess.check_output(cmd, shell=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def remove_os_repos(self, do_update=True, do_pro=False):
        """ Remove OS repos
        We do not re-build the package database in this function though.

        Args:
            do_update (bool): True if we do Smart Update at the end.
            do_pro (bool): True if we remove pro.

        Returns:
            dict: {'status': 'fail', 'error': ''} or {'status': 'success', 'error': ''}
        """
        result = {'status': 'fail', 'error': ''}
        if self.__error is None:  # no error yet
            if do_pro:
                repo_name = manage_config.pro_repo_name
            else:
                repo_name = manage_config.flex_repo_name

            # build to-be-removed list
            list_repos = manage_repo.list_repos()
            for repo in list_repos:
                if repo_name in repo:
                    command = "smart channel --remove '" + repo + "' -y"
                    remove_result = shell_ops.run_cmd_chk(command)
                    if remove_result['returncode']:  # fail
                        result['error'] = "remove failed: " + remove_result['cmd_output']
                        return result

            if do_update:
                update_result = shell_ops.run_cmd_chk("smart update")
                if update_result['returncode']:  # fail
                    result['error'] = "update failed: " + update_result['cmd_output']
                    return result

            result['status'] = 'success'
            result['error'] = ''
        else:  # fail
            result['error'] = str(self.__error)
        return result

    def add_os_repos(self, do_rcpl_update=False, user_name='', password=''):
        """ Add OS repos
        We do not re-build the package database in this function though.
        This logic does not work for flex to pro upgrade.
        Logic:
            If do_rcpl_update,
                remove existing one
                add the highest rcpl's repos.
            Else,
                If OS repos do not exist
                    add the current rcpl's repos.

        Args:
            do_rcpl_update (bool): True if we want to update to the highest RCPL.
            user_name (str): user name for Pro repo.
            password (str): password for Pro repo.

        Returns:
            dict: {'status': 'fail', 'error': ''} or {'status': 'success', 'error': ''}
        """
        result = {'status': 'fail', 'error': ''}
        if self.__error is None:  # no error yet
            target_repos_list = []
            if do_rcpl_update and self.higher_version:
                # remove existing one first
                remove_result = self.remove_os_repos(do_update=False, do_pro=self.__pro_enabled)
                if remove_result['status'] == 'fail':
                    result['error'] = 'Cannot remove old OS repos. ' + remove_result['error']
                    return result
                # get the highest RCPL's repos.
                target_repos_list = self.__repoUrls_highest
            else:
                if not self.check_os_repos_existed(check_pro=self.__pro_enabled):  # no OS repo yet
                    # get the current RCPL's repos.
                    target_repos_list = self.__repoUrls

            if target_repos_list:  # not empty
                # add
                repo_number = 0
                for url in target_repos_list:
                    repo_number += 1
                    if self.__pro_enabled:
                        repo_pre_name = manage_config.pro_repo_name
                        repo_name = repo_pre_name + str(repo_number)
                        user_name = user_name.replace("@", "%40")
                        url = url.replace("://", "://%s:%s@" % (user_name, password))
                        command = "smart channel --add '" + repo_name + "' type=rpm-md baseurl='" + url + "' -y"
                    else:
                        repo_pre_name = manage_config.flex_repo_name
                        repo_name = repo_pre_name + str(repo_number)
                        command = "smart channel --add '" + repo_name + "' type=rpm-md baseurl='" + url + "' -y"
                    self.__log_helper.logger.debug("About to add OS repo: " + str(repo_name) + " " + str(url))
                    # add
                    add_result = shell_ops.run_cmd_chk(command)
                    if add_result['returncode']:  # fail
                        if "error" in add_result['cmd_output']:
                            result['error'] = "Failed to add repository: " + add_result['cmd_output'][add_result['cmd_output'].index("error:") + 7:].replace("\n", "")
                        else:
                            result['error'] = "Error adding update repository: " + add_result['cmd_output']
                        self.__log_helper.logger.error("Failed to add repository. Error output: '%s'" % result['error'])
                        # remove OS repos upon failure
                        self.remove_os_repos(do_update=True, do_pro=self.__pro_enabled)
                        # TODO: check result['error'] to remove account and password. ://[account]:[password]@ to ://
                        return result
                    # update
                    command = "smart update '" + repo_name + "'"
                    update_result = shell_ops.run_cmd_chk(command)  # Attempt to connect to new repo
                    if update_result['returncode']:  # If attempt fails determine error and remove repo
                        # Sometimes, some special repo URL will not be removed from the cache file when the repo is removed. (repo add and then repo remove)
                        # If this happens, then "smart update this repo" will fail. So we want to manually delete the cache file.
                        if "OSError: [Errno 2] No such file or directory" in update_result['cmd_output']:
                            self.__log_helper.logger.debug("trying to remove cache file and retry...")
                            if os.path.isfile(manage_config.smart_cache_file):
                                self.__log_helper.logger.debug(manage_config.smart_cache_file + ' exists, so we will try to remove it.')
                                try:
                                    os.remove(manage_config.smart_cache_file)
                                    self.__log_helper.logger.debug("Try updating again............")
                                    update_result = shell_ops.run_cmd_chk(command)  # Attempt to connect to new repo
                                    if not update_result['returncode']:  # If it works
                                        continue  # go to the next loop item
                                except Exception as e:
                                    self.__log_helper.logger.error(manage_config.smart_cache_file + ' cannot be removed. ' + str(e))
                        if "error" in update_result['cmd_output']:
                            if "Invalid URL" in update_result['cmd_output']:
                                result['error'] = "Failed to add repository: Invalid URL."
                            elif "Failed to connect" in update_result['cmd_output'] or 'URL returned error: 503' in update_result['cmd_output']:
                                result['error'] = "Failed to add repository: Unable to connect to repository."
                            elif "Invalid XML" in update_result['cmd_output']:
                                result['error'] = "Failed to add repository: Repository XML file invalid. "
                            else:
                                result['error'] = update_result['cmd_output'][update_result['cmd_output'].index("error:") + 7:].replace("\n", "")
                        else:
                            result['error'] = 'Error adding repository: ' + update_result['cmd_output']
                        self.__log_helper.logger.error("Failed to add repository. Error output: '%s'" % result['error'])
                        # remove OS repos upon failure
                        self.remove_os_repos(do_update=True, do_pro=self.__pro_enabled)
                        # TODO: check result['error'] to remove account and password. ://[account]:[password]@ to ://
                        return result
                result['status'] = 'success'
                result['error'] = ''
            else:  # else of if target_repos_list
                result['status'] = 'success'
                result['error'] = ''
        else:  # else of if self.__error is None
            result['error'] = str(self.__error)
            # TODO: check result['error'] to remove account and password. ://[account]:[password]@ to ://
        return result

    def osUpdate(self, user_name='', password=''):
        """ Do OS Update
        Logic:
            If Flex:
                Force to replace existing flex repos with highest flex rcpl repos.
            Else (Pro):
                Force to replace existing pro repos with highest pro rcpl repos.
            Enable only the OS repos.
            Do Smart Upgrade.
            Enable the previous disabled repos (non-OS repos).
            Check default repo and update channel and build package database.

        Args:
            user_name (str): user name for Pro repo.
            password (str): password for Pro repo.

        Returns:
            dict: {'status': 'failure', 'message': ''} or {'status': 'success', 'message': ''}
        """
        self.__result['status'] = 'failure'
        if self.__error is None:  # no error yet

            # Flex: force to replace existing flex repos with highest rcpl repos.
            # Pro: force to replace existing pro repos with highest rcpl repos.
            add_result = self.add_os_repos(do_rcpl_update=True, user_name=user_name, password=password)
            if add_result['status'] == 'fail':
                self.__result['message'] = 'It failed to add OS repos. ' + add_result['error']
                return self.__result

            # enable only the OS repos
            response_repos = manage_repo.enable_only_os_repos()
            if response_repos['status'] is False:
                self.__result['message'] = 'It failed to disable non-OS repos.'
                return self.__result

            # do smart upgrade
            cmd_output = shell_ops.run_cmd_chk("smart upgrade -y")
            if cmd_output['returncode']:  # fail
                # re-enable the disabled repo
                manage_repo.enable_repo(response_repos['disabled_repos'])
                self.__result['message'] = "Error during upgrade process. Error: " + cmd_output['cmd_output']
                return self.__result

            # re-enable the disabled repo
            manage_repo.enable_repo(response_repos['disabled_repos'])

            # check default repo and update channel
            manage_repo.configure_default_repo()

            self.__result['status'] = 'success'
        else:
            self.__result['status'] = 'failure'

        return self.__result


@require()
class OSUpdate(object):
    exposed = True

    def __init__(self):
        self.__network_checker = network_ops.NetworkCheck()
        self.__log_helper = logging_helper.logging_helper.Logger()

    def POST(self):
        # Increased timeout value (12 hours) quark
        cherrypy.response.timeout = 43200

        result = {'status': 'failure', 'message': '', 'in_progress': False}

        try:
            header_cl = cherrypy.request.headers['Content-Length']
            cl_content = cherrypy.request.body.read(int(header_cl))
            kwargs = json.loads(cl_content)

            # do not do this if this is checking, not submitting
            check_network = True
            if 'is_checking' in kwargs:
                if kwargs['is_checking'] == 'True':
                    check_network = False
            if check_network:
                self.__network_checker.test_network_connection()
                if not self.__network_checker.get_stored_https_status():
                    result['message'] = 'Gateway does not have network connection to the repositories.'
                    return json.dumps(result)

            # grab credential
            user_name = ''
            password = ''
            if 'username' in kwargs:
                user_name = kwargs['username']
            if 'password' in kwargs:
                password = kwargs['password']
            # check type
            if 'type' in kwargs:
                target_type = kwargs['type']
                if target_type == 'check':
                    if 'request' in kwargs:
                        if kwargs['request'] == 'rcpl':
                            # =====================================
                            # Check RCPL
                            # =====================================
                            retrieving_work, result = manage_worker.do_work(manage_worker.worker_process_message_type_check_rcpl_update,
                                                                            kwargs)
                            if retrieving_work:
                                if result['status'] == 'success':
                                    # {u'status': u'success',
                                    #  u'message': u'{
                                    #       "status": "success",
                                    #       "message": "",
                                    #       "update": True/False
                                    #   }',
                                    #  u'in_progress': False,
                                    #  u'work_type': ''}
                                    # move the key work result to the 1st dictionary item
                                    json_data = json.loads(result['message'])
                                    result['status'] = json_data['status']  # this can still be 'failure'
                                    result['update'] = json_data['update']
                                    result['message'] = json_data['message']
                        elif kwargs['request'] == 'package':
                            # =====================================
                            # Check OS packages
                            # =====================================
                            retrieving_work, result = manage_worker.do_work(manage_worker.worker_process_message_type_check_os_packages_update,
                                                                            kwargs)
                            if retrieving_work:
                                if result['status'] == 'success':
                                    # {u'status': u'success',
                                    #  u'message': u'{
                                    #       "status": "success",
                                    #       "packages": [],
                                    #       "package_update": True/False
                                    #   }',
                                    #  u'in_progress': False,
                                    #  u'work_type': ''}
                                    # move the key work result to the 1st dictionary item
                                    json_data = json.loads(result['message'])
                                    result['status'] = json_data['status']  # this can still be 'failure'
                                    result['packages'] = json_data['packages']
                                    result['package_update'] = json_data['package_update']
                        else:
                            result['message'] = 'Unsupported check request: ' + str(kwargs['request'])
                    else:
                        result['message'] = 'The request data does not have request.'
                elif target_type == 'update_rcpl':
                    # =====================================
                    # do rcpl udpate
                    # =====================================
                    retrieving_work, result = manage_worker.do_work(manage_worker.worker_process_message_type_do_rcpl_update,
                                                                    kwargs)
                    if retrieving_work:
                        if result['status'] == 'success':
                            # {u'status': u'success',
                            #  u'message': u'{
                            #       "status": "success",
                            #       "message": ""
                            #   }',
                            #  u'in_progress': False,
                            #  u'work_type': ''}
                            # move the key work result to the 1st dictionary item
                            json_data = json.loads(result['message'])
                            result['status'] = json_data['status']  # this can still be 'failure'
                            result['message'] = json_data['message']
                elif target_type == 'update_packages':
                    # =====================================
                    # do os packages update
                    # =====================================
                    retrieving_work, result = manage_worker.do_work(manage_worker.worker_process_message_type_do_os_packages_update,
                                                                    kwargs)
                    if retrieving_work:
                        if result['status'] == 'success':
                            # {u'status': u'success',
                            #  u'message': u'{
                            #       "status": "success",
                            #       "message": "",
                            #       "p_list": []
                            #   }',
                            #  u'in_progress': False,
                            #  u'work_type': ''}
                            # move the key work result to the 1st dictionary item
                            json_data = json.loads(result['message'])
                            result['status'] = json_data['status']  # this can still be 'failure'
                            result['message'] = json_data['message']
                            result['p_list'] = json_data['p_list']
                else:
                    result['message'] = 'Unsupported request type: ' + str(target_type)
            else:
                result['message'] = 'The request data does not have type.'
        except Exception as e:
            result['status'] = 'failure'
            result['message'] = str(e)
        return json.dumps(result)
