#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import cherrypy
import json
import subprocess
from manage_auth import require
from tools import sysinfo_ops


@require()
class OSControls(object):
    exposed = True

    def GET(self, **kwargs):
        data_collect = sysinfo_ops.DataCollect()
        device_info = data_collect.getDataSet()
        return json.dumps(device_info)

    def POST(self):
        result = {'status': 'success', 'message': ''}

        try:
            subprocess.Popen('sleep 10s; sudo -u wra /usr/bin/dh-rfs', shell=True)
        except Exception as e:
            result['status'] = 'failure'
            result['message'] = str(e)

        return json.dumps(result)

    def PUT(self):
        result = {'status': 'success', 'message': ''}

        try:
            subprocess.Popen('sleep 10s; sudo shutdown -r now', shell=True)
        except Exception as e:
            result['status'] = 'failure'
            result['message'] = str(e)

        return json.dumps(result)
