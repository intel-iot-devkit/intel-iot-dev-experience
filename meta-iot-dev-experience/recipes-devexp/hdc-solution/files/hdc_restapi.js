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
// HDC_RESTAPI.JS
//
// Implement the HDC Generic REST API (POST) - module.Request()
//
// Request(
//		protocol=http|https,
//		host='<host-address>',
//		path='</path/...>',
//		data='{HDC POST DATA}',
//		callback=function(err, resultObj);
//
// ver 1.4 - 01/21/2016 - nnm
//		replace xml2json module with xml2js to removed node-xpat lib dependency which failed
//		on upgrade nodejs 0.12.x or ^4.2.x
//		add debug levels 
//
// ver 1.3 - 12/04/2015 - nnm
//		fixed the proxy opts header and basic auth for proxy
//		use http for proxy server and tunnel HDC API call through
//
// ver 1.2 - 12/02/2015 - nnm
//		add proxy handler for http.request(), global-tunnel did not change
//		use url-parse v1.0.5 - The darn node URL failed.
//
// ver 1.1 - 11/29/2015 - nnm
//		updated for release
// ver 1.0 - 11/20/2015 - nnm
// 		Production release
//
//--------------------------------------------------------------------------------------------------------------
'use strict';
var _debug = 0; // no debug

// function to set debug level
exports.setdebug = function(dbgLevel) {
	// Level 0: no debug log
	// Level 1: JSON
	// Level 2: XML + JSON
	// Level 3: Proxy
	_debug = dbgLevel;
};

// function to call the HDC REST API 
exports.request = function(protocol, hdchost, path, indata, callback) {
	
	// XML to JSON conversion module
	var parseString = require('xml2js').parseString;
	
	// use the url-parse module
	var urlParse = require('url-parse');

	// protocol selector for request module
	var protocalTypes = {
		http  : { module : require('http'), port : '80'},
		https : { module : require('https'), port : '443'}
	};

	// IMPORTANT - if proxy present, use http for proxy to https
	// 	No proxy - use https
	// 	Proxy - must use http to tunnel calls
	var protocolModule = protocalTypes[protocol].module;
	var orgPort = protocalTypes[protocol].port;
			
	if (_debug == 3) {
		console.log('DBG: http_proxy=' + process.env.http_proxy);
		console.log('DBG: HTTP_PROXY=' + process.env.HTTP_PROXY);
	}
	// get either environment variables for proxy
	var proxy_str = process.env.http_proxy;
	if (!proxy_str) proxy_str = process.env.HTTP_PROXY;
	
	if (proxy_str) {
		if (_debug == 3) console.log('DBG: use http for proxy');
		// reset to use http for proxy
		protocolModule = protocalTypes['http'].module;
	}

	// REST API options	- No Proxy
	var options = {
		// HDC host name & port	
		host : hdchost,
		port : orgPort,
		// HDC API endpoint
		path : path,
		// API method is POST
		method : 'POST',
		// API header for POST JSON data
		headers : {
			// HDC data type specific for the call
			 'content-type' : 'application/json'
			,'content-length' : Buffer.byteLength(JSON.stringify(indata))
		}
	};

	// Proxy handler replaces the path, host and port with the proxy information
	// Check (process.env.http_proxy != null) to replace the proxy settings
	var _proxyopts = options;
	
	// if the proxy is set, then replace it
	if (proxy_str) {
		if (_debug == 3) 
			console.log('DBG: **** Start Proxy handling - %s', proxy_str);
		var urlObj = urlParse(proxy_str);
		if (!urlObj) {
			console.log('ERR - Invalid proxy= %s', proxy_str);
			process.exit(1);
		}

		// create basic credential for proxy
		var username = 'username';
		var password = 'password';
		var auth = 'Basic ' + new Buffer(username + ':' + password).toString('base64');

		// REST API for proxy
		var proxy_options = {
			hostname : urlObj.hostname,
			// Proxy Port
			port : urlObj.port,
			// Proxy will redirect to the endpoint - MUST BE A FULL PATH 
			path : protocol + '://' + options.host + options.path,
			headers : {
				// proxy needs authorization
				"Proxy-Authorization" : auth,
				// MUST specify for redirection
				host : hdchost,
				// the content type and length the sent data - encoded as JSON
				'content-type' : 'application/json',
				'content-length' : Buffer.byteLength(JSON.stringify(indata))
			}
		};
		// IMPORTANT - Fill in the proxy setting for options
		_proxyopts.host = proxy_options.hostname;
		_proxyopts.port = proxy_options.port;
		_proxyopts.path = proxy_options.path;
		_proxyopts.headers = proxy_options.headers; 
		if (_debug == 3) {
			console.log('DBG: PROXY - host:%s - path:%s, port:%s', _proxyopts.path, _proxyopts.host, _proxyopts.port);
		}
	}

	if (_debug == 3) { console.log('DBG: HTTPS opts: ' + JSON.stringify(_proxyopts) + '\n');}

	// Parsing Options for xml2js - 
	// See 'https://github.com/Leonidas-from-XIV/node-xml2js' for the parsing options
	var parseOpts = {
		explicitChildren : false,
		explicitArray : false,
		explicitRoot : true,
		mergeAttrs : true,
		trim : true
	};

	// process call - callback with data
	var req = protocolModule.request(_proxyopts, function (res) {
			//if (_debug > 0) console.log('DBG: STATUS: ' + res.statusCode + ' - ' + res.statusMessage);
			//if (_debug > 0) console.log('DBG: HEADERS: ' + JSON.stringify(res.headers));
			var respStr = '';
			res.setEncoding('utf8');

			// on(data) - collect all data - HTTP response in multiple chunks
			res.on('data', function (resdata) {
				respStr += resdata;
			});

			// on(end) - callback() with the respJSON object
			res.on('end', function () {
				if (_debug == 2) 
					console.log('*** XML BODY:' + respStr +'\n');
				// convert XML to JSON 
				parseString(respStr, parseOpts, function (err, respJSON) {
					if (_debug == 1 || _debug == 2) 
						console.log('*** JSON =' + JSON.stringify(respJSON) + '\n');
						
					// callback with the JSON data
					return callback(null, respJSON);

				}); 
			});

			// on(close) - emit an 'end'
			res.on('close', function () {
				console.log('WRN - connection close!');
				res.emit('end')
			});
	});

	// handle error from server
	req.on('error', function (err) {
		console.error('ERR - Request Failed: ' + err.message);
		return callback(err);
	});

	// request write JSON data to server
	req.write(JSON.stringify(indata));
	req.end();
};
// EOF
