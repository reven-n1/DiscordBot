import datetime
import json
import math
import random
import sqlite3
from Bot_Token import token

db = sqlite3.connect('Bot_DB.db')
cursor = db.cursor()


class Bot:
    def __init__(self):
        self.token = token
        self.name = 'Amia(bot)'
        self.bot_img = 'BotImg.png'
        self.bot_channels = ['arkbot', 'bots', 'android']
        self.delete_quantity = 100
        self.ger_self_chance = 10
        self.ger_recoil = 86400
        self.ark_recoil = 28800
        self.six_star_chance = 2
        self.five_star_chance = 10
        self.four_star_chance = 60
        self.three_star_chance = 100
        self.stars_0_5 = '<:star:801095671720968203>'
        self.stars_6 = '<:star2:801105195958140928>'
        self.bot_info = {'info': ' хуйня никому не нужная(бот тупой, но перспективный(нет))',
                         'commands': {'!ger или !пук': 'Смачный пердеж кому-нибудь куда-нибудь..',
                                      '!myark или !майарк': 'Все полученые персонажи',
                                      '!ark или !арк': 'Рол персонажа',
                                      '!clear': 'Удаляет последние 100 сообщений(или число указанное после команды)'}}
        self.ger_variants = ['пернул в ротешник', 'насрал в рот', 'высрал какулю на лицо']
        self.bot_commands = ['!ger', '!пук', '!арк', '!ark', '!clear', '!members', '!commands']
        self.ger_self_variants = ['обосрался с подливой', 'напрудил в штанишки']
        # self.statuses = ['Warface', 'Жизнь', 'твоего батю', 'человека', 'Detroit: Become Human', 'RAID: Shadow Legends',
        #                  'программиста']
        self.server_music_is_pause = {}
        self.server_embed_id = {}
        self.server_previous_music = {}
        self.server_queue_list = {}

    def get_info(self):
        """
        :return: info list
        """

        info_list = []
        count = 0
        for line in self.bot_info['commands'].keys():
            info_list.append(f'{line} - ')
        for line in self.bot_info['commands'].values():
            info_list[count] += line
            count += 1

        return info_list

    @property
    async def statuses(self):
        return random.choice(self.statuses)

    async def return_delete_quantity(self):
        return self.delete_quantity

    async def add_music_to_queue(self, message, content, guild_id):
        try:
            youtube_src = content.split()[-1:1]
            self.server_queue_list[guild_id].append(youtube_src)
            await message.channel.send(f'Added to queue - `{youtube_src}!`', delete_after=15)

        except KeyError:
            youtube_src = content.split()[1]
            self.server_queue_list[guild_id] = [youtube_src]
            await message.channel.send(f'Added to queue - `{youtube_src}!`', delete_after=15)

        except IndexError:
            await message.channel.send('***Maybe you lose space or forgot to add link?***', delete_after=15)

    def get_commands(self):
        """
        :return: bot commands
        """

        out_str = ''
        for key, values in self.bot_info['commands'].items():
            out_str += f'{key} - {values}\n'
        return out_str

    def get_ark_collection(self, collection_owner_id):
        """
        This function returns al ark collection

        :param collection_owner_id: requested user id
        :return: character collection
        """

        cursor.execute(f"SELECT rarity, operator_name, operator_count FROM users_ark_collection "
                       f"WHERE user_id == '{collection_owner_id}'")
        res = sorted(cursor.fetchall())
        out_list = []
        prev_rar = 2
        for item in res:
            if prev_rar < item[0]:
                out_list.append('')
                out_list.append(f'{self.stars_0_5 * item[0]}')
            elif prev_rar < item[0] == 6:
                out_list.append('')
                out_list.append(f'{self.stars_6 * item[0]}')

            out_list.append(f'{item[1]} x{item[2]}')
            prev_rar = item[0]
        return out_list

    def ger_function(self, message_author, current_time, random_member):
        """
        "nf aeyrwbz gthlbn d hfyljvyjuj xktyf rfyfkf

        :param message_author: message_author
        :param current_time: datetime.now()
        :param random_member: random server member from server list
        :return: either cooldown time or ger
        """

        cursor.execute(f"SELECT user_id, last_ger FROM guild_users_info WHERE user_id == '{message_author.id}'")
        res = cursor.fetchone()
        if res is None:
            cursor.execute(f"INSERT INTO guild_users_info VALUES (?,?,?)",
                           (f"{message_author.id}", None, datetime.datetime.now()))
            last_time = datetime.datetime(2020, 11, 11, 11, 11, 11)
            db.commit()
        elif res[1] is None:
            last_time = datetime.datetime(2020, 11, 11, 11, 11, 11)
        else:
            last_time = datetime.datetime.strptime(res[1], '%Y-%m-%d %H:%M:%S.%f')

        time_difference = self.return_time_difference(current_time, last_time, 'ger')

        if time_difference is True:  # If more time passed allows !ger
            cursor.execute(
                f"UPDATE guild_users_info SET last_ger = '{datetime.datetime.now()}' WHERE user_id ='{message_author.id}'")
            db.commit()

            if random.randint(0, 101) >= self.ger_self_chance:  # Chance to обосраться

                return (f'{message_author.mention} '
                        f'{random.choice(self.ger_variants)} {random_member.mention}')
            else:
                return f'{message_author.mention} {random.choice(self.ger_self_variants)}'  # Самообсер

        else:
            return time_difference

    @staticmethod
    def get_barter_list(author_id):
        """
        Creates list of characters fro barter

        :param author_id: author id
        :return: list that contains rarity and character count
        """

        cursor.execute(
            f"SELECT rarity, operator_count, operator_name FROM users_ark_collection WHERE user_id == '{author_id}'"
            f" AND operator_count > 5 ")
        res = sorted(cursor.fetchall())
        barter_list = []
        for rarity, count, name in res:
            if rarity < 6:
                barter_list.append([rarity + 1, count // 5])
            new_count = count % 5
            if new_count == 0:
                cursor.execute(
                    f"DELETE FROM users_ark_collection WHERE user_id == '{author_id}' AND operator_count >= 5 ")
            else:
                cursor.execute(f"UPDATE users_ark_collection SET operator_count = '{new_count}'"
                               f"WHERE user_id ='{author_id}'AND operator_name == '{name}'")
            db.commit()
        return barter_list

    def ark_barter(self, barter_list, author_id):
        """
        Exchanges characters and calls function to add them to db

        :param barter_list: character list for barter
        :param author_id: author id
        :return: yield random character from list
        """

        for operators in barter_list:
            for count in range(0, operators[1]):
                choice_list = self.return_choice_list(operators[0])
                random_choice = random.choice(list(choice_list.values()))
                self.add_ark_to_db(author_id, random_choice)
                yield random_choice

    def return_choice_list(self, rarity):
        """
        This function creates list of characters

        :param rarity: character rarity
        :return: character list matching the rarity
        """

        choice_list = {}
        file = open('char_table.json', "rb")
        json_data = json.loads(file.read())  # Извлекаем JSON
        for line in json_data:
            tmp = json_data[str(line)]
            json_rarity = int(tmp['rarity']) + 1
            if rarity == json_rarity and tmp['itemDesc'] is not None:  # to ignore magalan skills and other rarities
                profession = ''
                if tmp['profession'] == 'CASTER':
                    profession = 'https://aceship.github.io/AN-EN-Tags/img/classes/class_caster.png'
                elif tmp['profession'] == 'SNIPER':
                    profession = 'https://aceship.github.io/AN-EN-Tags/img/classes/class_sniper.png'
                elif tmp['profession'] == 'WARRIOR':
                    profession = 'https://aceship.github.io/AN-EN-Tags/img/classes/class_guard.png'
                elif tmp['profession'] == 'PIONEER':
                    profession = 'https://aceship.github.io/AN-EN-Tags/img/classes/class_vanguard.png'
                elif tmp['profession'] == 'SUPPORT':
                    profession = 'https://aceship.github.io/AN-EN-Tags/img/classes/class_supporter.png'
                elif tmp['profession'] == 'MEDIC':
                    profession = 'https://aceship.github.io/AN-EN-Tags/img/classes/class_medic.png'
                elif tmp['profession'] == 'SPECIAL':
                    profession = 'https://aceship.github.io/AN-EN-Tags/img/classes/class_specialist.png'
                elif tmp['profession'] == 'TANK':
                    profession = 'https://aceship.github.io/AN-EN-Tags/img/classes/class_defender.png'
                character_id = line
                name = tmp['name'].replace(' ', '_').replace("'", "")
                description_first_part = tmp['itemUsage']
                description_sec_part = tmp['itemDesc']
                position = tmp['position']
                tags = ', '.join(tmp['tagList'])
                traits = tmp['description']
                if json_rarity == 6:
                    stars = self.stars_6
                else:
                    stars = self.stars_0_5
                choice_list[name] = character_id, name, description_first_part, description_sec_part, \
                                    position, tags, traits, profession, stars, json_rarity

        file.close()
        return choice_list

    def get_ark_rarity(self):
        """
        :return: random character rarity
        """

        rarity = random.randrange(0, 100000)
        if rarity <= self.six_star_chance * 1000:
            return 6
        elif rarity <= self.five_star_chance * 1000:
            return 5
        elif rarity <= self.four_star_chance * 1000:
            return 4
        elif rarity <= self.three_star_chance * 1000:
            return 3

    def get_ark(self, time_now, author_id):
        """
        Djpdhfoftn cjcjxre ltdjxre bkb reklfey

        :param time_now:
        :param author_id:
        :return: either cool down time or character data
        """

        cursor.execute(f"SELECT user_id, last_ark  FROM guild_users_info WHERE user_id == '{author_id}'")
        res = cursor.fetchone()
        if res is None:
            cursor.execute(f"INSERT INTO guild_users_info VALUES (?,?,?)",
                           (f"{author_id}", None, None))
            last_time = datetime.datetime(2020, 11, 11, 11, 11, 11)
            db.commit()
        elif res[1] is None:
            last_time = datetime.datetime(2020, 11, 11, 11, 11, 11)
        else:
            last_time = datetime.datetime.strptime(res[1], '%Y-%m-%d %H:%M:%S.%f')

        time_difference = self.return_time_difference(time_now, last_time, 'ark')

        if time_difference is True:  # If more time passed allow !ger

            choice_list = self.return_choice_list(self.get_ark_rarity())
            rand_item_from_list = random.choice(list(choice_list.values()))
            cursor.execute(
                f"UPDATE guild_users_info SET last_ark = '{datetime.datetime.now()}' WHERE user_id ='{author_id}'")

            self.add_ark_to_db(author_id, rand_item_from_list)
            return rand_item_from_list

        else:  # if passed time less then 24 h
            return time_difference

    @staticmethod
    def add_ark_to_db(author_id, rand_item_from_list):
        """
        This function adds a record to db

        :param author_id: author id
        :param rand_item_from_list: random character from list
        :return: None
        """

        cursor.execute(
            f"SELECT operator_count FROM users_ark_collection WHERE user_id == '{author_id}' "
            f"AND operator_name == '{rand_item_from_list[1]}'")
        res = cursor.fetchone()
        if res is None:
            cursor.execute(f"INSERT INTO users_ark_collection  VALUES (?,?,?,?)",
                           (f"{author_id}", rand_item_from_list[1], rand_item_from_list[9], 1))
        else:
            cursor.execute(f"UPDATE users_ark_collection SET operator_count = '{res[0] + 1}'"
                           f"WHERE user_id ='{author_id}'AND operator_name == '{rand_item_from_list[1]}'")
        db.commit()

    def return_time_difference(self, current_time, last_time, status):
        """
        This function return either True or cooldown time

        :param current_time: datetime.now()
        :param last_time: recent use
        :param status: ark or ger function
        :return:
        """
        time_difference = current_time - last_time  # Разница во времени между сейчас и прошлым прокрутом
        time_difference = math.floor(time_difference.total_seconds())  # Перевел в секунды
        sec = divmod(math.floor(time_difference), 60)  # sec[1] - секунды / sec[0] - оставшиеся минуты
        minutes = divmod(sec[0], 60)  # minutes[1] - минуты / minutes[0] - часы
        hours = minutes[0]  # часы
        if hours >= self.ger_recoil / 3600:  # If more time passed allow !ger
            return True

        else:  # if passed time less then 24 h
            if 'ark' in status:
                sentence = 'Копим орундум'
            else:
                sentence = 'Идет зарядка жепы'
            time_difference2 = self.ger_recoil - time_difference
            sec = divmod(math.floor(time_difference2), 60)  # sec[1] - секунды / sec[0] - оставшиеся минуты
            minutes = divmod(sec[0], 60)  # minutes[1] - минуты /
            hours = minutes[0]  # minutes[0] - часы
            if hours == 0:  # choice return output variants
                return f'{sentence}, осталось {minutes[1]} мин {sec[1]} сек'
            elif hours == 0 and minutes[1] == 0:
                return f'{sentence}, осталось {sec[1]} сек'
            else:
                return f'{sentence}, осталось {hours} ч {minutes[1]} мин {sec[1]} сек'
