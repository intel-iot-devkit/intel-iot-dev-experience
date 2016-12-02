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
// HDC_SNUM.JS - App to retrieve the device MAC address and format into '112233445566' format
// 
//	
//  Command Syntax:
//		node hdc_snum.js
//
//  Ver 1.0	 - 01/22/16 - nnm
//		Updated
//
//-------------------------------------------------------------------------------------------------------------- 

var macaddr = require('macaddress');

// function to strip chars from a string
function stripchars(string, chars) {
  return string.replace(RegExp('['+chars+']','g'), '');
}

// extract the eth0 MAC address - default WRA Agent use eth0: linux
macaddr.one(function (err, macString) {
   // strip the ':' from the mac to create the serial #
   var serialNum = stripchars(macString, ':');
   // output stdout for piping usage
   console.log(serialNum);  
});

// EOF
