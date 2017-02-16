from serverthrall import settings
import os
import ConfigParser


def config_exists():
    return os.path.isfile(settings.CONFIG_NAME)


def config_save(config):
    with open(settings.CONFIG_NAME, 'w') as f:
        config.write(f)


def config_load():
    config = ConfigParser.RawConfigParser()
    try:
        with open(settings.CONFIG_NAME) as f:
            config.readfp(f)
    except IOError:
        return None
    return config
