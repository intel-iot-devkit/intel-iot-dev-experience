# logging

We use logging.conf configuration file to config Python logging.
Check the following for background information:
    https://docs.python.org/2/howto/logging.html,
    https://docs.python.org/2/library/logging.config.html#logging-config-api
    https://docs.python.org/2/howto/logging-cookbook.html


## CherryPy Logging

Check http://docs.cherrypy.org/en/latest/basics.html#logging for details.
Modify [logger_cherrypy.access] and [logger_cherrypy.error] in logging.conf file to configure.

## How to use

logging.conf file is read at __init__.py file in logging_helper package.

Most of existing codes use [logger_backend_general] in logging.conf file.

When you want to do logging in your code, utilize tools.logging_helper.logging_helper.Logger.
Refer to other existing files about how to use it.
If you want to use different configuration, you can define it in logger.conf file and use the logger name you defined.

After changing the logging.conf file, restart the iot-dev-hub.service to read the new file.





