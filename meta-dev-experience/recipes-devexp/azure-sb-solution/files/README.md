#### README

This is the README for the azure-sb-solution. It provides instruction to setup the Azure SDK for node.js
and connect the device to an Azure ServiceBus to send and receive telemetry data as Topics.


rev 1.1 - 02/10/2016 - Nghia Nguyen
	add crypto support for Azure SB SAS connection string
	add proxy support with Azure.ServiceClient and environment variable http_proxy

rev 1.0 - 02/07/2016 - Nghia Nguyen
	initial release


#### Introduction

The Azure ServiceBus solution consists of the followings:

	1. azuresb_tx.js		- app to send telemetry data to an Azure Service Bus Topic
	2. azuresb_rx.js       	- app to receive msg data for a subscribed Topic
	3. memused.js	       	- app to report current memory used (KB))
	4. sbconfig.json     	- Encrypted SB SAS credentials
	5. package.json    	   	- The solution NPM package

	The master encryption key MUST BE set in the environment variables as (/etc/environment)

	$ export SB_CONFIG_PK=6e6e6d2d323031352d686463

This app encrypted the HDC configuration - archive for development only
	1. azuresb_crypto.js	- the crypto app to encrypted the sbcfg_origin.json credential
	2. sbcfg_origin.json 	- The original SB credential - not to install

##### Requirements

* install node.js ver ^0.6.15

* The azure-sb-solution required the following libraries:
	- azure  	v0.10.6
	- shelljs
	- macaddress
	- crypto

* Encrypting the Azure SB SAS (Shared Access Signature)
	- Get the Azure ServiceBus SAS Connection String and update the [sbcfg_origin.json]
	- Run the azuresb_crypto.js to generate the [sbconfig.json] file to deploy with the solution
	- Create an environment variable $SB_CONFIG_PK

* Install these modules (preferred globally)

  $ npm install azure
	- See the [/azure/Documentation] folder for the SDK testing

  $ npm install shelljs

* copy the [azure-sb-solution.tar.gz] to the target [/home/gwuser/azure-sb-solution] and install

  $ tar xvf azure-sb-solution.tar.gz
  $ npm install

##### Design Notes

1. The solution contained these files:
	* azuresb-tx.js :
		The Azure service-bus client to send telemetry data. The device ID is used as the SB/Topic.

	* azuresb_rx.js :
		The Azure service-bus client to receive topic data.  It uses the device ID as SB/Topic to
		subscribe to receive data from the Azure SB service.

	* sbconfig.json :
		The Azure Service-Bus configuration connection

	* azure-sb-txrx-nr-sample.json :
		Node_RED flow sample using the tx and rx app

2. The command syntax are:
   TX Command Syntax:
		node azuresb-tx.js <data> [-d#]
			<data>		: any topic data value
			[-d#]		: debug level [0..3] - 1: simple, 2 : topic

   RX Command Syntax:
		node azuresb-rx.js [topic-name] [-d#]
			[topic-name]	: the topic to subscribe for event
			[-d#]			: debug level [0..3]

3. The memused.js provides the current system memory consumption as telemetry data

##### Run TX/RX apps on command-line

* Get an Azure SB connection string from a SB service
  - create SB following this instruction - https://azure.microsoft.com/en-us/services/service-bus/
  - step-by-step creating a SB service
	https://azure.microsoft.com/en-us/documentation/articles/service-bus-dotnet-how-to-use-topics-subscriptions/

* Open a terminal windows, navigate to [/home/gwuser/azure-sb-solution/]

  $ node azuresb-tx.js <data>

	- use [-d#] for debugging

* Open a new terminal window, navigate to [/home/gwuser/azure-sb-solution]
  $ node azuresb-rx.js

	- use [-d#] for debugging

  The app should return the msg sent in by the azuresb-tx app.

##### Run Node-red

* Run node-red on the target

* [Optional] open a new terminal, run node-red

   $ $home/usr/lib64/node_modules/.bin/node-red

* In the Node_RED window, import the content of [azure-sb-txrx-nr-sample.json]
	into a new workspace the node-red IDE and deploy.

  - The flow reports the current system memory used to Azure SB/topic and retrieve it back
  - Both apps run at 10sec interval

##### Proxy Handling

* The azuresb-tx and rx apps use the Azure SDK ServiceClient class which automatically setup
  proxy using the environment variable HTTP_PROXY setting.

# eof
