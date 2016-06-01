#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import logging
import logging.config


class Logger(object):
    """Helper class to handle logging.
    """
    def __init__(self, logger_name='backend_general'):
        """ Logger constructor
        Args:
            logger_name (str): The logger to used... This should be one of the logger specified in logging.conf.
                               The default is 'backend_general'.

        Returns:
            Logger:
        """
        self.logger = logging.getLogger(logger_name)


