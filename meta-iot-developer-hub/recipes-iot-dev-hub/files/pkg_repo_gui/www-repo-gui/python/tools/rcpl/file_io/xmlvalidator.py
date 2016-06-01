# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

#!/usr/bin/env python


from lxml import etree as ET
from .. import exception

class XML_VALIDATOR(object):
    def __init__(self, m_xml_fname, m_schema_fname):
        self.xml_fname = m_xml_fname
        self.schema_fname = m_schema_fname
        self.error = None
        self.schema_root = None
        try:
            with open(self.schema_fname, 'r') as schema:
                self.schema_root = ET.XML(schema.read())
        except IOError:
            self.error = "[FATAL ERROR]:  Schema file not found in specified location"
            
            
        self.schema = ET.XMLSchema(self.schema_root)
        self.xml_parser = ET.XMLParser(schema=self.schema)
        
        self.validateXMLFile()
        
    def validateXMLFile(self):
       try:
           with open(self.xml_fname, 'r') as xml_file:
               ET.fromstring(xml_file.read(), self.xml_parser)
       except(IOError, ET.XMLSyntaxError) as err:
           if isinstance(err, IOError):
               self.error = exception.errors.FILEIO_ERROR(self.xml_fname, 5002)
           elif isinstance(err, ET.XMLSyntaxError):
               self.error =  err

#if __name__ == '__main__':
#    validator = XML_VALIDATOR('sw_change.xml', 'sw_change_schema.xsd')


            
