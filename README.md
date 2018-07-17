### [Download the latest release here](https://github.com/NullSoldier/serverthrall/releases/latest) and [join discord](https://discord.gg/5dK2TdN) if you have any issues.

Server Thrall is a python based dedicated server toolbox. It's not a GUI to manage your server. It adds new features to the dedicated server that are not previously supported. I also highly recommend enabling the ApiUploader plugin to get your own live server website at http://thrallbrowser.com.

### Quickstart
* [Download the latest zipped release here](https://github.com/NullSoldier/serverthrall/releases/latest)
* [Install and Setup Serverthrall](https://github.com/NullSoldier/serverthrall/wiki/Install-and-Setup-Serverthrall)
* [Check out some Common Issues|Common Issues](https://github.com/NullSoldier/serverthrall/wiki/Common-Issues)

### How To...
 * [Send notifications to discord before restarting|Setup-Restart-Notifications](https://github.com/NullSoldier/serverthrall/wiki/Setup-Restart-Notifications)
 * [Send notifications to players in game before restarting|Setup-Restart-Notifications](https://github.com/NullSoldier/serverthrall/wiki/Setup-Restart-Notifications)
 * [Setup your server for ThrallBrowser|Thrallbrowser](https://github.com/NullSoldier/serverthrall/wiki/Thrallbrowser)
 * [View a live map of all your players using GINFO|Ginfo-Integration](https://github.com/NullSoldier/serverthrall/wiki/Ginfo-Integration)
 * [Schedule automatic restarts|Server-Restarter-Plugin](https://github.com/NullSoldier/serverthrall/wiki/Server-Restarter-Plugin)
 * [Install mods into your server|Installing-Mods](https://github.com/NullSoldier/serverthrall/wiki/Installing-Mods)
 * [Notify you when the server is down|Deadmansnitch-Plugin](https://github.com/NullSoldier/serverthrall/wiki/Deadmansnitch-Plugin)
 * [Change the language ServerThrall uses|ConfigureLanguage](https://github.com/NullSoldier/serverthrall/wiki/ConfigureLanguage)
 * [Setup two servers on the same computer|Setup-two-servers-on-the-same-computer](https://github.com/NullSoldier/serverthrall/wiki/Setup-two-servers-on-the-same-computer)

### Plugins

Do not edit serverthrall.config while serverthrall is running. Your changes will be overwritten by serverthrall.

| Name | Description |
| --- | --- |
| **[ServerConfig](https://github.com/NullSoldier/serverthrall/wiki/Server-Config-Plugin)** | Allows you to configure common server settings from your server thrall config. If the config differs from expected, the config will be edited and the server restarted. |
| **DownRecovery** | Restarts the server if the server is offline. |
| **ServerUpdater** | Checks for updates and updates the server automatically |
| **ServerRestarter** | Will restart the server at defined intervals, and sends out a warning to RCON and Discord |
| **Discord** | Sends message to discord via webhooks. |
| **RemoteConsole** | Sends messages and commands to a conan exiles server via the RCON protocol. |
| **RestartManager** | Makes sure notifications are sent out during restarts and the waiting period for a restart is respected. Used by other plugins. |
| **[UptimeTracker](https://github.com/NullSoldier/serverthrall/wiki/Uptime-Tracker-Plugin)** | Records the percentage of time the server has been online. If the server thrall is closed, this counts against the uptime percentage. |
| **[ApiUploader](https://github.com/NullSoldier/serverthrall/wiki/Api-Uploader-Plugin)** | Uploads your server data to serverthrallapi so you can see your data online. If your **server_id** was `2`, you would access your servers characters at this URL: https://thrallbrowser.com/server/2/characters and you can fetch your REST API data at https://serverthrallapi.herokuapp.com/api/2/characters |
| **[DeadManSnitch](https://github.com/NullSoldier/serverthrall/wiki/Deadmansnitch-Plugin)** | https://deadmanssnitch.com Emails you when your server is down. You can sign up for a free account which gives one limited snitch. |

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
