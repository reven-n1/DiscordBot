from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import command, cooldown
from discord.ext.commands import Cog
from bot.__init__ import Amia
from random import choice


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot


    @cooldown(1, 86400, BucketType.user)
    @command(name="ger", aliases=["пук"])
    async def ger(self, ctx):
        """
        This this funny function farts on random server member or whoever called it
        """
        await ctx.message.delete()
        random_user = choice(ctx.message.guild.members)
        while random_user == ctx.message.author:
            random_user = choice(ctx.message.guild.members.name)
        ger_message = Amia.ger_function(ctx.message.author, random_user)
        await ctx.send(ger_message)


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Commands(bot))
