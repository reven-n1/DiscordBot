import datetime
from Bot import bot
from Bot import db, cursor
import discord.guild
import discord
import sqlite3
import json
import requests

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)


def main():
    amia = bot()

    @client.event
    async def on_ready():
        print(f'{client.user.name} - Logged')

    @client.event
    async def on_member_join(member):
        await add_to_ger_list(member)
        await member.send(f'Hi {member.name}')
        channel = get_channel()
        await channel.send(f'Hi {member}')

    @client.event
    async def on_message(message):
        if str(message.channel) in amia.bot_channels:  # Bot works only in correct channels

            if message.author == client.user:
                return

            elif message.content.startswith('!ger') or message.content.startswith('!пук'):  # Пук епт
                await message.delete()  # In the future I'll implement this through a decorator
                t = amia.ger_function(message, client.guilds, datetime.datetime.now())
                if 'Идет' in t:
                    await message.channel.send(t, delete_after=5)
                else:
                    await message.channel.send(t)

            elif message.content.startswith('!info'):  # Show bot info and description
                await message.delete()
                await message.channel.send(amia.get_info(), delete_after=10)
                embed = discord.Embed(color=0xff9900, title=amia.name)
                # response = requests.get('https://drive.google.com/file/d/
                # 12nIZ4J19Yp4AoR0N-Zcefw6M-42tl-vD/view?usp=sharing')
                # json_data = json.loads(response.text)  # Извлекаем JSON
                # embed.set_image(url='link')  # Устанавливаем картинку Embed'a
                embed.set_footer(text=f'Requested by {message.author.name}')
                await message.channel.send(embed=embed, delete_after=20)

            elif message.content.startswith('!commands'):  # Show all commands -> takes them from the "bot_info"
                await message.delete()
                await message.channel.send(amia.get_commands(), delete_after=10)

            elif message.content.startswith('!members'):  # Write all members to file
                await message.delete()

                for guild in client.guilds:
                    amia.get_init_members_list(guild.members)
                    # print(guild.member_count)

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
                await message.channel.send('Use "!commands" to see a list of commands', delete_after=10)

    client.run(amia.token)  # Run bot


def get_channel():
    for guild in client.guilds:
        for i in guild.channels:
            if i.name == 'основной':
                return i


async def add_to_ger_list(member_name):  # Call when new user join server

    cursor.execute(f"SELECT user_name FROM users_ger WHERE user_name == '{member_name}'")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users_ger VALUES ( ?,?)",
                       (f"{member_name}", datetime.datetime(2020, 11, 11, 11, 11, 11, 111111)))
    db.commit()

if __name__ == '__main__':
    main()
