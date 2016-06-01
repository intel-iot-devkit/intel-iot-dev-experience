#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import logging_helper
import logging.config
import logging
import os


__all__ = ["logging_helper"]
logging.config.fileConfig(os.path.dirname(__file__) + '/' + 'logging.conf')
