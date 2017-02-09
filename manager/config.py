import json
import pprint


def save_config(config):
    print 'Saving config'
    pprint.PrettyPrinter().pprint(config)
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)


def load_config():
    with open('config.json', 'a+') as config_file:
        config_file.seek(0)
        try:
            return json.load(config_file)
        except ValueError:
            return None
