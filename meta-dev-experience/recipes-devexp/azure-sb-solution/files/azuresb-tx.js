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
// azuresb-tx.js
//
// Node application to send a message data to the Azure ServiceBus (SB)
// specified by the the encrypted SAS stored in <sbconfig.json>
//
// Command Syntax:
//		node azuresb-tx.js <data> [-d#]
//			<data>		: any topic data value
//			[-d#]		: debug level [0..3] - 1: simple, 2 : topic
//
// The device uses its serial number as the topic to support multiple
// devices send data to the ServiceBus Topic.
//
// The topic path is http://<sb namespace>/topic/<sub-topic>
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

// macaddress cannot be used until upgrade to Node ^4.x
// var macaddress = require('macaddress');

// IMPORTANT: Node 0.10.39 is so old that synchronized execution is not available
// This code requires to use the'shelljs' and async for flow synchronization
require('shelljs/global');

// Stored Azure cloud SAS credentials in encrypted JSON. App decrypts the data in runtime
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
var devTopic = "MITelemetryTopic";  // default

// Check CMD syntax - check for input argv[] required param
if (process.argv.length < 3) {
	console.log('ERR - Command Syntax error, missing argument <data-value>');
	displayCmdHelp();
	process.exit(0);
}

// check for connection string the the Azure Service Bus
if (!sbconfig || !sbconfig.sbConnectionStr) {
   console.log('ERR - Unable to find or load <sbconfig.json> file');
   console.exit(1);
}

if (sbconfig.sbConnectionStr == 'ERR NO CONNECTION') {
   console.log('ERR - The <Azure ServiceBus connection string> is invalid');
   process.exit(1);
}

// get the input <data>  & [-d#] arguments - index from 0
if (!process.argv[2]) {
   console.log('ERR - Missing input <data>');
   process.exit(1);
}
var msgData = process.argv[2];  // msg data

if (process.argv.length > 3) {
   // test the first char for the '-' flag, the optional [-d#]
   if (process.argv[3][0] == '-') {
	   setDebug(process.argv[3]);
   }
}

// create the SB service object
if (_debug > 1) console.log('DBG - sbConnectionStr: ' + decrypt(sbconfig.sbConnectionStr, keypw));

var serviceBusObj = azure.createServiceBusService(decrypt(sbconfig.sbConnectionStr, keypw));
if (!serviceBusObj) {
   console.log('ERR - Unable to create the Azure ServiceBus service for Tx data');
   process.exit(1);
}

if (_debug > 0) {
	console.log('DBG - ServiceBus object created');
	// output service Bus info
	if (_debug > 1) OutputSBInfo();
}

// Create the SB Topic
var topicOptions = {
    "DefaultMessageTimeToLive" : "PT24H",				// message TTL in Topic is 24H
    "EnableDeadLetteringOnMessageExpiration" :  true 	//
};
createTopic(topicOptions);

// Send the message as JSON package for the Topic
var sbTopicMsg = {"Data": msgData,"Timestamp": String(Date.now()) };

sendMessage(JSON.stringify(sbTopicMsg));

console.log('send to Azure SB : ' + msgData);

// done

//-------------------------------- FUNCTIONS ------------------------------------------------------

// function to strip chars from a string
function stripchars(string, chars) {
  return string.replace(RegExp('['+chars+']','g'), '');
}

// create a topic for the gateway
function createTopic(opts) {
	// Get the device topic
	getDeviceTopic();

    // Create a new topic if not existed.
    serviceBusObj.createTopicIfNotExists(devTopic, opts, function (error) {
		// ignore error 409 - topic existed
		if (error && (error.statusCode != 409)) {
			console.log('ERR - Failed to create topic for device' + devTopic + ' error' + error);
		    return;
        }
    });

	// topic existed
    if (_debug > 0) console.log('DBG - Topic created or existed :' + devTopic);
}

// function to send the message
function sendMessage(message) {

	if (_debug > 0) console.log('DBG - sendMessage : '+ devTopic);

    // Send messages for subscribers
    serviceBusObj.sendTopicMessage(devTopic, message, function(error) {
        if (error) {
            console.log('ERR - Send Message: ' + error);
        }
        else {
            if (_debug > 0) console.log('DBG - Message : ' + message);
        }
    });
}

// function to create the SB topic from the device ID
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

// command help text
function displayCmdHelp() {
	// show the cmd syntax
	console.log('CMD Syntax:');
	console.log('	node azuresb-tx.js <data> [-d#]');
	console.log('		<data>		: the data value to be sent to SB');
	console.log('		[-d#]		: debug ON - level [1..3]');
};

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

// function to output the SB information
function OutputSBInfo() {
	// get all topics
	serviceBusObj.listTopics(function(error, result, response) {
		if (error) {
			console.log(error);
			return;
		}

		// dump only the match topic
		if (_debug > 1) {
			// search for the right topic to output
			for (var i in result) {
				// DBG - console.log('Topic Name :' + result[i].TopicName);
				if (result[i].TopicName == devTopic) {
					console.log('DBG - * SB Topic : ' + JSON.stringify(result[i], null, 3));
					return;
				}
			}
		}
		// dump every topics in SB
		console.log('DBG - * Service Bus : ' + JSON.stringify(result, null, 3));

	});
}

// function to encrypt text
function encrypt(text, key){
	var cipher = crypto.createCipher(algorithm, key);
	var crypted = cipher.update(text,'utf8','hex');

	crypted += cipher.final('hex');
	return crypted;
};

// function to decrypt text
function decrypt(text, key){
  var decipher = crypto.createDecipher(algorithm, key);
  var dec = decipher.update(text,'hex','utf8');

  dec += decipher.final('utf8');
  return dec;
};

// EOF
