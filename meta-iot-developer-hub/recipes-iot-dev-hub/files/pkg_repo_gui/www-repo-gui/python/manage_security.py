# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

from manage_auth import require
from server import shutdown_http_server
import subprocess
import json
import ast
import os
from cgi import escape
import cherrypy
from tools import logging_helper, sysinfo_ops
import manage_config
import manage_package
import manage_worker


def save_default_custom_harden_data(packages_removed, mec_updater):
    """ Replace the old default config files based on the input.

    Args:
        packages_removed (list): list of package names
        mec_updater (list): list of updater files with full path

    Returns:

    """
    log_helper = logging_helper.logging_helper.Logger()
    try:
        with open(manage_config.harden_image_packages_config_file, "w") as myfile:
            for pkg in packages_removed:
                myfile.write(pkg + "\n")
        with open(manage_config.harden_image_updater_config_file, "w") as myfile:
            for updater in mec_updater:
                myfile.write(updater + "\n")
    except Exception as e:
        log_helper.logger.error(str(e))


def get_default_custom_harden_data():
    """ Get the default data for harden image configuration.

    Returns:
        dict: {'packages_removed': {}, 'mec_updater': [], 'stig': [], 'stig_all': {}}
    """
    log_helper = logging_helper.logging_helper.Logger()
    # {'package_name_1': True, 'package_name_2': False, ......}
    # True means that this is to be removed and is not configurable by the user.
    # False means that the user can configure this to be removed or not.
    packages_removed_dict = {}
    return_data = {'packages_removed': {}, 'mec_updater': [], 'stig': [], 'stig_all': {}}
    try:

        try:
            with open('/lib/lockdown/devhub.sh', 'r') as pkg_list:
                for l in pkg_list:
                    if 'uninstall_package' in l:
                        p = l.split(" ")
                        package = p[1].strip("\n")
                        packages_removed_dict[package] = True
        except:
            pass

        # This is to read the harden_image_packages_config_file to get what user chose last time.
        # We are doing this after we processed the Wind River lock down script.
        #      This means that if a package is both specified in Wind River lock down script and this file,
        #      It will be give True instead of False in packages_removed_dict.
        if os.path.exists(manage_config.harden_image_packages_config_file):
            # read all lines first
            file_handle = open(manage_config.harden_image_packages_config_file, "r")
            file_lines = file_handle.readlines()
            file_handle.close()
            # get installed packages list
            packages_installed = manage_package.get_data_installed()
            if packages_installed is not None:
                packages_installed_dict = ast.literal_eval(packages_installed)
                # loop through lines
                for file_line in file_lines:
                    # removing training newline and white space
                    file_line = file_line.rstrip()
                    if file_line:  # if the line is not empty
                        # escape the package name since it will be used as part of shell command later.
                        file_line_escaped = escape(file_line, True)
                        # check if it is installed
                        if file_line_escaped in packages_installed_dict:
                            # check if it is not already there
                            if file_line_escaped not in packages_removed_dict:
                                packages_removed_dict[file_line_escaped] = False
        else:
            pass

        return_data['packages_removed'] = packages_removed_dict

        if os.path.exists(manage_config.harden_image_updater_config_file):
            # read all lines first
            file_handle = open(manage_config.harden_image_updater_config_file, "r")
            file_lines = file_handle.readlines()
            file_handle.close()
            for file_line in file_lines:
                # removing training newline and white space
                file_line = file_line.rstrip()
                if file_line:  # if the line is not empty
                    # escape the path
                    file_line_escaped = escape(file_line, True)
                    # check if the path exists as a file
                    if os.path.isfile(file_line_escaped):
                        return_data['mec_updater'].append(file_line_escaped)
        else:
            pass

        if os.path.exists(manage_config.harden_image_stig_config_file):
            # read all lines first
            file_handle = open(manage_config.harden_image_stig_config_file, "r")
            file_lines = file_handle.readlines()
            file_handle.close()
            for file_line in file_lines:
                # removing training newline and white space
                file_line = file_line.rstrip()
                if file_line:  # if the line is not empty
                    # escape the stig id
                    file_line_escaped = escape(file_line, True)
                    return_data['stig'].append(file_line_escaped)
        else:
            pass

        if os.path.exists(manage_config.harden_image_stig_all_file):
            with open(manage_config.harden_image_stig_all_file, 'r') as myfile:
                return_data['stig_all'] = json.load(myfile)
        else:
            pass

        return json.dumps(return_data)
    except:
        return json.dumps(return_data)


class SecurityAutomationWorker(object):
    def __init__(self):
        self.__log_helper = logging_helper.logging_helper.Logger()
        self.__command = ""
        self.__data_collect = sysinfo_ops.DataCollect()
        version = self.__data_collect.getSystemVersion()
        version = version.split('.')
        if int(version[3]) >= 18:
            self.__custom_image = True
        else:
            self.__custom_image = False

    def standard_harden_image(self, usb_device, admin_passwd, mec_passwd):
        # Build command to build standard harden image
        admin_passwd = admin_passwd.replace("'", "\'\"'\"\'")
        mec_passwd = mec_passwd.replace("'", "\'\"'\"\'")
        # Single quote to preserve special characters
        # Special double quote & escape handling for single quote in the password
        self.__command = ("deploytool -C -F -y -v 0 -Y -d "+ usb_device + " --lockdown" + " -p 'root:" + admin_passwd
                          + "' -p 'gwuser:" + admin_passwd + "' -p 'wra:" + admin_passwd + "' --mec-passwd='"
                          + mec_passwd +"'")

    def custom_harden_image(self, usb_device, packages_removed, updaters, users):
        # Build command for custom harden image
        user_list = []
        package_skip = []
        existing_users = []
        mec_updaters = ""

        if self.__custom_image == True:
            self.__command = ("deploytool -C -F -y -v 0 -Y -d " + usb_device + " --lockdown")
            if updaters:
                for u in updaters:
                    mec_updaters = mec_updaters + u + ":"
                self.__command = self.__command + " -u " + mec_updaters[:-1]

            try:
                with open('/lib/lockdown/devhub.sh', 'r') as pkg_list:
                    for l in pkg_list:
                        if 'uninstall_package' in l:
                            p = l.split(" ")
                            ps = p[1].strip("\n")
                            package_skip.append(ps)
            except:
                pass

            if packages_removed:
                for package in packages_removed:
                    if package in package_skip:
                        pass
                    else:
                        self.__command = self.__command + " -e " + package

            for user in users:
                if 'Embedded Control' in user['name']:
                    mec_passwd = user['pw'].replace("'", "\'\"'\"\'")
                    self.__command = (self.__command + " --mec-passwd='" + mec_passwd +"'")
                else:
                    user_list.append(user['name'])
                    pw = user['pw'].replace("'", "\'\"'\"\'")
                    self.__command = (self.__command + " -p '" + user['name'] + ":" + pw + "'")

            try:
                existing_users = self.__data_collect.getTargetAccounts()
            except Exception as e:
                self.__log_helper.logger.error("Failed to build account list")

            if user_list:
                remove_list = [i for i in existing_users if i not in user_list]
                for r in remove_list:
                    self.__command = self.__command + " -d " + r
        else:
            self.__command = "skip"


    def create_harden_image(self):
        returncode = 0
        error = ""
        if self.__command == "skip":
            returncode = 1
            error = "Unable to create custom image. WindRiver version WR7.0.0.18 or greater is required."
        else:
            try:
                    result = subprocess.check_output(self.__command, shell=True)
                    self.__log_helper.logger.info(str(result))
            except subprocess.CalledProcessError as scriptreturncode:
                    # ERR_FAIL=1                       Normal failure
                    # ERR_IS_RUNNING=2                  Another deploytool process is running.
                    # ERR_NOT_ROOT=3                    Need to run as root but it is not.'
                    # ERR_NO_ENOUGH_SIZE=4            # No enough space left to save image file.
                    # ERR_DEVICE_TOO_SMALL=5          # Device or image file size is too small.
                    # ERR_COMMAND_CHECK=6             # Required command is not found.
                    # ERR_PART_TYPES=7                # Not supported partition layout or format.
                    # ERR_PART_READY=8                # Partition node is not ready in the system.
                    # ERR_INVALID_FILE=9              # File does not exist or is invalid.
                    # ERR_BLOCK_DEVICE=10             # Device is not a block device.
                    # ERR_NO_GRUBFILE=11              # Cannot find the grub.conf file.
                    # ERR_UPDATE_GRUB=12              # Fail to modify the grub.conf file.
                    # ERR_NO_CAPFILE=13               # Fail to find the cap file for capsule update.
                    # ERR_EXTRACT_TARBALL=14          # Fail to extract the rootfs tarball.
                    # ERR_COPY_FILE=15                # Fail to copy file.
                    # ERR_CREATE_PART=16              # Fail to create partition in the device.
                    # ERR_FORMAT_FS=17                # Fail to format the file system.
                    # ERR_PARAMETER=32                # Invalid or conflicting command line parameter.
                    # ERR_SYSCALL=128                 # Error when call system functions.

                    self.__log_helper.logger.error('return code = ' + str(scriptreturncode.returncode) + 'value = ' + str(scriptreturncode.output))
                    returncode = scriptreturncode.returncode
                    if returncode == 2:
                        error = "Can't start two instance of SAVE IMAGE. (Error code " + str(scriptreturncode.returncode) + ")"
                    elif returncode == 5 or returncode == 4:
                        error = "USB flash drive does not have sufficient space. Insert a different drive and try again. (Error code " + str(scriptreturncode.returncode) + ")"
                    elif returncode == 6:
                        error = "Critical system commands are missing which prevents saving an OS image. Restore development gateway to a factory OS and try again. (Error code " + str(scriptreturncode.returncode) + ")"
                    elif returncode == 7:
                        error = "Unable to use this USB flash drive. Insert a different drive and try again.  (Error code " + str(scriptreturncode.returncode) + ")"
                    elif returncode == 16:
                        error = "Unable to use this USB flash drive. Insert a different drive and try again.  (Error code " + str(scriptreturncode.returncode) + ") (Failed to create partition on device)"
                    elif returncode == 17:
                        error = "Unable to use this USB flash drive. Insert a different drive and try again.  (Error code " + str(scriptreturncode.returncode) + ") (Failed to format the file system)"
                    elif returncode == 9 or returncode == 11 or returncode == 12 or returncode == 13:
                        error = "Critical system files are missing which prevents saving an OS image. Restore development gateway to a factory OS and try again  (Error code " + str(scriptreturncode.returncode) + ")"
                    elif returncode == 128:
                        error = "Error when calling system functions. Restore development gateway to a factory OS and try again. (Error code " + str(scriptreturncode.returncode) + ") (Error when calling system functions)"
                    else:
                        error = "Unexpected error occurred. Try again. (Error code " + str(scriptreturncode.returncode) + ")"
               
        if returncode == 0:
                response = ({
                    'status': "success",
                    'error': ''
                })
 
        else:
                response = ({
                    'status': "failure",
                    'error': error
                 })                      
        return json.dumps(response)                


@require() 
class SecurityAutomation(object):
    exposed = True

    def GET(self, **kwargs):
        if 'type' not in kwargs:
            return None
        else:
            if kwargs['type'] == 'save_image_custom':
                return get_default_custom_harden_data()
            else:
                return None

    def PUT(self, **kwargs):
        retrieving_work, worker_result = manage_worker.do_work(manage_worker.worker_process_message_type_toggle_https,
                                                               kwargs)
        try:
            if retrieving_work:
                if worker_result['status'] == 'success':
                    # {u'status': u'success',
                    #  u'message': '',
                    #  u'in_progress': False,
                    #  u'work_type': ''}
                    # move the key work result to the 1st dictionary item

                    # restart Dev Hub server on success
                    shutdown_http_server()

        except Exception as e:
            worker_result['status'] = 'failure'
            worker_result['message'] = str(e)
        return json.dumps(worker_result)

    def POST(self):
        # Increased timeout value (12 hours) quark
        cherrypy.response.timeout = 43200

        header_cl = cherrypy.request.headers['Content-Length']
        cl_content = cherrypy.request.body.read(int(header_cl))
        kwargs = json.loads(cl_content)

        retrieving_work, worker_result = manage_worker.do_work(manage_worker.worker_process_message_type_save_image,
                                                               kwargs)
        try:
            if retrieving_work:
                if worker_result['status'] == 'success':
                    # {u'status': u'success',
                    #  u'message': u'{
                    #    'status': '',
                    #    'error': ''
                    #     }',
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


