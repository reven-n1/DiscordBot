from discord.ext.commands import command, cooldown, group
from discord.ext.commands.core import is_nsfw
from pkg_resources import require
from library import user_channel_cooldown
from json.decoder import JSONDecodeError
from discord.ext.commands import Cog
from requests.exceptions import HTTPError, ConnectionError, Timeout
from discord import ApplicationContext, AutocompleteContext, Embed, Member, Option, slash_command
from random import choice
from library import data
import requests
import logging


def user_channel_type_cooldown(msg: ApplicationContext):
    channel_id = msg.channel.id
    user_id = msg.author.id
    type = msg.selected_options[0]['value'] if msg.selected_options else ''
    return hash(str(channel_id)+str(user_id)+str(type))


class Reactions(Cog):
    qualified_name = 'Reactions'
    description = 'Аниме реакшоны'

    def __init__(self, bot):
        self.bot = bot
        self.embed_color = data.get_embed_color

    def get_reaction_embed(self, category: str, phrase: str, nsfw=False):
        try:
            response = requests.get(f'https://api.waifu.pics/{"sfw" if not nsfw else "nsfw"}/{category}', timeout=10)
            img_url = response.json().get('url', None)
        except (JSONDecodeError, HTTPError, ConnectionError, Timeout) as e:
            logging.error(e)
            img_url = None
        if not img_url:
            embed = Embed(title='Неудалось подключиться к бд картинками(', color=self.embed_color,
                          description='Наша команда пыталась найти пикчу, но потерпела неудачу((')
            embed.set_image(url='https://c.tenor.com/tZ2Xd8LqAnMAAAAd/typing-fast.gif')
            return embed
        embed = Embed(title=phrase, color=self.embed_color)
        embed.set_image(url=img_url)
        return embed

    def sfw_autocomplete(self, ctx: AutocompleteContext):
        types = [
                    'waifu',
                    'neko',
                    'awoo',
                    'bully',
                    'cuddle',
                    'cry',
                    'hug',
                    'kiss',
                    'lick',
                    'pat',
                    'smug',
                    'bonk',
                    'yeet',
                    'blush',
                    'smile',
                    'wave',
                    'highfive',
                    'handhold',
                    'nom',
                    'bite',
                    'slap',
                    'kill',
                    'kick',
                    'happy',
                    'wink',
                    'poke',
                    'dance',
                    'cringe'
        ]
        return [type for type in types if type.lower().startswith(ctx.value.lower())]

    @slash_command(name='sfw', description='Аниме пикчи)')
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_type_cooldown)
    async def sfw_slash(self, ctx: ApplicationContext,
                  type: Option(str, description='Выбери что хочешь посмотреть', autocomplete=sfw_autocomplete),
                  member: Option(Member, required=False)):
        pharases_list = {
            'waifu': '',
            'neko': '',
            'awoo': '',
            'bully': f'{ctx.author.display_name} доебался до {member.display_name}' if member else f'{ctx.author.display_name} так и не понял до кого хотел доебаться и доебался до самого себя',
            'cuddle': f'{ctx.author.display_name} прижимает к себе {member.display_name}' if member else f'{ctx.author.display_name} хотел обнять кого-то, а обнял аниме девку',
            'cry': f'{member.display_name} довел до слез {ctx.author.display_name}' if member else f'Вы довели до слез {ctx.author.display_name}, зачем вы так?',
            'hug': f'{ctx.author.display_name} обнимает {member.display_name}' if member else f'{ctx.author.display_name} обнимает сам себя',
            'kiss':  f'{ctx.author.display_name} целует {member.display_name}' if member else f'{ctx.author.display_name} засосал аниме девочку',
            'lick': f'{ctx.author.display_name} облизал {member.display_name}' if member else f'{ctx.author.display_name} облизал аниме девочку',
            'pat': f'{ctx.author.display_name} погладил по головке {member.display_name}' if member else f'{ctx.author.display_name} погладил по головке аниме девочку',
            'smug': f'{ctx.author.display_name} показывает свое превосходство над {member.display_name}' if member else f'{ctx.author.display_name} показывает свое превосходство',
            'bonk':    f'{ctx.author.display_name} бьет {member.display_name}' if member else f'{ctx.author.display_name} бьет кого-то и промахивается',
            'yeet': f'{ctx.author.display_name} уебал {member.display_name}' if member else f'{ctx.author.display_name} разъебал всех',
            'blush': f'{ctx.author.display_name} покраснел от {member.display_name}' if member else f'{ctx.author.display_name} смущается',
            'smile': f'{ctx.author.display_name} улыбается {member.display_name}' if member else f'{ctx.author.display_name} улыбается',
            'wave': f'{ctx.author.display_name} помахал {member.display_name}' if member else f'{ctx.author.display_name} машет',
            'highfive': f'{ctx.author.display_name} дает пятюню {member.display_name}' if member else f'{ctx.author.display_name}, ты знаешь что это парная эмоция, да?',
            'handhold': f'{ctx.author.display_name} взял за руку {member.display_name}' if member else f'{ctx.author.display_name} взял за руку своего воображаемого трапика',
            'nom':  f'{ctx.author.display_name} кушает вместе с {member.display_name}' if member else f'{ctx.author.display_name} жрет',
            'bite':  f'{ctx.author.display_name} кусает {member.display_name}' if member else f'{ctx.author.display_name} делает кусь',
            'slap': f'{ctx.author.display_name} отвесил смачного леща {member.display_name}' if member else f'{ctx.author.display_name} дал аплеуху сам себе, лол',
            'kill':  f'{ctx.author.display_name} совершает уголовно-наказуемое деяние в отношении {member.display_name}' if member else f'{ctx.author.display_name} совершает Роскомнадзор',
            'kick': f'{ctx.author.display_name} уебал с ноги {member.display_name}' if member else f'{ctx.author.display_name} жостка крутанул вертушку',
            'happy': f'{ctx.author.display_name} счаслив вместе с {member.display_name}' if member else f'{ctx.author.display_name} радуется',
            'wink': f'{ctx.author.display_name} подмигнул {member.display_name}' if member else f'{ctx.author.display_name} моргнул одним глазом',
            'poke': f'{ctx.author.display_name} ткул {member.display_name}' if member else f'{ctx.author.display_name} пытаеться куда ткнуть но не может попасть',
            'dance': f'{ctx.author.display_name} флексит с {member.display_name}' if member else f'{ctx.author.display_name} отжигает на танцполе',
            'cringe': f'{ctx.author.display_name} кринжует от {member.display_name}' if member else f'{ctx.author.display_name} на кринже ваще'
        }
        if type in pharases_list:
            await ctx.response.send_message(embed=self.get_reaction_embed(type, pharases_list[type], nsfw=False))
        else:
            await ctx.response.send_message('Я таких картинок не знаю!', ephemeral=True)

    @slash_command(name='nsfw', description='Аниме пикчи)')
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_type_cooldown)
    @is_nsfw()
    async def nsfw_slash(self, ctx: ApplicationContext,
                         type: Option(str, description='Выбери что хочешь посмотреть', choices=['waifu', 'neko', 'trap', 'blowjob'], required=False)):
        if type is None:
            type = choice(['waifu', 'neko', 'trap', 'blowjob'])
        footers = {
            'waifu': f"{ctx.author.display_name} смотрит хентай!",
            'neko': f"{ctx.author.display_name} любитель фурри, ясно понятно",
            'trap': f"Фу бля, {ctx.author.display_name} любитель трапов походу",
            'blowjob': f"{ctx.author.display_name} любит сосать, курильщик походу"
        }
        embed = self.get_reaction_embed(type, '', nsfw=True)
        embed.set_footer(
            text=footers[type], icon_url=ctx.author.avatar.url if ctx.author.avatar else '')
        await ctx.response.send_message(embed=embed)

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="waifu",
             brief='Вайфу', description='Показать твоих любимих вайфу')
    async def waifu(self, ctx):
        await ctx.send(embed=self.get_reaction_embed('waifu', ''))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="neko",
             brief='Кошкодевочки', description='Показать твоих любимих кошкодевочек')
    async def neko(self, ctx):
        await ctx.send(embed=self.get_reaction_embed('neko', ''))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="awoo",
             brief='Волкодевочки', description='Показать твоих любимих волкодевочек')
    async def awoo(self, ctx):
        await ctx.send(embed=self.get_reaction_embed('awoo', ''))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="bully",
             brief='Доебаться', description='Доебаться до кого-то')
    async def bully(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} доебался до {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} так и не понял до кого хотел доебаться и доебался до самого себя'
        await ctx.send(embed=self.get_reaction_embed('bully', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="cuddle",
             brief='Обнимашки прижимашки', description='Сильные мужские объятья')
    async def cuddle(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} прижимает к себе {ctx.message.mentions[0].display_name} крепко крепко'
        else:
            phrase = f'{ctx.author.display_name} хотел обнять кого-то, а обнял аниме девку'
        await ctx.send(embed=self.get_reaction_embed('cuddle', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="cry",
             brief='Хнык хнык', description='Команда когда ты очень сильно расстроен')
    async def cry(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.message.mentions[0].display_name} довел до слез {ctx.author.display_name}'
        else:
            phrase = f'Вы довели до слез {ctx.author.display_name}, зачем вы так?'
        await ctx.send(embed=self.get_reaction_embed('cry', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="hug",
             brief='Обнимашки', description='Обними себя или друга')
    async def hug(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} обнимает {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} обнимает сам себя'
        await ctx.send(embed=self.get_reaction_embed('hug', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="kiss",
             brief='Поцелуй', description='Kissu Kissu')
    async def kiss(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} целует {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} засосал аниме девочку'
        await ctx.send(embed=self.get_reaction_embed('kiss', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="lick",
             brief='Лизь лизь', description='Облизать кого-то')
    async def lick(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} облизал {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} облизал аниме девочку'
        await ctx.send(embed=self.get_reaction_embed('lick', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="pat",
             brief='Погладить по головке', description='Погладить по головке. Не той головке, изваращенец! Бака!')
    async def pat(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} погладил по головке {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} погладил по головке аниме девочку'
        await ctx.send(embed=self.get_reaction_embed('pat', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="smug",
             brief='Самодовольное личико', description='S M U G')
    async def smug(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} показывает свое превосходство над {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} показывает свое превосходство'
        await ctx.send(embed=self.get_reaction_embed('smug', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="bonk",
             brief='Удар', description='Удар пяткой в нос')
    async def bonk(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} бьет {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} бьет кого-то и промахивается'
        await ctx.send(embed=self.get_reaction_embed('bonk', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="yeet",
             brief='Уебать', description='Как бомжи за окном, только аниме')
    async def yeet(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} уебал {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} разъебал всех'
        await ctx.send(embed=self.get_reaction_embed('yeet', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="blush",
             brief='Смущение^-^', description='Смущение^-^. Показывает насколько ты няша стесняша')
    async def blush(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} покраснел от {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} смущается'
        await ctx.send(embed=self.get_reaction_embed('blush', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="smile",
             brief='Улыбнись', description='Улыбнись')
    async def smile(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} улыбается {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} улыбается'
        await ctx.send(embed=self.get_reaction_embed('smile', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="wave",
             brief='Помахать', description='Помахать')
    async def wave(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} помахал {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} машет'
        await ctx.send(embed=self.get_reaction_embed('wave', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="highfive",
             brief='Дай пять', description='Дай пять')
    async def highfive(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} дает пятюню {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name}, ты знаешь что это парная эмоция, да?'
        await ctx.send(embed=self.get_reaction_embed('highfive', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="handhold",
             brief='Держимся за ручку', description='Держимся за ручку, ня!')
    async def handhold(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} взял за руку {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} взял за руку своего воображаемого трапика'
        await ctx.send(embed=self.get_reaction_embed('handhold', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="nom",
             brief='Омнононононом', description='Заварил дошик и радуется')
    async def nom(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} кушает вместе с {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} жрет'
        await ctx.send(embed=self.get_reaction_embed('nom', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="bite",
             brief='Кусь', description='Вцепиться зубами')
    async def bite(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} кусает {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} делает кусь'
        await ctx.send(embed=self.get_reaction_embed('bite', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="slap",
             brief='Пощечина', description='Пощечина')
    async def slap(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} отвесил смачного леща {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} дал аплеуху сам себе, лол'
        await ctx.send(embed=self.get_reaction_embed('slap', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="kill",
             brief='Убийство карается статьей 105 УКРФ',
             description="""Убийство, то есть умышленное причинение смерти другому человеку, -
    наказывается лишением свободы на срок от шести до пятнадцати лет с ограничением свободы на срок до двух лет либо без такового.
    2. Убийство:
        а) двух или более лиц;
        б) лица или его близких в связи с осуществлением данным лицом служебной деятельности или выполнением общественного долга;
        в) малолетнего или иного лица, заведомо для виновного находящегося в беспомощном состоянии, а равно сопряженное с похищением человека;
        г) женщины, заведомо для виновного находящейся в состоянии беременности;
        д) совершенное с особой жестокостью;
        е) совершенное общеопасным способом;
        е.1) по мотиву кровной мести;
        ж) совершенное группой лиц, группой лиц по предварительному сговору или организованной группой;
        з) из корыстных побуждений или по найму, а равно сопряженное с разбоем, вымогательством или бандитизмом;
        и) из хулиганских побуждений;
        к) с целью скрыть другое преступление или облегчить его совершение, а равно сопряженное с изнасилованием или насильственными действиями сексуального характера;
        л) по мотивам политической, идеологической, расовой, национальной или религиозной ненависти или вражды либо по мотивам ненависти или вражды в отношении какой-либо социальной группы;
        м) в целях использования органов или тканей потерпевшего, -
        н) утратил силу. - Федеральный закон от 08.12.2003 N 162-ФЗ
        наказывается лишением свободы на срок от восьми до двадцати лет с ограничением свободы на срок от одного года до двух лет, либо пожизненным лишением свободы, либо смертной казнью.
    """)
    async def kill(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} совершает уголовно-наказуемое деяние в отношении {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} совершает Роскомнадзор'
        await ctx.send(embed=self.get_reaction_embed('kill', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="kick",
             brief='Удар с ноги', description='Удар с ноги, чисто вертушка')
    async def kick(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} уебал с ноги {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} жостка крутанул вертушку'
        await ctx.send(embed=self.get_reaction_embed('kick', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="happy",
             brief='Счастье', description='Счастье, как будто оно есть')
    async def happy(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} счаслив вместе с {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} радуется'
        await ctx.send(embed=self.get_reaction_embed('happy', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="wink",
             brief='Подмигнуть', description='Подмигнуть')
    async def wink(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} подмигнул {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} моргнул одним глазом'
        await ctx.send(embed=self.get_reaction_embed('wink', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="poke",
             brief='Тыкнуть', description='Тык тык тык тык')
    async def poke(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} ткул {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} пытаеться куда ткнуть но не может попасть'
        await ctx.send(embed=self.get_reaction_embed('poke', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="dance",
             brief='Танцы', description='Танцы-шманцы')
    async def dance(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} флексит с {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} отжигает на танцполе'
        await ctx.send(embed=self.get_reaction_embed('dance', phrase))

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(name="cringe",
             brief='Крынж, уууу', description='Кринж, как будто в тик ток зашел')
    async def cringe(self, ctx):
        if ctx.message.mentions:
            phrase = f'{ctx.author.display_name} кринжует от {ctx.message.mentions[0].display_name}'
        else:
            phrase = f'{ctx.author.display_name} на кринже ваще'
        await ctx.send(embed=self.get_reaction_embed('cringe', phrase))

    # NSFW section
    @is_nsfw()
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @group(name='nsfw',
           brief='Кидает рандомную хентай картину, осторожно! Все персонажи достигли 18 лет.',
           description='Кидает рандомную хентай картину, осторожно! Все персонажи достигли 18 лет.', pass_context=True)
    async def nsfw(self, ctx):
        if ctx.invoked_subcommand is None:
            await choice(list(self.nsfw.commands)).callback(self, ctx)

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @nsfw.command(name='waifu',
                  brief='Кидает обычную хентай картину',
                  description='Кидает обычную хентай картину',
                  pass_context=True)
    async def nsfw_waifu(self, ctx):
        embed = self.get_reaction_embed('waifu', '', nsfw=True)
        embed.set_footer(
            text=f"{ctx.author.display_name} смотрит хентай!", icon_url=ctx.author.avatar.url if ctx.author.avatar else '')
        await ctx.send(embed=embed)

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @nsfw.command(name='neko',
                  brief='Кидает хентайную кошкодевочку',
                  description='Кидает хентай картину, мяу!',
                  pass_context=True)
    async def nsfw_neko(self, ctx):
        embed = self.get_reaction_embed('neko', '', nsfw=True)
        embed.set_footer(
            text=f"{ctx.author.display_name} любитель фурри, ясно понятно", icon_url=ctx.author.avatar.url if ctx.author.avatar else '')
        await ctx.send(embed=embed)

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @nsfw.command(name='trap',
                  brief='Кидает ловушку, caution!',
                  description='Чел, это мальчик, бля. Сука у неё хуй! Пиздец бле...',
                  pass_context=True)
    async def nsfw_trap(self, ctx):
        embed = self.get_reaction_embed('trap', '', nsfw=True)
        embed.set_footer(
            text=f"Фу бля, {ctx.author.display_name} любитель трапов походу", icon_url=ctx.author.avatar.url if ctx.author.avatar else '')
        await ctx.send(embed=embed)

    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @nsfw.command(name='blowjob',
                  brief='Пососи сученька',
                  description='Еще чуть чуть и здесь будут другие категории порно',
                  pass_context=True)
    async def nsfw_blowjob(self, ctx):
        embed = self.get_reaction_embed('blowjob', '', nsfw=True)
        embed.set_footer(
            text=f"{ctx.author.display_name} любит сосать, курильщик походу", icon_url=ctx.author.avatar.url if ctx.author.avatar else '')
        await ctx.send(embed=embed)


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Reactions(bot))
