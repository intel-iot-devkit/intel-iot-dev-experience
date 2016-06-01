# Copyright (c) 2016, Intel Corporation. All rights reserved.
# This file is licensed under the GPLv2 license.
# For the full content of this license, see the LICENSE.txt
# file at the top level of this source tree.

#Import this code module into the server like import hacGenerateReg
#And set end point generateHacRegCode = hacGenerateReg.HacGen()

import cherrypy
import os
import subprocess
import time
from datetime import datetime
import socket
from manage_auth import require

def HACGen():
    if isDeviceRegistered() and not(mustDoReregister()):
        return renderAlreadyRegistered()
    else:
        code = getNonExpiredPreexistingCode()
        if code == "":
            code = getNewCodeFromAppCloud(code)
        return renderNotRegistered(code)

def renderAlreadyRegistered():
    hacServerName = getHacServerName()
    vars = [hacServerName]
    output ="""<html lang="en">
        <link href="/css/dist/bootstrap.min.css" rel="stylesheet">
        <link href="/css/webfonts.css" rel="stylesheet">
        <link href="/css/dashboard.css" rel="stylesheet">
        <link href="/css/administration.css" rel="stylesheet">
        <link href="/css/global.css" rel="stylesheet">
        <head>
            <meta charset="utf-8">
            <title>HAC Registration</title>
            <meta name="description" content="Request if user want to re-register">
            <meta name="author" content="Intel">

            <link rel="stylesheet" href="css/styles.css?v=1.0">
            <script type="text/javascript">
                function gotoHelixAppCloud() {{
                    window.open("https://{0}/");
                }}
                function postbackForReregistration() {{
                    document.getElementById("reregister").value = "yes";
                    document.forms["hacForm"].submit();
                }}
            </script>
            <!-- <script src="http://"></script> -->
        </head>
        <body>
          <div class="row main admin-tools-body">
          <form method="get" id="hacForm" action="/api/hac" class="iot-panel">
		</br>
                <p>
                The device is already registered. Click this button unless re-registration is desired.</br>
		<button type="button" class="blue-button-sm" onclick="gotoHelixAppCloud();">Continue to App Cloud</button>
                </p>
                <p>
                Only click this button if re-registration is desired. Clicking this button will generate
                a new registration code and render the device unusable until registered again.</br>
                Note: Re-registration is required if proxy configuration has changed.</br>
                <button type="button" class="blue-button-sm" onclick="postbackForReregistration();">Register Again</button>
                </p>
                <p><input type="hidden" name="reregister" id="reregister" value="no"/></p>
          </form>
	  </div>
        </body>
        </html>""".format(*vars)
    return output

def renderNotRegistered(code):
    # Render HTML with the code in a text field
    hacServerName = getHacServerName()
    vars = [hacServerName, code]
    output ="""<html lang="en">
        <link href="/css/dist/bootstrap.min.css" rel="stylesheet">
        <link href="/css/webfonts.css" rel="stylesheet">
        <link href="/css/dashboard.css" rel="stylesheet">
        <link href="/css/administration.css" rel="stylesheet">
        <link href="/css/global.css" rel="stylesheet">
        <head>
            <meta charset="utf-8">
            <title>HAC Registration</title>
            <meta name="description" content="Gets HAC device registration code">
            <meta name="author" content="Intel">

            <link rel="stylesheet" href="css/styles.css?v=1.0">
            <script type="text/javascript">
                function gotoHelixAppCloud() {{
                    window.open("https://{0}/");
                }}
            </script>
            <!-- <script src="http://"></script> -->
        </head>
        <body>
          <div class="row main admin-tools-body">
          <form method="get" action="/api/hac" class="iot-panel">
                <p style="font-weight:bold;font-style:italic">
                Follow the steps below to register this device with App Cloud.</p>
                1. Please copy the registration code in the text box below to your clipboard (ctrl + c).</br>
		2. Then click the button to continue to Wind River Helix App Cloud.</br>
		3. In Wind River Helix App Cloud, create a new account or login with your existing account.</br>
		4. Click New Device and Register an existing device with the code you copied below.</br></br>
		Note: This code will expire after 20 minutes, so verify your email address and log back in at this time.</br>
		If you need a new code, simply come back to this page.  Always use the newest code you were given for registration.</br></br>
		<label>Unique ID</label>&nbsp;<input type="text" value="{1}" name="registrationCode" />
		</br>
		</br>
		<button type="button" class="blue-button-sm" onclick="gotoHelixAppCloud();">Continue to App Cloud</button>
                <input type="hidden" name="reregister" id="reregister" value="no"/>
          </form>
	  </div>
        </body>
        </html>""".format(*vars)
    return output

def isDeviceRegistered():
    try:
        setProxyEnvVar()
        data = subprocess.check_output(["registerTarget", "-i"])
        offset = data.find("not registered")
        if offset != -1:
            return False
        else:
            return True
    except:
        return False

def getNewCodeFromAppCloud(code):
    try:
        setProxyEnvVar()
        socksProxy = getSocksProxy()
        if socksProxy == "":
            data = subprocess.check_output(["registerTarget", "-n", "ANewDevice"])
        else:
            data = subprocess.check_output(["registerTarget", "-n", "ANewDevice", "-tap", socksProxy])
        # data = subprocess.check_output(["registerTarget", "-n", socket.gethostname()])
        offset = data.find("Device Registration Key:")
        code = data[offset+25:offset+30].rstrip()
        if code == "":
            code = "Error retrieving code from Helix App Cloud"
        else:
            writePreexistingCode(code, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
    except:
        code = "Error retrieving code from Helix App Cloud"
    restartHacService()
    return code

def getNonExpiredPreexistingCode():
    code = "" 
    try:
        regCodeFileName = "registrationCode.txt"
        if (os.path.isfile(regCodeFileName)):
            codeStr=""
            codeGenertionTimeStr=""
            regCodeFile = open(regCodeFileName )
            line = regCodeFile.readline()
            while line:
                if line.startswith("registration_code="):
                    parts = line.split("=")
                    if len(parts) > 1:
                        codeStr = parts[1]
                        codeStr = codeStr.replace('\n', '')
                if line.startswith("code_generation_time="):
                    parts = line.split("=")
                    if len(parts) > 1:
                        codeGenerationTimeStr = parts[1]
                        codeGenerationTimeStr = codeGenerationTimeStr.replace('\n', '')
                line = regCodeFile.readline()
            regCodeFile.close()
            if codeGenerationTimeStr != "":
                # compare now to codeGeneratonTimeStr to see if it is within 20 minutes
                utcNow = datetime.utcnow()
                codeGenerationTime = datetime.strptime(codeGenerationTimeStr, "%Y-%m-%d %H:%M:%S")
                if ((utcNow > codeGenerationTime) and (utcNow - codeGenerationTime).total_seconds() < 1200):
                    code = codeStr
    except:
        code = ""
    return code

def writePreexistingCode(code, codeGenerationTime):
    # Write registration code and code generation time into file
    try:
        regCodeFileName = "registrationCode.txt"
        regCodeFile = open(regCodeFileName, 'w')
        regCodeFile.write("registration_code=" + code + "\n")
        regCodeFile.write("code_generation_time=" + codeGenerationTime + "\n")
        regCodeFile.close()
    except:
        return
    return

def retrievePreexistingCode():
    # Retrieve registration code and code generation time from file
    code = ""
    codeGenerationTime = ""
    try:
        regCodeFileName = "registrationCode.txt"
        if (os.path.isfile(regCodeFileName)):
            regCodeFile = open(regCodeFileName)
            line = regCodeFile.readline()
            while line:
                if line.startswith("registration_code="):
                    parts = line.split("=")
                    if len(parts) > 1:
                        code = parts[1]
                        code = code.replace('\n', '')
                if line.startswith("code_generation_time="):
                    parts = line.split("=")
                    if len(parts) > 1:
                        codeGenerationTime = parts[1]
                        codeGenerationTime = codeGenerationTime.replace('\n', '')
                line = regCodeFile.readline()
            regCodeFile.close()
    except:
        code = ""
        codeGenerationTime = ""
    vars = [code, codeGenerationTime]
    return vars

def getHTTPSProxy():
    HTTPSproxy = ""
    # If there is one get the https_proxy from the Developer Hub proxy settings file
    try:
        envFileName = "/var/www/www-repo-gui/proxy_env"
        if (os.path.isfile(envFileName)):
            envFile = open(envFileName)
            line = envFile.readline()
            while line:
                if line.startswith("https_proxy="):
                    parts = line.split("=")
                    if len(parts) > 1:
                        HTTPSproxy = parts[1]
                        HTTPSproxy.replace('\n', '')
                line = envFile.readline()
            envFile.close()
    except:
        HTTPSproxy = ""
    return HTTPSproxy

def getSocksProxy():
    socksProxy = ""
    # If there is one get the socks_proxy from the Developer Hub proxy settings file
    try:
        envFileName = "/var/www/www-repo-gui/proxy_env"
        if (os.path.isfile(envFileName)):
            envFile = open(envFileName)
            line = envFile.readline()
            while line:
                if line.startswith("socks_proxy="):
                    parts = line.split("=")
                    if len(parts) > 1:
                        socksProxy = parts[1]
                        socksProxy.replace('\n', '')
                        if socksProxy.startswith("http"):
                            parts = socksProxy.split("/")
                            if len(parts) > 2:
                                socksProxy = parts[2]
                line = envFile.readline()
            envFile.close()
    except:
        socksProxy = ""
    return socksProxy

def setProxyEnvVar():
    # Get the https_proxy, if there is one, from the Developer Hub proxy settings file
    # and export it
    HTTPSproxy=getHTTPSProxy()
    if HTTPSproxy != "":
            os.environ["HTTPS_PROXY"] = HTTPSproxy

def getHacServerName():
    hacServer = ""
    try:
        fileName = "/etc/default/hacServer.cfg"
        if (os.path.isfile(fileName)):
            f = open(fileName)
            try:
                hacServer = f.read()
                hacServer = hacServer.replace('\n', '')
            except:
                hacServer = ""
            f.close()
    except:
        hacServer = ""
    return hacServer

def mustDoReregister():
    try:
        doReregister = cherrypy.request.params.get("reregister")
        if doReregister == "yes":
            return True
        else:
            return False
    except:
       return False

def restartHacService():
    subprocess.call(["systemctl restart hac.service"], shell=True)


@require()
class HAC(object):
    exposed = True

    def GET(self, **kwargs):
        return HACGen()
