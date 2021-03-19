# from random import choice
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot as BotBase, CommandNotFound
# from discord.ext import tasks
from Bot_Token import token

COGS = "Commands"


class Bot(BotBase):
    def __init__(self):
        self.Prefix = '!'
        self.Cogs = 'Commands'
        self.TOKEN = token
        self.VERSION = None
        self.scheduler = AsyncIOScheduler()
        super().__init__(command_prefix=self.Prefix)

    def setup(self):
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

    async def on_command_error(self, context, exception):
        if isinstance(exception, CommandNotFound):
            await context.send('***Wrong command, check commands list***')
    #
    # @tasks.loop(seconds=5.0)
    # async def status_setter(self):
    #     status = ['a','b','c']
    #     activity = discord.Game(name=choice(status))
    #     await bot.change_presence(status=discord.Status.idle, activity=activity)


bot = Bot()
