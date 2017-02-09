Automatically update and manage your conan exiles dedicated server by wrapping the entire process into a python script. The python script will manage your servers process as well as bring it down for updates, then back up again.

### Installation
* Install python 2.7.15
* Run install.bat

### Launching server
Just run runserver.bat and it will download the conan dedicated server for you. steamcmd.exe is provided so this is all you need.

### Features
 * Detect updates and update the server
 * Automatically reboot the server when it goes down for any reason
 * Specify raiding time in config and the server will change the setting and reboot automatically

### Coming Soon
 * Host a web UI to see who is online

### Code TODO
 * Move all prints to python logging module
 * Redo config system to make it more robust and immune to migration issues
 * Add colors to logging

### Example Log
```sh
> runserver.bat
An update is available from build 0 to 1613510
Launching server and waiting for child processes
Server running successfully
Server down... rebooting
Launching server and waiting for child processes
Server running successfully
```
