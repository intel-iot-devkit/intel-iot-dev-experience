#!/usr/bin/env python

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import subprocess 
import json
import ast
from tools import logging_helper
import manage_config
import manage_worker


class ServiceSupport(object):
    """ Class to get and handle the packages list file.
    """

    @staticmethod
    def get_service_info(data):
        log_helper = logging_helper.logging_helper.Logger()

        # Turn kwargs into (k,v) key pairs
        services = []

        # Note: we only support query for 1 service at a time.
        # for k in kwargs:
        #    self.__log_helper.logger.error(str(k))
        #    v = kwargs[k]
        #    self.__log_helper.logger.error(str(v))
        #    services += [(k, v)]

        if 'service' in data:
            services = [('service', data['service'])]

        # run systemctl on each service
        report = {}
        option = ['list-units', 'list-unit-files', '--no-legend']
        for k, v in services:
            if k.find('service') != -1:
                report[v] = {'LOAD': 'na', 'ACTIVE': 'na', 'State': 'disabled',
                             'SUB': 'Not Running'}
                try:
                    r = subprocess.check_output(['systemctl', option[0], option[2], v])
                    log_helper.logger.debug(str(r))
                    if v in r:
                        r = r.split()
                        if r[3] == 'dead' or r[3] == 'exited' or r[3] == 'abandoned':
                            service_state = 'Not Running'
                        else:
                            # Other process states are waiting, running, listening, mounted, active, plugged
                            service_state = 'Running'
                        report[v] = {'LOAD': 'loaded', 'ACTIVE': r[2], 'SUB': service_state}
                except subprocess.CalledProcessError as e:
                    log_helper.logger.error('return code = ' + str(e.returncode) + ' value = ' + str(e.output))

                try:
                    r = subprocess.check_output(['systemctl', option[1], option[2], v])
                    log_helper.logger.debug(str(r))
                    if v in r:
                        r = r.split()
                        # service state static means you can't disable service
                        if r[1] == 'enabled' or r[1] == 'static':
                            service_auto_run = 'enabled'
                        else:
                            # other service state are disabled and mask. mask state means you can't start service
                            service_auto_run = 'disabled'
                        report[v]['State'] = service_auto_run
                except subprocess.CalledProcessError as e:
                    log_helper.logger.error('return code = ' + str(e.returncode) + ' value = ' + str(e.output))

        return json.dumps(report)

    @staticmethod
    def control_service(data):
        response = {'status': "failure"}

        # Turn kwargs into (k,v) key pairs
        services = {}
        # for k in data:
        #     v = data[k]
        #     services[k] = v

        if 'services' in data:
            services['services'] = data['services']
        if 'action' in data:
            services['action'] = data['action']

        try:
            v = services['services']
            a = services['action']
            r = subprocess.call(['systemctl', a, v])
            if r == 0:
                response['status'] = "success"
        except:
            pass

        return json.dumps(response)

    @staticmethod
    def stop_node_red_experience():
        """ Get the current Node Red Experience service status, and stop the service.

        Returns:
            dict: {'status': 'success'/'failure', 'is_active': True/False}
        """
        response = {'status': 'failure', 'is_active': False}
        log_helper = logging_helper.logging_helper.Logger()
        try:
            # get the current active status
            request_data = {'service': manage_config.node_red_experience_service}
            request_return = json.loads(ServiceSupport.get_service_info(request_data))
            if manage_config.node_red_experience_service in request_return:
                request_return_2 = request_return[manage_config.node_red_experience_service]
                if 'ACTIVE' in request_return_2:
                    if request_return_2['ACTIVE'] == 'active':
                        response['is_active'] = True

            # if active, stop it
            if response['is_active']:
                request_data = {'action': 'stop', 'services': manage_config.node_red_experience_service}
                ServiceSupport.control_service(request_data)

            response['status'] = "success"
        except Exception as e:
            log_helper.logger.error(str(e))
        return response

    @staticmethod
    def start_node_red_experience():
        """ Start Node Red Experience service

        Returns:
            dict: {'status': 'success'/'failure'}
        """
        response = {'status': 'failure'}
        log_helper = logging_helper.logging_helper.Logger()
        try:
            request_data = {'action': 'start', 'services': manage_config.node_red_experience_service}
            ServiceSupport.control_service(request_data)
            response['status'] = 'success'
        except Exception as e:
            log_helper.logger.error(str(e))
        return response


class ServiceControl(object):
    exposed = True

    def __init__(self):
        self.__log_helper = logging_helper.logging_helper.Logger()

    def GET(self, **kwargs):
        # The syntax is [ip]/api/sc?service=node-red-experience.service
        return ServiceSupport.get_service_info(kwargs)

    def POST(self, **kwargs):
        retrieving_work, worker_result = manage_worker.do_work(manage_worker.worker_process_message_type_control_service,
                                                               kwargs)
        try:
            if retrieving_work:
                if worker_result['status'] == 'success':
                    # {u'status': u'success',
                    #  u'message': u'{
                    #    'status': ''
                    #     }',
                    #  u'in_progress': False,
                    #  u'work_type': ''}
                    # move the key work result to the 1st dictionary item
                    result_dict = ast.literal_eval(worker_result['message'])
                    worker_result['status'] = result_dict['status']  # this can still be 'failure'
        except Exception as e:
            worker_result['status'] = 'failure'
            worker_result['message'] = str(e)
        return json.dumps(worker_result)
