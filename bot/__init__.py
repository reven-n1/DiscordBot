from discord.ext.commands.errors import CommandOnCooldown, MissingPermissions
from discord import Activity, ActivityType, Game, Streaming, Intents
from discord.ext.commands import Bot as BotBase, CommandNotFound
from random import randint, choice
from bot.bot_token import token
from datetime import timedelta
from discord.ext import tasks
from logging import error
from bot.Bot import Bot
import os.path as path
from json import load
from math import ceil
from sys import exit
import traceback
import logging

# TODO wladbelsky
# 1. roma pdr
# 2. markdaun ridme.txt
# 3. embed ark ls
# 4. music bot (colaborative task)
# 5. move any strict numbers to cfg omg it so cool to have numbers in config man! cuz it look so professiAnal
# TODO reven_n1
# 1. move key to cfg
# 2. music bot (colaborative task)
# 3. hack pentagon
# 4. make me rich
# 5. buy slaves
# 6. elect presedent
# 7. build space rocket
# 8. invent electrocar
# 9. launch fucking electrocar in space on fucking rocket wtf man r u insane???


class Bot_init(BotBase):
    def __init__(self):
        self.Prefix = "!"
        self.TOKEN = token
        self.VERSION = None
        if not path.isfile("bot/config/config.json"):
            exit("'config.json' not found!")
        self.path_to_config = path.abspath("bot/config/config.json")
        super().__init__(command_prefix=self.Prefix, intents=Intents().all())


    def setup(self):
        with open(self.path_to_config,"rb") as json_config_file:
            data = load(json_config_file)
            try:
                for _ in data["default_settings"]["cog_list"]:
                    self.load_extension(f"bot.cogs.{_}")
            except KeyError:
                exit("'config.json' is damaged!")

        print("setup complete")


    def run(self, version):
        self.VERSION = version
        print("running setup...")
        self.setup()
        print("running bot...")
        super().run(self.TOKEN, reconnect=True)


    @staticmethod
    async def on_connect():
        print(" bot connected")
        

    async def on_ready(self):
        print(" ***bot ready***")
        status_setter.start()

       
    async def on_error(self, event_method, *args, **kwargs):
        logging.warning(traceback.format_exc())
        print(error)
        print(event_method)
        

    async def on_command_error(self, context, exception):

        await context.message.delete(delay=15)#change to cfg
        if isinstance(exception, CommandOnCooldown):
            cooldown_time = timedelta(seconds=ceil(exception.retry_after))
            if context.message.content == "!ger":
                await context.send(f"***Заряжаем жепу, осталось: {cooldown_time}***", delete_after=15)
            else:
                await context.send(f"***Копим орундум, осталось: {cooldown_time}***", delete_after=15)
            

        elif isinstance(exception, CommandNotFound):
            await context.send(f"{context.message.content} - ***Wrong command, check commands list***", delete_after=15)

        elif isinstance(exception, MissingPermissions):
            await context.send(f"{context.message.author} ***- You don't have permission to do that***", delete_after=15)

        else:
            print(exception)

bot = Bot_init()
Amia = Bot()


@tasks.loop(minutes=1.0)
async def status_setter():
    statuses = [set_gaming_status, set_listening_status, set_streaming_status, set_watching_status]

    with open("config/config.json","rb") as json_config_file:
            data = load(json_config_file)
            json_statuses = data["default_settings"]["bot_statuses"]
            statuses_list = []
            for _ in json_statuses:
                statuses_list.append(_)

    random_choice = randint(0, len(statuses_list)-1)
    await statuses[random_choice](choice(json_statuses[statuses_list[random_choice]]))


async def set_streaming_status(status):
    await bot.change_presence(activity=Streaming(name=status, url="https://www.twitch.tv/recrent"))


async def set_gaming_status(status):
    await bot.change_presence(activity=Game(status))


async def set_watching_status(status):
    await bot.change_presence(activity=Activity(type=ActivityType.watching, name=status))


async def set_listening_status(status):
    await bot.change_presence(activity=Activity(type=ActivityType.listening, name=status))