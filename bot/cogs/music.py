from discord.ext.commands import command
from discord.ext.commands import Cog
from bot.Bot import Bot as Amia


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot


#TODO: rewrite music cog file(all possible commands)



def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Commands(bot))
