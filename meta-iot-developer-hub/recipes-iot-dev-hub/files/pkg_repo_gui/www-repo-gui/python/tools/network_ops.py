#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import os
import urllib2
import socket
import ssl
from subprocess import check_output
from tools import logging_helper
import manage_config
import time
import json


class URLHeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"


class NetworkCheck(object):
    """Helper class to handle network operations.
    """
    def __init__(self):
        self.__remote_url = "google.com"
        self.__log_helper = logging_helper.logging_helper.Logger()

    def is_network_connected_url_header(self, secure=True, timeout_value=2):
        """Test network connection using HTTP HEAD request via urllib2.urlopen

        On Linux system,
            If there is no network, urllib2.urlopen throws exception without using the timeout value.
            If the proxy is not correct, urllib2.urlopen throws exception without using the timeout value.

        We do not rely on the os.environ to set the proxy values.  urllib2 is strict about the environment variable.
        The proxy address in os.environ["http_proxy"] or os.environ["https_proxy"] has to have http(s):// in the front.
        Thus, we read the environment variable and check the value, and set up urllib2 proxy directly.

        Args:
            secure (bool): The first parameter. Default to True. Use http or https.
            timeout_value (int): THe second parameter. Default to 2. The timeout in seconds.

        Returns:
            int: 0 if succeed, 1 if fail due to timeout, 2 if fail to due other reason.
        """
        try:
            self.__log_helper.logger.debug('timeout is ' + str(timeout_value))
            http_string = "http://"
            protocol_value = "http"
            env_value = os.getenv("http_proxy", "not_there")
            if secure:
                http_string = "https://"
                protocol_value = "https"
                env_value = os.getenv("https_proxy", "not_there")

            if env_value == "not_there":
                self.__log_helper.logger.debug("No proxy to use.")
            else:
                if env_value.startswith("http://"):
                    env_value = env_value[7:]
                elif env_value.startswith("https://"):
                    env_value = env_value[8:]
                proxy = urllib2.ProxyHandler({protocol_value: env_value})
                opener = urllib2.build_opener(proxy)
                urllib2.install_opener(opener)
                self.__log_helper.logger.debug("Proxy for connection check is " + str(protocol_value) + str(env_value))

            response = urllib2.urlopen(URLHeadRequest(http_string + self.__remote_url), timeout=timeout_value)
            self.__log_helper.logger.info('response url is ' + response.geturl())
            response.close()
            return 0
        except urllib2.URLError as e:
            # logging.exception(e)
            if isinstance(e.reason, socket.timeout):
                # For HTTP.
                return 1
            elif isinstance(e.reason, ssl.SSLError):
                if "timed out" in str(e.reason):
                    # For HTTPS: URLError: <urlopen error ('_ssl.c:574: The handshake operation timed out',)>
                    # For HTTPS: URLError: <urlopen error _ssl.c:491: The handshake operation timed out>
                    return 1
                else:
                    return 2
            else:
                return 2
        except socket.timeout as e:
            # logging.exception(e)
            return 1
        except Exception as e:
            # logging.exception(e)
            pass
        return 2

    def is_network_connected(self, secure=True, factor_value=1):
        """Test network connection

        If the network connection check fails due to timeout, then we try again.
            We try up to 3 times with increasing timeout value: factor * [1, 2, 4]
        Else, we return.

        Args:
            secure (bool): The first parameter. Default to True. Use http or https.
            factor_value (int): The second parameter. Default to 1. The timeout values are factor * [1, 2, 4].

        Returns:
            str: "True" if succeed, "False" if fail.
        """
        try:
            for i in range(3):
                r = self.is_network_connected_url_header(secure=secure, timeout_value=(factor_value * (2 ** i)))
                if r == 0:
                    # Succeed
                    return "True"
                elif r == 1:
                    # Fail due to timeout
                    continue
                else:
                    # Fail
                    return "False"
            return "False"  # It is Fail due to timeout all the time
        except:
            pass
        return "False"

    def is_network_connected_old(self):
        """Test network connection

        Returns:
            str: "True" if succeed, "False" if fail.
        """
        try:
            network_result = check_output("timeout 10 wget -O- https://google.com > /dev/null && echo True || echo False", shell=True)
            network_result = network_result.strip('\n')
            return network_result
        except:
            pass
        return "False"

    def test_network_connection(self, check_http=False, no_rest_period=False):
        """ Attempts to connect to google.com to see if a connection can be established.

        Args:
            check_http (bool): Check http or not.
            no_rest_period (bool): Have 60 seconds do-not-check period or not.

        Returns:
            tuple: tuple of the following 2 items.
                1) dict of key 'https_conn' with the value of 'True' or 'False', and
                   of key 'http_conn' with the value of 'True', 'False', or 'NA'
                2) Json string with key 'https_conn' and values 'True' or 'False, and
                   with key 'http_conn' and values 'True', 'False', or 'NA'
        """

        do_run_https = False
        if manage_config.network_status['https_conn'] == 'False':
            do_run_https = True
        else:
            if no_rest_period:
                do_run_https = True
            else:
                elapse_time = time.time() - manage_config.network_time
                if elapse_time > float(60):
                    do_run_https = True

        do_run_http = False
        if check_http:
            if manage_config.network_status['http_conn'] == 'False' or manage_config.network_status['http_conn'] == 'NA':
                do_run_http = True
            else:
                if no_rest_period:
                    do_run_http = True
                else:
                    elapse_time = time.time() - manage_config.network_time
                    if elapse_time > float(60):
                        do_run_http = True

        if do_run_https:
            self.__log_helper.logger.debug('run https network check.')
            manage_config.network_time = time.time()
            manage_config.network_status['https_conn'] = self.is_network_connected(secure=True, factor_value=3)

        if do_run_http:
            self.__log_helper.logger.debug('run http network check.')
            manage_config.network_time = time.time()
            manage_config.network_status['http_conn'] = self.is_network_connected(secure=False, factor_value=3)

        return manage_config.network_status, json.dumps(manage_config.network_status)

    def get_stored_https_status(self):
        """ Get the stored https connection status

        Returns:
            bool: True if https connection is up.
        """
        if manage_config.network_status['https_conn'] == "False":
            return False
        else:
            return True

    def get_stored_http_status(self):
        """ Get the stored http connection status

        Returns:
            bool: True if http connection is up.
        """
        if manage_config.network_status['http_conn'] == "False":
            return False
        else:
            return True
