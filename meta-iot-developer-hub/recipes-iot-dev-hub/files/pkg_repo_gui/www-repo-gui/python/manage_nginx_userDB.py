import os.path, time, re
import threading
from tools import logging_helper

class ManageNginxUserDB():
    def __init__(self):
        self.__stop = False
        self.__log_helper = logging_helper.logging_helper.Logger()

    def syncronize_nginx_user_db(self,forcedUpdate=False):
        p='/etc/shadow'
        pmt = os.path.getmtime(p)
        n='/etc/nginx/nginx_passwd'
        nmt = os.path.getmtime(n)
        a = [];
#        print 'p',time.ctime(pmt),'>',time.ctime(nmt),'np'
        if pmt > nmt or forcedUpdate:
            regx = re.compile(r'^([^:]+:\$6\$[^:]+):')
            with open(p,'r') as f:
                while True:
                    ll=f.readline()
                    if ll == '': break
                    m = regx.match(ll)
                    if m:
                        a.append(m.group(1)+'\n')
            with open(n,'w') as of:
                for ll in a:
                    of.write(ll)
            self.__log_helper.logger.debug("Nginx User DB updated")        

    def periodic_thread(self):
        if not self.__stop:            
            threading.Timer(10.0, self.periodic_thread).start()
            self.syncronize_nginx_user_db()

    def start_thread(self):
        self.__log_helper.logger.debug("Starting ManageNginxUserDB thread")
        self.syncronize_nginx_user_db(True)
        self.periodic_thread()

    def stop_thread(self):
        self.__log_helper.logger.debug("Stopping ManageNginxUserDB thread")
        self.__stop = True


