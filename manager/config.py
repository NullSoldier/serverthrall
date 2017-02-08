import json

DEFAULT_CONFIG = {'build_id': 0}


def save_config(config):
    print 'Saving config', config
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)


def load_config():
    config = None

    with open('config.json', 'a+') as config_file:
        config_file.seek(0)
        try:
            config = json.load(config_file)
        except ValueError:
            print 'No config found, creating new config'
            return (DEFAULT_CONFIG, True)

    return (config, False)
