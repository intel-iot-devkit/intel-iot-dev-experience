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

#include <stdio.h>
#include <stdlib.h>
#include "wra.h"

#define VERSION 1.3

//----------------------------------------------------------------------------------------------------------------------
// This sample progran send a numeric data with a data item name to the HDC server registerd by the WRA.
// Note: The HDC application is required to run with the 'wra' user account.
// 
// Command Syntax:
//	$ sudo -u wra ./hdc-send-data 
//		-h | --help			        : display command syntax
//		-i [data-item]			    : read input from stdin, optional data-item name
//		[data-item] <input-data>	: the optional data-item name and the input data value
//
//	if no [data-item] specified, the 'default-data'name will be used.
//  
//---------------------------------------------------------------------------------------------------------------------- 
int main(int argc, char * argv[]) 
{
	wra_handle 	wra = WRA_NULL;
	wra_tm_handle 	tm_data = WRA_NULL;
	wra_status 	rc = WRA_SUCCESS;
	char 		str_dataItem[] = "default-data";
	char		*ptr_dataItem = str_dataItem;    	// default item-name
	double 		n_data = 0.0;
	char		str_buffer[50];  			// max input number of 50 digits
	char 		*p = str_buffer, *end = NULL;

	// Check the input argc 
	if (argc == 1) 
	{
		// missing argument
		printf("ERR - Missing arguments, use -h | --help for the command syntax\n");
		return WRA_ERR_FAILED;
	}
	
	// #1: cmd -h | --help
 	if ((strcmp(argv[1], "-h") == 0) ||
	    (strcmp(argv[1], "--help") == 0))
	{		
		// display command help
		printf("hdc-send-data - ver: %.2f\n", VERSION); 
		printf("$ su wra hdc-send-data\n");
		printf("	-h | --help			        : display command syntax\n");
		printf("	-i [data-item]		  	    : read the input from stdin (piping) and optional data name\n");
		printf("	[data-item] <input-data>	: command-line optional data-item name and input-data\n");
		return  WRA_SUCCESS;	
	}

	// #2: cmd -i [data-item] |  cmd [data-item] <input-data>
 	if (strcmp(argv[1], "-i") == 0)
	{
		// get input-data from stdin
		scanf("%s", str_buffer);
		p = str_buffer;
		// get [data-item] name
		if (argc == 3) 
		   ptr_dataItem = argv[2];
	}	
	else
	{
		// get the cmd-line argument: [data-item] = argv[1] and <input-data> from argv[1|2]  
		p = argv[1];
		if (argc == 3) 
		{
			ptr_dataItem = argv[1];
			p = argv[2];
		}

	}
	
	// convert the input data to number
	n_data = strtod(p, &end);
	if (p == end)	// number conversion has failed
	{
		printf("ERR - Invalid input-data numerical value: %s\n", p);
		return WRA_ERR_FAILED;
	} 

	// the data and name to send
  	printf("HDC Data: %.2f - Data-Item: %s\n", n_data, ptr_dataItem);

	// get HDC agent handle
	wra = wra_gethandle();
	if (wra == WRA_NULL)
	{
		printf ("ERR - Could get agent handle\n");
		return WRA_ERR_FAILED;
	}

	// allocate a telemetry data object - [data-item] or "default-data"
	tm_data = wra_tm_create(WRA_TM_DATATM, ptr_dataItem);
	if (tm_data == WRA_NULL)
	{
		printf ("ERR - Could not create an data telemetry object: %s\n", ptr_dataItem);
		return WRA_ERR_FAILED;
	}

	// set telemetry data object attributes
	rc = wra_tm_setvalue_int(tm_data, WRA_TM_ATTR_PRIORITY, WRA_TM_PRIO_HIGH);
	// set the numeric data <n_Data> to send to HDC server  
	rc = wra_tm_setvalue_double (tm_data, WRA_TM_ATTR_DATA, n_data);
	   
	// send telemetry data object to the server
	if ((rc = wra_tm_post(wra, tm_data, WRA_NULL, WRA_NULL)) != WRA_SUCCESS) 
	{
		if (rc == WRA_ERR_NO_MEMORY)
		{
			printf ("ERR - could not post tm %s - returned WRA_ERR_NO_MEMORY\n", "wra_tm_post");
			rc = !WRA_SUCCESS;
		} else
			printf ("ERR - could not post tm %s - returned %d\n","wra_tm_post", rc);
	}

	// clean up - deallocate a telemetry data object
	if ((rc = wra_tm_destroy(tm_data)) != WRA_SUCCESS)
		printf("failed to deallocate a telemetry data object : %d\n", rc);

	// clean up - delete the handle 
	if ((rc = wra_delete_handle(wra)) != WRA_SUCCESS)
		printf("failed to delete the agent handle\n");

	return WRA_SUCCESS;
}
// EOF
