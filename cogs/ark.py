from discord.ext.commands import command
from discord.ext.commands import Cog
from Bot import Bot as Amia
from re import sub
import datetime
import discord


class Commands(Cog):
    def __init__(self, bot, bot_amia):
        self.bot = bot
        self.bot_amia = bot_amia


    @command(name="myark", aliases=["моидевочки"])
    async def myark(self, ctx):
        """
        This command sends embed with ark collection to channel.
        If collection empty -> returns 'Empty collection'

        :param ctx: context
        :return: discord.embed
        """
        await ctx.message.delete()
        embed = discord.Embed(color=0xff9900)
        ark_collection = self.bot_amia.get_ark_collection(ctx.message.author.id)
        if not ark_collection:
            embed.add_field(name=f"{ctx.message.author.name} collection", value="Empty collection(((")
        else:
            embed.add_field(name=f"{ctx.message.author.name} collection", value="\n".join(ark_collection))
        embed.set_thumbnail(url=ctx.message.author.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.message.author.name}")
        await ctx.send(embed=embed)


    @command(name="barter", aliases=["обмен"])
    async def barter(self, ctx):
        """
        This command serves to exchange characters if possible else returns 'Нет операторов на обмен'

        :param ctx: context
        :return: either calls ark_embed function or returns 'Нет операторов на обмен'
        """
        await ctx.message.delete()
        barter_list = self.bot_amia.get_barter_list(ctx.message.author.id)
        if barter_list:
            barter = self.bot_amia.ark_barter(barter_list, ctx.message.author.id)
            tmp = next(barter)
            try:
                while tmp:
                    await self.ark_embed(tmp, ctx.message)
                    tmp = next(barter)
            except StopIteration:
                pass
        else:
            await ctx.send("***Нет операторов на обмен***", delete_after=15)


    @command(name="ark", aliases=["арк"])
    async def ark(self, ctx):
        """
        Ark command

        :param ctx: context
        :return: either cooldown or character
        """
        await ctx.message.delete()
        tmp = self.bot_amia.get_ark(datetime.datetime.now(), ctx.message.author.id)
        if "Копим" in tmp:
            await ctx.send(tmp, delete_after=7)
        else:
            await self.ark_embed(tmp, ctx.message)


    @staticmethod
    async def ark_embed(character_data, message):
        """
        This command creates embed from received data

        :param character_data: char_id, name, desc_first_part, desc_sec_part, position, tags, traits, prof, emoji, rar
        :param message: to send to current channel
        :return: send embed to message channel
        """
        embed = discord.Embed(color=0xff9900, title=character_data[1],
                              description=str(character_data[8]) * character_data[9],
                              url=f"https://aceship.github.io/AN-EN-Tags/akhrchars.html?opname={character_data[1]}")
        embed.add_field(name="Description", value=f"{character_data[2]}\n{character_data[3]}", inline=False)
        embed.add_field(name="Position", value=character_data[4])
        embed.add_field(name="Tags", value=str(character_data[5]), inline=True)
        line = sub('[<@.>/]', '', character_data[6])  # Delete all tags in line
        embed.add_field(name="Traits", value=line, inline=False)
        embed.set_thumbnail(url=character_data[7])
        embed.set_image(url=f"https://aceship.github.io/AN-EN-Tags/img/characters/{character_data[0]}_1.png")
        embed.set_footer(text=f"Requested by {message.author.name}")
        await message.channel.send(embed=embed)


def setup(bot):
    """
    Firs function adds cogs and creates bot class instance

    :param bot: bot instance
    """
    bot_amia = Amia()
    bot.add_cog(Commands(bot, bot_amia))
