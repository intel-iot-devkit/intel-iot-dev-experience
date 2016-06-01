# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

"""
Created on Sun Nov 29 22:27:47 2015

@author: XION\alxwesmcmillan
"""

import os
from copy import copy
import xmlhandler
import xmlvalidator

class RCPLINDEX_WRITER(xmlhandler.XMLHANDLER):
    def __init(self, m_outFileName, m_rcpl_tree):
        super(RCPLINDEX_WRITER, self).__init__(None, m_outFileName)
        pass

class RCPLINDEX_READER(xmlhandler.XMLHANDLER):

    def __init__(self, inFileName, validation, signature_check = False, outFileName=None):
        super(RCPLINDEX_READER, self).__init__(inFileName, outFileName)
        
        if validation:
            libpath = os.path.dirname(os.path.realpath(__file__))
            if not signature_check:
                schema_path = os.path.abspath(os.path.normpath('%s/../schema/xml/rcplindex_no_signature.xsd' %(libpath)))
            else: 
                pass #this is a stub and requires importation of sec_management module
                schema_path = os.path.abspath(os.path.normpath('%s/../schema/xml/rcplindex_with_signature.xsd' %(libpath)))
            validator = xmlvalidator.XML_VALIDATOR(inFileName, schema_path )
        
            if validator.error:
                self.error = validator.error
                raise(Exception)
                return

        self.__root = self.root
        self.rcpl_dict = dict()
        
        self.__file_list = list()
        self.initializeAttributes()

    def load_index(self):
        
        __tmp_dict = dict()
        
        for index in self.__root.findall("."):
            for rcpl in index:
                self.getAttributes(rcpl)
                for fle in rcpl:
                    self.__file_list.append(fle.get("URL"))
                __tmp_dict[self.__version] = {"alias":self.__alias, "arch":self.__arch, "release":self.__release, "files":tuple(self.__file_list)}
                self.clearAll()
                
        self.rcpl_dict = copy(__tmp_dict)
        
    def getData(self):
        return self.rcpl_dict
        
    def getAttributes(self, rcpl):
        self.__alias = rcpl.get("alias")
        self.__version = rcpl.get("version")
        self.__release = rcpl.get("release")
        self.__arch = rcpl.get("arch")

    def initializeAttributes(self):
        self.__alias = str("NOT SET")
        self.__version = str("NOT SET")
        self.__release = str("NOT SET")
        self.__arch = str("NOT SET")
        
    def clearAll(self):
        self.initializeAttributes()
        self.__file_list = list()
