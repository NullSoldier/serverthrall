### [Download the latest release here](https://github.com/NullSoldier/serverthrall/releases/latest) and [join discord](https://discord.gg/5dK2TdN) if you have any issues.

Server Thrall is a python based dedicated server toolbox. It's not a GUI to manage your server. It adds new features to the dedicated server that are not previously supported. To get the full value out of server thrall, please read the Configuration for Plugins section. I also highly recommend enabling the ApiUploader plugin to get your own live server website at http://thrallbrowser.com.

### Installation
* [Download ServerThrall](https://github.com/NullSoldier/serverthrall/releases/download/v2.1.6/serverthrall.2.1.6.zip)
* Unzip somewhere on your computer

### How to run
**Click on serverthrall.exe** If this is your first time running it you will see Server Thrall download the Conan Exiles Dedicated Server and then create a new **serverthrall.config** file in the same directory. See more information below on what **serverthrall.config** contains.

### Common Issues
- **Q>** ServerThrall stops responding or processing for periods of time
- A> Disable Quick Edit by following the instructions here https://superuser.com/questions/555160/windows-command-prompt-freezing-on-focus/555204#555204
- **Q>** When the Conan Exiles server starts it opens up an error alert that says `The procedure entry point ?IsAlive@CThread@@QEBA_NXZ could not`
- A> This happens when steam is running at the same time. If you close steam the error goes away when launching Conan Exiles.

- **Q>** ServerThrall is stuck at **Waiting for config to exist**
- A> This can happen if ServerThrall crashes during the updater process. Your configurations may not exist anymore and you need to force an update by using `force_update_on_launch = true` in your **serverthrall.config**. I do not recommend leaving that option on.

- **Q>** I can't join my own server and I'm playing on the same computer I'm hosting my server on.
- A> Conan Exiles requires you to set your MULTIHOME for your server to your local IP address. Server thrall attempts to do this for you, but it may be failing depending on your computers network configuration. Check the logs when serverthrall starts the server to see if the IP matche your computers. If not, use the multihome config option documented below to override the setting to the correct ip address.

### Plugins

| Name | Description |
| --- | --- |
| **ServerConfig** | Allows you to configure common server settings from your server thrall config. If the config differs from expected, the config will be edited and the server restarted. |
| **DownRecovery** | Restarts the server if the server is offline. |
| **ServerUpdater** | Checks for updates and updates the server automatically |
| **ServerRestarter** | Will restart the server at defined intervals, and sends out a warning to RCON and Discord |
| **Discord** | Sends message to discord via webhooks. |
| **RemoteConsole** | Sends messages and commands to a conan exiles server via the RCON protocol. |
| **RestartManager** | Makes sure notifications are sent out during restarts and the waiting period for a restart is respected. Used by other plugins. |
| **UptimeTracker** | Records the percentage of time the server has been online. If the server thrall is closed, this counts against the uptime percentage. |
| **ApiUploader** | Uploads your server data to serverthrallapi so you can see your data online. If your **server_id** was `2`, you would access your servers characters at this URL: https://thrallbrowser.com/server/2/characters and you can fetch your REST API data at https://serverthrallapi.herokuapp.com/api/2/characters |
| **DeadManSnitch** | https://deadmanssnitch.com Emails you when your server is down. You can sign up for a free account which gives one limited snitch. |

### Configuration for Plugins
Do not edit serverthrall.config while serverthrall is running. Your changes will be overwritten by serverthrall.

| **ServerThrall** | | |
| --- | --- | --- |
| conan_server_directory | | A directory where ServerThrall should be able to find "ConanSandboxServer.exe". You don't need to set this unless you want to manage a server not installed by ServerThrall. |
| force_update_on_launch | false | Set to `true` to force ServerThrall to update and validate the conan exiles server files. This will then be turned off after it's read. Useful if you've accidently deleted or removed any files and your server won't launch.
| additional_arguments | | Passes additional arguments to ConanSandboxServer. Arguments are documented here, https://docs.unrealengine.com/en-us/Programming/Basics/CommandLineArguments. By default the only parameter passed to the server is **-nosteam** and **-MULTIHOME** with your local computers IP.
| set_high_priority | true | If `true`, ensures the operating system process priority for the conan exiles server is high. This works even if attaching or rebooting the server. |
| multihome | | Server Thrall will by default set your servers multihome argument to your local IP address. If this behavior is incorrect, or insufficient, you can override that value with this setting. Set this to your own computers IP to join a server on the same computer that you want to play on. |
| testlive | false | Set to `true` run your server for testlive, false to use the live version.  |

| **ServerConfig** | | |
| --- | --- | --- |
| enabled | true | Set to `true` or `false` to prevent this plugin from running |
| ServerName | My Server | Sets the name that will be displayed in the server list. |
| ServerPassword | Password123 | Sets the server password that will need to be entered to join the server. Leave blank for no password. |
| QueryPort | 27015 | Sets the query port for Steam matchmaking. Same as setting -QueryPort in the command line. |
| MaxPlayers | 50 | Sets the maximum number of players. |
| AdminPassword | SecretPassword | Sets the administrative password for the server. This will grant players administrative rights when used from the settings menu in-game. |
| MaxNudity | 2 | Sets the maximum nudity level allowed on the server. (0=None, 1=Partial, 2=Full) |
| IsBattlEyeEnabled | True | Enables/disables BattlEye protection for the server. |
| ServerRegion | 1 | Sets the server's region. (0=EU, 1=NA, 2=Asia) |
| ServerCommunity | 1 | Sets the server's play style (0=None, 1=Purist, 2=Relaxed, 3=Hard Core, 4=Role Playing, 5=Experimental) |
| PVPEnabled | True | Enables/disables PvP on the server. |
| NetServerMaxTickRate | 30 | Sets the maximum tick rate (update rate) for the server. |

| **DownRecovery** | | |
| --- | --- | --- |
| enabled | true | Set to true or false to prevent this plugin from running |
| discord_restart_message |  |  |

| **ServerUpdater** | | |
| --- | --- | --- |
| enabled | true | Set to true or false to prevent this plugin from running |
| discord_warning_message | | |
| discord_restart_message | | |
| rcon_warning_message | | |
| rcon_restart_message | | |

| **ServerRestarter** | | |
| --- | --- | --- |
| enabled | true | Set to true or false to prevent this plugin from running |
| restart_times | 6:00,10:00,16:00,20:00 | This field determines all the times the server is restarted. The format of this field is `6:00,10:00,16:00,20:00` where each time is 24 hour time with `HOURS:MINUTES`, separated by a coma. There is no limit to the amount of times you can specify. The times do not have to be in chronological order. |
| discord_warning_message | | |
| discord_restart_message | | |
| rcon_warning_message | | |
| rcon_restart_message | | |

| **UptimeTracker** | | |
| --- | --- | --- |
| enabled | true | Set to true or false to prevent this plugin from running |
| initial | |  unix timestamp of when the server uptime started to be recorded. Delete this to restart your uptime counter |

| **ApiUploader** | | |
| --- | --- | --- |
| enabled | true | Set to true or false to prevent this plugin from running |
| server_id | | The registered server id with serverthrallapi, used to access your data. |
| public_secret | | A public code you can give to your players to access a "public" view of your servers data. This is unused but will be used later.
| private_secret | | A secret code that is used to make modifications to your server and synchronize data. Do NOT give this out to your players |

| **DeadManSnitch** | | |
| --- | --- | --- |
| enabled | true | Set to true or false to prevent this plugin from running |
| snitch_url | | The url you get from deadmansnitch to snitch to. |

| **RestartManager** | | |
| --- | --- | --- |
| warning_minutes | 5 | How many minutes to give players before restarting |
| warning_send_discord | true | Warn discord that a restart is coming |
| warning_send_rcon | true | Warn players in game that a restart is coming |
| restart_send_discord | true | Message discord that a restart is happening |
| restart_send_rcon | true | Message players in game why they are being disconnected |

| **Discord** | | |
| --- | --- | --- |
| enabled | true | Set to true or false to prevent this plugin from running |
| ServerRestarter | | A webhook URL for the ServerRestarter plugin to send messages on. |
| DownRecovery | | A webhook URL for the DownRecovery plugin to send messages on. |
| ServerUpdater | | A webhook URL for the ServerUpdater plugin to send messages on. |
| stale_message_seconds | | Don't retry failed message on the webhook that are older than this time in seconds. |
| force_test_discord | | Send a test message to every hook to test if it works. |

| **RemoteConsole** | | |
| --- | --- | --- |
| enabled | true | Set to true or false to prevent this plugin from running |

### Example Config
```ini
[ServerThrall]
conan_server_directory = c:\serverthrall\vendor\server
force_update_on_launch = false
additional_arguments =
set_high_priority = false
testlive = false

[ServerConfig]
enabled = true
ServerName = "Test Server"
AdminPassword = ilovefruit
QueryPort = 27015
Port = 7777
RconEnabled = 1
RconPassword = ilovefruit
RconPort = 25575
RconMaxKarma = 60

[UptimeTracker]
enabled = false

[DownRecovery]
enabled = true

[ServerUpdater]
enabled = true

[ApiUploader]
enabled = true

[DeadManSnitch]
enabled = false
snitch_url = https://nosnch.in/...

[ServerRestarter]
enabled = true
restart_times = 2:56,1:00,4:00,9:00,16:00,20:00
force_restart_on_launch = false

[Discord]
enabled = true
ServerRestarter = https://discordapp.com/api/webhooks/...
DownRecovery = https://discordapp.com/api/webhooks/...
ServerUpdater = https://discordapp.com/api/webhooks/...

[RemoteConsole]
enabled = true

[RestartManager]
enabled = true
warning_minutes = 5
warning_send_discord = True
warning_send_rcon = True
restart_send_discord = True
restart_send_rcon = True
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

### ThrallBrowser
If you use the ApiUploader plugin, you should see your server at http://thrallbrowser.com and can browse your server info and give a nice live website to your players.

### Example Log
```sh
> runserver.bat
[serverthrall] Running version 2.0.8
[serverthrall] Initializing with plugin ApiUploader
[serverthrall] Initializing with plugin DeadManSnitch
[serverthrall] Initializing with plugin Discord
[serverthrall] Initializing with plugin DownRecovery
[serverthrall] Initializing with plugin ServerConfig
[serverthrall] Initializing with plugin ServerUpdater
[serverthrall] Initializing with plugin ServerRestarter
[serverthrall] Initializing with plugin UptimeTracker
[serverthrall] Launching server and waiting for child processes with extra arguments,  -MULTIHOME=192.168.2.18
[serverthrall] Server running successfully
[serverthrall.ServerUpdater] Auto updater ready, currently known buildid is 2729250
[serverthrall.UptimeTracker] Server Uptime at 87.06 percent
```
