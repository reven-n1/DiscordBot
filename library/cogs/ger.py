from discord.ext.commands.core import is_nsfw, guild_only
from discord.ext.commands import command, cooldown
from library import data, user_guild_cooldown
from discord.ext.commands import Cog
from random import randint, choice
from library import db, bot
from random import choice
from library import data
import discord


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__ger_self_chance = data.get_self_ger_chanse
        self.__ger_self_phrases = data.get_ger_self_phrases
        self.__ger_phrases = data.get_ger_phrases
        self.__db = db
        
        
    # cog commands ----------------------------------------------------------------------------------------------
    
    @is_nsfw()
    @guild_only()
    @cooldown(1, data.get_ger_cooldown, user_guild_cooldown)
    @command(name="ger", aliases=["пук"],
    brief='Пукает в рандома, или в себя)', description='Пукает в рандома, или в себя)')
    async def ger(self, ctx):
        """
        This funny function farts on random server member or whoever called it
        """
        await ctx.message.delete()
        random_user = choice(ctx.message.guild.members)
        while random_user == ctx.message.author:
            random_user = choice(ctx.message.guild.members)
        ger_message = self.ger_function(ctx.message.author, random_user)
        await ctx.send(ger_message)
    
    
    # functions ----------------------------------------------------------------------------------------------

    def ger_function(self, message_author:discord.member.Member, random_member:discord.member.Member) -> str:
        """
        Farts on random server member or whoever called it

        Args:
            message_author (message.author.id): requestor id
            random_member (guild.member): random guild member

        Returns:
            str: string with fart phrase
        """
        self.__db.statistic_increment('ger')
        if random_member.bot:
            self.__db.statistic_increment('ger_bot')
        if random_member.id == bot.user.id:
            self.__db.statistic_increment('ger_me')
        if randint(0, 101) >= self.__ger_self_chance:  # Chance to обосраться
            return (f"{message_author.mention} "
                    f"{choice(self.__ger_phrases)} {random_member.mention}")
        else:
            self.__db.statistic_increment('self_ger')
            return f"{message_author.mention} {choice(self.__ger_self_phrases)}"  # Самообсер



def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Commands(bot))    