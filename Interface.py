import datetime
import random
from asyncio import tasks
from discord.ext import tasks
from music_player import *
from Bot import Bot
import discord.guild
import discord
import re

#  Bot game statuses------------------------------------------------------------------------------->
status = ['Warface', 'Жизнь', 'твоего батю', 'человека', 'Detroit: Become Human', 'RAID: Shadow Legends',
          'программиста']

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
amia = Bot()


def main():
    @client.event
    async def on_ready():
        print(f'{client.user.name} - Logged')
        set_status.start()

    @client.event
    async def on_member_join(member):
        await member.send(f'Hi {member.name}')
        for guild in client.guilds:
            for channel in guild.channels:
                if channel.name == 'основной':
                    await channel.send(f'Привет {member.mention}')

    @client.event
    async def on_message(message):
        if str(message.channel) in amia.bot_channels:  # Bot works only in correct channels

            if message.author == client.user:
                return

            # Пердит в рандомного члена канала(можно и обосраться) --------------------------->
            elif message.content.startswith('!ger') or message.content.startswith('!пук'):  # Пук епт
                await message.delete()
                random_user = random.choice(client.get_guild(message.guild.id).members)
                while random_user == message.author:
                    random_user = random.choice(client.get_guild(message.guild.id).members)
                ger = amia.ger_function(message, datetime.datetime.now(), random_user)
                if 'Идет' in ger:
                    await message.channel.send(ger, delete_after=7)
                else:
                    await message.channel.send(ger)
            #  ------------------------------------------------------------------------------->

            # Gives 1 random character ------------------------------------------------------->
            elif message.content.startswith('!ark') or message.content.startswith('!арк'):
                await message.delete()
                tmp = amia.get_ark(datetime.datetime.now(), message.author.id)
                if 'Копим' in tmp:
                    await message.channel.send(tmp, delete_after=7)
                else:
                    await ark_embed(tmp, message)
            #  ------------------------------------------------------------------------------->

            # Show bot info and commands with description ------------------------------------>
            elif message.content.startswith('!info'):
                await message.delete()
                embed = discord.Embed(color=0xff9900, title=amia.name,
                                      url=f"https://www.youtube.com/watch?v=X5ULmETDiXI")
                embed.add_field(name='Description', value=amia.bot_info['info'], inline=False)
                embed.add_field(name='Commands',
                                value=str('\n'.join(amia.get_info())),
                                inline=True)
                embed.set_thumbnail(
                    url="https://aceship.github.io/AN-EN-Tags/img/characters/char_222_bpipe_race%231.png")
                embed.set_image(url="https://aceship.github.io/AN-EN-Tags/img/characters/char_002_amiya_epoque%234.png")
                embed.set_footer(text=f'Requested by {message.author.name}')
                await message.channel.send(embed=embed, delete_after=30)
            #  ------------------------------------------------------------------------------->

            # Show ark collection ------------------------------------------------------------>
            elif message.content.startswith('!myark') or message.content.startswith('!майарк'):
                embed = discord.Embed(color=0xff9900)
                collection = amia.get_ark_collection(message.author.id)
                if not collection:
                    embed.add_field(name=f'{message.author.name} collection', value='Empty collection(((')
                else:
                    embed.add_field(name=f'{message.author.name} collection', value='\n'.join(collection))
                embed.set_thumbnail(url=message.author.avatar_url)
                embed.set_footer(text=f'Requested by {message.author.name}')
                await message.channel.send(embed=embed)
                await message.delete()
            #  ------------------------------------------------------------------------------->

            #  Changes 5 identical characters to 1 higher grade ------------------------------>
            elif message.content.startswith('!barter') or message.content.startswith('!обмен'):
                await message.delete()
                barter_list = amia.get_barter_list(message.author.id)
                if barter_list:
                    barter = amia.ark_barter(barter_list, message.author.id)
                    tmp = next(barter)
                    try:
                        while tmp:
                            await ark_embed(tmp, message)
                            tmp = next(barter)
                    except StopIteration:
                        pass
                else:
                    await message.channel.send('***Нет операторов на обмен***', delete_after=15)
            #  ------------------------------------------------------------------------------->

            #  Add track to server queue ----------------------------------------------------->
            elif message.content.startswith('!add'):
                await amia.add_music_to_queue(message, message.content, message.guild.id)
            #  ------------------------------------------------------------------------------->

            #  Start's player ---------------------------------------------------------------->
            elif message.content.startswith('!play') or message.content.startswith('!врубай'):
                await message.delete()
                amia.server_music_is_pause[message.guild.id] = False
                try:
                    voice_channel = message.author.voice.channel
                    queue = amia.server_queue_list[message.guild.id]
                    await voice_channel.connect()
                    await play(message, queue, message.guild.id)
                except KeyError:
                    await message.channel.send("***Queue is empty***")
                except AttributeError:
                    await message.channel.send("***You aren't in the voice channel***")
                except discord.errors.ClientException:
                    await message.channel.send("***Already playing***")
            #  ------------------------------------------------------------------------------->

            #  Stop's player ----------------------------------------------------------------->
            elif message.content.startswith('!stop') or message.content.startswith('!тормози'):
                server = message.guild
                voice_channel = server.voice_client
                voice_channel.stop()
            #  ------------------------------------------------------------------------------->

            #  Start's next track ------------------------------------------------------------>
            elif message.content.startswith('!next') or message.content.startswith('!следующий'):
                server = message.guild
                voice_channel = server.voice_client
                try:
                    queue = amia.server_queue_list[message.guild.id]
                    voice_channel.stop()
                    await play(message, queue, message.guild.id)
                except KeyError:
                    await message.channel.send('***Bot isn\'t in the voice channel or queue is empty***')
            #  ------------------------------------------------------------------------------->

            # bot stop playing music and leaves form channel --------------------------------->
            elif message.content.startswith('!leave') or message.content.startswith('!вырубай'):
                try:
                    await message.delete()
                    voice_client = client.get_guild(message.guild.id).voice_client
                    voice_client.stop()
                    await voice_client.disconnect()
                    await asyncio.sleep(3)
                    await clear_from_music(message.guild.id)
                except AttributeError:
                    await message.channel.send('***Bot isn\'t in the voice channel***')
            #  ------------------------------------------------------------------------------->

            # Clear chat messages ------------------------------------------------------------>
            elif message.content.startswith('!clear'):  # Clear command -> clear previous messages
                tmp = message.content.split()
                if len(tmp) == 2 and tmp[1].isdigit():
                    await message.channel.purge(limit=int(message.content.split()[1]))
                else:
                    await message.channel.purge(limit=amia.delete_quantity)
            #  ------------------------------------------------------------------------------->

            # elif message.content.startswith('!mes'):
            #     print(type(message.guild.id))

            # If unknown command -> show message then delete it ------------------------------>
            elif message.content.startswith('!') and message.content not in amia.bot_commands:
                await message.delete()
                await message.channel.send(f'{message.content} - unknown command', delete_after=10)
                await message.channel.send('Use "!info" to see a list of commands', delete_after=10)
            #  ------------------------------------------------------------------------------->

    @tasks.loop(seconds=5)  # Set bot activity
    async def set_status():
        """
        :return: set activity  status
        """

        await client.change_presence(activity=discord.Game(random.choice(status)))

    client.run(amia.token)  # Run bot


#  Set ark info to embed ----------->
async def ark_embed(character_data, message):
    """
    This function creates embed from received data

    :param character_data: 0 : character_id      1 : name     2 : description_first_part      3 : description_sec_part  4 : position      5 : tags        6 : traits      7 : profession      8 : emoji       9 : rarity
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


if __name__ == '__main__':
    main()
