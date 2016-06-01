#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import sys, traceback


class ERRORS(Exception):
    def __init__(self, m_arg):
        self.args = m_arg

    def __call__(self, *args):
        return self.__class__(*(self.args + args))

class FILEIO_ERROR(ERRORS):
    sys.tracebacklimit = 0
    def __init__(self, m_filename, error_code):
        fileio_error_lookup = {5001: "Not Defined",  5002:"Specified file %s not found" %(m_filename)}

        try:
            m_args = fileio_error_lookup[error_code]

            super(ERRORS, self).__init__(m_args)

        except(KeyError):
            exc_type, exc_value, exc_traceback=sys.exc_info()
            line = exc_traceback.tb_lineno
            invalidErrorCode("install", error_code, line)

def invalidErrorCode(error_type, error_code, line):
    sys.exit("Invalid %s exception code of %i provided at line %d" %(error_type, error_code ,line))
