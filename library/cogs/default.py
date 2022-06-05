from discord import ApplicationContext, Interaction, Member, Option, TextChannel, slash_command, user_command
from discord.ext.commands import cooldown, guild_only
from library import user_guild_cooldown
from library.data.data_loader import DataHandler
from library.data.data_loader import DataHandler
from library.data.db.database import Database, Statistic, StatisticParameter, UsersArkCollection, UsersStatisticCounter
from library.data.pressf_images import fimages
from discord.ext.commands import Cog
from collections import namedtuple
from random import choice
import discord
import logging


data = DataHandler()


class Default(Cog):
    qualified_name = 'Default'
    description = 'Стандартные команды'

    def __init__(self, bot):
        self.bot = bot
        self.name = "Texass"
        self.__db = Database()
        self.options = DataHandler()

    # cog commands

    @slash_command(name="ping",
                   description='Замеряет задержку в развитии, твоем)')
    async def ping_slash(self, ctx: Interaction):
        """
        Checks ping
        """
        await ctx.response.send_message(f"Pong! {round(self.bot.latency*1000, 1)} ms")

    @slash_command(name="say",
                   description="Я скажу все что ты хочешь, братик.")
    @guild_only()
    @discord.default_permissions(
        administrator=True
    )
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
        emb = discord.Embed(title=title, color=user.color)
        emb.set_image(url="https://pbs.twimg.com/media/D-5sUKNXYAA5K9l.jpg")
        return emb

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
        emb = discord.Embed(title=title, color=user.color)
        emb.set_image(url=choice(fimages))
        return emb

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
        embed = discord.Embed(color=user.color, title=self.name,
                              url="https://discord.com/oauth2/authorize?client_id=885800080169398292&scope=&scope=applications.commands%20bot&permissions=3401792")
        embed.add_field(name="Описание",
                        value="Тупая деффка еще и бот", inline=False)
        embed.add_field(name="Версия", value=self.bot.VERSION, inline=False)
        with self.__db.get_session() as session:
            ark_total = session.query(Statistic.value).filter(Statistic.parameter_name == Statistic.Parameter.ARK.value).limit(1).scalar() or 0
            ark_total_chars = session.query(UsersArkCollection).count()
            ark_highest_six_user = session.query(UsersArkCollection.user_id).order_by(UsersArkCollection.operator_count.desc()).limit(1).scalar() or ''
            ark_highest_six_count = session.query(UsersArkCollection.operator_count).order_by(UsersArkCollection.operator_count.desc()).limit(1).scalar() or 0
            ger_stat_total = session.query(Statistic.value).filter(Statistic.parameter_name == Statistic.Parameter.GER.value).limit(1).scalar() or 0
            ger_stat_self = session.query(Statistic.value).filter(Statistic.parameter_name == Statistic.Parameter.SELF_GER.value).limit(1).scalar() or 0
            ger_stat_bot = session.query(Statistic.value).filter(Statistic.parameter_name == Statistic.Parameter.GER_BOT.value).limit(1).scalar() or 0
            ger_stat_me = session.query(Statistic.value).filter(Statistic.parameter_name == Statistic.Parameter.GER_ME.value).limit(1).scalar() or 0
            ger_uses = session.query(UsersStatisticCounter).join(StatisticParameter).filter(StatisticParameter.name == StatisticParameter.Parameter.GER_USE.value).order_by(UsersStatisticCounter.count.desc()).limit(5).all()
            ger_hit = session.query(UsersStatisticCounter).join(StatisticParameter).filter(StatisticParameter.name == StatisticParameter.Parameter.GER_HIT.value).order_by(UsersStatisticCounter.count.desc()).limit(5).all()
        embed.add_field(name="Статистика арков",
                        value=f"Арков выкручено за все время: {int(ark_total)}\nВсего собрано персонажей: {int(ark_total_chars)}", inline=False)
        embed.add_field(name="Больше всего 6* собрано",
                        value=f"<@{int(ark_highest_six_user)}> с количеством аж {int(ark_highest_six_count)} шестизведочных персонажей."
                        "Поздравляем Вас и вручаем вам самый ценный подарок: **наше увожение**",
                        inline=False)
        embed.add_field(name="Статистика пуков",
                        value=f"""Пуков за все время: {int(ger_stat_total)}
        Из них самообсеров: {int(ger_stat_self)}
        Попаданий по ботам: {int(ger_stat_bot)}
        Попаданий по мне:disappointed_relieved: : {int(ger_stat_me)}
        """, inline=False)
        embed.add_field(name="Топ засранцев",
                        value="\n".join([
                            f"<@{rec.user_id}>: {rec.count}" for rec in ger_uses
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

    @slash_command(name="info",
                   description='Информация и статистика бота')
    @guild_only()
    async def info_slash(self, ctx: ApplicationContext):
        """
        This command shows bot info
        """
        embed = self.info(ctx.author)
        await ctx.response.send_message(embed=embed, ephemeral=True)

    @slash_command(name="invite",
                   description='Показать ссылку-приглаешние этого бота')
    async def invite_slash(self, ctx: ApplicationContext):
        await ctx.respond('https://discord.com/oauth2/authorize?client_id=885800080169398292&scope=&scope=applications.commands%20bot&permissions=3401792', ephemeral=True)


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Default(bot))
