from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import command, cooldown
from discord.ext.commands import Cog
from bot.__init__ import Amia
from json import load
from re import sub
import discord


with open("bot/config/config.json","rb") as json_config_file:
    data = load(json_config_file)
    try:
        ark_cooldown = int(data["default_settings"]["ark"]["ark_recoil"])
    except KeyError:
        exit("'config.json' is damaged!")
        
class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command(name="myark", aliases=["моидевочки"])
    async def myark(self, ctx):
        """
        This command sends ark collection to private messages.\n
        If collection empty -> returns 'Empty collection'
        """
        await ctx.message.delete()
        ark_collection = Amia.get_ark_collection(ctx.message.author.id)
        collection_message = f"***{ctx.message.author.name}  collection***\n"+ "\n".join(ark_collection)
        await ctx.message.author.send(f"\n>>> {collection_message}")


    @command(name="barter", aliases=["обмен"])
    async def barter(self, ctx):
        """
        Serves to exchange 5 characters for 1 rank higher\n
        if possible else returns 'Нет операторов на обмен'
        """
        await ctx.message.delete()
        barter_list = Amia.get_barter_list(ctx.message.author.id)
        if barter_list:
            barter = Amia.ark_barter(barter_list, ctx.message.author.id)
            tmp = next(barter)
            try:
                while tmp:
                    await self.ark_embed(tmp, ctx.message)
                    tmp = next(barter)
            except StopIteration:
                pass
        else:
            await ctx.send("***Нет операторов на обмен***", delete_after=15)


    @cooldown(1, ark_cooldown, BucketType.user)
    @command(name="ark", aliases=["арк"])
    async def ark(self, ctx):      
        """
        Return a random arknigts character (from char_table.json)
        """
        await ctx.message.delete()
        character_data = Amia.get_ark(ctx.message.author.id)
        await self.ark_embed(character_data, ctx.message)


    @staticmethod
    async def ark_embed(character_data, message):
        """
        Generates embed form recieved ark data

        Args:
            character_data (list): random character data from char_table.json
            message (discord.message): message
        """
        embed = discord.Embed(color=0xff9900, title=character_data[1],
                              description=str(character_data[8]) * character_data[9],
                              url=f"https://aceship.github.io/AN-EN-Tags/akhrchars.html?opname={character_data[1]}")
        embed.add_field(name="Description", value=f"{character_data[2]}\n{character_data[3]}", inline=False)
        embed.add_field(name="Position", value=character_data[4])
        embed.add_field(name="Tags", value=str(character_data[5]), inline=True)
        line = sub("[<@.>/]", "", character_data[6])  # Delete all tags in line
        embed.add_field(name="Traits", value=line.replace("bakw", ""), inline=False)
        embed.set_thumbnail(url=character_data[7])
        embed.set_image(url=f"https://aceship.github.io/AN-EN-Tags/img/characters/{character_data[0]}_1.png")
        embed.set_footer(text=f"Requested by {message.author.name}")
        await message.channel.send(embed=embed)


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Commands(bot))
