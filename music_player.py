import asyncio
import json
import os
import discord
import requests
import youtube_dl

from Interface import amia, client

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,  # True
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, guild_id, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))  # not stream

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)

        for file in os.listdir(r"F:\Studying\DiscordBotAmia"):
            if data['id'] in file:
                old_name = os.path.basename(file)
                os.rename(old_name, old_name.replace(str(data['id']), str(guild_id)))

        filename = filename.replace(data['id'], str(guild_id))
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


#  Music player ----------------------->
async def play(message, queue, guild_id):
    """
    Music player function

    :param message: to catch some data
    :param queue: music queue from current server
    :param guild_id: current guild id
    :return: starts music player
    """

    server = message.guild
    voice_channel = server.voice_client
    try:
        link_tmp = queue[0]  # Link to YouTube video
        del queue[0]
        player = await YTDLSource.from_url(guild_id, link_tmp, loop=client.loop)
        voice_channel.play(player)
        await music_embed(message, player.data['webpage_url'], player.title, player.data['thumbnails'][-1]['url'])

        while True:
            # Check if track is on pause or it's over
            await music_status(voice_channel, message)
            if not voice_channel.is_playing() and amia.server_music_is_pause[message.guild.id]:
                pass
            elif not voice_channel.is_playing() and not amia.server_music_is_pause[message.guild.id] \
                    and queue != []:  # If  track is over -> delete it and start new
                await clear_from_music(guild_id)
                await play(message, queue, guild_id)
                break
            await asyncio.sleep(3)
    except IndexError:
        await message.channel.send('***Queue is empty***')
        await clear_from_music(message.guild.id)
        await voice_channel.disconnect()
        return 0
    except AttributeError:
        pass


async def clear_from_music(guild_id):
    """
    This function clears unused music

    :param guild_id: to clear only current guild files
    :return: clear from unused music
    """

    await asyncio.sleep(1)
    for file in os.listdir(r"F:\Studying\DiscordBotAmia"):
        if str(guild_id) in file:
            os.remove(file)


async def music_embed(message, video_link, player_title, img):
    """
    Send music embed to channel and add reactions to manage music player

    :param img: video preview
    :param message: to catch author and guild id
    :param video_link:
    :param player_title: music title
    :return: Set music player embed id to list
    """

    try:
        mes = await message.channel.fetch_message(amia.server_embed_id[message.guild.id])
        await mes.delete()
    except discord.errors.HTTPException:
        pass
    except KeyError:
        pass

    embed = discord.Embed(color=0xff9900, title=f'**Now playing:**   {player_title}')
    embed.add_field(name="YouTube", value=video_link)
    embed.set_image(url=img)
    embed.set_footer(text=f'Requested by {message.author.name}')
    emb = await message.channel.send(embed=embed)
    await emb.add_reaction('▶')
    await emb.add_reaction('⏸')
    await emb.add_reaction('⏹')
    await emb.add_reaction('⏪')
    await emb.add_reaction('⏩')
    amia.server_embed_id[message.guild.id] = emb.id


async def music_status(voice_channel, message):
    """
    This function manages music player by checking embed reactions

    :param voice_channel: to manage music player of the current guild
    :param message: to catch current guild id
    :return: Nothing. Check embed reactions -> manage the music player
    """

    try:
        mes = await message.channel.fetch_message(amia.server_embed_id[message.guild.id])
        play_count = mes.reactions[0].count
        pause_count = mes.reactions[1].count
        stop_count = mes.reactions[2].count
        next_count = mes.reactions[4].count

        if not voice_channel.is_playing() and amia.server_music_is_pause[message.guild.id]:
            if play_count % 2 == 0:
                await play(message, amia.server_queue_list[message.guild.id], message.guild.id)
        previous_count = mes.reactions[4].count
        if pause_count % 2 == 0:
            voice_channel.pause()
            amia.server_music_is_pause[message.guild.id] = True
        if pause_count % 2 == 1:
            voice_channel.resume()
            amia.server_music_is_pause[message.guild.id] = False
        if stop_count % 2 == 0:
            voice_channel.stop()
            amia.server_music_is_pause[message.guild.id] = True  #
        if next_count % 2 == 0:
            voice_channel.stop()
            amia.server_music_is_pause[message.guild.id] = False
            await play(message, amia.server_queue_list[message.guild.id], message.guild.id)
        if previous_count % 2 == 0:
            pass
    except discord.errors.NotFound:
        pass
