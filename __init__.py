from discord.ext.commands import Bot as BotBase, CommandNotFound
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot_token import token
from logging import error
# import os.path as path
import discord
# import json

COGS = "Commands"


class Bot_init(BotBase):
    def __init__(self):
        self.Prefix = '!'
        self.Cogs = 'Commands'
        self.TOKEN = token
        self.VERSION = None
        self.scheduler = AsyncIOScheduler()
        super().__init__(command_prefix=self.Prefix)

    def setup(self):

        # path_to_json = path.abspath("settings.json")
        # with open(path_to_json,"rb") as json_settings_file:
        #     data = json.load(json_settings_file)
        #     for _ in data['settings']['cog_list']:
        #         self.load_extension(f"{_}.py")
        #         print(f"{_} - loaded")

        self.load_extension(f"{COGS}")
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

    @staticmethod
    async def on_ready():
        print(" ***bot ready***")
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game('Жизнь'))

    async def on_error(self, event_method, *args, **kwargs):
        print(error)

    async def on_command_error(self, context, exception):
        if isinstance(exception, CommandNotFound):
            await context.message.delete()
            await context.send(f'{context.message.text} - ***Wrong command, check commands list***', delete_after=15)


bot = Bot_init()
