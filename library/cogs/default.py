from nextcord.ext.commands import command, has_permissions, cooldown, guild_only
from library import bot, data, user_guild_cooldown
from discord_slash.utils.manage_components import wait_for_component
from library.data.pressf_images import fimages
from nextcord.ext.commands import Cog
from collections import namedtuple
from random import choice
from library import db
from json import load
import nextcord
from discord_slash import cog_ext, SlashContext

class Default(Cog):
    qualified_name = 'Default'
    description = 'Стандартные команды'
    
    def __init__(self, bot):
        self.bot = bot
        self.name = "Amia(bot)"
        self.__delete_quantity = 100       
        self.__db = db
        
        with open("library/config/config.json","rb") as json_config_file:
            data = load(json_config_file)
            try:
                self.embed_color = int(data["default_settings"]["embed_color"],16)
            except KeyError:
                exit("'config.json' is damaged!")
     
     
    # cog commands------------------------------------------------------------------------------------------------------------------------

    @cog_ext.cog_slash(name="ping", )
    async def ping(self, ctx: SlashContext):
        from discord_slash.utils.manage_components import create_button, create_actionrow
        from discord_slash.model import ButtonStyle

        buttons = [
            create_button(style=ButtonStyle.green, label="A green button", custom_id='greeeny'),
            create_button(style=ButtonStyle.blue, label="A blue button", custom_id='useless')
        ]
        action_row = create_actionrow(*buttons)

        await ctx.send(content="Pong!",components=[action_row])
        button_ctx = await wait_for_component(bot, components=action_row)
        # await button_ctx.edit_origin(content="You pressed a button!")
        # await button_ctx.reply('U win')
        await button_ctx.edit_origin(content='U lose', components=None)
    

    @command(name="ping", aliases=["пинг"],
    brief='Понг. Проверяет пинг до дискорда.', description='Понг. Проверяет пинг до дискорда.')
    async def ping(self, ctx):
        """
        Checks ping
        """
        await ctx.send(f"Pong: `{round(self.bot.latency*1000, 1)}` ms")

    @command(name="hello", aliases=["hi", "привет"],
    brief='Привет, братик', description='Привет, братик')
    async def hello(self, ctx):
        """
        Congratulations command
        """
        await ctx.send(f"{choice(('Hello', 'Hi', 'Hey', 'Hiya'))} {ctx.author.mention}!")

    @command(name="say", aliases=["скажи"], 
    brief='Я скажу все что ты хочешь, братик.', description='Я скажу все что ты хочешь, братик. Разве что тебе админом нужно быть)')
    @guild_only()
    @has_permissions(administrator=True)
    async def say(self, ctx, *input):
        """
        Bot say what u what whenever u want. Need administrator rights.
        
        """
        #TODO: send pm or msg to channel via arguments
        await ctx.message.channel.send(" ".join(input))

    @guild_only()
    @command(name="f", aliases=["ф"], 
    brief='Отдать честь за почивших героев', description='Отдать честь за почивших героев. Можно упоминанием указать кого чтим.')
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_guild_cooldown)
    async def pressf(self, ctx, *input):
        """
        press f for fallen heroes.
        sends simple picture of saluting girl. can mention people
        """
        if len(ctx.message.mentions) > 0:
            title = f"**{ctx.author.display_name}** заплатил увожение за {ctx.message.mentions[0].display_name}"
        else:
            title=f"**{ctx.author.display_name}** заплатил увожение. o7"
        emb = nextcord.Embed(title=title, color=self.embed_color)
        emb.set_image(url="https://pbs.twimg.com/media/D-5sUKNXYAA5K9l.jpg")
        await ctx.message.channel.send(embed=emb)
        
    @guild_only()
    @command(name="o7", aliases=["07","о7"], 
    brief='Поприветсвовать командиров', description='Поприветсвовать командиров, а можно и кого-то конкретного')
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_guild_cooldown)
    async def o7(self, ctx, *input):
        """
        greet fellow commanders
        can mention whom to greet
        """
        if len(ctx.message.mentions) > 0:
            title = f"**{ctx.author.display_name}** приветствует {ctx.message.mentions[0].display_name}. o7"
        else:
            title=f"**{ctx.author.display_name}** приветствует вас командиры. o7"
        emb = nextcord.Embed(title=title, color=self.embed_color)
        emb.set_image(url=choice(fimages))
        await ctx.message.channel.send(embed=emb)  
              

    @command(name="avatar", aliases=["аватар"], 
    brief='Показывает аватар пользователя', 
    description='Показывает твой аватар. С помощью упоминания можно посмотреть аватар другого пользователя')
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_guild_cooldown)
    async def avatar(self, ctx, *input):
        if len(input) > 0:
            title = f"Аватар {ctx.message.mentions[0].display_name}"
            url = ctx.message.mentions[0].avatar_url
        else:
            title = f"Аватар {ctx.message.author.display_name}"
            url = ctx.message.author.avatar_url
        emb = nextcord.Embed(title=title, color=self.embed_color)
        emb.set_image(url=url)
        await ctx.message.channel.send(embed=emb)


    @guild_only()
    @command(name="info", aliases=["инфо"],
    brief='Информация и статистика бота', description='Информация и статистика бота')
    async def info(self, ctx):
        """
        This command shows bot info
        """
        embed = nextcord.Embed(color=self.embed_color, title=self.name,
                              url=f"https://www.youtube.com/watch?v=X5ULmETDiXI")
        embed.add_field(name="Описание", value="Тупая деффка еще и бот", inline=False)
        embed.add_field(name="Версия", value=bot.VERSION, inline=False)
        ark_stat = self.get_ark_stats()
        ger_stat = self.get_ger_stats()
        embed.add_field(name="Статистика арков", value=f"Арков выкручено за все время: {ark_stat.total}\nВсего собрано персонажей: {ark_stat.total_chars}", inline=False)
        embed.add_field(name="Больше всего 6* собрано", value=f"<@{ark_stat.best_dolboeb}> с количеством аж {ark_stat.dolboeb_count} шестизведочных персонажей. Поздравляем Вас и вручаем вам самый ценный подарок: **наше увожение**", inline=False)
        embed.add_field(name="Статистика пуков", value=f"""Пуков за все время: {ger_stat.total}
        Из них самообсеров: {ger_stat.total_self}
        Попаданий по ботам: {ger_stat.total_bot}
        Попаданий по мне:disappointed_relieved: : {ger_stat.total_me}""", inline=False)
        embed.set_thumbnail(
            url="https://aceship.github.io/AN-EN-Tags/img/factions/logo_rhodes.png")
        embed.set_image(url="https://aceship.github.io/AN-EN-Tags/img/characters/char_002_amiya_epoque%234.png")
        embed.set_footer(text=f"Requested by {ctx.message.author.display_name}")
        await ctx.send(embed=embed, delete_after=120)
    
    
    # functions----------------------------------------------------------------------------------------------------------------------------
    
    def __exec_stmts(self, stmts:list):
        results = []
        for stmt in stmts:
            result = self.__db.extract(stmt)
            result = int(result[0][0]) if result else 0
            results.append(result)
        return results

    def get_ark_stats(self):
        ark_stat = namedtuple('ark_stat', ['total', 'total_chars', 'best_dolboeb', 'dolboeb_count'])
        return ark_stat._make(self.__exec_stmts([
            "select value from statistic where parameter_name='ark'",
            "select count(*) from users_ark_collection",
            "select user_id from users_ark_collection where rarity=6 group by user_id order by sum(operator_count) desc limit 1",
            "select sum(operator_count) from users_ark_collection where rarity=6 group by user_id order by sum(operator_count) desc limit 1"
        ]))

    def get_ger_stats(self):
        ger_stat = namedtuple('ger_stat', ['total', 'total_self', 'total_bot', 'total_me'])
        return ger_stat._make(self.__exec_stmts([
            "select value from statistic where parameter_name='ger'",
            "select value from statistic where parameter_name='self_ger'",
            "select value from statistic where parameter_name='ger_bot'",
            "select value from statistic where parameter_name='ger_me'",
        ]))


    @property
    async def server_delete_quantity(self):
        """
        Default message delete quantity getter 

        Returns:
            int: quantity
        """
        return self.__delete_quantity


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Default(bot))
