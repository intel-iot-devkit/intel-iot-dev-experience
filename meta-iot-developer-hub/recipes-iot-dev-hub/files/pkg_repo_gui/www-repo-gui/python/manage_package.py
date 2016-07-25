#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import os
import codecs
import json
import rpm
import subprocess
import ast
from tools import logging_helper, data_ops, shell_ops, sysinfo_ops, network_ops
import manage_config
import manage_repo
import manage_pro_upgrade
import manage_worker
from manage_auth import require


# global variables used across multiple modules
constructed_packages_list = []  # only used by unit_test
constructed_packages_list_new = []  # only used by unit_test


def update_package_list():
    """ Grabs the curated.tar.gz file from download.01.org to update the curated package listings

    Returns:
        str: Json response with key 'status' and value 'success' or 'fail
    """
    log_helper = logging_helper.logging_helper.Logger()
    data_collector = sysinfo_ops.DataCollect()

    # Determine architecture and proper repository
    config = manage_config.read_config_file()
    developer_hub_url = config.get('DefaultRepo', 'base_repo')
    architecture, rcpl_version = data_collector.platform_details()
    developer_hub_url = developer_hub_url + rcpl_version + '/' + architecture
    curated_url = developer_hub_url + '/' + 'curated.xml.gz'
    local_path = '/tmp/curated.xml.gz'
    local_file = 'curated.txt'

    # Download and decompress the curated list
    # todo: this needs to return 'False' on timeout and give a json status of 'fail'
    shell_ops.run_command('timeout 5 wget %s -O %s' % (curated_url, local_path))
    data_ops.uncompress(local_path, local_file)
    build_package_database()

    # Remove tar file after use
    try:
        os.remove(local_path)
    except:  # todo: This needs to throw an error. Try 'except (OSError, IOError):'
        pass

    # From the UI if json == null then the response failed (timed out)
    response = ({
        'status': 'success'
    })
    response = json.dumps(response)
    log_helper.logger.debug("Finished updating package list: '%s'" % response)
    return response


def get_is_installed(process, package_name):
    """ Check if a specified package is installed.

    Args:
        process (Optional[subprocess]): (Optional) Previously opened shell subprocess.
                               None type object if a shell is not already open.
        package_name (str): Check if this package is installed

    Returns:
        tuple: 1st is True/False for installed or not. 2nd is dict with 'package' and 'installed' keys.
    """
    installed = False
    if process is None:
        if package_name in get_installed_packages(None):
            installed = True
    else:
        if package_name in get_installed_packages(process):
            installed = True

    response = {'package': package_name, 'installed': str(installed)}
    return installed, response


def get_installed_packages(process):
    """ Get a list of the installed packages from the smart --installed command

    Args:
        process (Optional[subprocess]): (Optional) shell subprocess. None type object if a shell is not already open.

    Returns:
        list: list of string.
    """
    if manage_config.use_new_get_installed_packages:
        my_list, my_dict = get_installed_packages_new()
        return my_list
    else:
        return get_installed_packages_original(process)


def get_installed_packages_original(process):
    """ Get a list of the installed packages from the smart --installed command

    Args:
        process (Optional[subprocess]): (Optional) shell subprocess. None type object if a shell is not already open.

    Returns:
        list: list of string.
    """
    if process is None:
        installed_packages = []
        result = shell_ops.run_command("smart query --installed --show-format=$name|")
        for line in result.split('|'):
            installed_packages.append(line)
        return installed_packages
    else:
        process.sendline('query --installed --show-format=$name|')
        process.expect('smart> ')
        return process.before.split('|')


def get_installed_packages_new():
    """ Get a list of the installed packages from rpm module

    Returns:
        tuple: 1st is list of installed package names. 2nd is dict.
    """
    dict_installed_packages = {}
    installed_packages = []
    log_helper = logging_helper.logging_helper.Logger()

    try:
        ts = rpm.TransactionSet()
        mi = ts.dbMatch()
    except Exception as e:
        log_helper.logger.error(str(e))
        return installed_packages, dict_installed_packages

    for h in mi:
        try:
            name = h['name']
            dict_installed_packages[name] = h['version'] + '-' + h['release']
            installed_packages.append(name)
        except Exception as e:
            log_helper.logger.error(str(e))
            continue
    return installed_packages, dict_installed_packages


def build_package_database():
    """ Parses curated and non-curated packages and places them into a json format.

    The json formatted string is saved to a file.
    """
    if manage_config.use_new_build_package_database:
        build_package_database_new()
    else:
        build_package_database_original()


def build_package_database_new():
    """ Parses curated and non-curated packages and places them into a json format.

    The requirements of using this is to make sure that smart update is called to update cache,
    when add/remove repo is done.

    The json formatted string is saved to a file.
    """
    global constructed_packages_list_new
    constructed_packages_list_new = []
    data = []
    curated_packages = []
    curated_dict = {}
    upgrade_dict = {}
    query_result = ''
    packages_added_dict = {}

    log_helper = logging_helper.logging_helper.Logger()
    log_helper.logger.debug("Starting Build...")

    # -------------------------------------------------
    # ------------- Step 1: Gather info ---------------
    # -------------------------------------------------

    # Get the latest installed packages list
    my_list, my_dict = get_installed_packages_new()

    # Get the info for curated packages
    try:
        file_path = os.path.dirname(os.path.realpath(__file__))
        my_file = codecs.open(file_path + '/' + 'curated.txt', 'r')
        curated_packages = json.loads(my_file.read())  # list of json
        my_file.close()
    except Exception as e:
        log_helper.logger.error('Read curated.txt failed with ' + str(e))

    # Create a list of dict for curated packages, this can be used later..... dict key checking is
    # more efficient (due to hash table) than linear loop search
    for pc in curated_packages:
        try:
            curated_dict[pc['name']] = {'image': pc['image'], 'title': pc['title'],
                                        'summary': pc['summary'], 'url': pc['url'],
                                        'description': pc['description'], 'vertical': pc['vertical'],
                                        'service': pc['service'], 'launch': pc['launch']}
        except Exception as e:
            log_helper.logger.error(str(e) + ' for ' + pc['name'])
            continue

    # ----------------------------------------------------------------------
    # ------------- Step 2: Handle packages for non-OS repos ---------------
    # ----------------------------------------------------------------------

    # Get channel list
    list_channels_string = manage_repo.list_repos_non_os_only()
    if list_channels_string is None:
        # something wrong. cannot read tracking file
        # ignore this error
        list_channels_string = []
    list_query_args = []
    if list_channels_string:  # not empty
        for channel in list_channels_string:
            list_query_args.append('--channel=' + channel)
        list_query_args.append('--show-format=$name#myinfo#$version#myinfo#$summary#myinfo#$group#myline#')

        # Use Smart module directly to run smart
        commands_list = ['newer', 'query']
        args_list = [[], list_query_args]
        smart_status, smart_error, smart_return = handle_smart_commands(commands_list, args_list)
        if smart_status == 'success':
            # Get upgrade list
            upgrade_output = smart_return[0]
            if 'No interesting upgrades' not in upgrade_output and upgrade_output != '':
                upgrade_output = upgrade_output[upgrade_output.rindex('---') + 3:]
                for line in upgrade_output.split('\n'):
                    if len(line) < 5:
                        continue
                    info = line.split('|')
                    str_name = info[0].strip()
                    upgrade_dict[str_name] = {'name': str_name,
                                              'installed_version': info[1].split(' ')[1],
                                              'upgrade_version': info[2].split(' ')[1],
                                              'upgrade_size': info[4].strip()}
            log_helper.logger.debug("Package upgrade list: '%s" % str(upgrade_dict))
            # Get packages
            query_result = smart_return[1]
    else:  # empty channel
        pass

    # loop through each package
    list_query_result = query_result.split('#myline#')
    for current_package in list_query_result:
        # safe guard the last entry
        if current_package == '\n' or current_package == '\n\n' or current_package == '':
            continue
        else:
            package_info = current_package.split('#myinfo#')
            if not (len(package_info) == 4):
                log_helper.logger.error(current_package + " does not have current format to be parsed!")
                continue

        # get package information
        str_name = package_info[0]
        str_version = package_info[1]
        str_summary = package_info[2]
        str_group = package_info[3]

        # check if package is already in the dict
        already_added = (str_name in packages_added_dict)

        # check if package is in installed list
        installed = False
        install_version = ''
        if str_name in my_dict:
            installed = True
            install_version = my_dict[str_name]

        # check if package has upgrade/update or not
        has_upgrade = False
        if str_name in upgrade_dict:
            has_upgrade = True

        package = {'name': str_name,
                   'version': str_version[:str_version.index('@')],
                   'summary': str_summary,
                   'group': str_group,
                   'image': 'packages.png',  # Default no icon
                   'title': str_name.replace('-', ' ').title(),
                   'installed': installed,
                   'curated': False,
                   'vertical': '',
                   'service': '',
                   'launch': ''
                   }
        build_package_database_parse_package(str_name=str_name, curated_dict=curated_dict,
                                             upgrade_dict=upgrade_dict, already_added=already_added,
                                             installed=installed, install_version=install_version,
                                             has_upgrade=has_upgrade, package=package,
                                             packages_added_dict=packages_added_dict)

    # -----------------------------------------------------------------------------------------
    # ------------- Step 3: Handle packages specified in pro packages list file ---------------
    # -----------------------------------------------------------------------------------------

    pro_status = manage_pro_upgrade.ProStatus()
    if pro_status.enabled_state()['result'] == 'True':
        log_helper.logger.info("Pro is enabled, so we check pro packages list file.")
        # Check the pro file list
        # Read the file to get package list
        query_result = ""
        list_query_args = []
        pro_package_list = manage_pro_upgrade.ProPackageList.get_packages()
        for package in pro_package_list:
            # check if package is in installed list
            if package in my_dict:  # installed
                # check if package is already in the dict
                if not (package in packages_added_dict):  # not added yet
                    list_query_args.append(package)
        if list_query_args:  # the argument list is not empty
            log_helper.logger.info('Pro packages list: ' + str(list_query_args))
            list_query_args.append('--installed')
            list_query_args.append('--show-format=$name#myinfo#$version#myinfo#$summary#myinfo#$group#myline#')
            # Run smart commands.
            commands_list = ['query']
            args_list = [list_query_args]
            smart_status, smart_error, smart_return = handle_smart_commands(commands_list, args_list)
            if smart_status == 'success':
                query_result = smart_return[0]
        log_helper.logger.debug("Before Pro packages list: " + str(len(packages_added_dict)))
        if query_result:  # We have query result. These are pro packages that are not added yet.
            list_query_result = query_result.split('#myline#')
            for current_package in list_query_result:
                # safe guard the last entry
                if current_package == '\n' or current_package == '\n\n' or current_package == '':
                    continue
                else:
                    package_info = current_package.split('#myinfo#')
                    if not (len(package_info) == 4):
                        log_helper.logger.error(current_package + " does not have current format to be parsed!")
                        continue
                # get package information
                str_name = package_info[0]
                str_version = package_info[1]
                str_summary = package_info[2]
                str_group = package_info[3]
                installed = True
                install_version = str_version[:str_version.index('@')]
                # check if package has upgrade/update or not
                has_upgrade = False
                if str_name in upgrade_dict:
                    has_upgrade = True
                package = {'name': str_name,
                           'version': install_version,
                           'summary': str_summary,
                           'group': str_group,
                           'image': 'packages.png',  # Default no icon
                           'title': str_name.replace('-', ' ').title(),
                           'installed': installed,
                           'curated': False,
                           'vertical': '',
                           'service': '',
                           'launch': ''
                           }
                build_package_database_parse_package(str_name=str_name, curated_dict=curated_dict,
                                                     upgrade_dict=upgrade_dict, already_added=False,
                                                     installed=installed, install_version=install_version,
                                                     has_upgrade=has_upgrade, package=package,
                                                     packages_added_dict=packages_added_dict)
        log_helper.logger.debug("After Pro packages list: " + str(len(packages_added_dict)))

    # -----------------------------------------------------------------------------------------
    # ------------- Step 4: Handle packages (not added yet) with update available -------------
    # -----------------------------------------------------------------------------------------

    # Check available updates for OS Packages.
    # upgrade_dict has all the available updates, including OS Packages.
    query_result = ""
    list_query_args = []
    for key, value in upgrade_dict.items():
        if not (key in packages_added_dict):  # not included, this is probably an OS package
            list_query_args.append(key)
    if list_query_args:  # Args list is not empty.  We have update that is not captured yet.
        list_query_args.append('--installed')
        list_query_args.append('--show-format=$name#myinfo#$version#myinfo#$summary#myinfo#$group#myline#')
        # Run Smart commands
        commands_list = ['query']
        args_list = [list_query_args]
        smart_status, smart_error, smart_return = handle_smart_commands(commands_list, args_list)
        if smart_status == 'success':
            query_result = smart_return[0]
    log_helper.logger.debug("Before OS Updates: " + str(len(packages_added_dict)))
    if query_result:  # We have query result. These are update packages that are not added yet.
        list_query_result = query_result.split('#myline#')
        for current_package in list_query_result:
            # safe guard the last entry
            if current_package == '\n' or current_package == '\n\n' or current_package == '':
                continue
            else:
                package_info = current_package.split('#myinfo#')
                if not (len(package_info) == 4):
                    log_helper.logger.error(current_package + " does not have current format to be parsed!")
                    continue
            # get package information
            str_name = package_info[0]
            str_version = package_info[1]
            str_summary = package_info[2]
            str_group = package_info[3]
            installed = True
            install_version = str_version[:str_version.index('@')]
            package = {'name': str_name,
                       'version': install_version,
                       'summary': str_summary,
                       'group': str_group,
                       'image': 'packages.png',  # Default no icon
                       'title': str_name.replace('-', ' ').title(),
                       'installed': installed,
                       'curated': False,
                       'vertical': '',
                       'service': '',
                       'launch': ''
                       }
            build_package_database_parse_package(str_name=str_name, curated_dict=curated_dict,
                                                 upgrade_dict=upgrade_dict, already_added=False,
                                                 installed=installed, install_version=install_version,
                                                 has_upgrade=True, package=package,
                                                 packages_added_dict=packages_added_dict)
    log_helper.logger.debug("After OS Updates: " + str(len(packages_added_dict)))

    # Change dict to list
    for key in packages_added_dict:
        data.append(packages_added_dict[key])

    constructed_packages_list_new = data

    # Output file with list of curated packages with additional info added
    with open(manage_config.package_data_file, 'w') as my_file:
        my_file.write(json.dumps(data))
    log_helper.logger.debug("Finished building package database. Output written to " + manage_config.package_data_file)


def build_package_database_original():
    """ Parses curated and non-curated packages and places them into a json format.

    The requirements of using this is to make sure that smart update is called to update cache,
    when add/remove repo is done.

    The json formatted string is saved to a file.
    """
    global constructed_packages_list_new
    constructed_packages_list_new = []
    data = []
    curated_packages = []
    curated_dict = {}
    upgrade_dict = {}
    query_result = ''
    packages_added_dict = {}

    log_helper = logging_helper.logging_helper.Logger()
    log_helper.logger.debug("Starting Build...")

    # Get the latest installed packages list
    my_list, my_dict = get_installed_packages_new()

    # Get the info for curated packages
    try:
        file_path = os.path.dirname(os.path.realpath(__file__))
        my_file = codecs.open(file_path + '/' + 'curated.txt', 'r')
        curated_packages = json.loads(my_file.read())  # list of json
        my_file.close()
    except Exception as e:
        log_helper.logger.error('Read curated.txt failed with ' + str(e))

    # Create a list of dict for curated packages, this can be used later..... dict key checking is
    # more efficient (due to hash table) than linear loop search
    for pc in curated_packages:
        try:
            curated_dict[pc['name']] = {'image': pc['image'], 'title': pc['title'],
                                        'summary': pc['summary'], 'url': pc['url'],
                                        'description': pc['description'], 'vertical': pc['vertical'],
                                        'service': pc['service'], 'launch': pc['launch']}
        except Exception as e:
            log_helper.logger.error(str(e) + ' for ' + pc['name'])
            continue

    # Get channel list
    list_channels_string = manage_repo.list_repos()
    list_query_args = []
    if list_channels_string:  # not empty
        for channel in list_channels_string:
            list_query_args.append('--channel=' + channel)
        list_query_args.append('--show-format=$name#myinfo#$version#myinfo#$summary#myinfo#$group#myline#')

        # Use Smart module directly to run smart

        # Prepare for args
        commands_list = ['newer', 'query']
        args_list = [[], list_query_args]

        # Run the commands
        p = subprocess.Popen(['python', 'smart_ops.py', str(commands_list), str(args_list)],
                             cwd='tools',
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        buffer_out = ""
        for line in iter(p.stdout.readline, ''):
            buffer_out += line
        if 'Error For Smart_ops.py' in buffer_out:
            log_helper.logger.error('Smart.ops.py running failed:  ' + str(buffer_out))
        else:
            results_list = buffer_out.split('#smart_opts_list#')
            if len(results_list) == 2:
                # Get upgrade list
                upgrade_output = results_list[0]
                if 'No interesting upgrades' not in upgrade_output and upgrade_output != '':
                    upgrade_output = upgrade_output[upgrade_output.rindex('---') + 3:]
                    for line in upgrade_output.split('\n'):
                        if len(line) < 5:
                            continue
                        info = line.split('|')
                        str_name = info[0].strip()
                        upgrade_dict[str_name] = {'name': str_name,
                                                  'installed_version': info[1].split(' ')[1],
                                                  'upgrade_version': info[2].split(' ')[1],
                                                  'upgrade_size': info[4].strip()}
                log_helper.logger.debug("Package upgrade list: '%s" % str(upgrade_dict))

                # Get packages
                query_result = results_list[1]
            else:
                log_helper.logger.error('Results do not have 2 items...' + str(len(results_list)))
    else:  # empty channel
        pass

    # loop through each package
    list_query_result = query_result.split('#myline#')
    for current_package in list_query_result:
        if current_package == '\n' or current_package == '\n\n' or current_package == '':  # safe guard the last entry
            continue
        else:
            package_info = current_package.split('#myinfo#')
            if not (len(package_info) == 4):
                log_helper.logger.error(current_package + " does not have current format to be parsed!")
                continue

        # get package information
        str_name = package_info[0]
        str_version = package_info[1]
        str_summary = package_info[2]
        str_group = package_info[3]

        # check if package is already in the dict
        already_added = (str_name in packages_added_dict)

        # check if package is in installed list
        installed = False
        install_version = ''
        if str_name in my_dict:
            installed = True
            install_version = my_dict[str_name]

        # check if package has upgrade/update or not
        has_upgrade = False
        if str_name in upgrade_dict:
            has_upgrade = True

        package = {'name': str_name,
                   'version': str_version[:str_version.index('@')],
                   'summary': str_summary,
                   'group': str_group,
                   'image': 'packages.png',  # Default no icon
                   'title': str_name.replace('-', ' ').title(),
                   'installed': installed,
                   'curated': False,
                   'vertical': '',
                   'service': '',
                   'launch': ''
                   }

        # check if package is in curated list
        if str_name in curated_dict:
            # print "Curated:  " + str_name + " installed: " + str(installed) + ' ' + install_version
            # Do not add duplicate ones
            if already_added:
                continue
            # Use the values in curated packages file
            curated_entry = curated_dict[str_name]
            package['curated'] = True
            package['image'] = curated_entry['image']
            package['title'] = curated_entry['title']
            package['summary'] = curated_entry['summary']
            package['url'] = curated_entry['url']
            package['description'] = curated_entry['description']
            package['vertical'] = curated_entry['vertical']
            package['service'] = curated_entry['service']
            package['launch'] = curated_entry['launch']
            if installed:
                package['version'] = install_version
                if has_upgrade:
                    package['upgrade_version'] = upgrade_dict[str_name]['upgrade_version']
            # Add this entry into the dict.
            packages_added_dict[str_name] = package
        else:
            # print "Non-curated:  " + str_name + " installed: " + str(installed) + ' ' + install_version
            # These fields are only for non-curated packages
            package['upgrade_version'] = ''
            package['depends'] = ''
            package['bundle'] = ''
            if already_added:  # Already an entry in the dict, only update if necessary.
                package_added = packages_added_dict[str_name]
                this_version_newer_than_recorded_one = data_ops.is_newer_version(package['version'],
                                                                                 package_added['version'])
                if not installed:  # Not installed, do not need to check upgrade.
                    if this_version_newer_than_recorded_one:
                        # Update entry
                        packages_added_dict[str_name]['version'] = package['version']
            else:  # Not in the dict yet. Add the entry to dict.
                if installed:  # Need to check upgrade
                    if has_upgrade:
                        package['upgrade_version'] = upgrade_dict[str_name]['upgrade_version']
                        package['version'] = upgrade_dict[str_name]['installed_version']
                # Add this entry into the dict.
                packages_added_dict[str_name] = package

    # Change dict to list
    for key in packages_added_dict:
        data.append(packages_added_dict[key])

    constructed_packages_list_new = data

    # Output file with list of curated packages with additional info added
    with open(manage_config.package_data_file, 'w') as my_file:
        my_file.write(json.dumps(data))
    log_helper.logger.debug("Finished building package database. Output written to " + manage_config.package_data_file)


def build_package_database_parse_package(str_name, curated_dict, upgrade_dict, already_added, installed,
                                         install_version, has_upgrade, package, packages_added_dict):
    """
    Args:
        str_name (str): package name
        curated_dict (dict): dictionary of curated packages
        upgrade_dict (dict): dictionary of upgrade packages
        already_added (bool): already added to packages_added_dict or not
        installed (bool): installed or not.
        install_version (str): installed version
        has_upgrade (bool): has upgrade/update or not
        package (dict): dictionary of this package
        packages_added_dict (dict): dictionary of packages list

    Returns:

    """
    # check if package is in curated list
    if str_name in curated_dict:
        # print "Curated:  " + str_name + " installed: " + str(installed) + ' ' + install_version
        # Do not add duplicate ones
        if already_added:
            return
        # Use the values in curated packages file
        curated_entry = curated_dict[str_name]
        package['curated'] = True
        package['image'] = curated_entry['image']
        package['title'] = curated_entry['title']
        package['summary'] = curated_entry['summary']
        package['url'] = curated_entry['url']
        package['description'] = curated_entry['description']
        package['vertical'] = curated_entry['vertical']
        package['service'] = curated_entry['service']
        package['launch'] = curated_entry['launch']
        if installed:
            package['version'] = install_version
            if has_upgrade:
                package['upgrade_version'] = upgrade_dict[str_name]['upgrade_version']
        # Add this entry into the dict.
        packages_added_dict[str_name] = package
    else:
        # print "Non-curated:  " + str_name + " installed: " + str(installed) + ' ' + install_version
        # These fields are only for non-curated packages
        package['upgrade_version'] = ''
        package['depends'] = ''
        package['bundle'] = ''
        if already_added:  # Already an entry in the dict, only update if necessary.
            package_added = packages_added_dict[str_name]
            this_version_newer_than_recorded_one = data_ops.is_newer_version(package['version'],
                                                                             package_added['version'])
            if not installed:  # Not installed, do not need to check upgrade.
                if this_version_newer_than_recorded_one:
                    # Update entry
                    packages_added_dict[str_name]['version'] = package['version']
        else:  # Not in the dict yet. Add the entry to dict.
            if installed:  # Need to check upgrade
                if has_upgrade:
                    package['upgrade_version'] = upgrade_dict[str_name]['upgrade_version']
                    package['version'] = upgrade_dict[str_name]['installed_version']
            # Add this entry into the dict.
            packages_added_dict[str_name] = package


def handle_smart_commands(list_commands=[], list_args=[]):
    """ Run multiple Smart commands using tools\smart_ops.py

    Args:
        list_commands (list): list of Smart commands to execute
        list_args (list): list of args for each Smart command

    Returns:
        tuple: 1st is status ('success' or 'fail'). 2nd is error message. 3rd is list of returns.
    """
    log_helper = logging_helper.logging_helper.Logger()
    len_of_commands = len(list_commands)
    p = subprocess.Popen(['python', 'smart_ops.py', str(list_commands), str(list_args)],
                         cwd='tools',
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    buffer_out = ""
    for line in iter(p.stdout.readline, ''):
        buffer_out += line
    if 'Error For Smart_ops.py' in buffer_out:
        error_message = 'Smart.ops.py running failed:  ' + str(buffer_out)
        log_helper.logger.error(error_message)
        return 'fail', error_message, []
    else:
        results_list = buffer_out.split('#smart_opts_list#')
        if len(results_list) == len_of_commands:
            return 'success', '', results_list
        else:
            error_message = 'Do not have same number of returns as the commands. Returns: ' + str(results_list)
            log_helper.logger.error(error_message)
            return 'fail', error_message, []


def get_package_info(package_name):
    """ Get additional package info from the 'smart info' command.

    Args:
        package_name (str): String name of RPM

    Returns:
        str: In string format, dictionary with keys: summary, url, license, size, description, group, version.
    """
    log_helper = logging_helper.logging_helper.Logger()
    log_helper.logger.debug("Getting additional package info for %s" % package_name)
    command = "smart info " + package_name
    output = shell_ops.run_command(command)
    description = ''
    version = ''
    if output.count('Name:') > 1:
        # Multiple versions available. Narrow down smart info scope to get accurate info for the current version
        response = shell_ops.run_command("smart query --installed " + package_name + " --show-format=$version")
        version = response[response.index('[100%]')+6:response.index('@')].replace('\n', '')
        if 'not' in version:  # Workaround for "(not installed)" case
            version = 'Unknown'

        output = output[output.rindex(version):]

        if 'Name' in output:
            if output.index('Name') > output.index('Description'):
                # Additional entry after description
                description = output[output.rindex("Description:") + 14: output.index("Name")].replace('\n', '').strip()
        else:
            description = output[output.rindex("Description:") + 14:].replace('\n', '').strip()
    else:
        version = output[output.index("Version:") + 9: output.index("Priority:")].replace('\n', '')
        version = version[:version.index('@')]
        if 'not' in version:  # Workaround for "(not installed)" case
            version = 'Unknown'
        description = output[output.rindex("Description:") + 14:].replace('\n', '').strip()

    url = output[output.index("Reference URLs:") + 16: output.index("Flags:")].replace('\n', '')
    my_license = output[output.index("License:") + 9: output.index("Installed Size:")].replace('\n', '')
    size = output[output.index("Installed Size:") + 16: output.index("Reference URLs:")].replace('\n', '')
    group = output[output.index("Group:") + 7: output.index("License:")].replace('\n', '')
    summary = output[output.index("Summary:") + 9: output.index("Description:")].replace('\​r\n', '')

    # escape special JSON charater (") if any in description and summary
    summary = summary.replace('"', '\\"')
    description = description.replace('"', '\\"')

    package = {
        'url': url,
        'license': my_license,
        'size': size,
        'description': description,
        'summary': summary,
        'group': group,
        'version': version
    }
    log_helper.logger.debug("Returning package info: " + str(package))
    return json.dumps(package)


def get_data():
    """ Get the data from the build_package_database function.

    Returns:
        str: File contents if the file exists or None if it does not exist.
    """
    log_helper = logging_helper.logging_helper.Logger()
    try:
        my_file = open(manage_config.package_data_file, 'r')
        output = my_file.read().decode('string_escape')
        my_file.close()
        return output
    # [Errno 2] No such file or directory: '/tmp/test.txt'
    # except IOError:
        # network_checker = network_ops.NetworkCheck()
        # if network_checker.get_stored_https_status() and network_checker.get_stored_http_status():
        #     log_helper.logger.debug("Database does not exist. Building database since network connection is ok...")
        #     build_package_database()
    except:
        # Note:
        # When we do not have the data file, that means that the network connection is not good when dev hub server is started.
        # When the user is setting up the network, we will create the data file if the settings are good.
        # Or when the network settings are from bad to good, we will also create the data file.
        return None


def remove_data_file():
    """ Remove the data file from build_package_database function.
    Returns:

    """
    try:
        os.remove(manage_config.package_data_file)
    except OSError:
        pass


def set_signature_verification_status(status):
    log_helper = logging_helper.logging_helper.Logger()
    log_helper.logger.debug("Smart config set to: rpm-check-signatures='%s'" % str(status))
    shell_ops.run_command("smart config --set rpm-check-signatures=" + str(status))


def package_transaction(command_type, package):
    """ Package management: handle smart calls

    Args:
        command_type (str): String 'install', 'remove', 'upgrade
        package (dict): String name of rpm package

    Returns:
        str: In string format, Json array with 'status' and 'error'
    """
    log_helper = logging_helper.logging_helper.Logger()
    command = ''
    pkg = ''

    # Halt unauthorized commands
    if command_type != "install" and command_type != "remove" \
            and command_type != "upgrade":
        return

    signature_status = ""

    try:
        signature_status = package['rpm']
        if signature_status == "untrusted":
            # untrusted RPM request
            # update smart config to install untrusted package
            set_signature_verification_status(False)
    except:
        pass

    if type(package) is dict:
        pkg = package['package']
        if pkg == "all":
            command = "smart " + command_type + " -y "
        else:
            command = "smart " + command_type + " -y " + pkg

    result = shell_ops.run_cmd_chk(command)
    log_helper.logger.debug("Ran command '%s' with returncode of '%s' and return of '%s'" % (command, result['returncode'], result['cmd_output']))
    response = parse_package_installation_result(pkg_name=pkg, result_dict=result)

    if signature_status == "untrusted":
        # reset signature verification
        set_signature_verification_status(True)

    if result['returncode'] == 0:
        # package list is updated. Recreate package database
        build_package_database()

    response['p_list'] = []
    if response['status'] == 'success':
        response['p_list'] = get_data()

    log_helper.logger.debug('Return from package_transaction')
    return json.dumps(response)


def parse_package_installation_result(pkg_name, result_dict):
    """ Parse the result of Smart's package installation
    Args:
        pkg_name (str): package name
        result_dict (dict): the result of using shell_ops.run_cmd_chk to run smart package install.

    Returns:
        dict: dict of the result. The key is 'status'. If the 'status' is not 'success', then an extra key 'error'
              describes the error message.

    """
    response = ({'status': "success", 'error': ''})

    if ('returncode' in result_dict) and ('cmd_output' in result_dict):
        if result_dict['returncode']:
            if "error:" in result_dict['cmd_output']:
                # User clicked install/uninstall/upgrade then refreshed and page and hit it again
                if "Configuration is in readonly mode" in result_dict['cmd_output']:  # Smart shell already open
                    error = "For " + pkg_name + ", please wait for background processes to finish then try again."
                    status = "failure"
                elif "no package provides" in result_dict['cmd_output']:
                    error = "The dependencies for '" + pkg_name + "' could not be found."
                    status = "failure"
                elif "matches no packages" in result_dict['cmd_output']:
                    error = "The package '" + pkg_name + "' could not be found in any repositories that have been added. Please check your network configuration and repositories list on the Administration page."
                    status = "failure"
                elif "not customer signed" in result_dict['cmd_output']:
                    error = "The package '" + pkg_name + "' is untrusted. Do you want to install untrusted package?"
                    status = "untrusted"
                elif "package is not signed" in result_dict['cmd_output']:
                    error = "The package '" + pkg_name + "' is untrusted. Do you want to install untrusted package?"
                    status = "untrusted"
                else:
                    error = "For " + pkg_name + ", "
                    error += result_dict['cmd_output'][result_dict['cmd_output'].index("error:") + 7:].replace("\n", "")
                    status = "failure"
                response = ({
                    'status': status,
                    'error': error
                })

    return response


def get_updates_for_os_packages():
    """ Get available package updates for OS packages.
    Returns:
        dict: {'package_update': False, 'packages': []} or {'package_update': True, 'packages': [list]}
    """
    log_helper = logging_helper.logging_helper.Logger()
    result = {'package_update': False, 'packages': []}

    # disable repo if it is in repo tracking file or it is the default Intel repo.
    response_repos = manage_repo.enable_only_os_repos()
    if response_repos['status'] is False:
        return result

    # Check newer
    # Prepare for args
    commands_list = ['newer']
    args_list = [[]]
    # Run the commands
    p = subprocess.Popen(['python', 'smart_ops.py', str(commands_list), str(args_list)],
                         cwd='tools',
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    buffer_out = ""
    for line in iter(p.stdout.readline, ''):
        buffer_out += line
    if 'Error For Smart_ops.py' in buffer_out:
        log_helper.logger.error('Smart.ops.py running failed:  ' + str(buffer_out))
    else:
        results_list = buffer_out.split('#smart_opts_list#')
        if len(results_list) == 1:
            # Get upgrade list
            upgrade_output = results_list[0]
            if 'No interesting upgrades' not in upgrade_output and upgrade_output != '':
                upgrade_output = upgrade_output[upgrade_output.rindex('---') + 3:]
                result['package_update'] = True
                for line in upgrade_output.split('\n'):
                    if len(line) < 5:
                        continue
                    info = line.split('|')
                    str_name = info[0].strip()
                    result['packages'].append(str_name)
        else:
            log_helper.logger.error('Results do not have only 1 item in list...' + str(results_list))

    # re-enable the disabled repo
    manage_repo.enable_repo(response_repos['disabled_repos'])

    return result


def do_updates_for_os_packages():
    """ Do updates for OS packages.
    Returns:
        dict: {'status': 'failure', 'message': '', 'p_list': []} or {'status': 'success', 'message': '', 'p_list': []}
    """
    log_helper = logging_helper.logging_helper.Logger()
    result = {'status': 'failure', 'message': '', 'p_list': []}

    # disable repo if it is in repo tracking file or it is the default Intel repo.
    response_repos = manage_repo.enable_only_os_repos()
    if response_repos['status'] is False:
        result['message'] = 'It failed to disable non-OS repos.'
        return result

    # smart upgrade
    # Prepare for args
    commands_list = ['upgrade']
    args_list = [['-y']]
    # Run the commands
    p = subprocess.Popen(['python', 'smart_ops.py', str(commands_list), str(args_list)],
                         cwd='tools',
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    buffer_out = ""
    for line in iter(p.stdout.readline, ''):
        buffer_out += line
    if 'Error For Smart_ops.py' in buffer_out:
        log_helper.logger.error('Smart.ops.py running failed:  ' + str(buffer_out))
        result['status'] = 'failure'
        result['message'] = str(buffer_out)
    else:
        results_list = buffer_out.split('#smart_opts_list#')
        if len(results_list) == 1:
            result['status'] = 'success'
            result['message'] = ''
        else:
            log_helper.logger.error('Results do not have only 1 item in list...' + str(results_list))
            result['status'] = 'failure'
            result['message'] = 'Results do not have only 1 item in list...' + str(results_list)

    # re-enable the disabled repo
    manage_repo.enable_repo(response_repos['disabled_repos'])

    # re-build package database
    build_package_database()

    result['p_list'] = get_data()
    return result


@require()
class Packages(object):
    exposed = True

    def GET(self, **kwargs):
        return get_data()

    def POST(self, **kwargs):
        retrieving_work, worker_result = manage_worker.do_work(manage_worker.worker_process_message_type_install_package,
                                                               kwargs)
        try:
            if retrieving_work:
                if worker_result['status'] == 'success':
                    # {u'status': u'success',
                    #  u'message': u'{
                    #    'status': '',
                    #    'error': '',
                    #    'p_list': []
                    #     }',
                    #  u'in_progress': False,
                    #  u'work_type': ''}
                    # move the key work result to the 1st dictionary item
                    result_dict = ast.literal_eval(worker_result['message'])
                    worker_result['status'] = result_dict['status']  # this can still be 'failure' or 'untrusted'
                    worker_result['error'] = result_dict['error']
                    worker_result['message'] = result_dict['error']
                    worker_result['p_list'] = result_dict['p_list']
        except Exception as e:
            worker_result['status'] = 'failure'
            worker_result['message'] = str(e)
        return json.dumps(worker_result)

    def PUT(self, **kwargs):
        retrieving_work, worker_result = manage_worker.do_work(manage_worker.worker_process_message_type_upgrade_package,
                                                               kwargs)
        try:
            if retrieving_work:
                if worker_result['status'] == 'success':
                    # {u'status': u'success',
                    #  u'message': u'{
                    #    'status': '',
                    #    'error': '',
                    #    'p_list': [],
                    #    'p_info': ''  (optional)
                    #     }',
                    #  u'in_progress': False,
                    #  u'work_type': ''}
                    # move the key work result to the 1st dictionary item
                    result_dict = ast.literal_eval(worker_result['message'])
                    worker_result['status'] = result_dict['status']  # this can still be 'failure'
                    worker_result['error'] = result_dict['error']
                    worker_result['message'] = result_dict['error']
                    worker_result['p_list'] = result_dict['p_list']
                    if 'p_info' in result_dict:
                        worker_result['p_info'] = result_dict['p_info']
        except Exception as e:
            worker_result['status'] = 'failure'
            worker_result['message'] = str(e)
        return json.dumps(worker_result)

    def DELETE(self, **kwargs):
        retrieving_work, worker_result = manage_worker.do_work(manage_worker.worker_process_message_type_remove_package,
                                                               kwargs)
        try:
            if retrieving_work:
                if worker_result['status'] == 'success':
                    # {u'status': u'success',
                    #  u'message': u'{
                    #    'status': '',
                    #    'error': '',
                    #    'p_list': []
                    #     }',
                    #  u'in_progress': False,
                    #  u'work_type': ''}
                    # move the key work result to the 1st dictionary item
                    result_dict = ast.literal_eval(worker_result['message'])
                    worker_result['status'] = result_dict['status']  # this can still be 'failure'
                    worker_result['error'] = result_dict['error']
                    worker_result['message'] = result_dict['error']
                    worker_result['p_list'] = result_dict['p_list']
        except Exception as e:
            worker_result['status'] = 'failure'
            worker_result['message'] = str(e)
        return json.dumps(worker_result)


@require()
class PackageInfo(object):
    exposed = True

    def GET(self, **kwargs):
        retrieving_work, worker_result = manage_worker.do_work(manage_worker.worker_process_message_type_get_package_info,
                                                               kwargs)
        try:
            if retrieving_work:
                if worker_result['status'] == 'success':
                    # {u'status': u'success',
                    #  u'message': u'{
                    #    'url': url,
                    #    'license': my_license,
                    #    'size': size,
                    #    'description': description,
                    #    'summary': summary,
                    #    'group': group,
                    #    'version': version
                    #     }',
                    #  u'in_progress': False,
                    #  u'work_type': ''}
                    # move the key work result to the 1st dictionary item
                    result_dict = ast.literal_eval(worker_result['message'])
                    worker_result['url'] = result_dict['url']
                    worker_result['license'] = result_dict['license']
                    worker_result['size'] = result_dict['size']
                    worker_result['description'] = result_dict['description']
                    worker_result['summary'] = result_dict['summary']
                    worker_result['group'] = result_dict['group']
                    worker_result['version'] = result_dict['version']
        except Exception as e:
            worker_result['status'] = 'failure'
            worker_result['message'] = str(e)
        return json.dumps(worker_result)
