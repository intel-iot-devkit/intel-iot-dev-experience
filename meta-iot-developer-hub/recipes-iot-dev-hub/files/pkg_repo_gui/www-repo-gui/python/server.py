#!/usr/bin/env python

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

import cherrypy
import os
import mimetypes
import manage_config
import manage_package
import manage_repo
import manage_proxy
import manage_auth
import manage_service
import manage_usb
import manage_os_controls
import manage_os_update
import manage_service
import manage_usb
import manage_hac
import manage_pro_upgrade
import manage_security
import manage_mec
import manage_self_update
import manage_oem_branding
import manage_nginx_userDB
import manage_worker
from tools import logging_helper, onetime_update, sysinfo_ops, network_ops


'''
Create a server using CherryPy and expose the /action/ directory.
These actions can be routed to @action_select and distributed by
calling different functions based on specified arguments.

Usage:
    /action/install_package?package=gedit
        action is "install_package"
        arguments are "package (key), gedit (value)"

    /action/add_repo?name=intel_repo&url=http://myurl
        action is "add_repo"
        arguments are "name (key), intel_repo (value)",
         "url (key), http://myurl (value)"
'''


class Server(object):
    authenticated = False
    proxy_override = False

    @cherrypy.expose
    def action(self, action, **kwargs):
        arg_list = []
        for key, value in kwargs.iteritems():
            arg_list.append([key, value])
        return action_select(action, arg_list)

    @cherrypy.expose
    def index(self):
        index_location = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        return open(index_location + '/index.html')


def server_stopping():
    # The following will trigger this:
    #       cherrypy.engine.restart() call, or restart triggered by file change.
    # The following won't trigger this:
    #       systemctl stop, systemctl restart
    temp_logger = logging_helper.logging_helper.Logger(logger_name='backend_general')
    temp_logger.logger.info('CherryPy server is stopping.....')
    # finish worker process
    manage_worker.finish()


if __name__ == '__main__':
    # Logging config
    my_logger = logging_helper.logging_helper.Logger(logger_name='backend_general')

    # read oem brandin config
    manage_oem_branding.OemBrandingHandler.GetOemBrandingConfig()

    # create tmp sessions folder if it not there
    temp_sessions_dir = '/tmp/cherrypy_sessions'
    if not os.path.exists(temp_sessions_dir):
        os.makedirs(temp_sessions_dir)
    # remove all files so that we expire sessions upon server restart
    try:
        filelist = os.listdir(temp_sessions_dir)
        for f in filelist:
            os.remove(temp_sessions_dir + '/' + f)
        pass
    except:
        pass

    # start worker process
    # When the server.py got killed by systemctl stop/restart, the sub process will be killed also.
    manage_worker.start()

    # gather system info
    data_collector = sysinfo_ops.DataCollect()
    sys_info_dict = data_collector.getDataSet()

    # test network
    network_checker = network_ops.NetworkCheck()
    network_checker.test_network_connection(check_http=manage_config.network_check_http)

    manage_config.cherrypy_session_timeout_chosen = manage_config.cherrypy_session_timeout_other
    if 'Quark' in sys_info_dict['model']:
        manage_config.cherrypy_session_timeout_chosen = manage_config.cherrypy_session_timeout_quark

    my_logger.logger.debug('Cherrpy session timeout (m): ' + str(manage_config.cherrypy_session_timeout_chosen))

    # If we want the session to exist even after cherrypy restart, we can use file storage below.
    # By default, it is RAM storage.

    # Server config
    cherrypy.config.update({
        'tools.sessions.on': True,
        'tools.sessions.timeout': manage_config.cherrypy_session_timeout_chosen,
        'tools.sessions.storage_type': "file",
        'tools.sessions.storage_path': temp_sessions_dir,
        'tools.auth.on': True
    })

    mimetypes.types_map['.svg'] = 'image/svg+xml'
    mimetypes.types_map['.svgz'] = 'image/svg+xml'

    root_config = {
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '',
            'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
        },
        '/secure': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'partials',
        },
        '/images': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'images',
        },
        '/branding': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'branding',
        },
        '/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'css',
        },
        '/js': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'js',
        },
        '/fonts': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'fonts',
        },
        '/favicon.ico': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.abspath(os.path.join(os.path.dirname(__file__), '../images/favicon.ico')),
        },
        'tools.staticdir.content_types': {'svg': 'image/svg+xml'},
    }
    error_location = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) + '/404.html'
    cherrypy.config.update({'error_page.404': error_location})

    cherrypy.tools.auth = cherrypy.Tool('before_handler', manage_auth.check_auth)

    # Configure server with directories
    app_config = {
        '/':
            {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
        }
    cherrypy.tree.mount(manage_package.Packages(), '/api/packages', config=app_config)
    cherrypy.tree.mount(manage_repo.Repository(), '/api/repository', config=app_config)
    cherrypy.tree.mount(manage_proxy.Proxy(), '/api/proxy', config=app_config)
    cherrypy.tree.mount(manage_self_update.SelfUpgrade(), '/api/selfupgrade', config=app_config)
    cherrypy.tree.mount(manage_auth.Auth(), '/api/auth', config=app_config)
    cherrypy.tree.mount(manage_security.SecurityAutomation(), '/api/sa', config=app_config)
    cherrypy.tree.mount(manage_service.ServiceControl(), '/api/sc', config=app_config)
    cherrypy.tree.mount(manage_os_controls.OSControls(), '/api/osc', config=app_config)
    cherrypy.tree.mount(manage_usb.USB_API(), '/api/usb', config=app_config)
    cherrypy.tree.mount(manage_pro_upgrade.EnablePro(), '/api/pro', config=app_config)
    cherrypy.tree.mount(manage_os_update.OSUpdate(), '/api/osup', config=app_config)
    cherrypy.tree.mount(Server(), '/', config=root_config)
    cherrypy.tree.mount(manage_hac.HAC(), '/api/hac', config=app_config)
    cherrypy.tree.mount(manage_package.PackageInfo(), '/api/packageinfo', config=app_config)
    cherrypy.tree.mount(manage_mec.MEC_API(), '/api/mec', config=app_config)
    cherrypy.tree.mount(manage_auth.Session(), '/api/validate_session', config=app_config)
    cherrypy.tree.mount(manage_oem_branding.OemBranding(), '/api/oembranding', config=app_config)
    cherrypy.server.unsubscribe()

    # Do the following config file operations at the Main Process.
    # Worker Process will not deal with the config file in initialization work.
    config = manage_config.read_config_file()

    hdc_config = config.get('HDC', 'config')
    if hdc_config == 'False':
        my_logger.logger.debug('setting hdc')
        manage_config.HDCSettings.set_hdc_server_details()
        rsys = onetime_update.RSYSLOG()
        rsys.update_rsyslog()
        node = onetime_update.NODEPATH()
        node.update_path()

    secure_http = config.get('SecurityAutomation', 'secure_http')
    if secure_http == 'true':
        https_server = cherrypy._cpserver.Server()
        https_server.socket_port = 3092
        https_server._socket_host = "0.0.0.0"
        # Enable SSL
        https_server.ssl_module = 'builtin'
        https_server.ssl_certificate = "/etc/nginx/ssl/ssl-cert-snakeoil.pem"
        https_server.ssl_private_key = "/etc/nginx/ssl/ssl-cert-snakeoil.key"
        https_server.subscribe()

    else:
        http_server = cherrypy._cpserver.Server()
        http_server.socket_port = 80
        http_server._socket_host = '0.0.0.0'
        http_server.subscribe()

    # Do this after the config file operation above.
    # Submit work (initializatio) to worker process
    # Later, GUI's authentication request will check it.
    type_dict = {'type': manage_worker.worker_process_message_type_initialization,
                 'id': manage_worker.worker_process_internal_init_work_id}
    s_result = manage_worker.submit_work(work_type=type_dict, internal_work=True)
    if s_result['status'] == 'failure':
        my_logger.logger.error('Failed to submit work: ' + str(s_result))

    cherrypy.engine.subscribe('stop', server_stopping)

    cherrypy.engine.start()
    nginx_userDB = manage_nginx_userDB.ManageNginxUserDB()
    nginx_userDB.start_thread()
    cherrypy.engine.block()
    nginx_userDB.stop_thread()

    # finish worker process
    manage_worker.finish()


def shutdown_http_server():
    #   import __main__
    #   __main__.http_server.unsubscribe()
    cherrypy.engine.restart()
