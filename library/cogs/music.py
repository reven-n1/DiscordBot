from discord import ApplicationContext, Interaction, Option, slash_command
from library.bot_token import spotipy_client_id, spotipy_client_secret
from wavelink.ext.spotify import SpotifyClient, SpotifyTrack
from discord.ext.commands.context import Context
from library.my_Exceptions.music_exceptions import *
from library.data.dataLoader import dataHandler
from discord.ext.commands import guild_only
from discord.errors import NotFound
from discord.ext import commands, pages
from random import shuffle
from copy import deepcopy
from enum import Enum
import datetime as dt
import typing as t
import wavelink
import discord
import asyncio
import logging
import re


URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
options = dataHandler()


class RepeatMode(Enum):
    NONE = 0
    ONE = 1
    ALL = 2


class Queue:
    _queue = []  #TODO type annotation
    position: int = 0
    repeat_mode: RepeatMode = RepeatMode.NONE
    _user_tracks = {}  #TODO type annotation

    @property
    def is_empty(self):
        return not self._queue

    @property
    def current_track(self) -> wavelink.Track:
        if not self._queue:
            raise QueueIsEmpty

        if self.position <= len(self._queue) - 1:
            return self._queue[self.position]

    @property
    def upcoming(self) -> list[wavelink.Track]:
        if not self._queue:
            raise QueueIsEmpty

        return self._queue[self.position + 1:]

    @property
    def history(self) -> list[wavelink.Track]:
        if not self._queue:
            raise QueueIsEmpty

        return self._queue[:self.position]

    @property
    def length(self):
        return len(self._queue)

    def add(self, user_id: int,  *args):
        for track in args:
            self._user_tracks[track] = user_id
        self._queue.extend(args)

    def get_next_track(self) -> wavelink.Track:
        if not self._queue:
            raise QueueIsEmpty

        self.position += 1

        if self.position < 0:
            self.position = 0
            return None
        if self.position > len(self._queue) - 1:
            if self.repeat_mode == RepeatMode.ALL:
                self.position = 0
            else:
                if self.position > len(self._queue):
                    self.position -= 1
                return None

        return self._queue[self.position]

    def set_repeat_mode(self, mode):
        if mode == "none":
            self.repeat_mode = RepeatMode.NONE
        elif mode == "1":
            self.repeat_mode = RepeatMode.ONE
        elif mode == "all":
            self.repeat_mode = RepeatMode.ALL

    def clear(self):
        self._queue.clear()
        self._user_tracks.clear()
        self.position = 0

    def shuffle(self):
        upcoming = self.upcoming
        shuffle(upcoming)
        self._queue[self.position + 1:] = upcoming

    def get_track_owner(self, track: wavelink.Track = None):
        if track:
            return self._user_tracks[track]
        elif self.current_track:
            return self._user_tracks[self.current_track]
        else:
            return False


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()
        timeout = int(dataHandler().get_chat_misc_cooldown_sec)
        self.selfDestructor = Player.SelfDestruct(timeout, self)

    class SelfDestruct:
        parent = None
        _task: asyncio.Task = None

        def __init__(self, timeout: int, parent, start=False):
            self.timeout = timeout
            self.parent = parent
            if start:
                self.start()

        def start(self):
            if not self._task or self._task.done():
                self._task = asyncio.create_task(self._run())

        async def _run(self):
            for _ in range(self.timeout):
                await asyncio.sleep(1)
                if self.parent.is_playing():
                    break
            if not self.parent.is_playing():
                await self.parent.teardown()

    async def teardown(self):
        try:
            self.queue.clear()
            await self.disconnect()
        except KeyError:
            pass

    async def add_tracks(self, ctx: Context, tracks) -> str:
        if not tracks:
            raise NoTracksFound

        response = 'Хз'
        if isinstance(tracks, wavelink.YouTubePlaylist):
            self.queue.add(ctx.author.id, *tracks.tracks)
            response = f"Добавила {len(tracks.tracks)} треков в очередь, сладенький."
        elif isinstance(tracks, wavelink.Track):
            self.queue.add(ctx.author.id, tracks)
            response = f"Добавила {len(tracks)} треков в очередь, сладенький."
        elif len(tracks) == 1:
            self.queue.add(ctx.author.id, tracks[0])
            response = f"Добавила {tracks[0].title} в очередь, сладенький."
        else:
            if (track := await self.choose_track(ctx, tracks)) is not None:
                self.queue.add(ctx.author.id, track)
                response = f"Добавила {track.title} в очередь, сладенький."

        if not self.is_playing() and not self.queue.is_empty:
            await self.start_playback()
        
        return response

    async def choose_track(self, ctx: Context, tracks: list):
        embed = discord.Embed(
            title="Выбери песню",
            description=(
                "\n".join(
                    f"**{i+1}.** {t.title} ({t.length//60000}:{str(t.length%60).zfill(2)})"
                    for i, t in enumerate(tracks[:5])
                )
            ),
            colour=options.get_embed_color,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Результаты поиска")
        embed.set_footer(
            text=f"Запросил {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else '')

        song_selector = Player.SongSelector(ctx.author.id, timeout=60)
        msg = await ctx.send(embed=embed, view=song_selector)
        choice = await song_selector.get_choice()
        await msg.delete()
        if choice >= 0:
            return tracks[choice]

    async def start_playback(self):
        await self.play(self.queue.current_track)

    async def advance(self):
        try:
            if (track := self.queue.get_next_track()):
                await self.play(track)
            else:
                await self.stop()
        except QueueIsEmpty:
            await self.stop()

    async def repeat_track(self):
        await self.play(self.queue.current_track)

    async def stop(self):
        self.selfDestructor.start()
        return await super().stop()

    async def disconnect(self, *, force: bool = False) -> None:
        self.queue.clear()
        return await super().disconnect(force=force)

    class SongSelector(discord.ui.View):
        class CallBackButton(discord.ui.Button):

            def __init__(self, user_id: int, style, label, custom_id, emoji=None):
                self.user_id = user_id
                super().__init__(style=style, label=label, custom_id=custom_id, emoji=emoji)

            async def callback(self, interaction: discord.Interaction):
                assert self.view is not None
                if interaction.user.id == self.user_id:
                    view: Player.SongSelector = self.view
                    view._choice = int(self.custom_id)
                    view._event.set()
                else:
                    await interaction.response.send_message(
                        "Эээй, ты не тот за кого себя выдаешь. Это запрос другого человека, найди себе свой!",
                        ephemeral=True
                    )
                await super().callback(interaction)

        _choice = -1
        _event = asyncio.Event()

        def __init__(self, requested_user_id: int, timeout=60, count=5):
            super().__init__(timeout=timeout)
            self._event.clear()
            for i in range(count):
                self.add_item(Player.SongSelector.CallBackButton(requested_user_id, label=str(i+1),
                                                                 style=discord.ButtonStyle.blurple, custom_id=str(i)))

        async def on_timeout(self):
            self._event.set()
            return await super().on_timeout()

        async def get_choice(self) -> int:
            await self._event.wait()
            self.stop()
            return int(self._choice)


class PlayerControls(discord.ui.View):
    player: Player
    ctx: Context
    _message: discord.Message
    _stop = False
    _task: asyncio.Task = None

    def __init__(self, player: Player, ctx: Context, update_interval=10):
        super().__init__(timeout=None)
        self.player = player
        self.ctx = ctx
        self.update_interval = update_interval
        self.create_update_task()

    @property
    def message(self) -> discord.Message:
        return self._message

    @message.setter
    def message(self, message: discord.Message):
        self.create_update_task()
        self._message = message

    def create_update_task(self):
        if not self._task or self._task.done():
            self._stop = False
            self._task = asyncio.create_task(self.update())

    async def update(self):
        await asyncio.sleep(self.update_interval)
        assert self.message
        while not self._stop:
            if not self.player.is_connected:
                await self.message.delete()
                self.stop()
                break
            try:
                await self.message.edit(embed=self.generate_player_embed())
            except NotFound:
                self._stop = True
                break
            await asyncio.sleep(self.update_interval)

    def stop(self):
        self._stop = True
        return super().stop()

    def generate_player_embed(self):
        play_state_emoji = ''
        if self.player.is_paused():
            play_state_emoji = '⏸️'
        elif self.player.is_playing:
            play_state_emoji = '▶️'
        else:
            play_state_emoji = '⏹️'
        embed = discord.Embed(
            title=f"{play_state_emoji}Сейчас играет",
            colour=options.get_embed_color,
            timestamp=dt.datetime.utcnow(),
        )
        embed.set_footer(
            text=f"Запросил {self.ctx.author.display_name}", icon_url=self.ctx.author.avatar.url if self.ctx.author.avatar else '')
        embed.add_field(name="Название трека",
                        value=self.player.queue.current_track.title if not self.player.queue.is_empty and self.player.queue.current_track
                        else "Очередь пуста, добавь музыку командой !p", inline=False)
        if not self.player.queue.is_empty and self.player.queue.current_track:

            embed.add_field(
                name="Исполнитель", value=self.player.queue.current_track.author, inline=False)

            position = divmod(self.player.position, 60)
            length = divmod(self.player.queue.current_track.length, 60)
            percent = round((self.player.position*20)/self.player.queue.current_track.length)
            embed.add_field(
                name="Время",
                value=f"{int(position[0])}:{round(position[1]):02}/{int(length[0])}:{round(length[1]):02}"
                f"\n[{':blue_square:'*percent}{':black_large_square:'*(20-percent)}]",
                inline=False
            )
        return embed

    @discord.ui.button(emoji='⏮️', style=discord.ButtonStyle.gray)
    async def prev(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            if not self.player.queue.history:
                await interaction.response.send_message('Это первый трек', ephemeral=True)
                return
        except QueueIsEmpty:
            await interaction.response.send_message('Очередь пуста', ephemeral=True)
            return
        if not interaction.user.guild_permissions.administrator and not (self.player.queue.get_track_owner() or interaction.user.id) == interaction.user.id:
            await interaction.response.send_message('Нельзя пропускать чужие треки!', ephemeral=True)
            return
        self.player.queue.position -= 2
        await self.player.advance()
        await asyncio.sleep(0.5)
        await interaction.response.edit_message(view=self, embed=self.generate_player_embed())

    @discord.ui.button(emoji='⏸️', style=discord.ButtonStyle.gray)
    async def play_pause(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.player.queue.is_empty:
            await interaction.response.send_message('В очереди больше ничего нет!', ephemeral=True)
            return
        if not self.player.is_paused():
            button.emoji = '▶️'
            await self.player.set_pause(True)
        else:
            button.emoji = '⏸️'
            await self.player.set_pause(False)
        await interaction.response.edit_message(view=self, embed=self.generate_player_embed())

    @discord.ui.button(emoji='⏹️', style=discord.ButtonStyle.gray)
    async def stop_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator and not (self.player.queue.get_track_owner() or interaction.user.id) == interaction.user.id:
            await interaction.response.send_message('Нельзя пропускать чужие треки!', ephemeral=True)
            return
        self.player.queue.clear()
        await self.player.stop()
        await asyncio.sleep(0.5)
        await interaction.response.edit_message(view=self, embed=self.generate_player_embed())

    @discord.ui.button(emoji='⏭️', style=discord.ButtonStyle.gray)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator and not (self.player.queue.get_track_owner() or interaction.user.id) == interaction.user.id:
            await interaction.response.send_message('Нельзя пропускать чужие треки!', ephemeral=True)
            return
        await self.player.advance()
        await asyncio.sleep(0.5)
        await interaction.response.edit_message(view=self, embed=self.generate_player_embed())

    @discord.ui.button(emoji='🔄', style=discord.ButtonStyle.gray)
    async def update_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(view=self, embed=self.generate_player_embed())


class Music(commands.Cog):
    qualified_name = 'Music'
    description = 'Играет музыку'
    player_controls = {}

    def __init__(self, bot):
        self.bot: discord.client.Client = bot
        self.bot.loop.create_task(self.start_nodes())
        self.spotify_client = SpotifyClient(client_id=spotipy_client_id, client_secret=spotipy_client_secret)

    @commands.Cog.listener()
    async def on_node_ready(self, node):
        logging.info(f" wavelink node `{node.identifier}` ready.")

    @commands.Cog.listener("on_track_stuck")
    @commands.Cog.listener("on_track_end")
    @commands.Cog.listener("on_track_exception")
    @commands.Cog.listener("on_player_stop")
    async def on_player_stop(self, node: wavelink.Node, payload):
        if hasattr(payload, 'error'):
            logging.warning(payload.error)
            return
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
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()

        nodes = {
            "MAIN": {
                "host": "127.0.0.1",
                "port": 2333,
                "password": "youshallnotpass",
                "identifier": "MAIN",
                "region": "europe",
            }
        }

        for node in nodes.values():
            await wavelink.NodePool.create_node(bot=self.bot, **node, spotify_client=self.spotify_client)

    async def get_player(self, ctx: commands.Context) -> Player:
        if not ctx.voice_client and ctx.author.voice:
            return await ctx.author.voice.channel.connect(cls=Player)
        else:
            return ctx.voice_client

    # music_group = discord.SlashCommandGroup("music", "Все что связанно с музыкой и больше")

    @commands.command(name="disconnect", aliases=["leave"],
                      brief='Отключиться от голосового канала', description='Отключиться от голосового канала')
    async def disconnect_command(self, ctx):
        player = await self.get_player(ctx)
        await player.teardown()
        await ctx.send("Ну все, пока.")

    @slash_command(name="disconnect",
                   description='Отключиться от голосового канала')
    @guild_only()
    async def disconnect_slash(self, interaction: discord.ApplicationContext):
        player = await self.get_player(interaction)
        await player.teardown()
        await interaction.response.send_message("Ну все, пока.")

    async def play(self, ctx, query: str) -> str:
        player = await self.get_player(ctx)
        if not player:
            return 'Не могу подключится'
        if query is None:
            if player.queue.is_empty:
                raise QueueIsEmpty
            await player.set_pause(False)
            if not player.is_playing():
                await player.start_playback()
            return "Продолжаем."

        else:
            query = query.strip("<>")
            if not re.match(URL_REGEX, query):
                return await player.add_tracks(ctx, await wavelink.YouTubeTrack.search(query))
            elif 'spotify.com' not in query:
                if 'list' not in query:
                    return await player.add_tracks(ctx, await wavelink.YouTubeTrack.search(query, return_first=True))
                else:
                    return await player.add_tracks(ctx, await wavelink.YouTubePlaylist.search(query))
            elif 'spotify.com' in query:
                return await player.add_tracks(ctx, await SpotifyTrack.search(query))
        return 'Чот я не поняла'

    @commands.command(name="play", aliases=["p"],
                      brief='Поиск музыки', description='Поиск твоей любимой музыки в интернете. Будем вместе слушать ^.^')
    async def play_command(self, ctx, *, query: t.Optional[str]):
        await ctx.reply(await self.play(ctx, query))

    @play_command.error
    async def play_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("Ничего в очереди нет(")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("Немогу подключиться к каналу, сорян(")
        else:
            logging.exception(exc)

    @slash_command(name="play",
                   description='Поиск твоей любимой музыки в интернете. Будем вместе слушать ^.^')
    @guild_only()
    async def play_slash(self, ctx: discord.ApplicationContext, query: discord.Option(str, "Поисковый запрос", default=None)):
        await ctx.interaction.response.defer()
        await ctx.interaction.followup.send(await self.play(ctx, query))

    @play_slash.error
    async def play_slash_error(self, ctx: ApplicationContext, exc):
        if isinstance(exc.original, QueueIsEmpty):
            await ctx.followup.edit_message("Ничего в очереди нет(")
        elif isinstance(exc.original, NoVoiceChannel):
            await ctx.followup.edit_message("Немогу подключиться к каналу, сорян(")
        else:
            logging.exception(exc)

    @commands.command(name="pause",
                      brief='Поставить на паузу', description='Поставить на паузу')
    async def pause_command(self, ctx):
        player = await self.get_player(ctx)

        if player.is_paused():
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
        player = await self.get_player(ctx)
        if not ctx.author.guild_permissions.administrator and not (player.queue.get_track_owner() or ctx.author.id) == ctx.author.id:
            await ctx.reply('Нельзя останавливать чужие треки, бака!')
            return
        player.queue.clear()
        await player.stop()
        await ctx.send("Остановлено")

    @commands.command(name="next", aliases=["skip"],
                      brief='Запустить следующий трек', description='Запустить следующий трек')
    async def next_command(self, ctx):
        player = await self.get_player(ctx)
        if not ctx.author.guild_permissions.administrator and not (player.queue.get_track_owner() or ctx.author.id) == ctx.author.id:
            await ctx.reply('Нельзя пропускать чужие треки, бака!')
            return
        await player.stop()
        if not player.queue.upcoming:
            await ctx.send("Ну вот и все")
        else:
            await ctx.send("Играем дальше")

    @next_command.error
    async def next_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("Очередь и так пустая, куда дальше?")

    @commands.command(name="previous", aliases=['prev'],
                      brief='Играть предыдущий трек', description='Играть предыдущий трек')
    async def previous_command(self, ctx):
        player = await self.get_player(ctx)
        if not ctx.author.guild_permissions.administrator and not (player.queue.get_track_owner() or ctx.author.id) == ctx.author.id:
            await ctx.reply('Нельзя пропускать чужие треки, бака!')
            return
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

        player = await self.get_player(ctx)
        player.queue.set_repeat_mode(mode)
        await ctx.send(f"Установила {mode} как режим повтора.")

    @slash_command(name="repeat",
                   description='Установить режим повтора.')
    @guild_only()
    async def repeat_slash(self, ctx: ApplicationContext, mode: Option(str, choices=['none', '1', 'all'])):
        player = await self.get_player(ctx)
        player.queue.set_repeat_mode(mode)
        await ctx.interaction.response.send_message(f"Установила {mode} как режим повтора.")

    @repeat_command.error
    async def repeat_command_error(self, ctx, exc):
        if isinstance(exc, InvalidRepeatMode):
            await ctx.send("Невалидный режим повтора, иди смотри справку")

    async def queue_pages(self, ctx):
        player = await self.get_player(ctx)
        show = 10
        embed = discord.Embed(
            title="Очередь",
            description=f"Показываю тебе до {show} следующих треков",
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_footer(
            text=f"Запросил {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.add_field(
            name="Сейчас играет",
            value=f"({player.queue.position+1}/{player.queue.length}) {player.queue.current_track.title}" if player.queue.current_track else
                  "Ничего сейчас не играет(\nЗапроси трек командой play",
            inline=False
        )
        pages_embeds = []
        if upcoming := player.queue.upcoming:
            for idx in range(0, len(upcoming), show):
                new_embed = deepcopy(embed)
                new_embed.add_field(
                    name="Далее в программе",
                    value="\n".join(f"{idx+player.queue.position+2+i}) {t.title}" for i, t in enumerate(upcoming[idx:idx + show]) if t),
                    inline=False
                )
                pages_embeds.append(new_embed)
        embed.add_field(name="Всего треков", value=player.queue.length, inline=False)
        return pages_embeds

    @commands.command(name="queue", aliases=["q"],
                      brief='Показать очередь', description='Показать очередь')
    async def queue_command(self, ctx):
        embeds = await self.queue_pages(ctx)
        await ctx.send(embed=embeds[0])

    @queue_command.error
    async def queue_command_error(self, ctx: Context, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("Ничего нет")

    @slash_command(name="queue", description='Показать очередь')
    @guild_only()
    async def queue_slash(self, ctx: ApplicationContext):
        paginator = pages.Paginator(pages=await self.queue_pages(ctx), disable_on_timeout=True, timeout=60)
        await paginator.respond(ctx.interaction)

    @queue_slash.error
    async def queue_slash_error(self, ctx: ApplicationContext, exc):
        await ctx.response.send_message("Ничего нет", ephemeral=True)

    @commands.command(name="shuffle",
                      brief='Перемешать очередь',
                      description='Перемешивает очередь чтобы тебе было не так противно слушать одни и те же плейлисты на повторе')
    async def shuffle_command(self, ctx):
        player = await self.get_player(ctx)
        player.queue.shuffle()
        await ctx.reply('Перемешала. Теперь как будто слушаешь новый плейлист.')

    @slash_command(name="shuffle",
                   description='Перемешивает очередь чтобы тебе было не так противно слушать одни и те же плейлисты на повторе')
    @guild_only()
    async def shuffle_slash(self, ctx: ApplicationContext):
        player = await self.get_player(ctx)
        player.queue.shuffle()
        await ctx.interaction.response.send_message('Перемешала. Теперь как будто слушаешь новый плейлист.')

    @commands.command(name="playing", aliases=["np"],
                      brief='Показать что сейчас играет', description='Показать что сейчас играет')
    async def playing_command(self, ctx: Context):
        player = await self.get_player(ctx)

        if not player.is_playing:
            raise PlayerIsAlreadyPaused

        if player in self.player_controls and not self.player_controls[player].is_finished():
            controls: PlayerControls = self.player_controls[player]
            try:
                if isinstance(controls._message, Interaction):
                    await controls._message.delete_original_message()
                else:
                    await controls._message.delete()
            except NotFound as e:
                logging.warning(e)
        else:
            controls = PlayerControls(player, ctx)
        controls.message = await ctx.send(embed=controls.generate_player_embed(), view=controls)
        self.player_controls[player] = controls

    @playing_command.error
    async def playing_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send("Ничего не играет(")

    @slash_command(name="np",
                   description='Показать что сейчас играет')
    @guild_only()
    async def playing_slash(self, ctx: ApplicationContext):
        player = await self.get_player(ctx)

        if player in self.player_controls and not self.player_controls[player].is_finished():
            controls: PlayerControls = self.player_controls[player]
            try:
                if isinstance(controls._message, Interaction):
                    await controls._message.delete_original_message()
                else:
                    await controls._message.delete()
            except NotFound as e:
                logging.warning(e)
        else:
            controls = PlayerControls(player, ctx)
        controls.message = await ctx.interaction.response.send_message(embed=controls.generate_player_embed(), view=controls)
        self.player_controls[player] = controls

    @commands.command(name="skipto", aliases=["playindex", "pi"],
                      brief='Перейти сразу к треку под номером N', description='Перейти сразу к треку под номером N. N указывать через пробел')
    async def skipto_command(self, ctx, index: int):
        player = await self.get_player(ctx)
        if not ctx.author.guild_permissions.administrator and not (player.queue.get_track_owner() or ctx.author.id) == ctx.author.id:
            await ctx.reply('Нельзя пропускать чужие треки, бака!')
            return
        if player.queue.is_empty:
            raise QueueIsEmpty

        if not 0 <= index <= player.queue.length:
            raise NoMoreTracks

        player.queue.position = index - 1
        await player.stop()
        await ctx.send(f"Играем музяку под номером {index}.")
        await player.start_playback()

    @skipto_command.error
    async def skipto_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("Ничего не играет.")
        elif isinstance(exc, NoMoreTracks):
            await ctx.send("Указан неверный номер(")

    @slash_command(name="skipto", aliases=["playindex", "pi"],
                   description='Перейти сразу к треку под номером index')
    async def skipto_slash(self, ctx: ApplicationContext, index: Option(int, description='Номер песни')):
        player = await self.get_player(ctx)
        if not ctx.author.guild_permissions.administrator and not (player.queue.get_track_owner() or ctx.author.id) == ctx.author.id:
            await ctx.reply('Нельзя пропускать чужие треки, бака!')
            return
        if player.queue.is_empty:
            await ctx.response.send_message('Ничего не играет.')

        if not 0 <= index <= player.queue.length:
            await ctx.response.send_message('Указан неверный номер')

        player.queue.position = index - 1
        await player.stop()
        await ctx.response.send_message(f"Играем музяку под номером {index}.")
        await player.start_playback()

    @commands.command(name="restart",
                      brief='Запустить трек заново', description='Запустить трек заново, все хуйня Саня, дайвай по новой!')
    async def restart_command(self, ctx):
        player = await self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        await player.seek(0)
        await ctx.send("Перезапустила")

    @restart_command.error
    async def restart_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("Нечего перезапускать")


def setup(bot):
    bot.add_cog(Music(bot))
