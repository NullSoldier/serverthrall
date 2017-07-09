from .thrallplugin import ThrallPlugin
from configparser import NoOptionError, NoSectionError


class ServerConfig(ThrallPlugin):

    CONFIG_MAPPING = {
        'ServerName':           ('Engine', 'OnlineSubsystemSteam', 'ServerName'),
        'ServerPassword':       ('Engine', 'OnlineSubsystemSteam', 'ServerPassword'),
        'GameServerQueryPort':  ('Engine', 'OnlineSubsystemSteam', 'GameServerQueryPort'),
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

    FIRST_WHITE_LIST = ('NetServerMaxTickRate',)

    def config_get_safe(self, src):
        try:
            return self.config.get(src)
        except NoOptionError:
            return None

    def sync_mapping(self,mapping):
        changed = False

        for src, dest in self.CONFIG_MAPPING.items():
            group, section, option = dest

            value = self.config_get_safe(src)
            original = self.thrall.conan_config.get(group, section, option)

            path = '%s/%s/%s=%s'

            if value is not None and value != original:
                self.logger.info('Syncing option %s to %s/%s/%s as %s' % (src, group, section, option, value))
                self.thrall.conan_config.set(group, section, option, value, option in self.FIRST_WHITE_LIST)
                changed = True

        return changed

    def tick(self):
        changed = self.sync_mapping(self.CONFIG_MAPPING)

        if changed:
            self.thrall.conan_config.save()
            self.logger.info('Restarting server for config to take into affect')
            self.server.close()
            self.server.start()