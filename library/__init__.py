from io import BytesIO
from discord import ApplicationContext
from discord.errors import Forbidden
from discord.ext.commands.context import Context
from discord.ext.commands.errors import CommandError, CommandOnCooldown, MissingPermissions, \
    NSFWChannelRequired, NoPrivateMessage
from discord import Activity, ActivityType, Game, Streaming, Intents
from discord.ext.commands import Bot, CommandNotFound
from library.data.dataLoader import dataHandler
from library.data.db.database import Database
from library.bot_token import token
from discord.embeds import Embed
from datetime import timedelta
from discord.ext import tasks
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

    async def get_exception_embed(self, ctx, exception: Exception) -> Embed:
        if isinstance(exception, CommandOnCooldown):
            cooldown_time = timedelta(seconds=ceil(exception.retry_after))
            if any(pfr in ctx.command.name for pfr in ["ger", "пук"]):
                return Embed(title=f"***Заряжаем жепу, осталось: {cooldown_time}***")
            elif any(pfr in ctx.command.name for pfr in ["ark", "арк"]):
                return Embed(title=f"***Копим орундум, осталось: {cooldown_time}***")
            else:
                return Embed(title=f"***Ожидайте: {cooldown_time}***")

        elif isinstance(exception, CommandNotFound):
            return Embed(title=choice((
                "Я же предупреждала! Пользуйся слешами.",
                "Не, не, не, пользуйся слешами",
                "Команды запрещены РКН, пользуйтесь слешами",
                "Команд больше нибудит, жи. Пользуся слешами",
                "Братик, я же говорила, слеши! Бака совсем чтоли?",
                "Dolboeb found, use slashes!",
                "Никак вы блять не научитесь. Слешы юзай.",
            )))

        elif isinstance(exception, MissingPermissions):
            return Embed(title=f"{ctx.author} ***- Я же сказала низя!***")

        elif isinstance(exception, NSFWChannelRequired):
            return Embed(title=f"{ctx.author} ***- Доступно только в NSFW ***")

        elif isinstance(exception, NoPrivateMessage):
            return Embed(title=f"{ctx.author} ***- Доступно только на сервере ***")

        elif ctx.command.has_error_handler() or ctx.cog.has_error_handler():
            logging.exception(exception)

        else:
            ctx.command.reset_cooldown(ctx)
            embed = Embed(title=f"Здарова {ctx.author.name}", description=f"тут такое дело, вот эта команда `{ctx.command.name}` "
                          "вызвала ошибку. Не спамь пожалуйста, разрабов я уже оповестила, они уже решают проблему:")
            embed.set_image(url=choice([
                'https://c.tenor.com/tZ2Xd8LqAnMAAAAd/typing-fast.gif',
                'https://c.tenor.com/TbTe1Nc6j34AAAAC/hacker-hackerman.gif',
                'https://c.tenor.com/CgGUXc-LDc4AAAAC/hacker-pc.gif',
                'https://c.tenor.com/lxkbKnHr7SoAAAAd/rocco-botte.gif',
                'https://c.tenor.com/esCBwJ7Tq4UAAAAd/pc-hack.gif',
                'https://c.tenor.com/9ItR8nSuxE0AAAAC/thumbs-up-computer.gif',
                'https://c.tenor.com/fRnYF76D4jUAAAAd/hack-hacker.gif'
            ]))

            super_progers = [319151213679476737, 355344401964204033]
            for proger in super_progers:
                await self.get_user(proger).send(f"Йо, разраб, иди фикси:\nМне какой-то черт (**{ctx.author.display_name}**) "
                                                 f"написал вот такую херню: `{ctx.message.content if ctx.message else ctx.command.name}` не ну ты прикинь и вот что "
                                                 f"из этого получилось: `{exception}`\nЯ в шоке с этих даунов. Они опять сломали меня. "
                                                 "Крч жду фикс в ближайшие пару часов иначе я знаю где ты живешь.")
            logging.exception(exception)
            return embed

    async def on_command_error(self, context: Context, exception: CommandError):
        try:
            await context.message.delete()
        except Forbidden as e:
            logging.warning(e)
        content = await self.get_exception_embed(context, exception)
        if isinstance(content, str):
            await context.send(content, delete_after=data.get_del_after)
        elif isinstance(content, Embed):
            await context.send(embed=content, delete_after=data.get_del_after)

    async def on_application_command_error(self, ctx: ApplicationContext, error):
        content = await self.get_exception_embed(ctx, error.original if hasattr(error, 'original') and error.original else error)
        if not content:
            return
        if not ctx.interaction.response.is_done():
            await ctx.interaction.response.send_message(embed=content, ephemeral=True)
        else:
            await ctx.interaction.followup.send(embed=content, ephemeral=True)


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
