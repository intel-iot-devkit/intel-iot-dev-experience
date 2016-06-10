# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

from manage_auth import require
from tools import shell_ops, logging_helper
import json
import os
import manage_worker
import ast


class DevHubUpdate(object):

    def __init__(self):
        self.__log_helper = logging_helper.logging_helper.Logger()
        self.__response = {'status': None}
        self.__script = '/tmp/update-iot-dev-hub.sh'
        self.__process = '#!/bin/bash\nsystemctl stop iot-dev-hub\nsmart upgrade -y iot-developer-hub\nsystemctl restart iot-dev-hub\nsystemctl start iot-dev-hub\n exit 0\n'

    def update(self):
        # make sure existing temp file is not used
        try:
            os.unlink(self.__script)
        except:
            # the file may not exist..
            pass

        try:
            dh_upgrade = open(self.__script, 'w+')
            dh_upgrade.write(self.__process)
            dh_upgrade.close()
            shell_ops.run_command('chmod 700 /tmp/update-iot-dev-hub.sh')
            shell_ops.run_command('systemctl --no-block start iot-dev-hub-update')
            self.__response['status'] = "success"
        except Exception as e:
            self.__log_helper.logger.error(str(e))
            self.__response['status'] = "failure"
        return self.__response


@require()
class SelfUpgrade(object):
    exposed = True

    def PUT(self, **kwargs):
        retrieving_work, worker_result = manage_worker.do_work(manage_worker.worker_process_message_type_self_upgrade,
                                                               kwargs)
        try:
            if retrieving_work:
                if worker_result['status'] == 'success':
                    # {u'status': u'success',
                    #  u'message': u'{
                    #    'status': ''
                    #     }',
                    #  u'in_progress': False,
                    #  u'work_type': ''}
                    # move the key work result to the 1st dictionary item
                    result_dict = ast.literal_eval(worker_result['message'])
                    worker_result['status'] = result_dict['status']  # this can still be 'failure'
        except Exception as e:
            worker_result['status'] = 'failure'
            worker_result['message'] = str(e)
        return json.dumps(worker_result)
