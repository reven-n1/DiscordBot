from discord.ext.commands import command, has_permissions, cooldown
from discord.ext.commands.cooldowns import BucketType
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

    @command(name="say", aliases=["скажи"], brief='This is the brief description', description='This is the full description')
    @has_permissions(administrator=True)
    async def say(self, ctx, *input):
        """
        Bot say what u what whenever u want. Need administrator rights.
        
        """
        #TODO: send pm or msg to channel via arguments
        await ctx.message.channel.send(" ".join(input))
        await ctx.message.delete()

    @command(name="f", aliases=["ф"], brief='This is the brief description', description='This is the full description')
    @cooldown(1, misc_cooldown, BucketType.user)
    async def pressf(self, ctx, *input):
        """
        press f for fallen heroes.
        sends simple picture of saluting girl. can mention people
        """
        if len(ctx.message.mentions) > 0:
            title = f"**{ctx.author.name}** заплатил увожение за {ctx.message.mentions[0].name}"
        else:
            title=f"**{ctx.author.name}** заплатил увожение. o7"
        emb = discord.Embed(title=title, color=self.embed_color)
        emb.set_image(url="https://pbs.twimg.com/media/D-5sUKNXYAA5K9l.jpg")
        await ctx.message.channel.send(embed=emb)
        
    @command(name="o7", aliases=["07","о7"], brief='This is the brief description', description='This is the full description')
    @cooldown(1, misc_cooldown, BucketType.user)
    async def o7(self, ctx, *input):
        """
        greet fellow commanders
        can mention whom to greet
        """
        fimages = [
            'https://cdn.discordapp.com/attachments/565648501048868949/695677855543066726/HufFEF.jpg',
            'https://avvesione.files.wordpress.com/2015/03/kantai_collection-12-fubuki-destroyer-salute-happy-smile-tears-sunset.jpg',
            'https://i.imgur.com/6OYJZKM.jpg',
            'https://i.pinimg.com/originals/60/f1/58/60f15833dc0891efd84a372124a04dea.png',
            'https://i.imgur.com/DXxQZsM.jpg',
            'https://i.pinimg.com/originals/56/46/be/5646be93a32ecea44d297a9513525a5e.png',
            'https://i.imgur.com/gGxWXpD.jpg',
            'https://animesolution.com/wp-content/uploads/2018/04/Violet-Evergarden-BD-01_04.00_2018.04.18_21.47.07.jpg',
            'https://avatars.mds.yandex.net/get-zen_doc/1537151/pub_5cebb83799144700b4c124ea_5cffb561aac1d000ab159282/scale_1200',
            'https://i.pinimg.com/originals/ac/b0/01/acb0014b1d0cff881956561eb9a703fd.jpg',
            'https://i0.hdslb.com/bfs/article/cc5872d4d51cf157a6b174d28a23953f4ae138e4.jpg',
            'http://i.imgur.com/NTfinyb.jpg',
            'http://i.imgur.com/qZ94OXg.jpg',
            'http://i.imgur.com/pcQIbNc.jpg',
            'http://i.imgur.com/zQxhi1X.jpg',
            'http://i.imgur.com/1d1CpO4.png',
            'http://i.imgur.com/0eaHxIb.jpg',
            'http://i.imgur.com/mRk1Bjy.jpg',
            'http://i.imgur.com/JCWfaM1.jpg',
            'http://i.imgur.com/JjaUkBP.jpg',
            'http://i.imgur.com/d3glxcB.jpg',
            'http://i.imgur.com/Byxj9wF.jpg',
            'http://i.imgur.com/oH2ps4l.jpg',
            'http://i.imgur.com/jtTDX8k.jpg',
            'http://i.imgur.com/VTVjDqL.jpg',
            'http://i.imgur.com/fqlXV4K.jpg',
            'http://i.imgur.com/vUrgqO8.jpg',
            'http://i.imgur.com/SbZRqBe.jpg',
            'http://i.imgur.com/Rhqbpe7.jpg',
            'http://i.imgur.com/Kq4S6RJ.jpg',
            'http://i.imgur.com/nmCUji8.jpg',
            'http://i.imgur.com/EVxrk0O.jpg',
            'http://i.imgur.com/k4QeHji.jpg',
            'http://i.imgur.com/wzmrSvG.jpg',
            'http://i.imgur.com/fFvkdIH.jpg',
            'http://i.imgur.com/pJFiYyB.jpg',
            'https://i.imgur.com/mNazpKN.jpg',
            'https://i.imgur.com/ksy3jnB.jpg',
            'https://i.imgur.com/H7Me1KN.jpg',
            'https://i.imgur.com/feJ5nsr.png',
            'https://i.imgur.com/LVYaJ9K.jpg',
            'https://i.imgur.com/23HhlIV.png',
            'https://i.imgur.com/Ei0iU1P.jpg',
            'https://i.imgur.com/Iz07AOZ.jpg',
            'https://i.imgur.com/pkxf5X0.jpg',
            'https://i.imgur.com/AQdjwMS.jpg',
            'https://i.imgur.com/DOqXc6x.jpg',
            'https://i.imgur.com/WZBeF7H.jpg',
            'https://i.imgur.com/wxniyid.jpg',
            'https://i.imgur.com/IpXcPjK.jpg',
            'https://i.imgur.com/CuvY8iU.jpg',
            'https://i.imgur.com/1x76Rdj.png',
            'https://i.imgur.com/0hO5uoZ.jpg',
            'https://i.imgur.com/UydLcBK.jpg',
            'https://funart.pro/uploads/posts/2019-12/1577048906_devushki-i-tanki-girls-panzer-movie-anime-1.png',
            'https://i.ytimg.com/vi/9ARHU3TNPlc/maxresdefault.jpg',
            'https://i.imgur.com/vk3rCEL.png',
            'https://i.imgur.com/4vBvYiH.jpg',
            'https://i.imgur.com/FBNIyLY.png',
            'https://i.imgur.com/nWW9hp9.jpg',
            'https://i.imgur.com/yjncZIs.jpg',
            'https://i.imgur.com/0QX2cj8.png',
            'https://i.imgur.com/UlV56vr.jpg',
            'https://i.imgur.com/rHqhc1p.jpg',
            'https://i.imgur.com/PrWdBTB.jpg',
            'https://i.imgur.com/XoPOqW2.jpg',
            'https://i.imgur.com/uFcFQFj.jpg',
            'https://i.imgur.com/UkXzLjM.jpg',
            'https://i.imgur.com/0sKarWt.png',
            'https://i.imgur.com/lumFs58.png',
            'https://i.imgur.com/KvX8GKF.png',
            'https://pm1.narvii.com/6869/05a87302bae47119e5149830d85b745bddfe8031r1-504-724v2_uhq.jpg',
        ]
        if len(ctx.message.mentions) > 0:
            title = f"**{ctx.author.name}** приветствует {ctx.message.mentions[0].name}. o7"
        else:
            title=f"**{ctx.author.name}** приветствует вас командиры. o7"
        emb = discord.Embed(title=title, color=self.embed_color)
        emb.set_image(url=choice(fimages))
        await ctx.message.channel.send(embed=emb)        

    @command(name="info", aliases=["инфо"])
    async def info(self, ctx):
        """
        This command shows bot info
        """
        await ctx.message.delete()
        embed = discord.Embed(color=self.embed_color, title=Amia.name,
                              url=f"https://www.youtube.com/watch?v=X5ULmETDiXI")
        embed.add_field(name="Description", value=Amia.bot_info["info"], inline=False)
        embed.add_field(name="Commands",
                        value=str("\n".join(Amia.get_info())),
                        inline=True)
        embed.set_thumbnail(
            url="https://aceship.github.io/AN-EN-Tags/img/characters/char_222_bpipe_race%231.png")
        embed.set_image(url="https://aceship.github.io/AN-EN-Tags/img/characters/char_002_amiya_epoque%234.png")
        embed.set_footer(text=f"Requested by {ctx.message.author.name}")
        await ctx.send(embed=embed, delete_after=30)


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Commands(bot))
