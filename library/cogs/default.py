from discord import ApplicationContext, Interaction, Member, Option, TextChannel, slash_command, user_command
from discord.ext.commands import command, has_permissions, cooldown, guild_only
from library import data, user_guild_cooldown
from library.data.dataLoader import dataHandler
from library.data.pressf_images import fimages
from discord.errors import HTTPException
from discord.ext.commands import Cog
from collections import namedtuple
from random import choice
from library import db
import discord
import logging


class Default(Cog):
    qualified_name = 'Default'
    description = 'Стандартные команды'

    def __init__(self, bot):
        self.bot = bot
        self.name = "Texass"
        self.__delete_quantity = 100
        self.__db = db
        self.options = dataHandler()
        self.embed_color = self.options.get_embed_color

    # cog commands

    @command(name="ping", aliases=["пинг"],
             brief='Замеряет задержку в развитии',
             description='Замеряет задержку в развитии, твоем)')
    async def ping_command(self, ctx):
        """
        Checks ping
        """
        await ctx.reply(f"Pong! {round(self.bot.latency*1000, 1)} ms")

    @slash_command(name="ping",
                   description='Замеряет задержку в развитии, твоем)')
    async def ping_slash(self, ctx: Interaction):
        """
        Checks ping
        """
        await ctx.response.send_message(f"Pong! {round(self.bot.latency*1000, 1)} ms")

    @command(name="say", aliases=["скажи"],
             brief='Я скажу все что ты хочешь, братик.',
             description='Я скажу все что ты хочешь, братик. Разве что тебе админом нужно быть)')
    @guild_only()
    @has_permissions(administrator=True)
    async def say(self, ctx, *args):
        """
        Bot say what u what whenever u want. Need administrator rights.
        """
        try:
            await ctx.message.delete()
        except HTTPException as e:
            logging.error(e)
        await ctx.message.channel.send(" ".join(args))
        logging.info(f'User {ctx.author.name} sent message as bot')
        logging.info(" ".join(args))

    @slash_command(name="say",
                   description="Я скажу все что ты хочешь, братик.")
    @guild_only()
    @has_permissions(administrator=True)
    async def say_slash(self, interaction: Interaction, msg: Option(str, description='Message', name='message'),
                        chnl: Option((TextChannel), name="channel", description="Choose a channel to say")):
        await self.bot.get_channel(chnl.id).send(msg)
        await interaction.response.send_message(
            "Alldone, boss", ephemeral=True
        )
        logging.info(f'User {interaction.user.name} sent message as bot')
        logging.info(msg)

    def pressf(self, user: Member, target: Member = None):
        if target:
            title = f"**{user.display_name}** заплатил увожение за {target.display_name}"
        else:
            title = f"**{user.display_name}** заплатил увожение. o7"
        emb = discord.Embed(title=title, color=self.embed_color)
        emb.set_image(url="https://pbs.twimg.com/media/D-5sUKNXYAA5K9l.jpg")
        return emb

    @command(name="f", aliases=["ф"],
             brief='Отдать честь за почивших героев',
             description='Отдать честь за почивших героев. Можно упоминанием указать кого чтим.')
    @guild_only()
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_guild_cooldown)
    async def pressf_command(self, ctx):
        """
        press f for fallen heroes.
        sends simple picture of saluting girl. can mention people
        """
        await ctx.message.channel.send(embed=self.pressf(ctx.author, ctx.message.mentions[0] if ctx.message.mentions else None))

    @slash_command(name="f",
                   description='Отдать честь за почивших героев. Можно упоминанием указать кого чтим.')
    @guild_only()
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_guild_cooldown)
    async def pressf_slash(self, ctx: Interaction, member: Option(Member, default=None)):
        """
        press f for fallen heroes.
        sends simple picture of saluting girl. can mention people
        """
        await ctx.response.send_message(embed=self.pressf(ctx.user, member))

    @user_command(name='f')
    @guild_only()
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_guild_cooldown)
    async def pressf_user(self, ctx: Interaction, member: Member):
        """
        press f for fallen heroes.
        sends simple picture of saluting girl. can mention people
        """
        await ctx.response.send_message(embed=self.pressf(ctx.user, member))

    def o7(self, user: Member, target: Member = None):
        if target:
            title = f"**{user.display_name}** приветствует {target.display_name}. o7"
        else:
            title = f"**{user.display_name}** приветствует вас командиры. o7"
        emb = discord.Embed(title=title, color=self.embed_color)
        emb.set_image(url=choice(fimages))
        return emb

    @command(name="o7", aliases=["07", "о7"],
             brief='Поприветсвовать командиров',
             description='Поприветсвовать командиров, а можно и кого-то конкретного')
    @guild_only()
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_guild_cooldown)
    async def o7_command(self, ctx):
        """
        greet fellow commanders
        can mention whom to greet
        """
        await ctx.message.channel.send(embed=self.o7(ctx.user, ctx.message.mentions[0] if ctx.message.mentions else None))

    @slash_command(name="o7", aliases=["07", "о7"],
                   description='Поприветсвовать командиров, а можно и кого-то конкретного')
    @guild_only()
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_guild_cooldown)
    async def o7_slash(self, ctx: Interaction, member: Option(Member, default=None)):
        """
        greet fellow commanders
        can mention whom to greet
        """
        await ctx.response.send_message(embed=self.o7(ctx.user, member))

    @user_command(name="o7")
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_guild_cooldown)
    @guild_only()
    async def o7_user(self, ctx: Interaction, member: Member):
        """
        greet fellow commanders
        can mention whom to greet
        """
        await ctx.response.send_message(embed=self.o7(ctx.user, member))

    @command(name="avatar", aliases=["аватар"],
             brief='Показывает аватар пользователя',
             description='Показывает твой аватар. С помощью упоминания можно посмотреть аватар другого пользователя')
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_guild_cooldown)
    async def avatar(self, ctx):
        url = None
        if ctx.message.mentions:
            title = f"Аватар {ctx.message.mentions[0].display_name}"
            if ctx.message.mentions[0].avatar:
                url = ctx.message.mentions[0].avatar.url
        else:
            title = f"Аватар {ctx.message.author.display_name}"
            if ctx.message.author.avatar:
                url = ctx.message.author.avatar.url
        if url:
            emb = discord.Embed(title=title, color=self.embed_color)
            emb.set_image(url=url)
            await ctx.send(embed=emb)
        else:
            await ctx.send('Аватар не найден')

    @user_command(
        name='Avatar'
    )
    async def avatar_user(self, interaction: Interaction, usr: Member):
        emb = discord.Embed(title='Avatarr')
        emb.set_image(url=usr.avatar.url)
        await interaction.response.send_message(
            embed=emb, ephemeral=True
        )

    def info(self, user: Member):
        embed = discord.Embed(color=self.embed_color, title=self.name,
                              url="https://discord.com/oauth2/authorize?client_id=885800080169398292&scope=bot&permissions=3401792")
        embed.add_field(name="Описание",
                        value="Тупая деффка еще и бот", inline=False)
        embed.add_field(name="Версия", value=self.bot.VERSION, inline=False)
        ark_stat = self.get_ark_stats()
        ger_stat = self.get_ger_stats()
        ger_use = self.get_stat_users('ger_use')
        ger_hit = self.get_stat_users('ger_hit')
        embed.add_field(name="Статистика арков",
                        value=f"Арков выкручено за все время: {ark_stat.total}\nВсего собрано персонажей: {ark_stat.total_chars}", inline=False)
        embed.add_field(name="Больше всего 6* собрано",
                        value=f"<@{ark_stat.best_dolboeb}> с количеством аж {ark_stat.dolboeb_count} шестизведочных персонажей."
                        "Поздравляем Вас и вручаем вам самый ценный подарок: **наше увожение**",
                        inline=False)
        embed.add_field(name="Статистика пуков",
                        value=f"""Пуков за все время: {ger_stat.total}
        Из них самообсеров: {ger_stat.total_self}
        Попаданий по ботам: {ger_stat.total_bot}
        Попаданий по мне:disappointed_relieved: : {ger_stat.total_me}
        """, inline=False)
        embed.add_field(name="Топ засранцев",
                        value="\n".join([
                            f"<@{rec.user_id}>: {rec.count}" for rec in ger_use
                        ]) or 'Статистика не найдена', inline=False)
        embed.add_field(name="Обосрали больше всего",
                        value="\n".join([
                            f"<@{rec.user_id}>: {rec.count}" for rec in ger_hit
                        ]) or 'Статистика не найдена', inline=False)

        embed.set_thumbnail(
            url="https://aceship.github.io/AN-EN-Tags/img/factions/logo_rhodes.png")
        embed.set_image(
            url="https://aceship.github.io/AN-EN-Tags/img/characters/char_102_texas_2.png")
        embed.set_footer(
            text=f"Requested by {user.display_name}")
        return embed

    @command(name="info", aliases=["инфо"],
             brief='Информация и статистика бота',
             description='Информация и статистика бота')
    @guild_only()
    async def info_command(self, ctx):
        """
        This command shows bot info
        """
        embed = self.info(ctx.author)
        await ctx.send(embed=embed, delete_after=self.options.get_chat_misc_cooldown_sec)
        try:
            await ctx.message.delete(delay=self.options.get_chat_misc_cooldown_sec)
        except Exception as e:
            logging.warning(e)

    @slash_command(name="info",
                   description='Информация и статистика бота')
    @guild_only()
    async def info_slash(self, ctx: ApplicationContext):
        """
        This command shows bot info
        """
        embed = self.info(ctx.author)
        await ctx.response.send_message(embed=embed, ephemeral=True)

    # functions----------------------------------------------------------------------------------------------------------------------------

    def __exec_stmts(self, stmts: list):
        results = []
        for stmt in stmts:
            result = self.__db.extract(stmt)
            result = int(result[0][0]) if result else 0
            results.append(result)
        return results

    def get_ark_stats(self):
        ark_stat = namedtuple(
            'ark_stat', ['total', 'total_chars', 'best_dolboeb', 'dolboeb_count'])
        return ark_stat._make(self.__exec_stmts([
            "select value from statistic where parameter_name='ark'",
            "select count(*) from users_ark_collection",
            "select user_id from users_ark_collection where rarity=6 group by user_id order by sum(operator_count) desc limit 1",
            "select sum(operator_count) from users_ark_collection where rarity=6 group by user_id order by sum(operator_count) desc limit 1"
        ]))

    def get_ger_stats(self):
        ger_stat = namedtuple(
            'ger_stat', ['total', 'total_self', 'total_bot', 'total_me'])
        return ger_stat._make(self.__exec_stmts([
            "select value from statistic where parameter_name='ger'",
            "select value from statistic where parameter_name='self_ger'",
            "select value from statistic where parameter_name='ger_bot'",
            "select value from statistic where parameter_name='ger_me'",
        ]))

    def get_stat_users(self, parameter, top=5):
        ger_top = namedtuple('stat_top', ['user_id', 'count'])
        return [ger_top._make(rec) for rec in
                self.__db.get_user_statistics(parameter, top)]

    @property
    async def server_delete_quantity(self):
        """
        Default message delete quantity getter

        Returns:
            int: quantity
        """
        return self.__delete_quantity


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Default(bot))
