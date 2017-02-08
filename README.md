Automatically update and manage your conan exiles dedicated server by wrapping the entire process into a python script. The python script will manage your servers process as well as bring it down for updates, then back up again.

### Installation
* Install python 2.7.15
* Run install.bat

### Launching server
Just run runserver.bat and it will download the conan dedicated server for you. steamcmd.exe is provided so this is all you need.

### Features
 * Detect updates and update the server

### Coming Soon
 * Turn off / on building damage during defined hours
 * Host a web UI to see who is online
 * Download and manage steamcmd

### Example Log
```sh
$ python runserver.py
No config found, creating new config
Saving config {'build_id': 0}
Launching server and waiting for child processes
Server running successfully
An update is available from build 0 to 1613510
Saving config {'build_id': '1613510'}
Launching server and waiting for child processes
Server running successfully
```