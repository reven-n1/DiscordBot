import datetime
import random
from Bot import Bot
import discord.guild
import discord
import re

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)


def main():
    amia = Bot()

    @client.event
    async def on_ready():
        print(f'{client.user.name} - Logged')

    @client.event
    async def on_member_join(member):
        await member.send(f'Hi {member.name}')
        channel = get_channel()
        await channel.send(f'Hi {member}')

    @client.event
    async def on_message(message):
        if str(message.channel) in amia.bot_channels:  # Bot works only in correct channels

            if message.author == client.user:
                return

            elif message.content.startswith('!ger') or message.content.startswith('!пук'):  # Пук епт
                await message.delete()
                random_user = random.choice(client.get_guild(message.guild.id).members)
                while random_user == message.author:
                    random_user = random.choice(client.get_guild(message.guild.id).members)
                ger = amia.ger_function(message, datetime.datetime.now(), random_user)
                if 'Идет' in ger:
                    await message.channel.send(ger, delete_after=5)
                else:
                    await message.channel.send(ger)

            elif message.content.startswith('!ark') or message.content.startswith('!арк'):  # Ark епт
                await message.delete()
                tmp = amia.get_ark(datetime.datetime.now(), message.author.id)
                if 'Копим' in tmp:
                    await message.channel.send(tmp)
                else:
                    # 0 - character_id      1- name     2 - description_first_part      3 - description_sec_part
                    # 4 - position      5 - tags        6 - traits      7 - profession      8 - emoji       9 - rarity
                    embed = discord.Embed(color=0xff9900, title=tmp[1],
                                          description=str(tmp[8]) * tmp[9],
                                          url=f"https://aceship.github.io/AN-EN-Tags/akhrchars.html?opname={tmp[1]}")
                    embed.add_field(name='Description', value=f'{tmp[2]}\n{tmp[3]}', inline=False)
                    embed.add_field(name='Position', value=tmp[4])
                    embed.add_field(name='Tags', value=str(tmp[5]), inline=True)
                    line = re.sub('[<@.>/]', '', tmp[6])  # Delete all tags in line
                    embed.add_field(name='Traits', value=line, inline=False)
                    embed.set_thumbnail(url=tmp[7])
                    embed.set_image(url=f"https://aceship.github.io/AN-EN-Tags/img/characters/{tmp[0]}_1.png")
                    embed.set_footer(text=f'Requested by {message.author.name}')
                    await message.channel.send(embed=embed)

            elif message.content.startswith('!info'):  # Show bot info and description
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
                await message.channel.send(embed=embed, delete_after=15)
                await message.delete()

            elif message.content.startswith('!myark') or message.content.startswith('!майарк'):
                # Show ark collection
                embed = discord.Embed(color=0xff9900)
                collection = amia.get_ark_collection(message.author.id)
                if not collection:
                    embed.add_field(name=f'{message.author.name} collection', value='Empty collection(((')
                else:
                    print(len(collection))
                    embed.add_field(name=f'{message.author.name} collection', value='\n'.join(collection))
                embed.set_thumbnail(url=message.author.avatar_url)
                embed.set_footer(text=f'Requested by {message.author.name}')
                await message.channel.send(embed=embed)
                await message.delete()

            elif message.content.startswith('!barter') or message.content.startswith('!обмен'):
                await message.delete()
                barter_list = amia.get_barter_list(message.author.id)
                if barter_list:
                    barter = amia.ark_barter(barter_list, message.author.id)
                    tmp = next(barter)
                    try:
                        while tmp:
                            # 0 - character_id      1- name     2 - description_first_part      3 - description_sec_part
                            # 4 - position      5 - tags        6 - traits      7 - profession      8 - emoji       9 - rarity
                            embed = discord.Embed(color=0xff9900, title=tmp[1],
                                                  description=str(tmp[8]) * tmp[9],
                                                  url=f"https://aceship.github.io/AN-EN-Tags/akhrchars.html?opname={tmp[1]}")
                            embed.add_field(name='Description', value=f'{tmp[2]}\n{tmp[3]}', inline=False)
                            embed.add_field(name='Position', value=tmp[4])
                            embed.add_field(name='Tags', value=str(tmp[5]), inline=True)
                            line = re.sub('[<@.>/]', '', tmp[6])  # Delete all tags in line
                            embed.add_field(name='Traits', value=line, inline=False)
                            embed.set_thumbnail(url=tmp[7])
                            embed.set_image(url=f"https://aceship.github.io/AN-EN-Tags/img/characters/{tmp[0]}_1.png")
                            embed.set_footer(text=f'Requested by {message.author.name}')
                            await message.channel.send(embed=embed)
                            tmp = next(barter)
                    except StopIteration:
                        pass

                else:
                    await message.channel.send('Нет операторов на обмен', delete_after=10)

            elif message.content.startswith('!clear'):  # Clear command -> clear previous messages
                await message.delete()
                await message.channel.send(str(message.content))
                tmp = message.content.split()
                if len(tmp) == 2 and tmp[1].isdigit():
                    await message.channel.purge(limit=int(message.content.split()[1]))
                else:
                    await message.channel.purge(limit=amia.delete_quantity)

            elif message.content.startswith('!') and message.content not in amia.bot_commands:
                # If unknown command -> show message then delete it
                await message.delete()
                await message.channel.send(f'{message.content} - unknown command', delete_after=10)
                await message.channel.send('Use "!info" to see a list of commands', delete_after=10)

    client.run(amia.token)  # Run bot


def get_channel():
    for guild in client.guilds:
        for i in guild.channels:
            if i.name == 'основной':
                return i


if __name__ == '__main__':
    main()
