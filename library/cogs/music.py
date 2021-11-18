from discord.ext import commands
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.commands import command, guild_only
import discord
from library.__init__ import data
import wavelink


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot
    
        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=self.bot)
        self.bot.loop.create_task(self.start_nodes())
    
    
    async def start_nodes(self):
        await self.bot.wait_until_ready()

        # Initiate our nodes. For this example we will use one server.
        # Region should be a discord.py guild.region e.g sydney or us_central (Though this is not technically required)
        await self.bot.wavelink.initiate_node(host='0.0.0.0',
                                              port=2333,
                                              rest_uri='http://127.0.0.1:2333',
                                              password='youshallnotpass',
                                              identifier='TEST',
                                              region='europe')
    
    
    @guild_only()
    @command(name="connect", aliases=["залетай"])
    async def connect_to_channel(self, ctx, channel: discord.VoiceChannel=None):
        """
        connects bot to channel
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise discord.DiscordException(f"***{ctx.message.author.mention} - join voice channel and try again ***")
        
        player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.send(f'Connected to **`{channel.name}`**')
        await player.connect(channel.id)
    
    
    @guild_only()
    @command(name="play", aliases=["играй"])
    async def play(self, ctx,  *, query: str):
        tracks = await self.bot.wavelink.get_tracks(f'ytsearch:{query}')

        if not tracks:
            return await ctx.send('Could not find any songs with that query.')

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.invoke(self.connect_)

        await ctx.send(f'Added {str(tracks[0])} to the queue.')
        await player.play(tracks[0])


    @guild_only()
    @command(name="add", aliases=["очередь"])
    async def add_music_to_queue(self, ctx, src:str) -> None:
        """
        adds song to server queue
        """
    pass

    
    @add_music_to_queue.error
    async def add_music_to_queue_handler(self, ctx, error):
        """
        self error handler for music command
        """
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("*** Не добавлена ссылка / название ***", delete_after=data.get_del_after)    


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Commands(bot))
