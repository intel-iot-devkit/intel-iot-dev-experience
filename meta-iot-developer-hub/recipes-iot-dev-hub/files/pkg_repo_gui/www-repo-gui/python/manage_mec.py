# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

from manage_auth import require
from tools import shell_ops
import json


class MEC(object):
    def __init__(self):
        self.mec_type = ""
        self.enabled = False
        self.installed = False

    def GetMecType(self):
        self.mec_type = ""
        try:
            result = shell_ops.run_command("sadmin license list")
            if "MEC Essential" in result:
                self.mec_type = "Essential"
            else:
                self.mec_type = "Pro"
        except:
                pass
        return self.mec_type
    
    def IsMecInstalled(self):
        try:
            result = shell_ops.run_command("sadmin version")
        except:
            pass
            result = ""        
        if "McAfee Solidifier" in result:
            self.installed = True
        return self.installed         
        
    def IsMecEnabled(self):
        try:
            result = shell_ops.run_command("sadmin status")
        except:
            pass
            result = ""        
        if "Enabled" in result:
            self.enabled = True 
        return self.enabled


@require() 
class MEC_API(object):
    exposed = True
  
    def GET(self, **kwargs):
        mec = MEC()
        response = ({
                      'status': 'success',
                      'type': mec.GetMecType(),
                      'installed': mec.IsMecInstalled(),
                      'enabled': mec.IsMecEnabled()
                    })
        return json.dumps(response)   
