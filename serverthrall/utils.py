import pprint


def print_config(config):
    confdict = {section: dict(config.items(section)) for section in config.sections()}
    pprint.PrettyPrinter().pprint(confdict)