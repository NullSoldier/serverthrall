import sqlite3
from .utils import parse_timestamp


class ConanDbClient(object):

    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def open(self):
        self.connection = sqlite3.connect(self.db_path)

    def close(self):
        self.connection.close()

    def get_characters(self):
        SQL = '''
            SELECT
                acc.online,
                ch.id,
                ch.char_name,
                ch.level,
                ch.playerId,
                ch.lastTimeOnline,
                ch.killerName,
                ch.guild,
                act.x,
                act.y,
                act.z
            FROM characters AS ch
            LEFT JOIN account AS acc ON ch.playerId = acc.user
            LEFT JOIN actor_position AS act ON ch.id = act.id;'''

        characters = []

        with sqlite3.connect(self.db_path) as connection:
            for row in connection.cursor().execute(SQL):
                characters.append({
                    'name': row[2],
                    'level': row[3],
                    'is_online': row[0],
                    'steam_id': row[4],
                    'conan_id': row[1],
                    'last_killed_by': row[6],
                    'last_online': parse_timestamp(row[5]),
                    'clan_id': row[7],
                    'x': row[8],
                    'y': row[9],
                    'z': row[10]})

        return characters

    def get_character(self, conan_id):
        raise Exception('get_character not supported')

    def get_clans(self):
        SQL = '''
            SELECT guildId, name, owner, messageOfTheDay FROM guilds
        '''

        guilds = []

        with sqlite3.connect(self.db_path) as connection:
            for row in connection.cursor().execute(SQL):
                guilds.append({
                    'id': row[0],
                    'name': row[1],
                    'owner_id': row[2],
                    'motd': row[3]
                })

        return guilds
