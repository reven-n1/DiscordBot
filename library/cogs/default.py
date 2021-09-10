from discord.ext.commands import command
from discord.ext.commands import Cog
from lib.__init__ import Amia
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


    @command(name="clear", aliases=["очистить"])
    async def clear(self, ctx):
        """
        Clears channel from messages(takes quantity to delete)(in default 1000)
        """
        await ctx.message.delete()
        message_text = ctx.message.content.split()
        if len(message_text) == 2 and message_text[1].isdigit():
            await ctx.message.channel.purge(limit=int(ctx.message.content.split()[1]))
        else:
            clear_limit = await Amia.server_delete_quantity
            await ctx.message.channel.purge(limit=clear_limit)


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Commands(bot))
