# cputemp.sh
#
# Shell script to report the current CPU temperature
#
# Command Syntax:  $ cputemp.sh
#
# ver 1.0 - 02/02/2016 - Nghia Nguyen
#	Initial version
#

#!/bin/bash
sensors | grep "Core 0:" | awk '{print $3}'

# eof
