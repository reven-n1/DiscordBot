from discord.ext.commands.core import is_nsfw, guild_only
from discord.ext.commands import command, cooldown
from library import user_guild_cooldown
from library.data.data_loader import DataHandler
from library.data.db.database import Database, Statistic, StatisticParameter
from discord.ext.commands import Cog
from random import randint, choice
from library import bot
from discord import Interaction, slash_command
import discord


data = DataHandler()


class Ger(Cog):
    qualified_name = 'Ger'
    description = 'Туалетный юмор'

    def __init__(self, bot):
        self.bot = bot
        self.__ger_self_chance = data.get_self_ger_chanse
        self.__ger_self_phrases = data.get_ger_self_phrases
        self.__ger_phrases = data.get_ger_phrases

    # cog commands ----------------------------------------------------------------------------------------------

    @slash_command(name="ger",
                   description='Пукает в рандома, или в себя)')
    @is_nsfw()
    @guild_only()
    @cooldown(1, data.get_ger_cooldown, user_guild_cooldown)
    async def ger_slash(self, ctx: Interaction):
        random_user = choice(ctx.guild.members)
        while random_user == ctx.user:
            random_user = choice(ctx.guild.members)
        ger_message = await self.ger_function(ctx.user, random_user)
        await ctx.response.send_message(ger_message)

    # functions ----------------------------------------------------------------------------------------------

    async def ger_function(self, message_author: discord.member.Member, random_member: discord.member.Member) -> str:
        """
        Farts on random server member or whoever called it

        Args:
            message_author (message.author.id): requestor id
            random_member (guild.member): random guild member

        Returns:
            str: string with fart phrase
        """
        db: Database = await Database()
        await db.increment_user_statistic(random_member.id, StatisticParameter.Parameter.GER_HIT)
        await db.increment_user_statistic(message_author.id, StatisticParameter.Parameter.GER_USE)
        await db.increment_statistic(Statistic.Parameter.GER)
        if random_member.bot:
            await db.increment_statistic(Statistic.Parameter.GER_BOT)
        if random_member.id == bot.user.id:
            await db.increment_statistic(Statistic.Parameter.GER_ME)
        if randint(0, 101) >= self.__ger_self_chance:  # Chance to обосраться
            return (f"{message_author.mention} "
                    f"{choice(self.__ger_phrases)} {random_member.mention}")
        await db.increment_statistic(Statistic.Parameter.SELF_GER)
        return f"{message_author.mention} {choice(self.__ger_self_phrases)}"  # Самообсер


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Ger(bot))
