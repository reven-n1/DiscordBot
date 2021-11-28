from library.my_Exceptions.music_exceptions import *
from discord.ext import commands
from enum import Enum
import datetime as dt
import typing as t
import wavelink
import discord
import asyncio
import re


URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}


class RepeatMode(Enum):
    NONE = 0
    ONE = 1
    ALL = 2


class Queue:
    def __init__(self):
        self._queue = []
        self.position = 0
        self.repeat_mode = RepeatMode.NONE


    @property
    def is_empty(self):
        return not self._queue
    

    @property
    def current_track(self):
        if not self._queue:
            raise QueueIsEmpty

        if self.position <= len(self._queue) - 1:
            return self._queue[self.position]
        

    @property
    def upcoming(self):
        if not self._queue:
            raise QueueIsEmpty

        return self._queue[self.position + 1:]
    

    @property
    def history(self):
        if not self._queue:
            raise QueueIsEmpty

        return self._queue[:self.position]
    

    @property
    def length(self):
        return len(self._queue)
    

    def add(self, *args):
        self._queue.extend(args)
        

    def get_next_track(self):
        if not self._queue:
            raise QueueIsEmpty

        self.position += 1

        if self.position < 0:
            return None
        elif self.position > len(self._queue) - 1:
            if self.repeat_mode == RepeatMode.ALL:
                self.position = 0
            else:
                return None

        return self._queue[self.position]
        

    def set_repeat_mode(self, mode):
        if mode == "none":
            self.repeat_mode = RepeatMode.NONE
        elif mode == "1":
            self.repeat_mode = RepeatMode.ONE
        elif mode == "all":
            self.repeat_mode = RepeatMode.ALL
            

    def empty(self):
        self._queue.clear()
        self.position = 0


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()
        

    async def connect(self, ctx, channel=None):
        if self.is_connected:
            raise AlreadyConnectedToChannel

        if (channel := getattr(ctx.author.voice, "channel", channel)) is None:
            raise NoVoiceChannel

        await super().connect(channel.id)
        return channel
    

    async def teardown(self):
        try:
            await self.destroy()
        except KeyError:
            pass
        

    async def add_tracks(self, ctx, tracks):
        if not tracks:
            raise NoTracksFound

        if isinstance(tracks, wavelink.TrackPlaylist):
            self.queue.add(*tracks.tracks)
        elif len(tracks) == 1:
            self.queue.add(tracks[0])
            await ctx.send(f"Добавила {tracks[0].title} в очередь, сладенький.")
        else:
            if (track := await self.choose_track(ctx, tracks)) is not None:
                self.queue.add(track)
                await ctx.send(f"Добавила {track.title} в очередь, сладенький.")

        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()
            

    async def choose_track(self, ctx, tracks):
        def _check(r, u):
            return (
                r.emoji in OPTIONS.keys()
                and u == ctx.author
                and r.message.id == msg.id
            )

        embed = discord.Embed(
            title="Выбери песню",
            description=(
                "\n".join(
                    f"**{i+1}.** {t.title} ({t.length//60000}:{str(t.length%60).zfill(2)})"
                    for i, t in enumerate(tracks[:5])
                )
            ),
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Результаты поиска")
        embed.set_footer(
            text=f"Запросил {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        msg = await ctx.send(embed=embed)
        for emoji in list(OPTIONS.keys())[:min(len(tracks), len(OPTIONS))]:
            await msg.add_reaction(emoji)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=_check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.message.delete()
        else:
            await msg.delete()
            return tracks[OPTIONS[reaction.emoji]]
        

    async def start_playback(self):
        await self.play(self.queue.current_track)
        

    async def advance(self):
        try:
            if (track := self.queue.get_next_track()) is not None:
                await self.play(track)
        except QueueIsEmpty:
            pass
        

    async def repeat_track(self):
        await self.play(self.queue.current_track)


class Music(commands.Cog, wavelink.WavelinkMixin):
    qualified_name = 'Music'
    description = 'Играет музыку'
    def __init__(self, bot):
        self.bot = bot
        self.wavelink = wavelink.Client(bot=bot)
        self.bot.loop.create_task(self.start_nodes())
        

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await self.get_player(member.guild).teardown()
                

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node):
        print(f" Wavelink node `{node.identifier}` ready.")

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node, payload):
        if payload.player.queue.repeat_mode == RepeatMode.ONE:
            await payload.player.repeat_track()
        else:
            await payload.player.advance()
            

    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Музыка доступна только на сервере")
            return False

        return True
    

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        nodes = {
            "MAIN": {
                "host": "127.0.0.1",
                "port": 2333,
                "rest_uri": "http://127.0.0.1:2333",
                "password": "youshallnotpass",
                "identifier": "MAIN",
                "region": "europe",
            }
        }

        for node in nodes.values():
            await self.wavelink.initiate_node(**node)
            

    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)
        
        
    # cog commands ------------------------------------------------------------------------- 

    @commands.command(name="connect", aliases=["join"],
    brief='Присоединиться к голосовому каналу', description='Присоединиться к голосовому каналу')
    async def connect_command(self, ctx, *, channel: t.Optional[discord.VoiceChannel]):
        player = self.get_player(ctx)
        channel = await player.connect(ctx, channel)
        await ctx.send(f"Присоединилась к вашей гейпати в {channel.name}.")
        

    @connect_command.error
    async def connect_command_error(self, ctx, exc):
        if isinstance(exc, AlreadyConnectedToChannel):
            await ctx.send("Уже зависаю с вами в канале.")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("Немогу подключиться к каналу, сорян(")
            

    @commands.command(name="disconnect", aliases=["leave"],
    brief='Отключиться от голосового канала', description='Отключиться от голосового канала')
    async def disconnect_command(self, ctx):
        player = self.get_player(ctx)
        await player.teardown()
        await ctx.send("Ну все, пока.")
        

    @commands.command(name="play", aliases=["p"],
    brief='Поиск музыки', description='Поиск твоей любимой музыки в интернете. Будем вместе слушать ^.^')
    async def play_command(self, ctx, *, query: t.Optional[str]):
        player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx)

        if query is None:
            if player.queue.is_empty:
                raise QueueIsEmpty

            await player.set_pause(False)
            await ctx.send("Продолжаем.")

        else:
            query = query.strip("<>")
            if not re.match(URL_REGEX, query):
                query = f"ytsearch:{query}"

            await player.add_tracks(ctx, await self.wavelink.get_tracks(query))
            

    @play_command.error
    async def play_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("Ничего в очереди нет(")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("Немогу подключиться к каналу, сорян(")
            

    @commands.command(name="pause", 
    brief='Поставить на паузу', description='Поставить на паузу')
    async def pause_command(self, ctx):
        player = self.get_player(ctx)

        if player.is_paused:
            raise PlayerIsAlreadyPaused

        await player.set_pause(True)
        await ctx.send("Пауза, давай передохнем немного")
        

    @pause_command.error
    async def pause_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send("И так ничего не играет")
            

    @commands.command(name="stop",
    brief='Остановить проигрывание', description='Остановить проигрывание и запустить выигрывание')
    async def stop_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.empty()
        await player.stop()
        await ctx.send("Остановлено")
        

    @commands.command(name="next", aliases=["skip"],
    brief='Запустить следующий трек', description='Запустить следующий трек')
    async def next_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.upcoming:
            raise NoMoreTracks

        await player.stop()
        await ctx.send("Играем дальше")
        

    @next_command.error
    async def next_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("Очередь и так пустая, куда дальше?")
        elif isinstance(exc, NoMoreTracks):
            await ctx.send("Это последний трек, братик")
            

    @commands.command(name="previous",
    brief='Играть предыдущий трек', description='Играть предыдущий трек')
    async def previous_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.history:
            raise NoPreviousTracks

        player.queue.position -= 2
        await player.stop()
        await ctx.send("Играем то что уже слушали. Это действительно такой хороший трек?")
        

    @previous_command.error
    async def previous_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("Очередь пуста(")
        elif isinstance(exc, NoPreviousTracks):
            await ctx.send("Это и так первый трек")


    @commands.command(name="repeat",
    brief='Установить режим повтора. Подробнее в расширенной справке', 
    description='Установить режим повтора.\nДоступные режимы: none, 1, all')
    async def repeat_command(self, ctx, mode: str):
        if mode not in ("none", "1", "all"):
            raise InvalidRepeatMode

        player = self.get_player(ctx)
        player.queue.set_repeat_mode(mode)
        await ctx.send(f"Установила {mode} как режим повтора.")
        

    @commands.command(name="queue", aliases=["q"],
    brief='Показать очередь', description='Показать очередь')
    async def queue_command(self, ctx, show: t.Optional[int] = 10):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        embed = discord.Embed(
            title="Очередь",
            description=f"Показываю тебе до {show} следующих треков",
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow()
        )
        # embed.set_author(name="Результаты")
        embed.set_footer(
            text=f"Запросил {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        embed.add_field(
            name="Сейчас играет",
            value=getattr(player.queue.current_track, "title",
                          "Ничего сейчас не играет(\nЗапроси трек командой play"),
            inline=False
        )
        if upcoming := player.queue.upcoming:
            embed.add_field(
                name="Далее в программе",
                value="\n".join(t.title for t in upcoming[:show]),
                inline=False
            )

        # TODO: делать ли фичу вот в чем вопрос
        msg = await ctx.send(embed=embed) 
        

    @queue_command.error
    async def queue_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("Ничего нет")
            

    # player info and commands -----------------------------------------------------------------
    
    @commands.command(name="playing", aliases=["np"],
    brief='Показать что сейчас играет', description='Показать что сейчас играет')
    async def playing_command(self, ctx):
        player = self.get_player(ctx)

        if not player.is_playing:
            raise PlayerIsAlreadyPaused

        embed = discord.Embed(
            title="Сейчас играет",
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow(),
        )
        # embed.set_author(name="Playback Information")
        embed.set_footer(
            text=f"Запросил {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Название трека",
                        value=player.queue.current_track.title, inline=False)
        embed.add_field(
            name="Исполнитель", value=player.queue.current_track.author, inline=False)

        position = divmod(player.position, 60000)
        length = divmod(player.queue.current_track.length, 60000)
        embed.add_field(
            name="Время",
            value=f"{int(position[0])}:{round(position[1]/1000):02}/{int(length[0])}:{round(length[1]/1000):02}",
            inline=False
        )

        await ctx.send(embed=embed)
        

    @playing_command.error
    async def playing_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send("Ничего не играет(")
            

    @commands.command(name="skipto", aliases=["playindex", "pi"],
    brief='Перейти сразу к треку под номером N', description='Перейти сразу к треку под номером N. N указывать через пробел')
    async def skipto_command(self, ctx, index: int):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        if not 0 <= index <= player.queue.length:
            raise NoMoreTracks

        player.queue.position = index - 2
        await player.stop()
        await ctx.send(f"Играем музяку под номером {index}.")
        

    @skipto_command.error
    async def skipto_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("Ничего не играет.")
        elif isinstance(exc, NoMoreTracks):
            await ctx.send("Указан неверный номер(")
            

    @commands.command(name="restart",
    brief='Запустить трек заново', description='Запустить трек заново, все хуйня Саня, дайвай по новой!')
    async def restart_command(self, ctx):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        await player.seek(0)
        await ctx.send("Перезапутила")
        

    @restart_command.error
    async def restart_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("Нечего перезапускать")


def setup(bot):
    bot.add_cog(Music(bot))
    

# TODO : continue playing from pause
# TODO : music embed with player buttons(stop, next, prev, pause, cont, etc)