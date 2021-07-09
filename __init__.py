from discord.ext.commands import Bot as BotBase, CommandNotFound
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from random import randint, choice
from discord.ext import tasks
from bot_token import token
from logging import error
import os.path as path
from json import load
from sys import exit
import discord


class Bot_init(BotBase):
    def __init__(self):
        self.Prefix = '!'
        self.Cogs = 'Commands'
        self.TOKEN = token
        self.VERSION = None
        self.scheduler = AsyncIOScheduler()
        if not path.isfile("config.json"):
            exit("'config.json' not found!")
        self.path_to_config = path.abspath("config.json")
        super().__init__(command_prefix=self.Prefix)


    def setup(self):
        with open(self.path_to_config,"rb") as json_config_file:
            data = load(json_config_file)
            try:
                for _ in data['default_settings']['cog_list']:
                    self.load_extension(f'cogs.{_}')
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
        status_setter.start(self.path_to_config)

       
    async def on_error(self, event_method, *args, **kwargs):
        print(error)
        print(event_method)
        print(error.message)
        

    async def on_command_error(self, context, exception):
        if isinstance(exception, CommandNotFound):
            await context.message.delete()
            await context.send(f'{context.message.content} - ***Wrong command, check commands list***', delete_after=15)


bot = Bot_init()


@tasks.loop(minutes=1.0)
async def status_setter(path_to_config):
    statuses = [set_gaming_status, set_listening_status, set_streaming_status, set_watching_status]

    with open(path_to_config,"rb") as json_config_file:
            data = load(json_config_file)
            json_statuses = data['default_settings']['bot_statuses']
            statuses_list = []
            for _ in json_statuses:
                statuses_list.append(_)

            random_choice = randint(0, len(statuses_list)-1)
            await statuses[random_choice](choice(json_statuses[statuses_list[random_choice]]))


async def set_streaming_status(status):
    await bot.change_presence(activity=discord.Streaming(name='recrent', url='https://www.twitch.tv/recrent'))


async def set_gaming_status(status):
    await bot.change_presence(activity=discord.Game(status))


async def set_watching_status(status):
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="на твой песюн"))


async def set_listening_status(status):
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="a song"))
 
