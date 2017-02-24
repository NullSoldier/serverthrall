# README FIRST

Conan Server Manager (now known as Server Thrall) is a python based dedicated server toolbox. It's not a GUI to manage your server, it adds new features to the dedicated server that are not previously supported. Please read the installation instructions carefully.

### Installation
* Install python 2.7.13 [Windows Installer](https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi)
* Download ServerThrall and unzip somewhere [Download ServerThrall](https://github.com/NullSoldier/conan-server-manager/archive/master.zip)
* Run install.bat

### How to run
**Click on runserver.bat** If this is your first time running it you will see a new **serverthrall.config** file appear in the same directory. See more information below on what the configuration contains.

### Configuration for Plugins
| Plugin | Description | Config |
| --- | --- | --- |
| | These are configuration options for the "ServerThrall" section and are app wide. | **conan_server_directory**: A directory where ServerThrall should be able to find "ConanSandboxServer.exe"<br>**force_update_on_launch**: Set to true or false to force ServerThrall to update and validate the conan exiles server files. Useful if you've accidently deleted or removed any files and your server won't launch.<br>**additional_arguments**: Passes additional arguments to ConanSandboxServer. This allows you to pass arguments like MULTIHOME if you want to play on the same computer as your server. By default the only parameter passed to the server is **-log** which is required for ServerThrall to work properly for now. |
| **DownRecovery** | Restarts the server if the server is offline. | **enabled**: Set to true or false to prevent this plugin from running |
| **ServerUpdater** | Checks for updates and updates the server automatically | **enabled**: Set to true or false to prevent this plugin from running<br>**installed_version**: the currently known server version. delete this key to force an update<br>**check_cooldown_seconds**: How long in seconds between checking for updates.<br>**last_checked_seconds**: The unix time stamp since this plugin has last checked for updates. |
| **UptimeTracker** | Records the percentage of time the server has been online. If the server thrall is closed, this counts against the uptime percentage. | **enabled**: Set to true or false to prevent this plugin from running<br>**seconds_up**: The total amount of seconds the server has been up<br>**initial**:  unix timestamp of when the server uptime started to be recorded. Delete this to restart your uptime counter |
| **RaidPlugin** | Allows you to set a period of time under which "Raiding" is enabled. This means that building damage will only be enabled during this time. Works by changing the games configuration and rebooting the server at the boundries of raiding times. This plugin modifies the CanDamagePlayerOwnedStructures option in ServerSettings. | **enabled**: Set to true or false to prevent this plugin from running<br>**start_hour**: The hour of the day that raiding should be enabled. This should be in 24 hour time. So 17 would be 5pm in the servers computers timezone.<br>**length_in_hours**: The number of hours after start_hour that raiding should be enabled. |

###Example Config
```ini
[ServerThrall]
force_update_on_launch = false
conan_server_directory = c:\..\conan\vendor\server
additional_arguments = -MULTIHOME=192.168.2.4 -QueryPort=27019 -GameServerQueryPort=27020 -ServerName=FooServer -MaxPlayers=20
[UptimeTracker]
initial = 1487425465.0
seconds_up = 1261.0
enabled = false
[DownRecovery]
enabled = true
[ServerUpdater]
enabled = true
installed_version = 1643774
[RaidManager]
enabled = true
start_hour = 17
length_in_hours = 5
```

### Coming Soon
 * Discord integration
 * Server event stream
   * Players logging in / out
   * Player deaths
   
### Example Log
```sh
> runserver.bat
[serverthrall] Found running server, attaching
[serverthrall] Initializing with plugin UptimeTracker
[serverthrall] Initializing with plugin DownRecovery
[serverthrall] Initializing with plugin ServerUpdater
[serverthrall] Initializing with plugin RaidManager
[serverthrall] Found running server, attaching
[serverthrall.UptimeTracker] Uptime at 98.12 percent (679.0 / 692.0)
[serverthrall.ServerUpdater] Autoupdater running, currently known buildid is 1643774
[serverthrall.RaidManager] Raiding is currently OFF in the server.
[serverthrall.RaidManager] Raiding is enabled from 05:00 PM to 01:00 AM
[serverthrall.RaidManager] Preparing to turn ON raiding.
[serverthrall] Launching server and waiting for child processes
[serverthrall] Server running successfully
```
