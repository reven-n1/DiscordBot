from discord.ext.commands import command, cooldown, group
from discord.ext.commands.core import is_nsfw
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

    @slash_command(name='sfw', description='Аниме пикчи)')
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_type_cooldown)
    async def sfw_slash(self, ctx: ApplicationContext,
                        type: Option(str, description='Выбери что хочешь посмотреть',
                        choices=['waifu', 'neko', 'awoo', 'shinobu', 'megumin'])):
        await ctx.interaction.response.defer()
        await ctx.followup.send(embed=self.get_reaction_embed(type, '', nsfw=False))

    def reaction_autocomplete(self, ctx: AutocompleteContext):
        types = [
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

    @slash_command(name='reaction', description='Аниме реакшоны')
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_type_cooldown)
    async def reaction_slash(self, ctx: ApplicationContext,
                             type: Option(str, description='Выбери эмоцию', autocomplete=reaction_autocomplete),
                             member: Option(Member, description='Выбери кого упомянуть (для парных эмоций)', required=False)):
        await ctx.interaction.response.defer()
        pharases_list = {
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
            await ctx.followup.send(embed=self.get_reaction_embed(type, pharases_list[type], nsfw=False))
        else:
            await ctx.followup.send('Я таких картинок не знаю!')

    @slash_command(name='nsfw', description='Пошлые аниме пикчи))')
    @cooldown(1, data.get_chat_misc_cooldown_sec, user_channel_type_cooldown)
    @is_nsfw()
    async def nsfw_slash(self, ctx: ApplicationContext,
                         type: Option(str, description='Выбери что хочешь посмотреть', choices=['waifu', 'neko', 'trap', 'blowjob'], required=False)):
        await ctx.interaction.response.defer()
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
        await ctx.followup.send(embed=embed)


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Reactions(bot))
