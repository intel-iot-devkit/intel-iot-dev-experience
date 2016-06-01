#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

###########################################
# Do not use this module directly with the main CherryPy server.py
##########################################

import os
import contextlib
import sys
import ast
from cStringIO import StringIO
import smart
import smart.commands.newer
import smart.commands.query
import smart.commands.channel
import smart.commands.upgrade
import pwd

# global variables
std_out_redirected = ''


@contextlib.contextmanager
def redirect_std_out():
    global std_out_redirected
    original_out = sys.stdout
    new_out = None
    try:
        new_out = StringIO()
        sys.stdout = new_out
        yield new_out
    finally:
        sys.stdout = original_out
        if new_out is None:
            std_out_redirected = ''
        else:
            std_out_redirected = new_out.getvalue()


def run_commands(commands_list, args_list, reload_channels=True):
    """ Run Smart commands
    Args:
        commands_list (list): list of commands. commands = newer, query, channel
        args_list (list): list of arguments list
        reload_channels (bool): reload channel or not

    Returns:
        string: string representing the list of string of results. Each list item is separated by #smart_opts_list#
    """
    global std_out_redirected
    str_result_list = ''
    result = ''

    if len(args_list) != len(commands_list):
        print 'Error For Smart_ops.py: args and commands have different lengths!'
        return str_result_list

    try:
        if os.getuid() == 0:
            os.environ["HOME"] = pwd.getpwuid(0)[5]

        with redirect_std_out() as output:  # Doing this, we can discard the stdout message.
            ctrl = smart.init(command=None)
            smart.initDistro(ctrl)
            smart.initPlugins()
            smart.initPycurl()
            smart.initPsyco()
            if reload_channels:
                ctrl.reloadChannels()

        for index in range(len(args_list)):
            args = args_list[index]
            command = commands_list[index]

            # Prepare for options
            opts = None
            if command == 'newer':
                opts = smart.commands.newer.parse_options(args)
            elif command == 'channel':
                opts = smart.commands.channel.parse_options(args)
            elif command == 'query':
                opts = smart.commands.query.parse_options(args)
            elif command == 'upgrade':
                opts = smart.commands.upgrade.parse_options(args)
            else:
                print 'Error For Smart_ops.py: ' + command + ' is not supported.'

            # Run the command
            if opts is not None:
                if command == 'newer':
                    with redirect_std_out() as output:
                        smart.commands.newer.main(ctrl, opts, reloadchannels=False)
                    result = std_out_redirected
                elif command == 'channel':
                    with redirect_std_out() as output:
                        smart.commands.channel.main(ctrl, opts)
                    result = std_out_redirected
                elif command == 'query':
                    with redirect_std_out() as output:
                        smart.commands.query.main(ctrl, opts, reloadchannels=False)
                    result = std_out_redirected
                elif command == 'upgrade':
                    with redirect_std_out() as output:
                        smart.commands.upgrade.main(ctrl, opts)
                    result = std_out_redirected
                else:
                    print 'Error For Smart_ops.py: ' + command + ' is not supported.'
                    result = ''

            if index == (len(args_list) - 1):
                str_result_list += result
            else:
                str_result_list += (result + '#smart_opts_list#')

        ctrl.saveSysConf()
        ctrl.restoreMediaState()
        smart.deinit()
    except Exception as e1:
        print 'Error For Smart_ops.py: ' + str(e1)
        smart.deinit()
    return str_result_list


# We need to run "smart" related stuff in a separate process.... "Smart" does not run well together with "CherryPy".
# For example, When "CherryPy" handles a REST request, it uses a different thread to run the handling application.
# Smart has to be run in the main thread.
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print 'Error For Smart_ops.py: Only accept 2 arguments. 1st is list of commands. 2nd if list of list of args.'
    else:
        str_list_commands = sys.argv[1]
        str_list_list_args = sys.argv[2]
        try:
            list_command = ast.literal_eval(str_list_commands)
            list_list_args = ast.literal_eval(str_list_list_args)
            result_list = run_commands(list_command, list_list_args, reload_channels=True)
            print result_list  # We need this so that the calling scripts can grab the stdout.
        except Exception as e:
            print 'Error For Smart_ops.py: ' + str(e)
