import os

class RSYSLOG(object):
    """Update log file to reduce journal entries
    """
    def __init__(self):
        self.__update_required = True
        self.__file = '/etc/rsyslog.conf'
        self.__bk_file = '/etc/rsyslog.conf.bk'
        self.__update = '''# Filtering of unwanted messages\n#\n:msg, contains, "Error: Serialport /dev/ttyRH-USB not open." Stop\n\n#\n#Set the default permissions\n'''

    def update_rsyslog(self):
        try:
            os.rename(self.__file, self.__bk_file)
        except:
            pass
        with open(self.__bk_file, 'r') as infile, open(self.__file, 'w+') as ofile:
            for line in infile:
                if 'Serialport /dev/ttyRH-USB not open' in line:
                    self.__update_required = False
                if 'Set the default permissions' in line and self.__update_required == True:
                    ofile.write(self.__update)
                else:
                    ofile.write(line)

class NODEPATH(object):
    """Update NODE_PATH environment variable
    """
    def __init__(self):
        self.__update_required = True
        self.__file = '/etc/profile'
        self.__bk_file = '/etc/profile.bk'
        self.__update = '''NODE_PATH=/usr/lib/node_modules\nexport NODE_PATH \n\numask 022\n'''

    def update_path(self):
        try:
            os.rename(self.__file, self.__bk_file)
        except:
            pass
        with open(self.__bk_file, 'r') as infile, open(self.__file, 'w+') as ofile:
            for line in infile:
                if 'NODE_PATH' in line:
                    self.__update_required = False
                if 'umask 022' in line and self.__update_required == True:
                    ofile.write(self.__update)
                else:
                    ofile.write(line)
