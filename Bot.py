import random
from Bot_Token import token


class bot:
    def __init__(self):
        self.token = token
        self.name = 'Amia(bot)'
        self.bot_img = 'BotImg.png'  # !!!!!!!!!!!!!!!!!!
        self.bot_channels = ['arkbot', '']
        self.delete_quantity = 100
        self.ger_self_chance = 10
        self.ger_recoil = 24
        self.ark_recoil = 12
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
        with open('GerList', 'w') as f:
            for member in client_guilds:
                f.writelines(f'{str(member)}\n')

    def ger_function(self, messege, guilds):
        if random.randint(0, 101) >= self.ger_self_chance:
            for guild in guilds:
                tmp = random.choice(guild.members)
                while tmp == messege.author:
                    tmp = random.choice(guild.members)
                return (f'{messege.author.mention} '
                        f'{random.choice(self.ger_variants)} {tmp.mention}')
        else:
            return f'{messege.author.mention} {random.choice(self.ger_self_variants)}'

    def get_ark(self):
        pass
