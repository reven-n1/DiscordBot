from discord.ext.commands import Cog


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_member_join(self, member):
        """
        On join command greets new member and send him rules
        """
        await member.send("f")

    
    @Cog.listener()
    async def on_member_remove(self, member):
        """
        On join command greets new member and send him rules
        """
        await self.bot.channel("основной").send("fck u")
    


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Commands(bot))
