/*
 * Copyright (c) 2016 Intel Corporation.
 *
 * MIT LICENSE
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 * LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
//--------------------------------------------------------------------------------------------------
// azuresb-rx.js
//
// Node application to subscrite to an Azure ServiceBus (SB) topic to get notify
// The SB is specified by the the encrypted SAS stored in <sbconfig.json>
//
// Command Syntax:
//		node azuresb-rx.js [topic-name] [-d#]
//			[topic-name]	: the topic to subscribe for event
//			[-d#]			: debug level [0..3]
//
// The device uses its serial number as the topic to subscribe to the
// telemetry data sent by the GW to the ServiceBus
//
// SB Limitation:
// - number of concurrent connection to a SB service is 1000
// - number of topics is 10,000
// - max topic message size is 245KB, name is max at 50chars
// - max subscription to topic is 2000
//
// See Azure Service Bus documentation for more information
// 		http://azure.github.io/azure-sdk-for-node/azure-sb/latest/ServiceBusService.html
//
//  ver 1.0 - 02/02/2016 - nnm
//  	Initial version
//--------------------------------------------------------------------------------------------------

"use strict"

// global debug
var _debug = 0;

var azure = require('azure');
var sbconfig=require('./sbconfig.json');

//var macaddress = require('macaddress');

// IMPORTANT: Node 0.10.39 is so old that synchronized execution is not available
// This code requires to use the'shelljs' and async for flow synchronization
require('shelljs/global');

// Stored Azure cloud credentials in encrypted JSON. App decrypts the data in runtime
// Nodejs encryption with CTR and key  - See azuresb_crypto.js
var crypto = require('crypto'),
    algorithm = 'aes-256-ctr',	 		// algorithm is one of '$ openssl list-cipher-algorithms'
    keypw = process.env.SB_CONFIG_PK; 	// see azuresb_crypto.js

if (!keypw) {
	console.log('ERR - Missing the environment variable SB_CONFIG_PK');
	exit(1);
}

// Turn off - client sends self signed certificate to server with https rejection
process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

//-------------------------------- MAIN -------------------------------------------------------------
var devTopic 		= "No-Topic";  		// default
var sbSubscriber 	= 'MI-SB-Receiver';

if (!sbconfig) {
   console.log('ERR - Unable to find or load <sbconfig.json> file');
   process.exit(1);
}
// check for connection string the the Azure Service Bus
if (!sbconfig || !sbconfig.sbConnectionStr) {
   console.log('ERR - Unable to find or load <sbconfig.json> file');
   process.exit(1);
}

// process optional arguments. Check for _debug flag [-d] - argv[].length > 3.
if (process.argv.length > 2) {
	// test the first char for the '-' flag for [-d#]
	if (process.argv[2][0] == '-') {
		setDebug(process.argv[2]);

		// autogenerate the topic = [devTopic]
		getDeviceTopic();
	}
	else
	{
		// not a debug flag - it is the [topic-name]
		devTopic =  process.argv[2];
		// Min MAC addr = 12 digits
		if (devTopic.length < 12) {
			console.log('ERR - Invaliad device topic #: ' + sbTopic);
		}

		// check for debug flag after the [topic#]@3
		if (process.argv.length > 3)
			setDebug(process.argv[3]);
	}
} else {
	// Default get the device ID as the topic = [devTopic]
	getDeviceTopic();
}

// create the SB object - decrypt the SAS string first
if (_debug > 1) console.log('DBG - sbConnectionStr: ' + decrypt(sbconfig.sbConnectionStr, keypw));

var serviceBusObj = azure.createServiceBusService(decrypt(sbconfig.sbConnectionStr, keypw));
if (!serviceBusObj) {
	console.log('ERR - Unable to create the Azure ServiceBus service for receiving');
	process.exit(1);
}

if (_debug > 0) console.log('DBG - topic: ' + devTopic + ' sub: ' + sbSubscriber);

// subscribe to the SB:topic to get the messages notification
createSubscription(devTopic, sbSubscriber);
receiveMessages(devTopic, sbSubscriber);

// done

//====================================== FUNCTIONS ==================================================

// function to strip chars from a string
function stripchars(string, chars) {
	return string.replace(RegExp('['+chars+']','g'), '');
}

// function to create the SB topic from device ID
function getDeviceTopic() {
	// getthe device serial number
	// Replace macaddress with shell command for synchronization - non OS portable
	var cmd = "ifconfig | grep eth0 | awk '{print $5}'";
	// Use shelljs exec()
	var outStr = exec(cmd, {silent:true}).output;

	// strip the ':' from the mac to create the serial # - trim off \n and space
	devTopic = stripchars(outStr, ':').trim();

	if (_debug > 0) console.log('DBG - Device Topic : ' + devTopic);
}

// function to create the subscription to the input topic
function createSubscription(topic, subscriber) {

	// First try to get the subscription - if fail, create it
	serviceBusObj.getSubscription(topic, subscriber, function(err) {
		if (err) {
			// Create subscriptions
			serviceBusObj.createSubscription(topic, subscriber, function (err) {
				if (err) {
					console.log('ERR - Create SB subscription failed @Topic: ' + topic + ' - ' + err);
					process.exit(1);  // terminate process
				}
				// success
				if (_debug > 0)
					console.log('DBG - Create subscriber successful ' + subscriber);
			});
		}
		if (_debug > 0)
			console.log('DBG - Get subscriber successful ' + subscriber);
	});
}

// function to receive message subscribed from the SB:Topic
function receiveMessages(topic, subscriber) {

	// timeout waiting for msg in 15 sec (integer)
	var opts = { "timeoutIntervalInS" : 15 };

    // Receive the messages for the subscription.
    serviceBusObj.receiveSubscriptionMessage(topic, subscriber, opts, function (error, message) {
        if (error) {
            console.log('WRN - Receive SB msg failed - ' + error);
        } else {
			// get the message body and output the data
            var msgBody = JSON.parse(message.body);
            if (_debug > 0)
				console.log('DBG - Receive SB msg: ' + JSON.stringify(msgBody) + ' @Topic:' + topic
						+ ':' + subscriber);
			// Output to console the message data
			console.log(msgBody.Data);
        }
    });
}

// helper to set debug level
function setDebug(dbgLevel) {
	// set the debug level
	switch (dbgLevel) {
		case "-d1":
		    _debug = 1;
		    break;
		case "-d2" :
			 _debug = 2;
			 break;
		case "-d3" :
			 _debug = 3;
			 break;
	 }

	 console.log('Debug level: '+ _debug);
};

// function to decrypt text
function decrypt(text, key){
  var decipher = crypto.createDecipher(algorithm, key);
  var dec = decipher.update(text,'hex','utf8');

  dec += decipher.final('utf8');
  return dec;
};

// EOF
