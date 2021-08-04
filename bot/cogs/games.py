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
        await ctx.send(f"test by - {ctx.author.mention}!")
        await Amia.get_info()


def setup(bot):
    """
    Firs function adds cogs and creates bot class instance

    :param bot: bot instance
    """
    bot.add_cog(Commands(bot))
