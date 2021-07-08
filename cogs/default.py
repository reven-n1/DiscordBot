from discord.ext.commands import command
from discord.ext.commands import Cog
from Bot import Bot as Amia
from random import choice
import datetime
import discord
import re



class Commands(Cog):
    def __init__(self, bot, bot_amia):
        self.bot = bot
        self.bot_amia = bot_amia

    @command(name="test", aliases=["тест"])
    async def test(self, ctx):
        await ctx.send(f"test by - {ctx.author.mention}!")


def setup(bot):
    """
    Firs function adds cogs and creates bot class instance

    :param bot: bot instance
    """
    bot_amia = Amia()
    bot.add_cog(Commands(bot, bot_amia))
