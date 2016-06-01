#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

from tools import logging_helper
import gzip


def byteify(input_string):
    """ Used to convert unicode json arrays objects to a string.

    Args:
        input_string (str):

    Returns:
        dict:
    """
    if isinstance(input_string, dict):
        return {byteify(key): byteify(value) for key, value in input_string.iteritems()}
    elif isinstance(input_string, list):
        return [byteify(element) for element in input_string]
    elif isinstance(input_string, unicode):
        return input_string.encode('utf-8')
    else:
        return input_string


def uncompress(local_path, local_file):
    """ Uncompress gz file types.

    Args:
        local_path (str): path URI to the .gz file to be uncompressed
        local_file (str): path URI to the output uncompressed file
    """
    log_helper = logging_helper.logging_helper.Logger()
    block_size = 16384
    try:
        gz_input = gzip.GzipFile(local_path)
        curated_data = gz_input.read(block_size)
        if len(curated_data) > 0:
            curated_output = open(local_file, "w")
            while curated_data:
                curated_output.write(curated_data)
                curated_data = gz_input.read(block_size)
            curated_output.close()
    except:
        log_helper.logger.error("Error decompressing %s" % local_path)


def is_newer_version(str_version_new, str_version_original):
    """ Compare to check if the version is newer.
    Args:
        str_version_new (str): the new version, e.g. 2.8.1-r0.0
        str_version_original (str):  the original version

    Returns:
        bool: True if newer. False if not.
    """
    log_helper = logging_helper.logging_helper.Logger()
    array_version_original = str_version_original.split('-r')
    array_version_new = str_version_new.split('-r')
    is_newer = False
    if array_version_new[0] > array_version_original[0]:  # compare version
        is_newer = True
    elif array_version_new[0] == array_version_original[0]:  # compare release
        if len(array_version_new) == 2 and len(array_version_original) == 2:
            if array_version_new[1] > array_version_original[1]:  # compare release
                is_newer = True
        else:
            log_helper.logger.error('Cannot interpret versions: ' + str_version_new + ' v.s. ' + str_version_original)
    return is_newer
