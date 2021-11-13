from discord.ext.commands import command, has_permissions, cooldown, guild_only
from discord.ext.commands.cooldowns import BucketType
from library.data.presf_images import fimages
from discord.ext.commands import Cog
from library.__init__ import Amia
from random import choice
from json import load
import discord

with open("library/config/config.json","rb") as json_config_file:
    data = load(json_config_file)
    try:
        misc_cooldown = int(data["default_settings"]["chat_misc_cooldown"])
    except KeyError:
        exit("'config.json' is damaged!") 


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("library/config/config.json","rb") as json_config_file:
            data = load(json_config_file)
            try:
                self.embed_color = int(data["default_settings"]["embed_color"],16)
            except KeyError:
                exit("'config.json' is damaged!")
     


    @command(name="hello", aliases=["hi","привет"])
    async def hello(self, ctx):
        """
        Congratulations command
        """
        await ctx.message.delete()
        await ctx.send(f"{choice(('Hello', 'Hi', 'Hey', 'Hiya'))} {ctx.author.mention}!")

    @command(name="say", aliases=["скажи"], brief='Говорить устами бота', description='Говорить устами бота')
    @guild_only()
    @has_permissions(administrator=True)
    async def say(self, ctx, *input):
        """
        Bot say what u what whenever u want. Need administrator rights.
        
        """
        #TODO: send pm or msg to channel via arguments
        await ctx.message.channel.send(" ".join(input))
        await ctx.message.delete()

    @guild_only()
    @command(name="f", aliases=["ф"], brief='Отдать честь за почивших героев', description='Отдать честь за почивших героев')
    @cooldown(1, misc_cooldown, BucketType.user)
    async def pressf(self, ctx, *input):
        """
        press f for fallen heroes.
        sends simple picture of saluting girl. can mention people
        """
        if len(ctx.message.mentions) > 0:
            title = f"**{ctx.author.display_name}** заплатил увожение за {ctx.message.mentions[0].display_name}"
        else:
            title=f"**{ctx.author.display_name}** заплатил увожение. o7"
        emb = discord.Embed(title=title, color=self.embed_color)
        emb.set_image(url="https://pbs.twimg.com/media/D-5sUKNXYAA5K9l.jpg")
        await ctx.message.channel.send(embed=emb)
        
    @guild_only()
    @command(name="o7", aliases=["07","о7"], brief='Поприветсвовать командиров', description='Поприветсвовать командиров, а можно и конкретного')
    @cooldown(1, misc_cooldown, BucketType.user)
    async def o7(self, ctx, *input):
        """
        greet fellow commanders
        can mention whom to greet
        """
        if len(ctx.message.mentions) > 0:
            title = f"**{ctx.author.display_name}** приветствует {ctx.message.mentions[0].display_name}. o7"
        else:
            title=f"**{ctx.author.display_name}** приветствует вас командиры. o7"
        emb = discord.Embed(title=title, color=self.embed_color)
        emb.set_image(url=choice(fimages))
        await ctx.message.channel.send(embed=emb)  
              

    @command(name="avatar", aliases=["аватар"], brief='Показывает аватар пользователя', description='Показывает твой аватар. С помощью упоминания можно посмотреть аватар другого пользователя')
    @cooldown(1, misc_cooldown, BucketType.user)
    async def avatar(self, ctx, *input):
        if len(input) > 0:
            title = f"Аватар {ctx.message.mentions[0].display_name}"
            url = ctx.message.mentions[0].avatar_url
        else:
            title = f"Аватар {ctx.message.author.display_name}"
            url = ctx.message.author.avatar_url
        emb = discord.Embed(title=title, color=self.embed_color)
        emb.set_image(url=url)
        await ctx.message.channel.send(embed=emb)


    @guild_only()
    @command(name="info", aliases=["инфо"])
    async def info(self, ctx):
        """
        This command shows bot info
        """
        await ctx.message.delete()
        embed = discord.Embed(color=self.embed_color, title=Amia.name,
                              url=f"https://www.youtube.com/watch?v=X5ULmETDiXI")
        embed.add_field(name="Description", value="Тупая деффка еще и бот", inline=False)
        
        commands = []
        for command in self.bot.walk_commands():
            commands.append(command.name)

        ark_stat = Amia.get_ark_stats()
        ger_stat = Amia.get_ger_stats()
        embed.add_field(name="Статистика арков", value=f"Арков выкручено за все время: {ark_stat.total}\nВсего собрано персонажей: {ark_stat.total_chars}", inline=False)
        embed.add_field(name="Статистика пуков", value=f"""Пуков за все время: {ger_stat.total}
        Из них самообсеров: {ger_stat.total_self}
        Попаданий по ботам: {ger_stat.total_bot}
        Попаданий по мне:disappointed_relieved: : {ger_stat.total_me}""", inline=False)
        
        embed.set_thumbnail(
            url="https://aceship.github.io/AN-EN-Tags/img/factions/logo_rhodes.png")
        embed.set_image(url="https://aceship.github.io/AN-EN-Tags/img/characters/char_002_amiya_epoque%234.png")
        embed.set_footer(text=f"Requested by {ctx.message.author.display_name}")
        await ctx.send(embed=embed, delete_after=30)


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Commands(bot))
