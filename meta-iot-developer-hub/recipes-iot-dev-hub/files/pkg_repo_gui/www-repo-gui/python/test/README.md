# unit_test

We use python's built-in unittest module. This folder includes all the Unit Testing scripts.

The main one is "unit_test.py". This one should run all other test cases included in other "unit_test_XXX.py" files.
Please add your new test cases in this file. Check comments to see where to add your own cases.

Each "unit_test_XXX.py" file is the test for a function block.
Write a new "unit_test_XXX.py" to test a function block. Check other "unit_test_XXX.py" files for references, and search for "python unittest" for more information.
https://docs.python.org/2/library/unittest.html

Please utilize unit_test_utility module to do init and wrap-up in your test scripts. Check other files for reference.

When you run these Unit Testing, we overwrite the logging settings defined in python\tools\logging_helper\logging.conf. The goal is to suppress the logging and only get the testing results.
You can change that at unit_test_utility.py's UtilityHelper class's __init__ function.


## modules included in test

* developer_hub_config:                   tested by unit_test_config
* manage_auth.py:                         tested by unit_test_auth
* manage_config.py:                       tested by unit_test_config
* manage_hac.py:                          tested by unit_test_hac
* manage_hub.py:                          tested by unit_test_hub
* manage_mec.py:                          tested by unit_test_security
* manage_os_controls.py:                  tested by unit_test_os_controls
    OSControls::POST (factory reset) is not tested.
    OSControl::PUT (shutdwon) is not tested.
* manage_os_update.py:                    tested by unit_test_os_update
* manage_package.py:                      tested by unit_test_package
* manage_pro_upgrade.py:                  tested by unit_test_pro_upgrade
* manage_proxy.py:                        tested by unit_test_proxy
* manage_repo.py:                         tested by unit_test_repo
* manage_security.py:                     tested by unit_test_security
* manage_self_update.py:                  tested by unit_test_self_update
* manage_service.py:                      tested by unit_test_service
* tools\data_ops:                         tested by unit_test_data_ops
* tools\network_ops:                      tested by unit_test_network_ops
* tools\shell_ops:                        tested by unit_test_shell_ops
* tools\sysinfo_ops:                      tested by unit_test_sysinfo_ops


## running the test

* To run the overall testing, go to python folder path and then run
    export http_proxy=http://proxy-chain.intel.com:911
    export https_proxy=http://proxy-chain.intel.com:912
    export no_proxy=intel.com,.intel.com,localhost,127.0.0.1
    python -m unittest test.unit_test
* To run each individual function block testing, go to python folder path and then run
    export http_proxy=http://proxy-chain.intel.com:911
    export https_proxy=http://proxy-chain.intel.com:912
    export no_proxy=intel.com,.intel.com,localhost,127.0.0.1
    python -m unittest test.unit_test_XXX
* To run a specific testing method, go to python folder path and then run
    export http_proxy=http://proxy-chain.intel.com:911
    export https_proxy=http://proxy-chain.intel.com:912
    export no_proxy=intel.com,.intel.com,localhost,127.0.0.1
    python -m unittest test.unit_test_XXX.TestXXXX.test_XXXX
    For example,
        python -m unittest test.unit_test_usb.TestUsb.test_usb_api_get
        

## testing pro server

May need to update the url in [ProRepo] of developer_hub_config file. Add /ondemand/ before remote.php.






