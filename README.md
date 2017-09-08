### [Download the latest release here](https://github.com/NullSoldier/serverthrall/releases/latest) and [join discord](https://discord.gg/5dK2TdN) if you have any issues.

Server Thrall is a python based dedicated server toolbox. It's not a GUI to manage your server, it adds new features to the dedicated server that are not previously supported. To get the full value out of server thrall, please read the Configuration for Plugins section.

### Installation
* [Download ServerThrall](https://github.com/NullSoldier/serverthrall/releases/download/v2.0.6/serverthrall.2.0.6.zip)
* Unzip somewhere on your computer

### How to run
**Click on serverthrall.exebat** If this is your first time running it you will see Server Thrall download the Conan Exiles Dedicated Server and then create a new **serverthrall.config** file in the same directory. See more information below on what **serverthrall.config** contains.

### Common Issues
- **Q>** When the Conan Exiles server starts it opens up an error alert that says `The procedure entry point ?IsAlive@CThread@@QEBA_NXZ could not`
- A> This happens when steam is running at the same time. If you close steam the error goes away when launching Conan Exiles.

- **Q>** ServerThrall is stuck at **Waiting for config to exist**
- A> This can happen if the config doesn't exist, but if ServerThrall crashes during the updater process your configurations may not exist anymore and you need to force an update by using `force_update_on_launch = true` in your **serverthrall.config**. I do not recommend leaving that option on.

- **Q>** ServerThrall uses the 32bit server executable by default, how can I change that?
- A> Set `conan_exe_name`, `conan_exe_subpath` under `[ServerThrall]` in **serverthrall.config** to customize this

### Configuration for Plugins
Do not edit serverthrall.config while serverthrall is running. Your changes will be overwritten by serverthrall.

| Plugin | Description | Config |
| --- | --- | --- |
| | These are configuration options for the "ServerThrall" section and are app wide. | **conan_server_directory**: A directory where ServerThrall should be able to find "ConanSandboxServer.exe"<br>**force_update_on_launch**: Set to true or false to force ServerThrall to update and validate the conan exiles server files. Useful if you've accidently deleted or removed any files and your server won't launch.<br>**additional_arguments**: Passes additional arguments to ConanSandboxServer. This allows you to pass arguments like MULTIHOME if you want to play on the same computer as your server. By default the only parameter passed to the server is **-log** which is required for ServerThrall to work properly for now.<br>**set_high_priority** If true, ensures the operating system process priority for the conan exiles server is high. This works even if attaching or rebooting the server.<br>**conan_exe_name** The name of the CE server executable. It's used to figure out if CE server is installed, or to find the process and attach if it's already running. |
| **ServerConfig** | Allows you to configure common server settings from your server thrall config. If the config differs from expected, the config will be edited and the server restarted. |**enabled**: Set to true or false to prevent this plugin from running<br> **ServerName**=My Server: Sets the name that will be displayed in the server list.<br> **ServerPassword**=Password123: Sets the server password that will need to be entered to join the server. Leave blank for no password.<br> **QueryPort**=27015: Sets the query port for Steam matchmaking. Same as setting -QueryPort in the command line.<br> **MaxPlayers**=70: Sets the maximum number of players.<br> **AdminPassword**=SecretPassword: Sets the administrative password for the server. This will grant players administrative rights when used from the settings menu in-game.<br> **MaxNudity**=2: Sets the maximum nudity level allowed on the server. (0=None, 1=Partial, 2=Full)<br> **IsBattlEyeEnabled**=True: Enables/disables BattlEye protection for the server.<br> **ServerRegion**=1: Sets the server's region. (0=EU, 1=NA, 2=Asia)<br> **ServerCommunity**=1: Sets the server's play style (0=None, 1=Purist, 2=Relaxed, 3=Hard Core, 4=Role Playing, 5=Experimental)<br> **PVPBlitzServer**=False: Enables/disables Blitz mode. (accelerated progression)<br> **PVPEnabled**=True: Enables/disables PvP on the server.<br> **NetServerMaxTickRate**=30: Sets the maximum tick rate (update rate) for the server. **WARNING**: High values can cause unwanted behavior.<br> |
| **DownRecovery** | Restarts the server if the server is offline. | **enabled**: Set to true or false to prevent this plugin from running |
| **ServerUpdater** | Checks for updates and updates the server automatically | **enabled**: Set to true or false to prevent this plugin from running<br>**installed_version**: the currently known server version. delete this key to force an update<br>**check_cooldown_seconds**: How long in seconds between checking for updates.<br>**last_checked_seconds**: The unix time stamp since this plugin has last checked for updates. |
| **UptimeTracker** | Records the percentage of time the server has been online. If the server thrall is closed, this counts against the uptime percentage. | **enabled**: Set to true or false to prevent this plugin from running<br>**seconds_up**: The total amount of seconds the server has been up<br>**initial**:  unix timestamp of when the server uptime started to be recorded. Delete this to restart your uptime counter |
| **ApiUploader** | Uploads your server data to serverthrallapi so you can see your data online. If your **server_id** was `2`, and your **private_secret** was `200cd768-5b1d-11e7-9e82-d60626067254` you would access your servers characters at this URL: https://serverthrallapi.herokuapp.com/api/2/characters?private_secret=200cd768-5b1d-11e7-9e82-d60626067254  | **enabled**: Set to true or false to prevent this plugin from running<br>**server_id**: The registered server id with serverthrallapi, used to access your data.<br>**public_secret**: A public code you can give to your players to access a "public" view of your servers data. This is unused but will be used later.<br>**private_secret** A secret code that is used to make modifications to your server and synchronize data. Do NOT give this out to your players |
| **DeadManSnitch** | https://deadmanssnitch.com Emails you when your server is down. You can sign up for a free account which gives one limited snitch. | **snitch_url**: The url you get from deadmansnitch to snitch to. |


### Example Config
```ini
[ServerThrall]
force_update_on_launch = false
conan_server_directory = c:\Users\Jason\Desktop\Projects\serverthrall\vendor\server
additional_arguments = -MULTIHOME=192.168.2.15
set_high_priority = false

[UptimeTracker]
initial = 1487425465.0
seconds_up = 1261.0
enabled = true

[DownRecovery]
enabled = true

[ServerUpdater]
enabled = true
installed_version = 1933316

[ApiUploader]
enabled = true

[ServerConfig]
enabled = true
ServerName = Awesome Server
NetServerMaxTickRate = 60
MaxPlayers = 8
AdminPassword = 1234
MaxNudity = 2
PVPBlitzServer = False
PVPEnabled = True
ServerCommunity = 1
IsBattlEyeEnabled = True
```

### Ginfo Integration
Ginfo Integration allows you to track the position of players on your server in real time on the [Ginfo Map](https://conanexiles.ginfo.gg)

**Set up the Integration:**
* You'll need to be the admin of a ginfo group
* Open the panel of your group by clicking on your groups button in the left bar
* Click on the "..." more button at the top right of the panel
* Open the "Access Tokens" Menu
* Create an access token
* Copy your group's UID and access token to your **serverthrall.config** under the `ApiUploader` section

```
[ApiUploader]
enabled = true
ginfo_group_uid = <GROUP UID>
ginfo_access_token = <ACCESS TOKEN>
```

### Coming Soon
 * Access your server data from an online REST API
 * Online UI to audit your player's actions

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
