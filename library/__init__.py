import aiohttp
from discord import ApplicationContext
from discord.errors import Forbidden
from discord.ext.commands.context import Context
from discord.ext.commands.errors import CommandError, CommandOnCooldown, MissingPermissions, \
     NSFWChannelRequired, NoPrivateMessage
from discord import Activity, ActivityType, Intents
from discord.ext.commands import CommandNotFound
from discord import Bot
from library.data.data_loader import DataHandler
from library.bot_token import token
from discord.embeds import Embed
from datetime import timedelta
from discord.ext import tasks
from random import choice
from math import ceil
import feedparser
import logging

from library.data.db.database import Database


logging.basicConfig(format='%(asctime)s|%(levelname)s|file:%(module)s.py func:%(funcName)s:%(lineno)d: %(message)s', level=logging.INFO)


class Bot_init(Bot):
    def __init__(self):
        self.Prefix = "!"
        self.TOKEN = token
        self.VERSION = None
        intents = Intents().all()
        intents.message_content = False
        super().__init__(command_prefix=self.Prefix,
                         case_insensitive=True,
                         intents=intents,
                         help_command=None
                         )

    def setup(self):
        for _ in DataHandler().get_cog_list:
            self.load_extension(f"library.cogs.{_}")
        logging.info("setup complete")

    def run(self, version):
        self.VERSION = version
        logging.info("running setup...")
        self.setup()
        logging.info("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        logging.info("bot connected")
        logging.info(f"latensy:{round(self.latency*1000, 1)} ms")
        await super().on_connect()

    async def on_ready(self):
        logging.info("***bot ready***")
        logging.info('Servers connected to:')
        for guild in self.guilds:
            logging.info(f"{guild.name} ({guild.id}), owner: {guild.owner.name}#{guild.owner.discriminator}")
        await Database()  # init database
        self.status_setter.start()

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
            if any(pfr in ctx.command.name for pfr in ["ark", "арк"]):
                return Embed(title=f"***Копим орундум, осталось: {cooldown_time}***")
            return Embed(title=f"***Ожидайте: {cooldown_time}***")

        if isinstance(exception, CommandNotFound):
            return Embed(title=choice((
                "Я же предупреждала! Пользуйся слешами.",
                "Не, не, не, пользуйся слешами",
                "Команды запрещены РКН, пользуйтесь слешами",
                "Команд больше нибудит, жи. Пользуся слешами",
                "Братик, я же говорила, слеши! Бака совсем чтоли?",
                "Dolboeb found, use slashes!",
                "Никак вы блять не научитесь. Слешы юзай.",
            )))

        if isinstance(exception, MissingPermissions):
            return Embed(title=f"{ctx.author} ***- Я же сказала низя!***")

        if isinstance(exception, NSFWChannelRequired):
            return Embed(title=f"{ctx.author} ***- Доступно только в NSFW ***")

        if isinstance(exception, NoPrivateMessage):
            return Embed(title=f"{ctx.author} ***- Доступно только на сервере ***")

        if ctx.command.has_error_handler() or ctx.cog.has_error_handler():
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
                'https://c.tenor.com/fRnYF76D4jUAAAAd/hack-hacker.gif',
                'https://tenor.com/view/hack-pc-guy-fawkes-hacker-gif-17047231',
                'https://tenor.com/view/anton-hacker-hack-ha-bogus-gif-24545968'
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
            await context.send(content, delete_after=DataHandler().get_del_after)
        elif isinstance(content, Embed):
            await context.send(embed=content, delete_after=DataHandler().get_del_after)

    async def on_application_command_error(self, ctx: ApplicationContext, error):
        content = await self.get_exception_embed(ctx, error.original if hasattr(error, 'original') and error.original else error)
        if not content:
            return
        await ctx.respond(embed=content, ephemeral=True)

    @tasks.loop(minutes=5.0)
    async def status_setter(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://myanimelist.net/rss.php?type=rwe&u=wladbelsky', timeout=60.0) as response:
                if response.ok and response.status == 200:
                    content = await response.content.read()
                else:
                    logging.warn("Can't get status from myanimelist.net")
                    return
        try:
            feed = feedparser.parse(content)
            await self.change_presence(activity=Activity(type=ActivityType.watching, name=feed['entries'][0]['title']))
        except IndexError:
            logging.warn('MAL RSS response invalid')


bot = Bot_init()


def user_guild_cooldown(msg):
    guild_id = msg.guild.id
    user_id = msg.author.id
    return hash(str(guild_id)+str(user_id))


def user_channel_cooldown(msg):
    channel_id = msg.channel.id
    user_id = msg.author.id
    return hash(str(channel_id)+str(user_id))
