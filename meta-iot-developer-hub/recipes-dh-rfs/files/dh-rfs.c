#include "wra.h"
#include <stdio.h>

wra_handle wra_h;       /* Agent handle */
wra_status rc;          /* Return code  */

int main()
{
   /* Get a handle to the agent */
   wra_h = wra_gethandle();
   if ( wra_h == WRA_NULL )
   {
      printf("We failed to get agent handle\n");
      return WRA_ERR_FAILED;
   }

   rc = wra_restore_factory_software_image( wra_h );

   printf("Error: We should not get here because the previous call should reset the board.\n");
}

