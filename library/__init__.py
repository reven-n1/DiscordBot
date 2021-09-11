from discord.ext.commands.errors import CommandOnCooldown, MissingPermissions, \
NSFWChannelRequired, NoPrivateMessage
from discord import Activity, ActivityType, Game, Streaming, Intents
from discord.ext.commands import Bot as BotBase, CommandNotFound
from library.bots.Default_bot import Default_bot
from library.data.json_data import cog_list
from library.bot_token import token
from random import randint, choice
from datetime import timedelta
from discord.ext import tasks
from logging import error
from json import load
from math import ceil
import traceback
import logging


class Bot_init(BotBase):
    def __init__(self):
        self.Prefix = "!"
        self.TOKEN = token
        self.VERSION = None
        super().__init__(command_prefix=self.Prefix, intents=Intents().all())


    def setup(self):
        bot.remove_command('help')
        for _ in cog_list:
            self.load_extension(f"library.cogs.{_}")

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

        await context.message.delete(delay=7)# TODO: change to cfg

        if isinstance(exception, CommandOnCooldown):
            cooldown_time = timedelta(seconds=ceil(exception.retry_after))
            if any(pfr in context.message.content for pfr in ["!ger", "!пук"]):
                await context.send(f"***Заряжаем жепу, осталось: {cooldown_time}***", delete_after=15)
            elif any(pfr in context.message.content for pfr in ["!ark", "!арк"]):
                await context.send(f"***Копим орундум, осталось: {cooldown_time}***", delete_after=15)
            else:
                await context.send(f"***Ожидайте: {cooldown_time}***", delete_after=15)
            
        elif isinstance(exception, CommandNotFound):
            await context.send(f"{context.message.content} - ***В последнее время я тебя совсем не понимаю***:crying_cat_face: ", delete_after=15)

        elif isinstance(exception, MissingPermissions):
            await context.send(f"{context.message.author} ***- Я же сказала низя!***", delete_after=15)

        elif isinstance(exception, NSFWChannelRequired):
            await context.send(f"{context.message.author} ***- Доступно только в NSFW ***", delete_after=15)

        elif isinstance(exception, NoPrivateMessage):
            await context.send(f"{context.message.author} ***- Доступно только на сервере ***", delete_after=15)

        else:
            print(exception)


bot = Bot_init()
Amia = Default_bot()


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