from discord.ext.commands import command
from discord.ext.commands import Cog
from Bot import Bot as Amia
from random import choice
import discord


class Commands(Cog):
    def __init__(self, bot, bot_amia):
        self.bot = bot
        self.bot_amia = bot_amia


    @command(name="hello", aliases=["hi"])
    async def hello(self, ctx):
        await ctx.send(f"{choice(('Hello', 'Hi', 'Hey', 'Hiya'))} {ctx.author.mention}!")


    @command(name="info", aliases=["инфо"])
    async def info(self, ctx):
        """
        This command set bot info and commands list to discord embed

        :param ctx: context
        :return: send discord.embed to channel
        """
        await ctx.message.delete()
        embed = discord.Embed(color=0xff9900, title=self.bot_amia.name,
                              url=f"https://www.youtube.com/watch?v=X5ULmETDiXI")
        embed.add_field(name="Description", value=self.bot_amia.bot_info["info"], inline=False)
        embed.add_field(name="Commands",
                        value=str("\n".join(self.bot_amia.get_info())),
                        inline=True)
        embed.set_thumbnail(
            url="https://aceship.github.io/AN-EN-Tags/img/characters/char_222_bpipe_race%231.png")
        embed.set_image(url="https://aceship.github.io/AN-EN-Tags/img/characters/char_002_amiya_epoque%234.png")
        embed.set_footer(text=f"Requested by {ctx.message.author.name}")
        await ctx.send(embed=embed, delete_after=30)


    @command(name="clear", aliases=["очистить"])
    async def clear(self, ctx):
        """
        Clears channel from messages

        :param ctx: context
        """
        await ctx.message.delete()
        tmp = ctx.message.content.split()
        if len(tmp) == 2 and tmp[1].isdigit():
            await ctx.message.channel.purge(limit=int(ctx.message.content.split()[1]))
        else:
            clear_limit = await self.bot_amia.server_delete_quantity
            await ctx.message.channel.purge(limit=clear_limit)


def setup(bot):
    """
    Firs function adds cogs and creates bot class instance

    :param bot: bot instance
    """
    bot_amia = Amia()
    bot.add_cog(Commands(bot, bot_amia))
