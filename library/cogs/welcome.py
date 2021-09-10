from discord.ext.commands import command, cooldown
from discord.ext.commands import Cog
from discord.ext.commands.cooldowns import BucketType

#TODO: rewrite on_join -> congr new users

class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_member_join(self, member):
        """
        On join command greets new member and send him rules
        """
 
        print(member.guild.id)
        await member.guild.get_channel("основной").send("f")
        #await discord.utils.get(server.channels, name="основной").send('dd')
    
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
