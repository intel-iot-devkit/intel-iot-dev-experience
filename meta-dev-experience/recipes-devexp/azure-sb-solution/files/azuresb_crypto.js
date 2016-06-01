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

//--------------------------------------------------------------------------------------------------------------
//
// azuresb_crypto.js - Generate the config settings for the Azure SB app
//
//  Ver 1.0 - 02/07/2016 - Nghia Nguyen
//		First release
//
//		IMPORTANT: This app only runs in prebuilt time to generate encrypted app credential
//--------------------------------------------------------------------------------------------------------------
'use strict';

// Nodejs encryption with CTR and key  - Use this in the reader
var crypto = require('crypto'),
    algorithm = 'aes-256-ctr',
    keypw = '6e6e6d2d323031352d686463';  // IMPORTANT - set SB_CONFIG_PK with this value

// function to encrypt text
function encrypt(text){
	var cipher = crypto.createCipher(algorithm, keypw);
	var crypted = cipher.update(text,'utf8','hex');

	crypted += cipher.final('hex');
	return crypted;
};

// function to decrypt text - REFERENCE
function decrypt(text){
  var decipher = crypto.createDecipher(algorithm, keypw);
  var dec = decipher.update(text,'hex','utf8');

  dec += decipher.final('utf8');
  return dec;
};

console.log('start app');

//--------------------------------------------------------------------------
// Default azuresb_sbconfig.json file name
var jsonFileName = './sbconfig.json';

// IMPORTANT - DO NOT CHANGE THIS
var sb_origin = require('./sbcfg_origin.json');

var sb_config_data = {
	"sbConnectionStr" : "AZURE Service-Bus SAS Needed"
};

// Encrypt the config data and set it back
sb_config_data.sbConnectionStr = encrypt(sb_origin.sbConnectionStr);

// convert to a string
var configJsonStr = JSON.stringify(sb_config_data);

console.log('AzureSB_Config encrypted : ' + configJsonStr);

// encrypt the content and save to sbconfig.json
var fs = require('fs');

// write the JSON object as a string
fs.writeFile(jsonFileName, configJsonStr, function (err) {
  if (err)
     return console.log('ERR - Failed writing file : ' + err);
});

console.log('encryption success');

// EOF
