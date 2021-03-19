import asyncio
import datetime
from random import choice
import re
import discord
from discord.ext.commands import Cog  # , BucketType
from discord.ext.commands import command  # , cooldown
import music_player as m_p
from Bot import Bot as Amia


class Commands(Cog):
    def __init__(self, bot, bot_amia):
        self.bot = bot
        self.bot_amia = bot_amia

    # @command(name="hello", aliases=["hi"])
    # async def hello(self, ctx):
    #     await ctx.send(f"{choice(('Hello', 'Hi', 'Hey', 'Hiya'))} {ctx.author.mention}!")

    @command(name='info', aliases=['инфо'])
    async def info(self, ctx):
        """
        This command set bot info and commands list to discord embed

        :param ctx: context
        :return: send discord.embed to channel
        """
        await ctx.message.delete()
        embed = discord.Embed(color=0xff9900, title=self.bot_amia.name,
                              url=f"https://www.youtube.com/watch?v=X5ULmETDiXI")
        embed.add_field(name='Description', value=self.bot_amia.bot_info['info'], inline=False)
        embed.add_field(name='Commands',
                        value=str('\n'.join(self.bot_amia.get_info())),
                        inline=True)
        embed.set_thumbnail(
            url="https://aceship.github.io/AN-EN-Tags/img/characters/char_222_bpipe_race%231.png")
        embed.set_image(url="https://aceship.github.io/AN-EN-Tags/img/characters/char_002_amiya_epoque%234.png")
        embed.set_footer(text=f'Requested by {ctx.message.author.name}')
        await ctx.send(embed=embed, delete_after=30)

    @command(name='myark', aliases=['майарк'])
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
            embed.add_field(name=f'{ctx.message.author.name} collection', value='Empty collection(((')
        else:
            embed.add_field(name=f'{ctx.message.author.name} collection', value='\n'.join(ark_collection))
        embed.set_thumbnail(url=ctx.message.author.avatar_url)
        embed.set_footer(text=f'Requested by {ctx.message.author.name}')
        await ctx.send(embed=embed)

    @command(name='barter', aliases=['обмен'])
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
            await ctx.send('***Нет операторов на обмен***', delete_after=15)

    @command(name='add')
    async def add(self, ctx):
        """
        This command adds track to queue

        :param ctx: context
        """
        await self.bot_amia.add_music_to_queue(ctx.message, ctx.message.content, ctx.message.guild.id)

    @command(name='play')
    async def play(self, ctx):
        """
        This command starts music_player if server queue isn't empty

        :param ctx: context
        :return: 'Queue is empty', 'You aren't in the voice channel', 'Already playing' in extensions cases
        """
        await ctx.message.delete()
        self.bot_amia.server_music_is_pause[ctx.message.guild.id] = False
        try:
            voice_channel = ctx.message.author.voice.channel
            queue = self.bot_amia.server_queue_list[ctx.message.guild.id]
            await voice_channel.connect()
            await m_p.play(ctx.message, queue, ctx.message.guild.id, self.bot_amia)
        except KeyError:
            await ctx.message.channel.send("***Queue is empty***")
        except AttributeError:
            await ctx.message.channel.send("***You aren't in the voice channel***")
        except discord.errors.ClientException:
            await ctx.message.channel.send("***Already playing***")

    @command(name='stop')
    async def stop(self, ctx):
        """
        Stops music player

        :param ctx: context
        """
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_channel.stop()

    @command(name='next')
    async def next(self, ctx):
        """
        Starts next track

        :param ctx: context
        :return: 'Bot isn't in the voice channel or queue is empty' in extension case
        """
        await ctx.message.delete()
        server = ctx.message.guild
        voice_channel = server.voice_client
        try:
            queue = self.bot_amia.server_queue_list[ctx.message.guild.id]
            voice_channel.stop()
            await m_p.play(ctx.message, queue, ctx.message.guild.id, self.bot_amia)
        except KeyError:
            await ctx.send('***Bot isn\'t in the voice channel or queue is empty***')

    @command(name='leave')
    async def leave(self, ctx):
        """
        Disconnected bot from voice channel

        :param ctx: context
        :return: 'Bot isn't in the voice channel' in extension case
        """
        try:
            await ctx.message.delete()
            voice_client = ctx.message.guild.voice_client
            voice_client.stop()
            await voice_client.disconnect()
            await asyncio.sleep(3)
            await m_p.clear_from_music(ctx.message.guild.id)
        except AttributeError:
            await ctx.send('***Bot isn\'t in the voice channel***')

    # @command(name="fact")
    # @cooldown(1, 60, BucketType.guild)
    # async def animal_fact(self, ctx):
    #     await ctx.send(f"fact")

    @command(name="clear")
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
            await ctx.message.channel.purge(limit=await self.bot_amia.return_delete_quantity())

    @command(name='ger', aliases=['пук'])
    async def ger(self, ctx):
        """
        This command calls ger function

        :param ctx: context
        :return: either cooldown or ger
        """
        await ctx.message.delete()
        random_user = choice(ctx.message.guild.members)
        while random_user == ctx.message.author:
            random_user = choice(ctx.message.guild.members.names)
        ger = self.bot_amia.ger_function(ctx.message.author, datetime.datetime.now(), random_user)
        if 'Идет' in ger:
            await ctx.send(ger, delete_after=7)
        else:
            await ctx.send(ger)

    @command(name='ark', aliases=['арк'])
    async def ark(self, ctx):
        """
        Ark command

        :param ctx: context
        :return: either cooldown or character
        """
        await ctx.message.delete()
        tmp = self.bot_amia.get_ark(datetime.datetime.now(), ctx.message.author.id)
        if 'Копим' in tmp:
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
        embed.add_field(name='Description', value=f'{character_data[2]}\n{character_data[3]}', inline=False)
        embed.add_field(name='Position', value=character_data[4])
        embed.add_field(name='Tags', value=str(character_data[5]), inline=True)
        line = re.sub('[<@.>/]', '', character_data[6])  # Delete all tags in line
        embed.add_field(name='Traits', value=line, inline=False)
        embed.set_thumbnail(url=character_data[7])
        embed.set_image(url=f"https://aceship.github.io/AN-EN-Tags/img/characters/{character_data[0]}_1.png")
        embed.set_footer(text=f'Requested by {message.author.name}')
        await message.channel.send(embed=embed)


def setup(bot):
    """
    Firs function adds cogs and creates bot class instance

    :param bot:
    :return:
    """
    bot_amia = Amia()
    bot.add_cog(Commands(bot, bot_amia))
