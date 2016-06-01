# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

from lxml import etree as ET 
from .. import exception
from tools import logging_helper

class XMLHANDLER(object):
    def __init__(self, inFileName, outFileName, parent = None):

        object.__init__(self)

        self.error = None

        self.__log_helper = logging_helper.logging_helper.Logger()
        
        if not outFileName:
            self.__outFileName = None

            self.__outFileName = outFileName

        if not inFileName:
            self.__inFileName = None
        else:
            self.__inFileName = inFileName

        try:
            self.tree = ET.parse(self.__inFileName)
            self.root = self.__getRootNode()
        except (IOError, ET.XMLSyntaxError) as err:
            if isinstance(err, IOError):
                raise(exception.errors.FILEIO_ERROR(self.__inFileName, 5002))

            elif isinstance(err, ET.XMLSyntaxError):
                self.__log_helper.logger.error(str(err))
                self.error = err
            else:
                self.error = "Unexpected exception raised"

    def __getRootNode(self):
        return self.tree.getroot()

    def __setRootNode(self):
        pass

    def writeXMLtoFile(self):
        pass
