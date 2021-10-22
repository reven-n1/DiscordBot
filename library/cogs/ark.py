from library.my_Exceptions.validator import NonOwnedCharacter, NonExistentCharacter
from discord.ext.commands.core import guild_only, is_nsfw
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import command, cooldown
from library.bots.Ark_bot import Ark_bot
from discord.ext.commands import Cog
from library.__init__ import data
from re import sub
import discord


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Amia = Ark_bot()


    @command(name="myark", aliases=["моидевочки","майарк"])
    async def myark(self, ctx, char_name:str=""):
        """
        This command sends ark collection to private messages.\n
        If collection empty -> returns 'Empty collection'
        """
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            await ctx.message.delete()

        ark_collection = self.Amia.get_ark_collection(ctx.message.author.id)

        # TODO: rewrite if->True part

        if char_name == "":
            all_character_count = self.Amia.get_ark_count()
            user_chara_count = 0
            for characters in ark_collection.values():
                user_chara_count += len(characters)
            collection_message = discord.Embed(title=f"{ctx.author.display_name}'s collection {user_chara_count}/{all_character_count} \
                                              ({round((user_chara_count/all_character_count)*100,2)}%)", color=data.get_embed_color)
            for rarity, characters in ark_collection.items():
                characters_list = ""
                for character in characters:
                    characters_list += f"{character[1]} x {character[2]}\n"
                collection_message.add_field(name=":star:"*rarity if rarity<6 else ":star2:"*rarity, value=characters_list, inline=False)
            if len(ark_collection) == 0:
                collection_message.add_field(name="Ти бомж", value="иди покрути девочек!")
            collection_message.set_footer(text=f"Используй команду !майарк <имя> чтоб посмотреть на персонажа.")
            await ctx.message.author.send(embed=collection_message)
            
        else:
            try:
                await ctx.message.author.send(embed=self.ark_embed(self.Amia.show_character(char_name, ctx.message.author.id), ctx.message))

            except NonOwnedCharacter:
                await ctx.message.author.send("***Лох, у тебя нет такой дивочки***")
            
            except NonExistentCharacter:
                await ctx.message.author.send("***Лошара, даже имя своей вайфу не запомнил((***")

            
    @guild_only()
    @command(name="barter", aliases=["обмен"])
    async def barter(self, ctx):
        """
        Serves to exchange 5 characters for 1 rank higher\n
        if possible else returns 'Нет операторов на обмен'
        """
        await ctx.message.delete()
        barter_list = self.Amia.get_barter_list(ctx.message.author.id)
        if barter_list:
            barter = self.Amia.ark_barter(barter_list, ctx.message.author.id)
            try:
                new_char = next(barter)
                
                while new_char:
                    await ctx.message.channel.send(embed=self.ark_embed(new_char, ctx.message))
                    new_char = next(barter)
            except StopIteration:
                pass
        else:
            await ctx.send("***Нет операторов на обмен***", delete_after=15)


    @is_nsfw()
    @guild_only()
    @cooldown(1, data.get_ark_cooldown, BucketType.user)
    @command(name="ark", aliases=["арк"])
    async def ark(self, ctx):      
        """
        Return a random arknigts character (from char_table.json)
        """
        await ctx.message.delete()
        character_data = self.Amia.roll_random_character(ctx.message.author.id)
        await ctx.message.channel.send(embed=self.ark_embed(character_data, ctx.message))


    @staticmethod
    def ark_embed(character_data, message):
        """
        Generates embed form recieved ark data

        Args:
            character_data (list): random character data from char_table.json
            message (discord.message): message
        """
        embed = discord.Embed(color=data.get_embed_color, title=character_data.name,
                              description=str(character_data.stars) * character_data.rarity,
                              url=f"https://aceship.github.io/AN-EN-Tags/akhrchars.html?opname={character_data.name}")
        embed.add_field(name="Description", value=f"{character_data.description_first_part}\n{character_data.description_sec_part}", \
                        inline=False)
        embed.add_field(name="Position", value=character_data.position)
        embed.add_field(name="Tags", value=str(character_data.tags), inline=True)
        line = sub("[<@.>/]", "", character_data.traits)  # Delete all tags in line
        embed.add_field(name="Traits", value=line.replace("bakw", ""), inline=False)
        embed.set_thumbnail(url=character_data.profession)
        embed.set_image(url=f"https://aceship.github.io/AN-EN-Tags/img/characters/{character_data.character_id}_1.png")
        embed.set_footer(text=f"Requested by {message.author.display_name}")
        return embed


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Commands(bot))
