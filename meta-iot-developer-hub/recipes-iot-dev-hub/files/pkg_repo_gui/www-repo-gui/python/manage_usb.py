#!/usr/bin/env python

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import subprocess
from json import dumps
from manage_auth import require


class UsbSupport(object):

    def list_usbs(self):
        mu = MANAGE_USB()
        return mu.list_usbs()


class MANAGE_USB(object):
    def __init__(self):
        self.usbs = []
        self.myparts = []

    def to_readable(self, number):
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
        if number == 0:
            return '0 B'

        i = 0
        while (number >= 1024) and (i < len(suffixes)-1):
            number /= 1024.
            i += 1
        f = ('%.2f' % number).rstrip('0').rstrip('.')
        return '%s %s' % (f, suffixes[i])

    def list_usbs(self):
        with open('/proc/partitions', 'r') as parts:
            for line in parts:
                self.myparts.append(line.split())

        for field in self.myparts[2:]:
            devid = field[3]  # 4th column of the '/proc/partitions' output
            sz = ""
            try:
                # we expect a usb drive to be named "/dev/sd-" where - is a letter, b, c, etc
                if devid[0] != 's' or devid[1] != 'd':
                    continue  #
                if devid[-1:] in ['0', '1', '2', '3', '4', '5', '6',
                                  '7', '8', '9']:  # if devid in range(0, 9)
                    continue  # ignore numbered devices; only care about "main" device

                # basis for "USB" drive is if removable, per Linux. 
                is_removable = None
                m_vendor = None
                m_model = None
                with open('/sys/block/'+devid+'/removable', 'r') as typeid:
                    is_removable = typeid.read()

                with open('/sys/block/'+devid+'/device/model', 'r') as model:
                    m_model = model.read().rstrip('\n').rstrip(' ')

                with open('/sys/block/'+devid+'/device/vendor', 'r') as vendor:
                    m_vendor = vendor.read().rstrip('\n').rstrip(' ')

                if int(is_removable) == 1:
                    result = subprocess.check_output(["blockdev", "--getsize64", "/dev/"+devid]).rstrip('\n')
                    newresult = self.to_readable(int(result))
                    dev = "%s-%s (/dev/%s)" % (m_vendor, m_model, devid)
                    self.usbs.append({"Name": "%s-%s (/dev/%s)" % (m_vendor, m_model, devid),
                                      "Size": newresult,
                                      "Device": "/dev/%s" % devid})
            except subprocess.CalledProcessError as e:
                return_code = e.returncode

        my_json = dumps(self.usbs, sort_keys=False, indent=4, separators=(',', ': '))
        return my_json


@require()         
class USB_API(object):
    exposed = True
    
    def GET(self, **kwargs):
        us = UsbSupport()
        u = us.list_usbs()
        return u
