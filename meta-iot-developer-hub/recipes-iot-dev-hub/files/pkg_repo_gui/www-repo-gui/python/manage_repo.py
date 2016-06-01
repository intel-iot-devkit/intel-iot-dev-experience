#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import subprocess
import json
import sys
import os
import ast
from tools import logging_helper, network_ops, shell_ops, sysinfo_ops
import manage_config
import manage_package
import manage_worker
from manage_auth import require


sys.path.append('..')


class RepoTracking(object):
    """ Class to track the repos added/removed by the user from GUI
    """

    @staticmethod
    def add_to_tracking(name):
        """ Add the repo (wht [name] to tracking file.
        Args:
            name (str): the name of the repo

        Returns:
            str: Json string with key 'status' with values 'success' or 'failure' and 'error' with None or 'Error message'
        """
        log_helper = logging_helper.logging_helper.Logger()
        response = {'status': 'failure', 'error': None}
        try:
            # check if tracking file exists. If not, create one.
            if os.path.exists(manage_config.repo_tracking_file):
                log_helper.logger.debug(manage_config.repo_tracking_file + " exists already. Appending....")
                with open(manage_config.repo_tracking_file, "a") as myfile:
                    myfile.write(name + "\n")
            else:
                log_helper.logger.debug(manage_config.repo_tracking_file + " does not exist. Creating and Writing....")
                with open(manage_config.repo_tracking_file, "w") as myfile:
                    myfile.write(name + "\n")
            response['status'] = 'success'
        except Exception as e:
            log_helper.logger.error("add_to_tracking failed..." + str(e))
            response['error'] = str(e)
        return json.dumps(response)

    @staticmethod
    def remove_from_tracking(name):
        """  Remove the repo with [name] from tracking file.
        Args:
            name (str): the name of the repo

        Returns:
            str: Json string with key 'status' with values 'success' or 'failure' and 'error' with None or 'Error message'
        """
        log_helper = logging_helper.logging_helper.Logger()
        response = {'status': 'failure', 'error': None}
        try:
            if os.path.exists(manage_config.repo_tracking_file):
                log_helper.logger.debug(manage_config.repo_tracking_file + " exists. Removing the entry.")
                # read all lines first
                file_handle = open(manage_config.repo_tracking_file, "r")
                file_lines = file_handle.readlines()
                file_handle.close()
                # filter and write back to the file
                with open(manage_config.repo_tracking_file, "w") as myfile:
                    for file_line in file_lines:
                        # log_helper.logger.debug(file_line + "   " + str(len(file_line)))
                        # removing training newline and white space
                        temp_file_line = file_line.rstrip()
                        if temp_file_line != name:
                            myfile.write(file_line)
            else:
                log_helper.logger.debug(manage_config.repo_tracking_file + " does not exist. Cannot remove the entry.")
            response['status'] = 'success'
        except Exception as e:
            log_helper.logger.error("add_to_tracking failed..." + str(e))
            response['error'] = str(e)
        return json.dumps(response)

    @staticmethod
    def reset():
        """ Remove the tracking file.
        Returns:

        """
        try:
            os.remove(manage_config.repo_tracking_file)
        except OSError:
            pass

    @staticmethod
    def read_from_tracking():
        """ Read from tracking file.
        Returns:
            list: list of lines in the tracking file.
        """
        log_helper = logging_helper.logging_helper.Logger()
        return_list = []
        try:
            if os.path.exists(manage_config.repo_tracking_file):
                # read all lines first
                file_handle = open(manage_config.repo_tracking_file, "r")
                file_lines = file_handle.readlines()
                for file_line in file_lines:
                    # removing training newline and white space
                    file_line = file_line.rstrip()
                    return_list.append(file_line)
                file_handle.close()
                return return_list
            else:
                return []
        except Exception as e:
            log_helper.logger.error("read_from_tracking failed..." + str(e))
            return None

    @staticmethod
    def check_in_tracking(name):
        """ Check if the repo with name is in tracking file.
        Args:
            name (str): the name of the repo

        Returns:
            bool: True if it is in the repo.
        """
        log_helper = logging_helper.logging_helper.Logger()
        try:
            if os.path.exists(manage_config.repo_tracking_file):
                # read all lines first
                found = False
                file_handle = open(manage_config.repo_tracking_file, "r")
                file_lines = file_handle.readlines()
                file_handle.close()
                for file_line in file_lines:
                    # removing training newline and white space
                    file_line = file_line.rstrip()
                    if file_line == name:
                        found = True
                        break
                return found
            else:
                return False
        except Exception as e:
            log_helper.logger.error("check_in_tracking failed..." + str(e))
            return False

    @staticmethod
    def filter_repo_list(repos, keep_tracking=True):
        """ Filter the input repos list by keeping/removing the repo in tracking file.
        Args:
            repos (list): list of repo names.
            keep_tracking (bool): True to keep the repos in tracking file. False to remove the repos in tracking file.

        Returns:
            list: The filtered repos list.
        """
        log_helper = logging_helper.logging_helper.Logger()
        try:
            if os.path.exists(manage_config.repo_tracking_file):
                # read all lines first
                found = False
                file_handle = open(manage_config.repo_tracking_file, "r")
                file_lines = file_handle.readlines()
                file_handle.close()
                # filter
                filtered_repos = []
                for repo in repos:
                    in_tracking_file = False
                    for file_line in file_lines:
                        # removing training newline and white space
                        file_line = file_line.rstrip()
                        if file_line == repo:
                            in_tracking_file = True
                            break
                    log_helper.logger.debug(repo + " is in tracking file? " + str(in_tracking_file))
                    if keep_tracking:
                        if in_tracking_file:
                            filtered_repos.append(repo)
                        else:
                            pass
                    else:
                        if in_tracking_file:
                            pass
                        else:
                            filtered_repos.append(repo)
                return filtered_repos
            else:
                return repos
        except Exception as e:
            log_helper.logger.error("filter_repo_list failed..." + str(e))
            return repos


def configure_default_repo(check_network_again=True):
    """  Reads the configuration file for the corresponding architecture dedicated repository.
    Configure the default repository if it has not already been configured.
    Args:
        check_network_again (bool):  True if we need to check network again.
    """
    log_helper = logging_helper.logging_helper.Logger()
    data_collector = sysinfo_ops.DataCollect()
    data_collector.getDataSet()

    config = manage_config.read_config_file()
    developer_hub_url = config.get('DefaultRepo', 'base_repo')
    architecture, rcpl_version = data_collector.platform_details()
    developer_hub_url = developer_hub_url + rcpl_version + '/' + architecture

    # Check if repository already configured
    try:
        cmd = "smart channel --show | grep " + developer_hub_url
        subprocess.check_output(cmd, shell=True)
        log_helper.logger.debug("Default repository is configured.")
        update_channels(CheckNetworkAgain=check_network_again)
    except subprocess.CalledProcessError:
        # Verify entry does not exist with different URL. Then configure default repository.
        try:
            cmd = "smart channel --show | grep " + manage_config.default_repo_name
            subprocess.check_output(cmd, shell=True)
            remove_repo(manage_config.default_repo_name)
        except:
            pass
        log_helper.logger.debug("Configuring default repository...")
        # Do not need to smart update.
        # When there is no network, smart update takes a long time to timeout.
        # Also, we want to add the default repo no matter what.
        add_repo(developer_hub_url, "None", "None", manage_config.default_repo_name,
                 from_startup=True, check_network_again=check_network_again)


def list_repos(do_filter=False, keep_tracking=True):
    """ List all repositories from the 'smart channel --list' command.
    Args:
        do_filter (bool): True to perform filtering.
        keep_tracking (bool): True to keep the repos in tracking file. False to remove the repos in tracking file.
    Returns:
        list: list of String of channel names
    """
    if manage_config.use_new_list_repos:
        result = list_repos_new(do_filter=do_filter, keep_tracking=keep_tracking)
    else:
        result = list_repos_original(do_filter=do_filter, keep_tracking=keep_tracking)
    return result


def list_repos_original(do_filter=False, keep_tracking=True):
    """ List all repositories from the 'smart channel --list' command.
    Args:
        do_filter (bool): True to perform filtering.
        keep_tracking (bool): True to keep the repos in tracking file. False to remove the repos in tracking file.
    Returns:
        list: list of String of channel names
    """
    log_helper = logging_helper.logging_helper.Logger()
    response = []
    channel_list = shell_ops.run_command('smart channel --list').split("\n")
    for item in channel_list:
        if item != "" and 'rpmsys' not in item:
            response.append(item)
    if do_filter:
        response = RepoTracking.filter_repo_list(response, keep_tracking=keep_tracking)
    log_helper.logger.debug("List of repositories: '%s'" % str(response))
    return response


def list_repos_new(do_filter=False, keep_tracking=True):
    """ List all repositories from smart's cache /var/lib/smart/channels.

    The requirements of using this is to make sure that smart update is called to update cache,
    when add/remove repo is done.

    Args:
        do_filter (bool): True to perform filtering.
        keep_tracking (bool): True to keep the repos in tracking file. False to remove the repos in tracking file.
    Returns:
        list: list of String of channel names
    """
    log_helper = logging_helper.logging_helper.Logger()
    response = []

    # Smart cache should be updated already upon repo/channel ops.

    # Find out the channels by checking /var/lib/smart/channels folder. (This won’t include rpmsys channel.)
    try:
        for f in os.listdir(manage_config.smart_cache_path):
            if os.path.isfile(manage_config.smart_cache_path + '/' + f):
                repo_name = f.split('%%')[0]
                if not (repo_name in response):
                    response.append(repo_name)
    except Exception as e:
        log_helper.logger.debug(str(e))

    if do_filter:
        response = RepoTracking.filter_repo_list(response, keep_tracking=keep_tracking)
    log_helper.logger.debug("List of repositories: '%s'" % str(response))
    return response


def list_repos_os_only():
    """ Return list of OS repos. OS Repos are repos not in the tracking file, and not the default Intel repo.
    Returns:
        list: list of OS repos.
    """
    log_helper = logging_helper.logging_helper.Logger()
    repos = list_repos(do_filter=True, keep_tracking=False)
    filtered_repos = []
    for repo in repos:
        if repo != manage_config.default_repo_name:
            filtered_repos.append(repo)
    log_helper.logger.debug("OS repos: " + str(filtered_repos))
    return filtered_repos


def list_repos_non_os_only():
    """ Return list of non-OS repos. non-OS Repos are repos in the tracking file, or the default Intel repo.
    Returns:
        list: list of non-OS repos.
    """
    log_helper = logging_helper.logging_helper.Logger()
    tracking_lines = RepoTracking.read_from_tracking()
    if tracking_lines is None:
        # something wrong, cannot read from tracking file
        return None
    repos = list_repos()
    filtered_repos = []
    for repo in repos:
        if repo == manage_config.default_repo_name:  # default Intel repo
            filtered_repos.append(repo)
        else:
            in_tracking = False
            for tracking_line in tracking_lines:
                if repo == tracking_line:
                    in_tracking = True
                    break
            if in_tracking:  # added by user from Dev Hub, disable it.
                filtered_repos.append(repo)
    log_helper.logger.debug("non-OS repos: " + str(filtered_repos))
    return filtered_repos


def add_repo(url, user_name, password, name, from_startup=False, from_GUI=False, check_network_again=True):
    """ Add a repository to the channel cache.

    Args:
        url (str): Location of the repository
        user_name (str): Login protected repository username
        password (str): Login protected repository password
        name (str): Desired name of the repository
        from_startup (bool): True if this is called by server.py start-up
        from_GUI (bool): True if this is called by front-end
        check_network_again (bool): True if need to check network again

    Returns:
        str: Json string with keys
                'status' = 'success' or 'failure', and
                'error' = '', and
                'p_list' = new packages list
    """
    log_helper = logging_helper.logging_helper.Logger()
    response = {'status': 'failure', 'error': '', 'p_list': []}

    if ' ' in url:
        response['error'] = "Failed to add repository: URL cannot contain spaces"
        log_helper.logger.error("Error: URL cannot contain spaces")
        return json.dumps(response)

    if 'http://' in url or 'https://' in url:
        pass
    else:
        response['error'] = "Failed to add repository: URL must contain protocol (example: http://)"
        log_helper.logger.error("Error: URL must contain protocol")
        return json.dumps(response)

    # use the original list_repos to get all repos so that we can check name.
    repo_list = list_repos()
    if name in repo_list:  # Confrim repo does not exist
        response['error'] = "Duplicate name"
        log_helper.logger.error("Error: Duplicate repository name '%s'" % name)
        return json.dumps(response)

    if user_name != "None":  # Build URL with unique user identification 
        user_name = user_name.replace("@", "%40")
        if password == "None":
            url = url.replace("://", "://%s@" % user_name)
        else:
            url = url.replace("://", "://%s:%s@" % (user_name, password))

    command = "smart channel --add '" + name + "' type=rpm-md baseurl='" + url + "' -y"
    result = shell_ops.run_cmd_chk(command)
    if result['returncode']:
        if "error" in result['cmd_output']:
            remove_repo(name)
            error = "Failed to add repository: " + result['cmd_output'][result['cmd_output'].index("error:") + 7:].replace("\n", "")
            response['error'] = error
            log_helper.logger.error("Failed to add repository. Error output: '%s'" % response['error'])
    else:
        # If this is run by server.py startup, we do not do update if we do not have network.
        do_update = True
        if from_startup:
            # run by startup, need to see if the network is good or not.
            network_checker = network_ops.NetworkCheck()
            if network_checker.get_stored_https_status() and network_checker.get_stored_http_status():  # yes network
                do_update = True
            else:
                do_update = False
        else:
            pass

        if do_update:
            command = "smart update '" + name + "'"
            result = shell_ops.run_cmd_chk(command)  # Attempt to connect to new repo
        else:
            result = {'returncode': None, 'cmd_output': None}
        if result['returncode']:  # If attempt fails determine error and remove repo
            if "error" in result['cmd_output']:
                if "Invalid URL" in result['cmd_output']:
                    response['error'] = "Failed to add repository: Invalid URL."
                elif "Failed to connect" in result['cmd_output'] or 'URL returned error: 503' in result['cmd_output']:
                    response['error'] = "Failed to add repository: Unable to connect to repository."
                elif "Invalid XML" in result['cmd_output']:
                    response['error'] = "Failed to add repository: Repository XML file invalid. "
                else:
                    response['error'] = result['cmd_output'][result['cmd_output'].index("error:") + 7:].replace("\n", "")
            else:
                response['error'] = 'Error adding repository'
            remove_repo(name)
            log_helper.logger.error("Failed to add repository. Error output: '%s'" % response['error'])
        else:  # Update channels and package list
            # Need to track the repos first, before update_channels().
            if from_GUI:
                log_helper.logger.debug("Adding repo " + name + " to tracking list.")
                tracking_result = RepoTracking.add_to_tracking(name)
                js_data = json.loads(tracking_result)
                if js_data['status'] != "success":
                    remove_repo(name)
                    log_helper.logger.error("Failed to add repo into tracking. Error: " + str(tracking_result))
                else:
                    response['status'] = "success"
            else:
                response['status'] = "success"

            update_channels(CheckNetworkAgain=check_network_again)

            log_helper.logger.debug("Successfully added repository '%s'" % name)

    response['p_list'] = manage_package.get_data()
    return json.dumps(response)
    

def remove_repo(name, UpdateCache=False, from_GUI=False):
    """ Remove a repository from the channel cache.

    Args:
        name (str): Name of the repository from 'smart channel --list'
        UpdateCache (bool): False if we do not want to do smart update. True if we want to do smart update.
        from_GUI (bool): true if this is called by front-end

    Returns:
        str: Json string with keys
                'status' = 'success' or 'fail', and
                'p_list' = new packages list

    """
    log_helper = logging_helper.logging_helper.Logger()
    log_helper.logger.debug("Removing repository named '%s'" + name)
    response = ({
            'status': "failure",
        })

    result = subprocess.check_output(["smart", "channel", "--remove", name, "-y"])
    if "error:" in result:
        log_helper.logger.error("Failed to remove repository named '%s'" % name)
    else:
        if UpdateCache:
            network_checker = network_ops.NetworkCheck()
            network_checker.test_network_connection(check_http=manage_config.network_check_http)
            if network_checker.get_stored_https_status() and network_checker.get_stored_http_status():
                subprocess.check_output(['smart', 'update'])

        if from_GUI:
            log_helper.logger.debug("Removing repo " + name + " from tracking list.")
            tracking_result = RepoTracking.remove_from_tracking(name)
            js_data = json.loads(tracking_result)
            if js_data['status'] != "success":
                log_helper.logger.error("Failed to remove repo from tracking. Error: " + str(tracking_result))
            else:
                response['status'] = "success"
                log_helper.logger.debug("Successfully removed repository named '%s'" % name)
        else:
            response['status'] = "success"
            log_helper.logger.debug("Successfully removed repository named '%s'" % name)

    # package list is updated. Recreate pacakge database
    manage_package.build_package_database()
    response['p_list'] = manage_package.get_data()
    return json.dumps(response)


def update_channels(CheckNetworkAgain=True):
    """ Update the channel cache.
    Args:
        CheckNetworkAgain (bool):  True if we want to check network again.
    Returns:
        str: Json string with keys
                'status' = 'success' or 'failure', and
                'p_list' = new packages list
    """
    log_helper = logging_helper.logging_helper.Logger()
    response = ({
        'status': "failure",
    })

    do_run = False
    network_checker = network_ops.NetworkCheck()
    if CheckNetworkAgain:
        network_checker.test_network_connection(check_http=manage_config.network_check_http)
    if network_checker.get_stored_https_status() and network_checker.get_stored_http_status():
        do_run = True

    if do_run:
        # We need this "smart update"... Add repo is relying on this.
        shell_ops.run_command("smart update")
        response = ({
                'status': "success",
            })
        log_helper.logger.debug("Successfully updated channel.")
        manage_package.update_package_list()

    response['p_list'] = manage_package.get_data()
    return json.dumps(response)


def enable_only_os_repos():
    """ Enable only OS repos.
    OS packages are at OS repos. OS Repos are repos not in the tracking file, and not the default Intel repo.
    So, if a repo is in the tracking file or is the default Intel repo, we need to disable it.
    Returns:
        dict: {'status': True, 'disabled_repos': [list]} or {'status': False, 'disabled_repos': []}
    """
    log_helper = logging_helper.logging_helper.Logger()
    result = {'status': True, 'disabled_repos': []}
    repos = list_repos_non_os_only()
    if repos is None:
        # something wrong. cannot read tracking file
        # ignore this error.
        repos = []
    channel_args_list = []
    for repo in repos:
        channel_args_list.append('--disable')
        channel_args_list.append(repo)
        result['disabled_repos'].append(repo)

    # Prepare for args
    commands_list = ['channel']
    args_list = [channel_args_list]

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
        result['status'] = False
        result['disabled_repos'] = []
    else:
        results_list = buffer_out.split('#smart_opts_list#')
        if len(results_list) != 1:
            log_helper.logger.error('Smart.ops.py result should only have 1 item in list:  ' + str(results_list))
            result['status'] = False
            result['disabled_repos'] = []

    return result


def enable_repo(repo_list):
    """ Enable the specified repo.
    Args:
        repo_list (list): list of repo names to enable.

    Returns:
        dict: {'status': True} or {'status': False}
    """
    log_helper = logging_helper.logging_helper.Logger()
    result = {'status': True}
    channel_args_list = []
    for repo in repo_list:
        channel_args_list.append('--enable')
        channel_args_list.append(repo)

    # Prepare for args
    commands_list = ['channel']
    args_list = [channel_args_list]

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
        result['status'] = False
    else:
        results_list = buffer_out.split('#smart_opts_list#')
        if len(results_list) != 1:
            log_helper.logger.error('Smart.ops.py result should only have 1 item in list:  ' + str(results_list))
            result['status'] = False

    return result


@require()
class Repository(object):
    exposed = True

    def GET(self, **kwargs):
        retrieving_work, worker_result = manage_worker.do_work(manage_worker.worker_process_message_type_get_repo,
                                                               kwargs)
        try:
            if retrieving_work:
                if worker_result['status'] == 'success':
                    # {u'status': u'success',
                    #  u'message': u'[
                    #    'repo1',
                    #    'repo2'
                    #     ]',
                    #  u'in_progress': False,
                    #  u'work_type': ''}
                    # move the key work result to the 1st dictionary item
                    result_list = ast.literal_eval(worker_result['message'])
                    worker_result['list'] = result_list
        except Exception as e:
            worker_result['status'] = 'failure'
            worker_result['message'] = str(e)
        return json.dumps(worker_result)

    def POST(self, **kwargs):
        retrieving_work, worker_result = manage_worker.do_work(manage_worker.worker_process_message_type_add_repo,
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

    def PUT(self, **kwargs):
        retrieving_work, worker_result = manage_worker.do_work(manage_worker.worker_process_message_type_update_repo,
                                                               kwargs)
        try:
            if retrieving_work:
                if worker_result['status'] == 'success':
                    # {u'status': u'success',
                    #  u'message': u'{
                    #    'status': '',
                    #    'p_list': []
                    #     }',
                    #  u'in_progress': False,
                    #  u'work_type': ''}
                    # move the key work result to the 1st dictionary item
                    result_dict = ast.literal_eval(worker_result['message'])
                    worker_result['status'] = result_dict['status']  # this can still be 'failure'
                    worker_result['p_list'] = result_dict['p_list']
        except Exception as e:
            worker_result['status'] = 'failure'
            worker_result['message'] = str(e)
        return json.dumps(worker_result)

    def DELETE(self, **kwargs):
        retrieving_work, worker_result = manage_worker.do_work(manage_worker.worker_process_message_type_remove_repo,
                                                               kwargs)
        try:
            if retrieving_work:
                if worker_result['status'] == 'success':
                    # {u'status': u'success',
                    #  u'message': u'{
                    #    'status': '',
                    #    'p_list': []
                    #     }',
                    #  u'in_progress': False,
                    #  u'work_type': ''}
                    # move the key work result to the 1st dictionary item
                    result_dict = ast.literal_eval(worker_result['message'])
                    worker_result['status'] = result_dict['status']  # this can still be 'failure'
                    worker_result['p_list'] = result_dict['p_list']
        except Exception as e:
            worker_result['status'] = 'failure'
            worker_result['message'] = str(e)
        return json.dumps(worker_result)
