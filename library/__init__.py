from discord.ext import commands
from discord.ext.commands.core import command
from discord.ext.commands.errors import CommandOnCooldown, MissingPermissions, \
NSFWChannelRequired, NoPrivateMessage
from discord import Activity, ActivityType, Game, Streaming, Intents
from discord.ext.commands import Bot as BotBase, CommandNotFound
from library.bots.Default_bot import Default_bot
from library.data.dataLoader import dataHandler
from library.data.db.database import Database
from library.bot_token import token
from datetime import timedelta
from discord.ext import tasks
from random import randint
from logging import error
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
        for _ in data.get_cog_list:
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
        await context.message.delete(delay=data.get_del_delay)
 
        if isinstance(exception, CommandOnCooldown):
            cooldown_time = timedelta(seconds=ceil(exception.retry_after))
            if any(pfr in context.message.content for pfr in ["!ger", "!пук"]):
                await context.send(f"***Заряжаем жепу, осталось: {cooldown_time}***", delete_after=data.get_del_after)
            elif any(pfr in context.message.content for pfr in ["!ark", "!арк"]):
                await context.send(f"***Копим орундум, осталось: {cooldown_time}***", delete_after=data.get_del_after)
            else:
                await context.send(f"***Ожидайте: {cooldown_time}***", delete_after=data.get_del_after)
            
        elif isinstance(exception, CommandNotFound):
            await context.send(f"{context.message.content} - ***В последнее время я тебя совсем не понимаю***:crying_cat_face: ", delete_after=data.get_del_after)

        elif isinstance(exception, MissingPermissions):
            await context.send(f"{context.message.author} ***- Я же сказала низя!***", delete_after=data.get_del_after)

        elif isinstance(exception, NSFWChannelRequired):
            await context.send(f"{context.message.author} ***- Доступно только в NSFW ***", delete_after=data.get_del_after)

        elif isinstance(exception, NoPrivateMessage):
            await context.send(f"{context.message.author} ***- Доступно только на сервере ***", delete_after=data.get_del_after)
            
        elif context.command.has_error_handler() or context.cog.has_error_handler():
            return

        else:
            await context.message.channel.send(f"Здарова {context.message.author.mention}, тут такое дело, вот эта команда "
                                               f"`{context.message.content}` вызвала ошибку, разрабов я уже оповестила, "
                                               "так что не спамь там все дела, веди себя хорошо)"
                                                ,delete_after=data.get_del_after)
            #super_progers = [319151213679476737, 355344401964204033]
            super_progers = [355344401964204033]
            for proger in super_progers:
                await self.get_user(proger).send(f"Йо, разраб, иди фикси:\nМне какой-то черт (**{context.message.author.display_name}**) "
                                                  f"написал вот такую херню: `{context.message.content}` не ну ты прикинь и вот что "
                                                  f"из этого получилось: `{exception}`\nЯ в шоке с этих даунов. Они опять сломали меня. "
                                                  "Крч жду фикс в ближайшие пару часов иначе я знаю где ты живешь.")
            print(exception)


bot = Bot_init()
Amia = Default_bot()
db = Database()
data = dataHandler()


@tasks.loop(minutes=1.0)
async def status_setter():
    statuses = [gaming_status, listening_status, streaming_status, watching_status]
    random_status = randint(0, 3)
    await statuses[random_status](data.get_bot_status(statuses[random_status].__name__))


async def streaming_status(status):
    await bot.change_presence(activity=Streaming(name=status, url="https://www.twitch.tv/recrent"))


async def gaming_status(status):
    await bot.change_presence(activity=Game(status))


async def watching_status(status):
    await bot.change_presence(activity=Activity(type=ActivityType.watching, name=status))


async def listening_status(status):
    await bot.change_presence(activity=Activity(type=ActivityType.listening, name=status))