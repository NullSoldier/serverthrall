language_map = {
    'en': {
        'minute': 'minute',
        'minutes': 'minutes'
    },
    'pl': {
        'minute': 'minuta',
        'minutes': 'minut'
    }
}

class Localization():

    def __init__(self, config):
        self.config = config

    def return_word(self, key):
        language = self.config.get('language')

        if language is None or language not in language_map:
            language = 'en'

        if key not in language_map[language]:
            return key
        
        return language_map[language][key]