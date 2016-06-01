# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import os
import json
from datetime import datetime
import xml.etree.ElementTree as etree
from tools import logging_helper
import manage_config


class OemBrandingHandler(object):

    @staticmethod
    def GetOemBrandingConfig():
        log_helper = logging_helper.logging_helper.Logger()
        try:
            base_path = os.path.dirname(__file__)
            config_file = base_path + '/../branding/config.xml'
            xml_tree = etree.parse(config_file)
            xml_root = xml_tree.getroot()  # customizations
            # find if legacy file exists or not
            legacy_logo_file_path = base_path + '/../branding/oem-branding.png'
            if os.path.exists(legacy_logo_file_path):
                manage_config.oem_branding_config['logo_file'] = '/branding/oem-branding.png'
            else:
                # customizations \ custom-logo
                xml_logo = xml_root.find('custom-logo')
                if xml_logo is None:
                    manage_config.oem_branding_config['logo_file'] = ''
                else:
                     # customizations \ custom-logo \ logo-file
                    xml_logo_file = xml_logo.find('logo-file')
                    if xml_logo_file is None:
                        manage_config.oem_branding_config['logo_file'] = ''
                    else:
                        logo_file_path = base_path + '/../branding/logos/' + xml_logo_file.text
                        if os.path.exists(logo_file_path):
                            manage_config.oem_branding_config['logo_file'] = '/branding/logos/' + xml_logo_file.text
                        else:
                            manage_config.oem_branding_config['logo_file'] = ''

            log_helper.logger.debug('logo file ' + manage_config.oem_branding_config['logo_file'])

            # customizations \ custom-eulas
            xml_eulas = xml_root.find('custom-eulas')
            if xml_eulas is None:
                manage_config.oem_branding_config['eula_files'] = []
            else:
                # customizations \ custom-euals \ html-file
                xml_eulas_files = xml_eulas.findall('html-file')
                for eula_file in xml_eulas_files:
                    eula_file_path = base_path + '/../branding/eulas/' + eula_file.text
                    if os.path.exists(eula_file_path):
                        # get last modified date time
                        temp_time = str(datetime.fromtimestamp(os.path.getmtime(eula_file_path)))
                        manage_config.oem_branding_config['eula_files'].append('/branding/eulas/' + eula_file.text)
                        manage_config.oem_branding_config['eula_files_datetime'].append(temp_time)

            log_helper.logger.debug('eulas file ' + str(manage_config.oem_branding_config['eula_files']))

        except Exception as e:
            log_helper.logger.error(str(e))


class OemBranding(object):
    exposed = True
  
    def GET(self, **kwargs):
        response = ({
                      'status': 'success',
                      'result': manage_config.oem_branding_config
                    })
        return json.dumps(response)   
