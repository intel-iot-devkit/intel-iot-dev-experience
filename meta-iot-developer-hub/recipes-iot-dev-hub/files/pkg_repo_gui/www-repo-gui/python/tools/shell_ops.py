#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import subprocess


def run_command(command):
    """ Run a shell command.

    Args:
        command (str): String command to be sent to a subprocess terminal call.

    Returns:
        str: String with full response from shell call.

    """
    p = subprocess.Popen(command.split(),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    buffer_out = ""
    for line in iter(p.stdout.readline, ''):
        buffer_out += line
    return buffer_out


def run_cmd_chk(command):
    """ Run a shell command with check output. Check returncode and output

    Args:
        command (str): String command to be sent to a subprocess terminal call.

    Returns:
        dict: dic with returncode and cmd_output key.

    """
    result = {'returncode': None, 'cmd_output': None}
    p = subprocess.Popen(command, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    result['cmd_output'] = p.communicate()[0]
    result['returncode'] = p.poll()
    return result
