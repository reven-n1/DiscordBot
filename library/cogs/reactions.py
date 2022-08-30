from discord.ext.commands import cooldown
from discord.ext.commands.core import is_nsfw
from json.decoder import JSONDecodeError
from discord import Cog
from discord import ApplicationContext, AutocompleteContext, Embed, Member, Option, slash_command
from random import choice
from library.data.data_loader import DataHandler
import logging
import aiohttp


data = DataHandler()


def user_channel_type_cooldown(msg: ApplicationContext):
    channel_id = msg.channel.id
    user_id = msg.author.id
    type = msg.selected_options[0]['value'] if msg.selected_options else ''
    return hash(str(channel_id)+str(user_id)+str(type))


class Reactions(Cog):
    qualified_name = 'Reactions'
    description = 'Аниме реакшоны'

    pharases_list = {
            'bully': ['{sender} доебался до {target}', '{sender} так и не понял до кого хотел доебаться и доебался до самого себя'],
            'cuddle': ['{sender} прижимает к себе {target}', '{sender} хотел обнять кого-то, а обнял аниме девку'],
            'cry': ['{target} довел до слез {sender}', 'Вы довели до слез {sender}, зачем вы так?'],
            'hug': ['{sender} обнимает {target}', '{sender} обнимает сам себя'],
            'kiss': ['{sender} целует {target}', '{sender} засосал аниме девочку'],
            'lick': ['{sender} облизал {target}', '{sender} облизал аниме девочку'],
            'pat': ['{sender} погладил по головке {target}', '{sender} погладил по головке аниме девочку'],
            'smug': ['{sender} показывает свое превосходство над {target}', '{sender} показывает свое превосходство'],
            'bonk': ['{sender} бьет {target}', '{sender} бьет кого-то и промахивается'],
            'yeet': ['{sender} уебал {target}', '{sender} разъебал всех'],
            'blush': ['{sender} покраснел от {target}', '{sender} смущается'],
            'smile': ['{sender} улыбается {target}', '{sender} улыбается'],
            'wave': ['{sender} помахал {target}', '{sender} машет'],
            'highfive': ['{sender} дает пятюню {target}', '{sender}, ты знаешь что это парная эмоция, да?'],
            'handhold': ['{sender} взял за руку {target}', '{sender} взял за руку своего воображаемого трапика'],
            'nom': ['{sender} кушает вместе с {target}', '{sender} жрет'],
            'bite': ['{sender} кусает {target}', '{sender} делает кусь'],
            'slap': ['{sender} отвесил смачного леща {target}', '{sender} дал аплеуху сам себе, лол'],
            'kill': ['{sender} совершает уголовно-наказуемое деяние в отношении {target}', '{sender} совершает Роскомнадзор'],
            'kick': ['{sender} уебал с ноги {target}', '{sender} жостка крутанул вертушку'],
            'happy': ['{sender} счаслив вместе с {target}', '{sender} радуется'],
            'wink': ['{sender} подмигнул {target}', '{sender} моргнул одним глазом'],
            'poke': ['{sender} ткул {target}', '{sender} пытаеться куда ткнуть но не может попасть'],
            'dance': ['{sender} флексит с {target}', '{sender} отжигает на танцполе'],
            'cringe': ['{sender} кринжует от {target}', '{sender} на кринже ваще'],
        }

    def __init__(self, bot):
        self.bot = bot
        self.embed_color = data.get_embed_color

    async def get_reaction_embed(self, category: str, phrase: str, nsfw=False):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.waifu.pics/{"sfw" if not nsfw else "nsfw"}/{category}', timeout=10) as response:
                    if response.ok and response.status == 200:
                        content = await response.json()
                    else:
                        logging.warn("Can't get image from waifu.pics")
                img_url = content.get('url', None)
        except (JSONDecodeError, aiohttp.ContentTypeError, KeyError) as e:
            logging.exception(e)
            img_url = None
        if not img_url:
            embed = Embed(title='Неудалось подключиться к бд картинками(', color=self.embed_color,
                          description='Наша команда пыталась найти пикчу, но потерпела неудачу((')
            embed.set_image(url='https://c.tenor.com/tZ2Xd8LqAnMAAAAd/typing-fast.gif')
            return embed
        embed = Embed(title=phrase, color=self.embed_color)
        embed.set_image(url=img_url)
        return embed

    @slash_command(name='sfw', description='Аниме пикчи)')
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_type_cooldown)
    async def sfw_slash(self, ctx: ApplicationContext,
                        type: Option(str, description='Выбери что хочешь посмотреть',
                                     choices=['waifu', 'neko', 'awoo', 'shinobu', 'megumin']
                                     )
                        ):
        await ctx.defer()
        await ctx.respond(embed=await self.get_reaction_embed(type, '', nsfw=False))

    def reaction_autocomplete(self, ctx: AutocompleteContext):
        return filter(lambda x: x.lower().startswith(ctx.value.lower()), self.pharases_list.keys())

    @slash_command(name='reaction', description='Аниме реакшоны')
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_type_cooldown)
    async def reaction_slash(self, ctx: ApplicationContext,
                             type: Option(str, description='Выбери эмоцию', autocomplete=reaction_autocomplete),
                             member: Option(Member, description='Выбери кого упомянуть (для парных эмоций)', required=False)):
        await ctx.defer()
        if type in self.pharases_list:
            if member:
                pharase = self.pharases_list[type][0].format(sender=ctx.author.display_name, target=member.display_name)
            else:
                pharase = self.pharases_list[type][1].format(sender=ctx.author.display_name)
            await ctx.respond(embed=await self.get_reaction_embed(type, pharase, nsfw=False))
        else:
            await ctx.respond('Я таких картинок не знаю!')

    @slash_command(name='nsfw', description='Пошлые аниме пикчи))')
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_type_cooldown)
    @is_nsfw()
    async def nsfw_slash(self, ctx: ApplicationContext,
                         type: Option(str, description='Выбери что хочешь посмотреть', choices=['waifu', 'neko', 'trap', 'blowjob'], required=False)):
        await ctx.defer()
        if type is None:
            type = choice(['waifu', 'neko', 'blowjob', 'trap'])
        footers = {
            'waifu': f"{ctx.author.display_name} смотрит хентай!",
            'neko': f"{ctx.author.display_name} любитель фурри, ясно понятно",
            'trap': f"Фу бля, {ctx.author.display_name} любитель трапов походу",
            'blowjob': f"{ctx.author.display_name} любит сосать, курильщик походу"
        }
        embed = await self.get_reaction_embed(type, '', nsfw=True)
        embed.set_footer(
            text=footers[type], icon_url=ctx.author.avatar.url if ctx.author.avatar else '')
        await ctx.followup.send(embed=embed)


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Reactions(bot))
