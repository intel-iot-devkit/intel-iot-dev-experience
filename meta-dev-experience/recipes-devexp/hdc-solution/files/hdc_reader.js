/*
 * Copyright (c) 2015 Intel Corporation.
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

//-------------------------------------------------------------------------------------------------------------- 
//
// HDC_READER.JS - An HDC Server Data Access App
// 
//	1. Use the hdc_restapi to perform HDC cloud access with HTTPS://
//	2. Call FindOne API to get the systemId
//	3. Call findCurrentValue to get the current CPU_TEMP value
//
//  Command Syntax:
//		node hdc_reader <data-name> [deviceSerial#] [-d#]
//			<data-name>   	: the name data item value stored in HDC cloud
//			[deviceSerial#] : the gateway device serial number (MAC addr)
//			[-d#] 			: debug ON, # = debug level {d1: JSON, -d2: JSON+XML, -d3: Proxy}
// 
//  ver 1.9 - 01/20/16 - nnm
//		update hdc_reader to read device serial # by default if one is not specified
//		replace xml2json with xml2js to fix node-xpat lib crashed when upgrade to newer node (^0.12.9 | ^4.0.x)
//		add -d# to support debug level
//		add crypto to encrypt/decrypt HDC config data - pre-encryted 'hdc_config.json' file.
//		add Nodejs TLS rejects self-signed certificate - DEPTH_ZERO_SELF_SIGNED_CERT	
//
//	ver 1.8 - 12/02/15 - nnm
//		add manual proxy handler for HDC
//		added back modelNumber for the HDC findone() API
//
//	ver 1.7 - 11/29/15 - nnm
//		add -d for debugging and proxy handler
//
//  Ver 1.6 - 11/25/15 - nnm
//		added errors handling
//
//  Ver 1.5 - 11/23/15 - nnm
//  	production release    
//-------------------------------------------------------------------------------------------------------------- 
// global debug
var _debug = false;  

// IMPORTANT: Node 0.10.39 is so old that synchronized execution is not available
// This code requires to use the'shelljs' and async for flow synchronization
require('shelljs/global');

// HDC REST API module
var hdc_restapi = require('./hdc_restapi');

// Turn off - client sends self signed certificate to server with https rejection 
process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";


// Stored HDC cloud credentials in encrypted JSON. App decrypts the data in runtime 
// Nodejs encryption with CTR and key  - See hdc_crypto.js 
var crypto = require('crypto'),
    algorithm = 'aes-256-ctr',	 		// algorithm is one of '$ openssl list-cipher-algorithms'			
    keypw = process.env.HDC_CONFIG_PK; 	// see hdc_crypto.js 
if (!keypw) {
	console.log('ERR - Missing the environment variable HDC_CONFIG_PK');
	exit(1);
} 
 
// load the encrypted HDC config data    
var hdc_enc_config = require('./hdc_config.json');
if (!hdc_enc_config) {
	console.log('ERR - Missing hdc_config.json file');
	process.exit(1);		
}

// Decrypt the HDC config data to use in app
var hdchost 		= decrypt(hdc_enc_config.hdchost); 
var authStr	 		= decrypt(hdc_enc_config.authStr);
var devhdcmodel 	= decrypt(hdc_enc_config.devhdcmodel); 

// BDG - console.log('Decrypted hdchost: ' + hdchost);
// DBG - console.log('Decrypted authStr: ' + authStr);
// DBG - console.log('Decrypted devhdcmode: ' + devhdcmodel);

var api_findone_path = '/services/v2/rest/asset/findOne?' + authStr;
var api_getdata_path = '/services/v2/rest/dataItem/findCurrentValues?' + authStr;

// REST API input JSON - note: the default <data-name> is used in hdc-send-data app
var api_findone_data   = {"serialNumber":"ERROR Input_argv[]-###", "modelNumber": devhdcmodel};
var api_findvalue_data = {"name":"default-data", "assetId":"ERROR assetId read-from-hdc"}; 

// check for input argv[] required param 
if (process.argv.length < 3) {
	console.log('ERR - Command Syntax error, missing argument <data-name>');
	displayCmdHelp();
	process.exit(0);		
}

// fill in the data-name from input argument - note: argv[0] : 'node'
if (!process.argv[2]) {
	console.log('ERR - Invalid <data-name> argument');
	process.exit(0);		
}	
api_findvalue_data['name'] =  String(process.argv[2]);

// #1 - process the device serial number	
// Replace macaddress with shell command for synchronization - non OS portable			
var cmd = "ifconfig | grep eth0 | awk '{print $5}'";
// Use shelljs exec()
var outStr = exec(cmd, {silent:true}).output; 

// strip the ':' from the mac to create the serial # - trim off \n and space
var devID = stripchars(outStr, ':').trim();
api_findone_data.serialNumber = devID;	

// #2 - process cmd-line input
// process optional arguments. Check for _debug flag [-d] - argv[].length > 3.
if (process.argv.length > 3) {
   // test the first char for the '-' flag, the optional [device serial #]
   if (process.argv[3][0] == '-') {
	   setDebug(process.argv[3]);
   } 
   else
   {
	   // DBG - console.log('process argv[3] = ' + process.argv[3]);
	   // not a debug flag - it is the device serial #	
	   api_findone_data['serialNumber'] =  String(process.argv[3]);
	   // Min MAC addr = 12 digits
	   if (api_findone_data['serialNumber'].length < 12) {
		  console.log('WRN - Invaliad device serial #: ' + api_findone_data.serialNumber);
	   }
	   // check for debug flag after the [deviceSerial#]@3 
	   if (process.argv.length > 4) 
			setDebug(process.argv[4]);
   }
}

if (_debug > 0 && _debug < 3) 
	console.log('* api_findone_data:'+ JSON.stringify(api_findone_data));
	
// Call FindOne API to get the device Asset-id
hdc_restapi.request('https',
	hdchost,
	api_findone_path,						// REST API Path
	api_findone_data,						// REST API POST(Input Data)
	function (err, respObj) {
		// if no error - process result
		
		if (!err && (respObj != null)) {
			var asset = respObj['v2:Asset'];
			// Extract the device assetId == systemId
			if (!asset) {
				console.log('ERR - Unable to get assetId');
				process.exit(1);
			}			
			// get the assetId
			var assetId = asset['systemId'];
			if (!assetId) {
				console.log('ERR - Received invalid assetId - ' + JSON.stringify(asset));
				process.exit(1); 
			}  		
			
			if (_debug > 0 && _debug < 3) console.log('Found assetId=' + assetId);     		
						
			// Set the assetId with new value
			api_findvalue_data.assetId = String(assetId);
		} 
		
		// debug - REST API findvalue_data
		if (_debug > 0 && _debug < 3) console.log('* api_findvalue_data:'+ JSON.stringify(api_findvalue_data));		
		
		// Nested call FindCurrentValues to get CPU_TEMP value
		hdc_restapi.request('https',
			hdchost,
			api_getdata_path,						// REST API PATH
			api_findvalue_data,						// REST API POST(Input Data)
			function (err, respObj) {
				// if no error - process result
				if (err) {
					console.log('ERR - api_findvalue_data failed - ' + String(err));
					process.exit(err);
				}
								
				var dataItems = respObj['v2:FindDataItemValueResult']['v2:dataItemValues'];
				// Extract the dataItem - use 'http://www.jsoneditoronline.org/' to see JSON level
				if (!dataItems) {
					if (_debug > 0 && _debug < 3) console.log('ERR - Invalid [v2:dataItemValues] : ' + JSON.stringify(respObj));
					console.log('ERR - Cannot locate [v2:dataItemValues] data for <data-name> : ' + api_findvalue_data['name']);
					process.exit(1);
				} else {
					// console.log('result:' + JSON.stringify(dataItems));	  		
					var data = dataItems['v2:dataItemValue'];
					if (!data) {
						console.log('ERR - Receive invalid [v2:dataItemValue] : ' + JSON.stringify(dataItems));
						process.exit(1);
					}
					// Found the data
					var theValue = data['v2:value'];				
					// return the <data-name> value to stdout
					console.log(theValue);     		
					return theValue;
				} 
				
		}); 
});

// end of app
	
//==========================================================================================================
// HELPER FUNCTIONS

// function to encrypt text
function encrypt(text){
	var cipher = crypto.createCipher(algorithm, keypw);
	var crypted = cipher.update(text,'utf8','hex');
	
	crypted += cipher.final('hex');
	return crypted;
};

// function to decrypt text 
function decrypt(text){
  var decipher = crypto.createDecipher(algorithm, keypw);
  var dec = decipher.update(text,'hex','utf8');
  
  dec += decipher.final('utf8');
  return dec;
};

// function to strip chars from a string
function stripchars(string, chars) {
  return string.replace(RegExp('['+chars+']','g'), '');
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
	 // Set the RESTAPI module
	 hdc_restapi.setdebug(_debug);				
};

// command help text
function displayCmdHelp() {
	// show the cmd syntax
	console.log('Cmd syntax: node hdc_reader <data-name> [deviceSerial#] [-d#]');
	console.log('    <data-name>     : the name data item value stored in HDC cloud');
	console.log('    [deviceSerial#] : the gateway device serial number (MAC addr)');
	console.log('    [-d#]           : debug ON, # = debug level {d1: JSON, -d2: JSON+XML, -d3: Proxy}');
};

// EOF
