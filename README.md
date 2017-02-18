# README FIRST

Conan Server Manager (now known as Server Thrall) is a python based dedicated server toolbox. It's not a GUI to manage your server, it adds new features to the dedicated server that are not previously supported. Please read the installation instructions carefully.

### Installation
* Install python 2.7.13 [Windows Installer](https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi)
* Download ServerThrall and unzip somewhere [Download ServerThrall](https://github.com/NullSoldier/conan-server-manager/archive/master.zip)
* Run install.bat

### How to run
**Click on runserver.bat** If this is your first time running it you will see a new **serverthrall.config** file appear in the same directory. See more information below on what the configuration contains.

### Included Plugins
| Plugin | Description | Config |
| --- | --- | --- |
| **DownRecovery** | Restarts the server if the server is offline. | None |
| **ServerUpdater** | Checks for updates and updates the server automatically | **installed_version**: the currently known server version. delete this key to force an update |
| **UptimeTracker** | Records the percentage of time the server has been online. If the server thrall is closed, this counts against the uptime percentage. | **seconds_up**: The total amount of seconds the server has been up<br>**initial**:  unix timestamp of when the server uptime started to be recorded. Delete this to restart your uptime counter |
| **RaidPlugin** | Allows you to set a period of time under which "Raiding" is enabled. This means that building damage will only be enabled during this time. Works by changing the games configuration and rebooting the server at the boundries of raiding times. | None |

###Example Config
```ini
[ServerThrall]
conan_server_directory = c:\Users\Developer\Desktop\Projects\conan\vendor\server
[UptimeTracker]
initial = 1487425465.0
seconds_up = 383.0
[DownRecovery]
[ServerUpdater]
installed_version = 1639449
```

### Coming Soon
 * Discord integration
 * Server event stream
   * Players logging in / out
   * Player deaths
   
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
