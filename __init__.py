from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot as BotBase, CommandNotFound
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

    async def on_command_error(self, context, exception):
        if isinstance(exception, CommandNotFound):
            await context.send('***Wrong command, check commands list***')


bot = Bot()

