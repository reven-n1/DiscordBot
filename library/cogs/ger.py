from discord.ext.commands.core import is_nsfw, guild_only
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import command, cooldown
from library.data.json_data import ger_cooldown
from library.bots.Fun_bot import Fun_bot
from discord.ext.commands import Cog
from random import choice


Fun_bot = Fun_bot()


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @is_nsfw()
    @guild_only()
    @cooldown(1, ger_cooldown, BucketType.user)
    @command(name="ger", aliases=["пук"])
    async def ger(self, ctx):
        """
        This funny function farts on random server member or whoever called it
        """
        await ctx.message.delete()
        random_user = choice(ctx.message.guild.members)
        while random_user == ctx.message.author:
            random_user = choice(ctx.message.guild.members)
        ger_message = Fun_bot.ger_function(ctx.message.author, random_user)
        await ctx.send(ger_message)


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Commands(bot))
