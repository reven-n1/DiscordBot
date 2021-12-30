from io import BytesIO
from nextcord.errors import Forbidden
from nextcord.ext.commands.context import Context
from nextcord.ext.commands.errors import CommandError, CommandOnCooldown, MissingPermissions, \
    NSFWChannelRequired, NoPrivateMessage
from nextcord import Activity, ActivityType, Game, Streaming, Intents
from nextcord.ext.commands import Bot, CommandNotFound
from library.data.dataLoader import dataHandler
from library.data.db.database import Database
from library.bot_token import token
from nextcord.embeds import Embed
from datetime import timedelta
from nextcord.ext import tasks
from random import choice
from math import ceil
import feedparser
import requests
import logging

logging.basicConfig(format='%(asctime)s|%(levelname)s|file:%(module)s.py func:%(funcName)s:%(lineno)d: %(message)s', level=logging.INFO)


class Bot_init(Bot):
    def __init__(self):
        self.Prefix = "!"
        self.TOKEN = token
        self.VERSION = None
        super().__init__(command_prefix=self.Prefix,
                         case_insensitive=True,
                         intents=Intents().all(),
                         help_command=None
                         )

    def setup(self):
        for _ in data.get_cog_list:
            self.load_extension(f"library.cogs.{_}")
        logging.info("setup complete")

    def run(self, version):
        self.VERSION = version
        logging.info("running setup...")
        self.setup()
        logging.info("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        logging.info(" bot connected")
        logging.info(f" latensy:{round(self.latency*1000, 1)} ms")
        await super().on_connect()

    async def on_ready(self):
        logging.info(" ***bot ready***")
        status_setter.start()

    async def close(self):
        logging.info("Closing on keyboard interrupt...")
        await super().close()

    async def on_error(self, event_method, *args, **kwargs):
        logging.exception(event_method)

    async def on_command_error(self, context: Context, exception: CommandError):
        try:
            await context.message.delete()
        except Forbidden as e:
            logging.warning(e)
        if isinstance(exception, CommandOnCooldown):
            cooldown_time = timedelta(seconds=ceil(exception.retry_after))
            if any(pfr in context.message.content for pfr in ["!ger", "!пук"]):
                await context.send(f"***Заряжаем жепу, осталось: {cooldown_time}***", delete_after=data.get_del_after)
            elif any(pfr in context.message.content for pfr in ["!ark", "!арк"]):
                await context.send(f"***Копим орундум, осталось: {cooldown_time}***", delete_after=data.get_del_after)
            else:
                await context.send(f"***Ожидайте: {cooldown_time}***", delete_after=data.get_del_after)

        elif isinstance(exception, CommandNotFound):
            await context.send(f"{context.message.content} - ***В последнее время я тебя совсем не понимаю*** :crying_cat_face: ", delete_after=data.get_del_after)

        elif isinstance(exception, MissingPermissions):
            await context.send(f"{context.message.author} ***- Я же сказала низя!***", delete_after=data.get_del_after)

        elif isinstance(exception, NSFWChannelRequired):
            await context.send(f"{context.message.author} ***- Доступно только в NSFW ***", delete_after=data.get_del_after)

        elif isinstance(exception, NoPrivateMessage):
            await context.send(f"{context.message.author} ***- Доступно только на сервере ***", delete_after=data.get_del_after)

        elif context.command.has_error_handler() or context.cog.has_error_handler():
            logging.warning(exception)

        else:
            context.command.reset_cooldown(context)
            embed = Embed(title=f"Здарова {context.message.author.name}", description=f"тут такое дело, вот эта команда `{context.message.content}` "
                          "вызвала ошибку. Не спамь пожалуйста, разрабов я уже оповестила, они уже решают проблему:")
            embed.set_footer(text=f'Эта смешная картинка пропадет через {data.get_del_after} секунд')
            embed.set_image(url=choice([
                'https://c.tenor.com/tZ2Xd8LqAnMAAAAd/typing-fast.gif',
                'https://c.tenor.com/TbTe1Nc6j34AAAAC/hacker-hackerman.gif',
                'https://c.tenor.com/CgGUXc-LDc4AAAAC/hacker-pc.gif',
                'https://c.tenor.com/lxkbKnHr7SoAAAAd/rocco-botte.gif',
                'https://c.tenor.com/esCBwJ7Tq4UAAAAd/pc-hack.gif',
                'https://c.tenor.com/9ItR8nSuxE0AAAAC/thumbs-up-computer.gif',
                'https://c.tenor.com/fRnYF76D4jUAAAAd/hack-hacker.gif'
            ]))
            await context.message.channel.send(embed=embed, delete_after=data.get_del_after)
            super_progers = [319151213679476737, 355344401964204033]
            for proger in super_progers:
                await self.get_user(proger).send(f"Йо, разраб, иди фикси:\nМне какой-то черт (**{context.message.author.display_name}**) "
                                                 f"написал вот такую херню: `{context.message.content}` не ну ты прикинь и вот что "
                                                 f"из этого получилось: `{exception}`\nЯ в шоке с этих даунов. Они опять сломали меня. "
                                                 "Крч жду фикс в ближайшие пару часов иначе я знаю где ты живешь.")
            logging.exception(exception)


db = Database()
bot = Bot_init()
data = dataHandler()


def user_guild_cooldown(msg):
    guild_id = msg.guild.id
    user_id = msg.author.id
    return hash(str(guild_id)+str(user_id))


def user_channel_cooldown(msg):
    channel_id = msg.channel.id
    user_id = msg.author.id
    return hash(str(channel_id)+str(user_id))


@tasks.loop(minutes=5.0)
async def status_setter():
    try:
        resp = requests.get('https://myanimelist.net/rss.php?type=rwe&u=wladbelsky', timeout=60.0)
    except requests.ReadTimeout:
        logging.warn("Timeout when reading MAL RSS")
        return

    content = BytesIO(resp.content)

    try:
        feed = feedparser.parse(content)
        await bot.change_presence(activity=Activity(type=ActivityType.watching, name=feed['entries'][0]['title']))
    except IndexError:
        logging.warn('MAL RSS response invalid')
