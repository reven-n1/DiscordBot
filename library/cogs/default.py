from discord.ext.commands import command, has_permissions
from discord.ext.commands.core import guild_only
from discord.ext.commands import Cog
from library.__init__ import Amia
from random import choice
import discord


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command(name="hello", aliases=["hi"])
    async def hello(self, ctx):
        """
        Congratulations command
        """
        await ctx.message.delete()
        await ctx.send(f"{choice(('Hello', 'Hi', 'Hey', 'Hiya'))} {ctx.author.mention}!")

    @command(name="say", aliases=["скажи"], brief='This is the brief description', description='This is the full description')
    @guild_only()
    @has_permissions(administrator=True)
    async def say(self, ctx, *input):
        """
        Bot say what u what whenever u want. Need administrator rights.
        """
        #TODO: send pm or msg to channel via arguments
        await ctx.message.channel.send(" ".join(input))
        await ctx.message.delete()

    @guild_only()
    @command(name="info", aliases=["инфо"])
    async def info(self, ctx):
        """
        This command shows bot info
        """
        await ctx.message.delete()
        embed = discord.Embed(color=0xff9900, title=Amia.name,
                              url=f"https://www.youtube.com/watch?v=X5ULmETDiXI")
        embed.add_field(name="Description", value=Amia.bot_info["info"], inline=False)
        embed.add_field(name="Commands",
                        value=str("\n".join(Amia.get_info())),
                        inline=True)
        embed.set_thumbnail(
            url="https://aceship.github.io/AN-EN-Tags/img/characters/char_222_bpipe_race%231.png")
        embed.set_image(url="https://aceship.github.io/AN-EN-Tags/img/characters/char_002_amiya_epoque%234.png")
        embed.set_footer(text=f"Requested by {ctx.message.author.name}")
        await ctx.send(embed=embed, delete_after=30)


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Commands(bot))
