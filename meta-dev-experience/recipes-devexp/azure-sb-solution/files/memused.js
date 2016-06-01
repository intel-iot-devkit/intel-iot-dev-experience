// memused
//
// Node app to report the system memory used
//
// ver 1.0 - 02/02/2016 - Nghia Nguyen

// IMPORTANT: Node 0.10.39 is so old that synchronized execution is not available
// This code requires to use the'shelljs' and async for flow synchronization
require('shelljs/global');

// report memmory used in KB
var cmd = "vmstat -s | grep 'used memory' | awk '{print $1}'";

// Use shelljs exec()
var outStr = exec(cmd, {silent:true}).output;

console.log(outStr);

// EOF
