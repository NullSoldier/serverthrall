class SettingInfo():

    def __init__(self, file, section, option, default=None, unquote=False, transform=str):
        self.file = file
        self.section = section
        self.option = option
        self.default = default
        self.unquote = unquote
        self.transform = transform

    def __str__(self):
        return '%s.%s.%s' % (self.file, self.section, self.option)


CONAN_SETTINGS_MAPPING = {
    'ServerName':           SettingInfo('Engine', 'OnlineSubsystem', 'ServerName', unquote=True),
    'ServerPassword':       SettingInfo('Engine', 'OnlineSubsystem', 'ServerPassword'),
    'QueryPort':            SettingInfo('Engine', 'OnlineSubsystemSteam', 'GameServerQueryPort', default='27015'),
    'NetServerMaxTickRate': SettingInfo('Engine', '/Script/OnlineSubsystemUtils.IpNetDriver', 'NetServerMaxTickRate'),

    'RconEnabled':  SettingInfo('Game', 'RconPlugin', 'RconEnabled'),
    'RconPassword': SettingInfo('Game', 'RconPlugin', 'RconPassword'),
    'RconPort':     SettingInfo('Game', 'RconPlugin', 'RconPort'),
    'RconMaxKarma': SettingInfo('Game', 'RconPlugin', 'RconMaxKarma'),
    'MaxPlayers':   SettingInfo('Game', '/Script/Engine.GameSession', 'MaxPlayers'),

    'AdminPassword':                    SettingInfo('ServerSettings', 'ServerSettings', 'AdminPassword'),
    'MaxNudity':                        SettingInfo('ServerSettings', 'ServerSettings', 'MaxNudity'),
    'IsBattlEyeEnabled':                SettingInfo('ServerSettings', 'ServerSettings', 'IsBattlEyeEnabled'),
    'ServerRegion':                     SettingInfo('ServerSettings', 'ServerSettings', 'serverRegion', default=0),
    'ServerCommunity':                  SettingInfo('ServerSettings', 'ServerSettings', 'ServerCommunity'),
    'PVPEnabled':                       SettingInfo('ServerSettings', 'ServerSettings', 'PVPEnabled'),
    'BuildingPreloadRadius':            SettingInfo('ServerSettings', 'ServerSettings', 'BuildingPreloadRadius'),
    'MaxBuildingDecayTime':             SettingInfo('ServerSettings', 'ServerSettings', 'MaxBuildingDecayTime'),
    'MaxDecayTimeToAutoDemolish':       SettingInfo('ServerSettings', 'ServerSettings', 'MaxDecayTimeToAutoDemolish'),

    'PlayerOfflineThirstMultiplier':    SettingInfo('ServerSettings', 'ServerSettings', 'PlayerOfflineThirstMultiplier', transform=float),
    'PlayerOfflineHungerMultiplier':    SettingInfo('ServerSettings', 'ServerSettings', 'PlayerOfflineHungerMultiplier', transform=float),
    'PlayerIdleThirstMultiplier':    SettingInfo('ServerSettings', 'ServerSettings', 'PlayerIdleThirstMultiplier', transform=float),
    'PlayerIdleHungerMultiplier':    SettingInfo('ServerSettings', 'ServerSettings', 'PlayerIdleHungerMultiplier', transform=float),
    'PlayerActiveThirstMultiplier':    SettingInfo('ServerSettings', 'ServerSettings', 'PlayerActiveThirstMultiplier', transform=float),
    'PlayerActiveHungerMultiplier':    SettingInfo('ServerSettings', 'ServerSettings', 'PlayerActiveHungerMultiplier', transform=float),

    'LogoutCharactersRemainInTheWorld': SettingInfo('ServerSettings', 'ServerSettings', 'LogoutCharactersRemainInTheWorld'),

    'KickAFKPercentage': SettingInfo('ServerSettings', 'ServerSettings', 'KickAFKPercentage', transform=float),
    'KickAFKTime':       SettingInfo('ServerSettings', 'ServerSettings', 'KickAFKTime', transform=float),
}
