language_map = {
    'en': {
        'minute': 'minute',
        'minutes': 'minutes',
        'never': 'never'
    },
    'pl': {
        'minute': 'minuta',
        'minutes': 'minut',
        'never': 'nigdy'
    }
}

class Localization():

    def __init__(self, config):
        self.config = config

    def return_word(self, key):
        language = self.config.get('language', default='en')

        if language not in language_map:
            language = 'en'

        if key not in language_map[language]:
            return key

        return language_map[language][key]
