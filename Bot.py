import datetime
import math
import random
import sqlite3
from Bot_Token import token

db = sqlite3.connect('Bot_DB.db')
cursor = db.cursor()


class bot:
    def __init__(self):
        self.token = token
        self.name = 'Amia(bot)'
        self.bot_img = 'BotImg.png'  # !!!!!!!!!!!!!!!!!!
        self.bot_channels = ['arkbot', '']
        self.delete_quantity = 100
        self.ger_self_chance = 10
        self.ger_recoil = 86400
        self.ark_recoil = 12
        self.six_star_chance = 2
        self.five_star_chance = 10
        self.four_star_chance = 60
        self.three_star_chance = 100
        self.bot_info = {'info': ' - хуйня никому не нужная(бот тупой, но перспективный(нет))',
                         'commands': {'!ger или !пук': 'Смачный пердеж кому-нибудь куда-нибудь..',
                                      '!myark или !майарк': 'Все полученые персонажи',
                                      '!ark или !арк': 'Рол персонажа',
                                      '!clear': 'Удаляет последние 10 сообщений(кол-во можно настроить)'}}
        self.ger_variants = ['пернул в ротешник', 'насрал в рот', 'высрал какулю на лицо']
        self.bot_commands = ['!ger', '!пук', '!арк', '!ark', '!clear', '!members', '!commands']
        self.ger_self_variants = ['обосрался с подливой', 'напрудил в штанишки']

    def get_info(self):
        out_str = self.name + self.bot_info['info']
        return out_str

    def get_commands(self):
        out_str = ''
        for key, values in self.bot_info['commands'].items():
            out_str += f'{key} - {values}\n'
        return out_str

    def get_init_members_list(self, client_guilds):  # Use once when init to server
        for member in client_guilds:
            cursor.execute(f"INSERT INTO users_ger VALUES ( ?,?)",
                           (str(member), datetime.datetime(2020, 11, 11, 11, 11, 11, 111111)))
            db.commit()

            print(member)

    def ger_function(self, messege, guilds, tme, file='GerList.txt'):

        # ->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Open file(GerList.txt) with ger recoils and check last ger time
        # if it's the first time(no date)  -> set date to 2020 year to allow user use !ger
        cursor.execute(f"SELECT * FROM users_ger WHERE user_name == '{messege.author}'")
        res = cursor.fetchone()
        if res is None:
            cursor.execute(f"INSERT INTO users_ger VALUES (?,?)", (f"{messege.author}", datetime.datetime.now()))
            last_time = datetime.datetime(2020, 11, 11, 11, 11, 11)
            db.commit()
        else:
            last_time = datetime.datetime.strptime(res[1], '%Y-%m-%d %H:%M:%S.%f')

        # with open(file, 'r') as f:
        #     for line in f:
        #         if f'{messege.author}' in line:
        #             tmp = line.replace(f'{messege.author}', '')
        #             if tmp.lstrip() == '':
        #                 last_time = datetime.datetime(2020, 11, 11, 11, 11, 11)
        #             else:
        #                 last_time = tmp.strip()
        #                 last_time = datetime.datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S.%f')

        # ->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        time_difference = tme - last_time  # Разница во времени между сейчас и прошлым прокрутом
        time_difference = math.floor(time_difference.total_seconds())  # Перевел в секунды
        sec = divmod(math.floor(time_difference), 60)  # sec[1] - секунды / sec[0] - оставшиеся минуты
        minutes = divmod(sec[0], 60)  # minutes[1] - минуты / minutes[0] - часы
        hours = minutes[0]  # часы

        if hours >= self.ger_recoil / 3600:  # If more time passed allow !ger

            cursor.execute(
                f"UPDATE users_ger SET last_ger_time = '{datetime.datetime.now()}' WHERE user_name ='{messege.author}'")
            db.commit()

            if random.randint(0, 101) >= self.ger_self_chance:  # Chance to обосраться

                # for line in fileinput.input(file, inplace=1):  # Set new time of !ger
                #     if f'{messege.author}' in line:
                #         line = line.replace(line, f'{messege.author} {tme}\n')
                #     sys.stdout.write(line)

                for guild in guilds:
                    tmp = random.choice(guild.members)
                    while tmp == messege.author:  # Не дать автору серануть в себя
                        tmp = random.choice(guild.members)
                    return (f'{messege.author.mention} '
                            f'{random.choice(self.ger_variants)} {tmp.mention}')
            else:
                return f'{messege.author.mention} {random.choice(self.ger_self_variants)}'  # Самообсер

        else:  # if passed time less then 24 h
            time_difference2 = self.ger_recoil - time_difference
            sec = divmod(math.floor(time_difference2), 60)  # sec[1] - секунды / sec[0] - оставшиеся минуты
            minutes = divmod(sec[0], 60)  # minutes[1] - минуты /
            hours = minutes[0]  # minutes[0] - часы
            if hours == 0:  # choice return output variants
                return f'Идет зарядка жопы, осталось {minutes[1]} мин {sec[1]} сек'
            elif hours == 0 and minutes[1] == 0:
                return f'Идет зарядка жопы, осталось {sec[1]} сек'
            else:
                return f'Идет зарядка жопы, осталось {hours} ч {minutes[1]} мин {sec[1]} сек'

    def get_ark_rarity(self):

        rarity = random.randrange(0, 100)
        if rarity <= self.six_star_chance:
            return 0
        elif rarity <= self.five_star_chance:
            return 0
        elif rarity <= self.four_star_chance:
            return 0
        elif rarity <= self.three_star_chance:
            return 0
