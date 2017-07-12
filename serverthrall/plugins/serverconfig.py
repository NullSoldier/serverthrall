from .thrallplugin import ThrallPlugin
from configparser import NoOptionError


class ServerConfig(ThrallPlugin):

    CONFIG_MAPPING = {
        'ServerName':           ('Engine', 'OnlineSubsystemSteam', 'ServerName'),
        'ServerPassword':       ('Engine', 'OnlineSubsystemSteam', 'ServerPassword'),
        'QueryPort':            ('Engine', 'OnlineSubsystemSteam', 'QueryPort'),
        'Port':                 ('Engine', 'URL', 'Port'),
        'MaxPlayers':           ('Game', '/Script/Engine.GameSession', 'MaxPlayers'),
        'AdminPassword':        ('ServerSettings', 'ServerSettings', 'AdminPassword'),
        'MaxNudity':            ('ServerSettings', 'ServerSettings', 'MaxNudity'),
        'IsBattleEyeEnabled':   ('ServerSettings', 'ServerSettings', 'IsBattleEyeEnabled'),
        'ServerRegion':         ('ServerSettings', 'ServerSettings', 'ServerRegion'),
        'ServerCommunity':      ('ServerSettings', 'ServerSettings', 'ServerCommunity'),
        'PVPBlitzServer':       ('ServerSettings', 'ServerSettings', 'PVPBlitzServer'),
        'PVPEnabled':           ('ServerSettings', 'ServerSettings', 'PVPEnabled'),
        'NetServerMaxTickRate': ('Engine', '/Script/OnlineSubsystemUtils.IpNetDriver', 'NetServerMaxTickRate'),
    }

    DEFAULT_WHITE_LIST = []

    def config_get_safe(self, src):
        try:
            return self.config.get(src)
        except NoOptionError:
            return None

    def sync_mapping(self, mapping):
        changed = False

        for src, dest in self.CONFIG_MAPPING.items():
            group, section, option = dest

            value = self.config_get_safe(src)
            original = self.thrall.conan_config.get(group, section, option)

            if value is not None and value != original:
                use_default_config = option in self.DEFAULT_WHITE_LIST
                path = self.thrall.conan_config.set(group, section, option, value, use_default_config)
                self.logger.info('Syncing %s.%s=%s, %s' % (section, option, value, path))
                changed = True

        return changed

    def tick(self):
        self.thrall.conan_config.refresh()
        changed = self.sync_mapping(self.CONFIG_MAPPING)

        if changed:
            self.logger.info('Restarting server for config to take into affect')
            self.server.close()
            self.thrall.conan_config.save()
            self.server.start()
