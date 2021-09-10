from discord.ext.commands import command, cooldown
from discord.ext.commands import Cog
from discord.ext.commands.cooldowns import BucketType
from library.bot.Bot import Bot as Amia
import discord


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="tst3", aliases=["tst33"])
    async def test(self, ctx):
        """
        Test command
        """
        await ctx.send(discord.utils.get(ctx.guild.channels ,name="основной").id)


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Commands(bot))
