from discord.ext.commands import command
from discord.ext.commands import Cog
from Bot import Bot as Amia
from random import choice
import datetime


class Commands(Cog):
    def __init__(self, bot, bot_amia):
        self.bot = bot
        self.bot_amia = bot_amia

    @command(name='ger', aliases=['пук'])
    async def ger(self, ctx):
        """
        This command calls ger function

        :param ctx: context
        :return: either cooldown or ger
        """
        await ctx.message.delete()
        random_user = choice(ctx.message.guild.members)
        while random_user == ctx.message.author:
            random_user = choice(ctx.message.guild.members.names)
        ger_message = self.bot_amia.ger_function(ctx.message.author, datetime.datetime.now(), random_user)
        if 'Идет' in ger_message:
            await ctx.send(ger_message, delete_after=7)
        else:
            await ctx.send(ger_message)


def setup(bot):
    """
    Firs function adds cogs and creates bot class instance

    :param bot: bot instance
    """
    bot_amia = Amia()
    bot.add_cog(Commands(bot, bot_amia))