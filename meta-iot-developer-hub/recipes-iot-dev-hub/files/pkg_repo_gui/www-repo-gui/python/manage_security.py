# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

from manage_auth import require
from server import shutdown_http_server
import subprocess
import json
import ast
import cherrypy
from tools import logging_helper
import manage_config
import manage_worker


class SecurityAutomationWorker(object):
    def __init__(self):
        self.__log_helper = logging_helper.logging_helper.Logger()

    def create_harden_image(self, usb_device, admin_passwd, mec_passwd):
        returncode = 0
        error = ""
        try:
                # Special double quote & escape handling for single quote in the password
                admin_passwd = admin_passwd.replace("'","\'\"'\"\'")
                mec_passwd = mec_passwd.replace("'","\'\"'\"\'")
                # Single quote to preserve special charaters
                result = subprocess.check_output("deploytool -C -F -y -v 0 -Y -d "+ usb_device + " --lockdown" + " -p 'root:" + admin_passwd + "' -p 'gwuser:" + admin_passwd + "' -p 'wra:" + admin_passwd + "' --mec-passwd='" + mec_passwd +"'", shell=True) 
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

    def POST(self, **kwargs):
        # Increased timeout value (12 hours) quark
        cherrypy.response.timeout = 43200

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
