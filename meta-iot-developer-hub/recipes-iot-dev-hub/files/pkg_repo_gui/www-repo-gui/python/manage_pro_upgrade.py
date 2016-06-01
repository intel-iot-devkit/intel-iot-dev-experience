# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import cherrypy
import subprocess
import os
import json
import ast
from cgi import escape
from tools import logging_helper, network_ops, shell_ops, sysinfo_ops, rcpl
import manage_config
import manage_repo
import manage_os_update
import manage_package
from manage_auth import require
import manage_worker


class ProPackageList(object):
    """ Class to get and handle the packages list file.
    """

    @staticmethod
    def get_packages():
        """ Get list of pro packages.

        Returns:
            list: list of package name
        """
        log_helper = logging_helper.logging_helper.Logger()
        package_list = []
        try:
            if os.path.exists(manage_config.pro_packages_file):
                # read all lines first
                file_handle = open(manage_config.pro_packages_file, "r")
                file_lines = file_handle.readlines()
                file_handle.close()
                for file_line in file_lines:
                    # removing training newline and white space
                    file_line = file_line.rstrip()
                    if file_line:  # if the line is not empty
                        # escape the package name since it will be used as part of shell command later.
                        file_line_escaped = escape(file_line, True)
                        package_list.append(file_line_escaped)
                return package_list
            else:
                return package_list
        except Exception as e:
            log_helper.logger.error("get_packages failed..." + str(e))
            return package_list


class ProStatus(object):

    def __init__(self):
        self.__config = manage_config.read_config_file()
        self.__config_file = os.path.dirname(__file__) + '/' + 'developer_hub_config'
        self.__pro_status = {'result': None}

    def enabled_state(self):
        try:
            status = self.__config.get('ProRepo', 'enable_pro')
            if status != 'True':
                status = 'False'
            self.__pro_status['result'] = status
        except:
            # If another process/thread is writing the file, then we will run into exception.
            # In this case, we report that we don't know the status.
            self.__pro_status['result'] = 'NA'
        return self.__pro_status

    def upgrade_status(self, status):
        self.__config.set('ProRepo', 'enable_pro', status)
        set_config = open(self.__config_file, 'w')
        self.__config.write(set_config)


class ProRepo(object):

    def __init__(self):
        self.__install_list = []
        self.__log_helper = logging_helper.logging_helper.Logger()
        self.__has_failure = False
        self.__result_dict = {}
        self.__str_status_failure = 'failure'
        self.__str_status_success = 'success'
        self.__str_status_key = 'status'
        self.__str_error_key = 'error'
        self.__str_error = ''
        self.__config = ProStatus()

    def os_upgrade(self, user_name, password):
        self.__result_dict[self.__str_status_key] = self.__str_status_failure
        self.__result_dict[self.__str_error_key] = ''

        self.__config.upgrade_status('True')

        updater = manage_os_update.OS_UPDATER(sysinfo_ops.rcpl_version, sysinfo_ops.arch,
                                              user_name=user_name, password=password)

        # Add pro repositories
        if not self.__has_failure:
            repo_result = updater.add_os_repos(do_rcpl_update=False, user_name=user_name, password=password)
            if repo_result['status'] == 'fail':
                self.__str_error += repo_result['error']
                self.__has_failure = True

        # Install Pro Packages
        build_list = ProPackageList()
        self.__install_list = build_list.get_packages()
        if not self.__has_failure:
            for package in self.__install_list:
                self.__log_helper.logger.debug('Installing ' + str(package))
                try:
                    command = "smart install -y " + package
                    result = shell_ops.run_cmd_chk(command)
                    response = manage_package.parse_package_installation_result(pkg_name=package, result_dict=result)
                    if 'status' in response:
                        if (response['status'] != 'success') and ('error' in response):
                            self.__has_failure = True
                            self.__str_error += response['error']
                            self.__str_error += ' '
                except Exception as e:
                    self.__has_failure = True
                    self.__str_error += ("For " + package + ", " + str(e))
                    self.__str_error += ' '
                    pass

        if self.__has_failure:
            self.__log_helper.logger.error("Package installation failed:  " + self.__str_error)
            self.__result_dict[self.__str_status_key] = self.__str_status_failure
            self.__result_dict[self.__str_error_key] = self.__str_error
            self.__config.upgrade_status('False')
            updater.remove_os_repos(do_update=True, do_pro=True)
        else:
            self.__result_dict[self.__str_status_key] = self.__str_status_success
            self.__log_helper.logger.debug(str(self.__result_dict))
            # Remove old repositories
            updater.remove_os_repos(do_update=True, do_pro=False)

        # Rebuild package database, now that we have pro repos.
        manage_package.build_package_database()

        # Update GUI
        return json.dumps(self.__result_dict)


@require()
class EnablePro(object):
    exposed = True

    def GET(self, **kwargs):
        config = ProStatus()
        pro_status = config.enabled_state()
        return json.dumps(pro_status)

    def POST(self, **kwargs):
        # Increased timeout value (12 hours) quark
        cherrypy.response.timeout = 43200

        log_helper = logging_helper.logging_helper.Logger()
        header_cl = cherrypy.request.headers['Content-Length']
        cl_content = cherrypy.request.body.read(int(header_cl))
        kwargs = json.loads(cl_content)

        retrieving_work, worker_result = manage_worker.do_work(manage_worker.worker_process_message_type_pro_upgrade,
                                                               kwargs)
        try:
            if retrieving_work:
                if worker_result['status'] == 'success':
                    # {u'status': u'success',
                    #  u'message': u'{"status": "success", "error": ""}',
                    #  u'in_progress': False,
                    #  u'work_type': ''}
                    # move the key work result to the 1st dictionary item
                    result_dict = ast.literal_eval(worker_result['message'])
                    worker_result['status'] = result_dict['status']  # this can still be 'failure'
                    worker_result['error'] = result_dict['error']
                    worker_result['message'] = worker_result['error']  # copy the error message if any
        except Exception as e:
            worker_result['status'] = 'failure'
            worker_result['message'] = str(e)
        return json.dumps(worker_result)
