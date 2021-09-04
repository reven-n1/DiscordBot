from discord.ext.commands import command, cooldown
from discord.ext.commands import Cog
from discord.ext.commands.cooldowns import BucketType
from bot.Bot import Bot as Amia


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @cooldown(1,20, BucketType.user)
    @command(name="tst3", aliases=["tst33"])
    async def test(self, ctx):
        """
        Test command
        """
        await ctx.send(ctx.message.author.id)


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Commands(bot))
