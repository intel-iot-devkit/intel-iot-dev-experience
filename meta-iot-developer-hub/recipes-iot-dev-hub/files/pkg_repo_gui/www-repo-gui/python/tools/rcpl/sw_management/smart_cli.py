#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import subprocess
import os
from .. import exception
from tools import logging_helper, shell_ops
import manage_config


class REPO_HANDLER(object):
    def __init__(self):
        self.__error = None
        self.__repo_number = 0
        self.__result = dict()
        self.__response = dict()
        self.__log_helper = logging_helper.logging_helper.Logger()

    def add(self, repo_urls):
        self.__response['status'] = "failure"
        for url in repo_urls:
            self.__repo_number += 1
            repo_name = manage_config.flex_repo_name + str(self.__repo_number)
            self.__log_helper.logger.debug(str(repo_name) + " " + str(url))
            command = "smart channel --add '" + repo_name + "' type=rpm-md baseurl=" + url + " -y"
            result = shell_ops.run_cmd_chk(command)
            if result['returncode']:
                if "error" in result['cmd_output']:
                    self.action(repo_name, 'remove', 'WR')
                    self.__error = "Failed to add repository: " + result['cmd_output'][result['cmd_output'].index("error:") + 7:].replace("\n", "")
                else:
                    self.__error = "Error adding update repository"
                self.__response['message'] = self.__error
                self.__log_helper.logger.error("Failed to add repository. Error output: '%s'" % self.__response['message'])
                return self.__response
            else:
                command = "smart update '" + repo_name + "'"
                result = shell_ops.run_cmd_chk(command)  # Attempt to connect to new repo
                if result['returncode']:  # If attempt fails determine error and remove repo

                    # Sometimes, some special repo URL will not be removed from the cache file when the repo is removed. (repo add and then repo remove)
                    # If this happens, then "smart update this repo" will fail. So we want to manually delete the cache file.
                    if "OSError: [Errno 2] No such file or directory" in result['cmd_output']:
                        self.__log_helper.logger.debug("trying to remove cache file and retry...")
                        if os.path.isfile(manage_config.smart_cache_file):
                            self.__log_helper.logger.debug(manage_config.smart_cache_file + ' exists, so we will try to remove it.')
                            try:
                                os.remove(manage_config.smart_cache_file)
                                self.__log_helper.logger.debug("Try updating again............")
                                result = shell_ops.run_cmd_chk(command)  # Attempt to connect to new repo
                                if not result['returncode']:  # If it works
                                    continue  # go to the next loop
                            except Exception as e:
                                self.__log_helper.logger.error(manage_config.smart_cache_file + ' cannot be removed. ' + str(e))

                    if "error" in result['cmd_output']:
                        if "Invalid URL" in result['cmd_output']:
                            self.__response['message'] = "Failed to add repository: Invalid URL."
                        elif "Failed to connect" in result['cmd_output'] or 'URL returned error: 503' in result['cmd_output']:
                            self.__response['message'] = "Failed to add repository: Unable to connect to repository."
                        elif "Invalid XML" in result['cmd_output']:
                            self.__response['message'] = "Failed to add repository: Repository XML file invalid. "
                        else:
                            self.__response['message'] = result['cmd_output'][result['cmd_output'].index("error:") + 7:].replace("\n", "")
                    else:
                        self.__response['message'] = 'Error adding repository: ' + str(result['cmd_output'])

                    self.action(repo_name, 'remove', 'WR')
                    self.__log_helper.logger.error("Failed to add repository. Error output: '%s'" % self.__response['message'])
                    return self.__response
        self.__response['status'] = "success"
        self.__log_helper.logger.debug(str(self.__response))
        return self.__response

    def action(self, m_repo, action, type):
        cmd_output = dict()
        for repo in m_repo:
            if type == 'not_WR' and manage_config.flex_repo_name not in repo:
                self.__log_helper.logger.debug(str(action) + " " + str(repo))
                cmd_output = shell_ops.run_cmd_chk("smart channel --" + action + " " + repo + " -y")
                if cmd_output['returncode']:
                    return cmd_output
            if type == 'WR' and manage_config.flex_repo_name in repo:
                self.__log_helper.logger.debug(str(action) + " " + str(repo))
                cmd_output = shell_ops.run_cmd_chk("smart channel --" + action + " " + repo + " -y")
                if cmd_output['returncode']:
                    return cmd_output
        if action == 'remove':
            cmd_output = shell_ops.run_cmd_chk("smart update")
        cmd_output['returncode'] = 0
        return cmd_output
