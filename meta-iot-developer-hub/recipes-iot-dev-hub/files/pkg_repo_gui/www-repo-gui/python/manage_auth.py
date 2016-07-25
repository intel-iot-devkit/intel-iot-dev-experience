#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

# from cherrypy._cpcompat import copyitems
import cherrypy
import json
import pexpect
import pwd
from cgi import escape
from tools import logging_helper

SESSION_KEY = '_cp_username'


def check_auth(*args, **kwargs):
    """ A tool that looks in config for 'auth.require'.

    If found and it is not None, a login is required and
    the entry is evaluated as a list of conditions that the user must fulfill.
    """
    log_helper = logging_helper.logging_helper.Logger()
    log_helper.logger.debug(str(cherrypy.request.config))
    conditions = cherrypy.request.config.get('auth.require', None)
    log_helper.logger.debug('conditions are ' + str(conditions))

    target_method = False
    if '/api/sa' in str(cherrypy.url()):
        if 'POST' == str(cherrypy.request.method):
            target_method = True
    if '/api/osup' in str(cherrypy.url()):
        if 'POST' == str(cherrypy.request.method):
            target_method = True
    if '/api/pro' in str(cherrypy.url()):
        if 'POST' == str(cherrypy.request.method):
            target_method = True
    if target_method:
        pass  # do nothing for now....
        # log_helper.logger.error('XXXXXXXXX   Is Target  XXXXXXXXXXXXXXXX!!!')

    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        log_helper.logger.debug('username is ' + str(username))
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    raise cherrypy.HTTPError("401 Unauthorized")
        else:
            raise cherrypy.HTTPError("401 Unauthorized")


def require(*conditions):
    """A decorator that appends conditions to the auth.require config variable.
    """
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate
    

def authenticate_user(username, password):
    """ Try to authenticate user.

    Used in login.html for user authentication as root to gain access to index.html
    for package management and administration.

    Args:
        username (str):
        password (str):

    Returns:
        dict:
    """

    log_helper = logging_helper.logging_helper.Logger()
    username = escape(username, True)
    password = escape(password, True)
    try:
        child = pexpect.spawn('login %s' % username)
        child.expect('Password:')
        child.sendline(password)
        result = child.expect(['Login incorrect', username])
        child.close()
    except Exception as err:
        log_helper.logger.error('Error authenticating. Reason: ' + str(err))
        result = 0

    if result == 0:
        log_helper.logger.debug('Authentication failed.')
        response = ({
            'status': "failure"
        })
    else:
        log_helper.logger.debug('Authentication succeeded.')
        response = ({
            'status': "success"
        })
        cherrypy.session.regenerate()
        cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
    return response


def set_password(username, current_password, new_password):
    """ Change the password of root

    Args:
        username (str): User to assign new password to
        current_password (str): Current password
        new_password (str): New password
    Returns:
        str: json string.
    """
    response = ({
        'status': "failure"
    })    
    log_helper = logging_helper.logging_helper.Logger()
    auth_check = authenticate_user(username, current_password)
    if auth_check['status'] == 'failure':
        response['error'] = 'Error: Authorization Failed'
        log_helper.logger.debug('response is ' + str(response))
        return json.dumps(response)

    pwd.getpwnam('%s' % username)
    child = pexpect.spawn('passwd %s' % username)
    option = child.expect(['Enter new UNIX password:', pexpect.TIMEOUT])
    if option == 0:
        # User is root: "Enter new UNIX password:"
        child.sendline(new_password)
        child.expect('Retype new UNIX password:')
        child.sendline(new_password)
        child.expect('passwd: password updated successfully')
        child.close()
        response['status'] = 'success'
    elif option == 1:
        child.sendline(current_password)
        validity = child.expect(['Enter new UNIX password:', 'password unchanged'])
        if validity == 0:
            # Current password correct
            child.sendline(new_password)
            child.expect('Retype new UNIX password:')
            child.sendline(new_password)
            child.expect('passwd: password updated successfully')
            child.close()
            response['status'] = 'success'
        elif validity == 1:
            # Current password incorrect
            response['status'] = 'failure'
            response['error'] = "Invalid password for user '%s'" % username
    return json.dumps(response)

  
def logout_user():
    sess = cherrypy.session
    username = sess.get(SESSION_KEY, None)
    sess[SESSION_KEY] = None
    if username:
        cherrypy.request.login = None
    response = ({
        'status': "success"
    })        
    return json.dumps(response)


class Auth(object):
    exposed = True

    def POST(self):
        return_result = {'status': 'failure', 'init_in_progress': False}
        header_cl = cherrypy.request.headers['Content-Length']
        cl_content = cherrypy.request.body.read(int(header_cl))
        kwargs = json.loads(cl_content)

        first_pass = False

        if 'do_auth' not in kwargs:
            auth_check = authenticate_user(kwargs['username'], kwargs['password'])
            if auth_check['status'] == 'success':
                first_pass = True
            else:
                pass
        else:
            if kwargs['do_auth'] == 'False':
                first_pass = True
            else:
                auth_check = authenticate_user(kwargs['username'], kwargs['password'])
                if auth_check['status'] == 'success':
                    first_pass = True
                else:
                    pass

        if first_pass:  # authentication worked
            return_result['status'] = 'success'
            # authenticated, check to see if the worker process is done.
            import manage_worker  # keep this one here
            type_dict = {'type': manage_worker.worker_process_message_type_initialization,
                         'id': manage_worker.worker_process_internal_init_work_id}
            worker_result = manage_worker.retrieve_work_result(work_type=type_dict)
            if worker_result['status'] == 'success':
                return_result['init_in_progress'] = False
            else:
                if worker_result['in_progress']:
                    return_result['init_in_progress'] = True
                else:
                    # We cannot retrieve the work result of the initialization.
                    # Some other request may already read it and then deleted it.
                    # so treat it as fine.
                    return_result['init_in_progress'] = False
        else:  # authentication failed
            return_result['status'] = 'failure'
        return json.dumps(return_result)

    def PUT(self, **kwargs):
        header_cl = cherrypy.request.headers['Content-Length']
        cl_content = cherrypy.request.body.read(int(header_cl))
        kwargs = json.loads(cl_content)
        return set_password(kwargs['username'], kwargs['password'], kwargs['newpassword'])

    def GET(self, **kwargs):
        return logout_user()

@require()        
class Session(object):
    exposed = True  
    def POST(self): 
        response = ({
            'status': "success"
        })     
        return json.dumps(response)
