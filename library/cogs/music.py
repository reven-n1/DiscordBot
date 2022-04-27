from email.message import Message
from discord import ApplicationContext, Interaction, InteractionMessage, Option, slash_command
from library.bot_token import spotipy_client_id, spotipy_client_secret
from wavelink.ext.spotify import SpotifyClient, SpotifyTrack, SpotifyRequestError
from discord.ext.commands.context import Context
from library.my_Exceptions.music_exceptions import NoVoiceChannel, QueueIsEmpty, NoTracksFound
from library.data.dataLoader import dataHandler
from discord.ext.commands import guild_only
from discord.ext import commands, pages
from typing import Dict, List
from random import shuffle
from asyncio import sleep
from copy import deepcopy
from enum import Enum
import datetime as dt
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
    _queue: List[wavelink.Track] = []
    position: int = 0
    repeat_mode: RepeatMode = RepeatMode.NONE
    _user_tracks: Dict[wavelink.Track, int] = {}

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

    @property
    def all(self):
        return self._queue

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
        if self.current_track:
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
        parent: wavelink.Player = None
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
                if self.parent.is_playing() and not self.parent.is_paused():
                    break
            if not self.parent.is_playing() or self.parent.is_paused():
                await self.parent.teardown()

    async def teardown(self):
        self.queue.clear()
        await self.disconnect()

    async def add_tracks(self, ctx: Context, tracks, playlist=False) -> str:
        if not tracks:
            raise NoTracksFound

        response = 'Ясно понятно'
        if isinstance(tracks, wavelink.YouTubePlaylist):
            self.queue.add(ctx.author.id, *tracks.tracks)
            response = f"Добавила {len(tracks.tracks)} треков в очередь, сладенький."
        elif isinstance(tracks, (list, set, tuple)) and playlist:
            self.queue.add(ctx.author.id, *tracks)
            response = f"Добавила {len(tracks)} треков в очередь, сладенький."
        elif isinstance(tracks, wavelink.Track):
            self.queue.add(ctx.author.id, tracks)
            response = f"Добавила {tracks.title} в очередь, сладенький."
        elif isinstance(tracks, (list, set, tuple)) and len(tracks) == 1:
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
                    f"**{i+1}.** {t.title} ({int(t.length//60)}:{int(float(str(t.length%60).zfill(2)))})"
                    for i, t in enumerate(tracks[:5])
                )
            ),
            colour=ctx.author.color,
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
        if self.queue.current_track:
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

    async def pause(self) -> None:
        self.selfDestructor.start()
        return await super().pause()

    async def set_pause(self, pause: bool) -> None:
        if pause:
            self.selfDestructor.start()
        return await super().set_pause(pause)

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
    _player: Player
    _ctx: Context
    _interaction: Interaction = None
    _message: Message = None
    _stop = False
    _task: asyncio.Task = None

    def __init__(self, player: Player, ctx: Context, update_interval=10):
        super().__init__(timeout=None)
        self._player = player
        self._ctx = ctx
        self.update_interval = update_interval

    @property
    def interaction(self) -> Interaction:
        return self._interaction

    @interaction.setter
    def interaction(self, interaction: Interaction):
        self._interaction = interaction
        self._message = None
        self.create_update_task()

    @property
    def message(self) -> Message:
        return self._message

    @message.setter
    def message(self, message: Interaction):
        self._message = message
        self.create_update_task()

    def create_update_task(self):
        if not self._task or self._task.done():
            self._stop = False
            self._task = asyncio.create_task(self.update())

    async def update(self):
        while not self._stop:
            await asyncio.sleep(self.update_interval)
            if not self._message and self._interaction:
                msg = await self._interaction.original_message()
                self._message = await self._interaction.channel.fetch_message(msg.id)
            if not self._player.is_connected():
                await self._message.delete()
                self.stop()
            try:
                await self._message.edit(embed=self.generate_player_embed())
            except discord.HTTPException as e:
                self.stop()
                logging.warning(e)
                await self._message.delete()
            except Exception as e:
                logging.exception(e)

    def stop(self):
        self._stop = True
        self._message = None
        self._interaction = None
        return super().stop()

    def is_stopped(self):
        return self._stop

    def generate_player_embed(self):
        play_state_emoji = ''
        if self._player.is_paused():
            play_state_emoji = '⏸️'
        elif self._player.is_playing():
            play_state_emoji = '▶️'
        else:
            play_state_emoji = '⏹️'
        embed = discord.Embed(
            title=f"{play_state_emoji}Сейчас играет",
            colour=self._ctx.author.colour,
            timestamp=dt.datetime.utcnow(),
        )
        embed.set_footer(
            text=f"Запросил {self._ctx.author.display_name}", icon_url=self._ctx.author.avatar.url if self._ctx.author.avatar else '')
        embed.add_field(name="Название трека",
                        value=self._player.queue.current_track.title if not self._player.queue.is_empty and self._player.queue.current_track
                        else "Очередь пуста, добавь музыку командой /play", inline=False)
        if not self._player.queue.is_empty and self._player.queue.current_track:

            embed.add_field(
                name="Исполнитель", value=self._player.queue.current_track.author, inline=False)

            position = divmod(self._player.position, 60)
            length = divmod(self._player.queue.current_track.length, 60)
            percent = round((self._player.position*20)/self._player.queue.current_track.length)
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
            if not self._player.queue.history:
                await interaction.response.send_message('Это первый трек', ephemeral=True)
                return
        except QueueIsEmpty:
            await interaction.response.send_message('Очередь пуста', ephemeral=True)
            return
        if not interaction.user.guild_permissions.administrator and not (self._player.queue.get_track_owner() or interaction.user.id) == interaction.user.id:
            await interaction.response.send_message('Нельзя пропускать чужие треки!', ephemeral=True)
            return
        self._player.queue.position -= 2
        await self._player.advance()
        await asyncio.sleep(0.5)
        await interaction.response.edit_message(view=self, embed=self.generate_player_embed())

    @discord.ui.button(emoji='⏸️', style=discord.ButtonStyle.gray)
    async def play_pause(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self._player.queue.is_empty:
            await interaction.response.send_message('В очереди больше ничего нет!', ephemeral=True)
            return
        if not self._player.is_paused():
            button.emoji = '▶️'
            await self._player.set_pause(True)
        else:
            button.emoji = '⏸️'
            await self._player.set_pause(False)
        await interaction.response.edit_message(view=self, embed=self.generate_player_embed())

    @discord.ui.button(emoji='⏹️', style=discord.ButtonStyle.gray)
    async def stop_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator and not (self._player.queue.get_track_owner() or interaction.user.id) == interaction.user.id:
            await interaction.response.send_message('Нельзя пропускать чужие треки!', ephemeral=True)
            return
        self._player.queue.clear()
        await self._player.stop()
        await asyncio.sleep(0.5)
        await interaction.response.edit_message(view=self, embed=self.generate_player_embed())

    @discord.ui.button(emoji='⏭️', style=discord.ButtonStyle.gray)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator and not (self._player.queue.get_track_owner() or interaction.user.id) == interaction.user.id:
            await interaction.response.send_message('Нельзя пропускать чужие треки!', ephemeral=True)
            return
        await self._player.advance()
        await asyncio.sleep(0.5)
        await interaction.response.edit_message(view=self, embed=self.generate_player_embed())

    @discord.ui.button(emoji='🔄', style=discord.ButtonStyle.gray)
    async def update_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(view=self, embed=self.generate_player_embed())


class Music(commands.Cog):
    qualified_name = 'Music'
    description = 'Играет музыку'
    player_controls: Dict[Player, PlayerControls] = {}

    def __init__(self, bot):
        self.bot: discord.client.Client = bot
        self.bot.loop.create_task(self.start_nodes())
        self.spotify_client = SpotifyClient(client_id=spotipy_client_id, client_secret=spotipy_client_secret)

    @commands.Cog.listener()
    async def on_node_ready(self, node):
        logging.info(f" wavelink node `{node.identifier}` ready.")

    @commands.Cog.listener("on_wavelink_track_stuck")
    @commands.Cog.listener("on_wavelink_track_exception")
    async def on_player_stop(self, player: Player, track: wavelink.Track, exception: Exception = None, *args, **kwargs):
        if exception:
            logging.warning(exception)
            player.advance()
            return

    @commands.Cog.listener("on_wavelink_track_end")
    async def on_track_end(self, player: Player, track: wavelink.Track, reason: str):
        if reason == 'FINISHED':
            if player.queue.repeat_mode == RepeatMode.ONE:
                await player.repeat_track()
            else:
                await player.advance()

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

    async def get_player(self, ctx: commands.Context, connect=False) -> Player:
        if not ctx.voice_client and ctx.author.voice and connect:
            return await ctx.author.voice.channel.connect(cls=Player)
        if ctx.voice_client:
            return ctx.voice_client
        raise NoVoiceChannel()

    @slash_command(name="disconnect",
                   description='Отключиться от голосового канала')
    @guild_only()
    async def disconnect_slash(self, interaction: discord.ApplicationContext):
        player = await self.get_player(interaction)
        await player.teardown()
        await interaction.response.send_message("Ну все, до новых встреч, пока!")

    async def play(self, ctx, query: str) -> str:
        player = await self.get_player(ctx, connect=True)
        if not re.match(URL_REGEX, query):
            return await player.add_tracks(ctx, await wavelink.YouTubeTrack.search(query))
        if 'spotify.com' not in query:
            if 'list' not in query:
                return await player.add_tracks(ctx, await wavelink.YouTubeTrack.search(query, return_first=True))
            return await player.add_tracks(ctx, await wavelink.YouTubePlaylist.search(query))
        if 'spotify.com' in query:
            tries = 10
            res = None
            while tries > 0:
                try:
                    if 'track' in query:
                        res = await player.add_tracks(ctx, await SpotifyTrack.search(query, return_first=True))
                    else:
                        res = await player.add_tracks(ctx, await SpotifyTrack.search(query), playlist=True)
                except SpotifyRequestError as e:
                    logging.exception(e)
                    tries -= 1
                    await sleep(5)
                else:
                    return res
        return 'Чот я не поняла'

    @slash_command(name="play",
                   description='Поиск твоей любимой музыки в интернете. Будем вместе слушать ^.^')
    @guild_only()
    async def play_slash(self, ctx: discord.ApplicationContext, query: discord.Option(str, "Поисковый запрос")):
        await ctx.interaction.response.defer()
        try:
            await ctx.interaction.followup.send(await self.play(ctx, query))
        except NoVoiceChannel:
            await ctx.interaction.followup.send('Ты не подключен к каналу!')
        except Exception as e:
            await ctx.interaction.followup.send('Ошибочка вышла')
            logging.exception(e)

    @play_slash.error
    async def play_slash_error(self, ctx: ApplicationContext, exc):
        if isinstance(exc.original, QueueIsEmpty):
            await ctx.followup.edit_message("Ничего в очереди нет(")
        elif isinstance(exc.original, NoVoiceChannel):
            await ctx.followup.edit_message("Немогу подключиться к каналу, сорян(")
        else:
            logging.exception(exc)

    @slash_command(name="repeat",
                   description='Установить режим повтора.')
    @guild_only()
    async def repeat_slash(self, ctx: ApplicationContext, mode: Option(str, choices=['none', '1', 'all'])):
        player = await self.get_player(ctx, connect=False)
        player.queue.set_repeat_mode(mode)
        await ctx.interaction.response.send_message(f"Установила {mode} как режим повтора.")

    async def queue_pages(self, ctx):
        player = await self.get_player(ctx, connect=False)
        show = 10
        embed = discord.Embed(
            title="Очередь",
            description=f"Показываю тебе до {show} следующих треков",
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_footer(
            text=f"Запросил {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        try:
            current_track = player.queue.current_track
        except QueueIsEmpty:
            current_track = None
        embed.add_field(
            name="Сейчас играет",
            value=f"({player.queue.position+1}/{player.queue.length}) {player.queue.current_track.title}" if current_track else
                  "Ничего сейчас не играет(\nЗапроси трек командой play",
            inline=False
        )
        embed.add_field(name="Всего треков", value=player.queue.length, inline=False)
        pages_embeds = []
        if upcoming := player.queue.all:
            for idx in range(0, len(upcoming), show):
                new_embed = deepcopy(embed)
                new_embed.add_field(
                    name="Очередь",
                    value="\n".join(f"{idx+1+i}) {t.title}" for i, t in enumerate(upcoming[idx:idx + show]) if t),
                    inline=False
                )
                pages_embeds.append(new_embed)
        if not pages_embeds:
            pages_embeds.append(embed)
        return pages_embeds

    @slash_command(name="queue", description='Показать очередь')
    @guild_only()
    async def queue_slash(self, ctx: ApplicationContext):
        await ctx.response.defer()
        custom_buttons = [
            pages.PaginatorButton("first", emoji="⏪", style=discord.ButtonStyle.gray),
            pages.PaginatorButton("prev", emoji="⬅", style=discord.ButtonStyle.gray),
            pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True),
            pages.PaginatorButton("next", emoji="➡", style=discord.ButtonStyle.gray),
            pages.PaginatorButton("last", emoji="⏩", style=discord.ButtonStyle.gray),
        ]
        paginator = pages.Paginator(pages=await self.queue_pages(ctx),
                                    use_default_buttons=False,
                                    custom_buttons=custom_buttons)
        await paginator.respond(ctx.interaction)
        asyncio.create_task(self.queue_updater(paginator, ctx))

    async def queue_updater(self, paginator: pages.Paginator, ctx: ApplicationContext):
        player = await self.get_player(ctx, connect=False)
        while not paginator.is_finished() and player.is_connected():
            await sleep(10)
            current_page = paginator.current_page
            try:
                paginator.pages = await self.queue_pages(ctx)
                paginator.page_count = len(paginator.pages) - 1
            except NoVoiceChannel:
                break
            if current_page > len(paginator.pages) - 1:
                current_page = 0
            try:
                await paginator.goto_page(current_page)
            except discord.HTTPException as e:
                logging.warning(e)
                break
        try:
            await paginator.disable()
        except discord.HTTPException:
            pass

    @queue_slash.error
    async def queue_slash_error(self, ctx: ApplicationContext, exc):
        if isinstance(exc.original, QueueIsEmpty):
            await ctx.response.send_message("Ничего нет", ephemeral=True)
        else:
            await self.no_voice_error(ctx, exc)

    @slash_command(name="shuffle",
                   description='Перемешивает очередь чтобы тебе было не так противно слушать одни и те же плейлисты на повторе')
    @guild_only()
    async def shuffle_slash(self, ctx: ApplicationContext):
        player = await self.get_player(ctx, connect=False)
        if not player:
            await ctx.interaction.response.send_message('Нет подключения к войсу')    
        player.queue.shuffle()
        await ctx.interaction.response.send_message('Перемешала. Теперь как будто слушаешь новый плейлист.')

    @slash_command(name="np",
                   description='Показать что сейчас играет и управлять воспроизведением')
    @guild_only()
    async def playing_slash(self, ctx: ApplicationContext):
        player = await self.get_player(ctx)

        if player in self.player_controls:
            controls: PlayerControls = self.player_controls[player]
            try:
                await controls._message.delete()
            except discord.HTTPException as e:
                logging.warning(e)
        else:
            controls = PlayerControls(player, ctx)
        controls.interaction = await ctx.interaction.response.send_message(embed=controls.generate_player_embed(), view=controls)
        self.player_controls[player] = controls

    @slash_command(name="skipto", description='Перейти сразу к треку под номером index')
    @guild_only()
    async def skipto_slash(self, ctx: ApplicationContext, index: Option(int, description='Номер песни', min_value=1)):
        player = await self.get_player(ctx)
        if not ctx.author.guild_permissions.administrator and not (player.queue.get_track_owner() or ctx.author.id) == ctx.author.id:
            await ctx.response.send_message('Нельзя пропускать чужие треки, бака!')
            return
        if player.queue.is_empty:
            await ctx.response.send_message('Ничего не играет.')
            return
        if not (0 < index < player.queue.length):
            await ctx.response.send_message('Указан неверный номер')
            return

        player.queue.position = index - 1
        await player.stop()
        await ctx.response.send_message(f"Играем музяку под номером {index}.")
        if not player.is_playing():
            await player.start_playback()

    @disconnect_slash.error
    @repeat_slash.error
    @shuffle_slash.error
    @playing_slash.error
    @skipto_slash.error
    async def no_voice_error(self, ctx: ApplicationContext, exc):
        if isinstance(exc.original, NoVoiceChannel):
            await ctx.respond("Нет подключения к войсу!", ephemeral=True)
        else:
            raise exc


def setup(bot):
    bot.add_cog(Music(bot))
