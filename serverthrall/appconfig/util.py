from configparser import RawConfigParser
from serverthrall import settings
import os


def _save(config, name):
    with open(name, 'w') as f:
        config.write(f)


def _load(name)
    config = RawConfigParser()
    config.optionxform = str

    try:
        with open(name) as f:
            config.readfp(f)
    except IOError:
        return None
    return config

def config_save(config):
    _save(settings.CONFIG_NAME)

def config_load():
    return _load(settings.CONFIG_NAME)

def config_save(config):
    _save(settings.DATA_NAME)

def data_load():
    return _load(settings.DATA_NAME)
