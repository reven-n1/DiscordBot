from nextcord.ext.commands import command, cooldown
from nextcord.errors import Forbidden
from nextcord.ext.commands import Cog
from json import load
from library import data, user_channel_cooldown
import nextcord

from library.data.dataLoader import dataHandler

async def send_embed(ctx, embed):
    """
    Function that handles the sending of embeds
    -> Takes context and embed to send
    - tries to send embed in channel
    - tries to send normal message when that fails
    - tries to send embed private with information abot missing permissions
    If this all fails: https://youtu.be/dQw4w9WgXcQ
    """
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send("Hey, seems like I can't send embeds. Please check my permissions :)")
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? :slight_smile: ", embed=embed)


class Help(Cog):
    qualified_name = 'Помощь'
    description = 'Помощь помощь помощь'
    def __init__(self, bot):
        self.bot = bot
        self.options = dataHandler()
        self.embed_color = self.options.get_embed_color


    @cooldown(10, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(brief='Показать помощь, ня', description='Показать помощь, ня')
    async def help(self, ctx, *input):
        #TODO: уменьшить кол-во if, aka пофиксить логику, йоу
        
        emb = nextcord.Embed(title="Помощь, угу...", color=self.embed_color)
        emb.set_thumbnail(url="https://media.discordapp.net/attachments/595920342141370381/596022380628017173/O7_12.png")
        if len(input) == 0:
            for cog in self.bot.cogs.values():
                emb.add_field(name=cog.qualified_name, value=cog.description, inline=False)
            emb.set_footer(text=f"Чтобы узнать подробнее о группе команд введите: !help <группа>")

        elif len(input) == 1:
            selected_cog = None
            for cog in self.bot.cogs.values():
                if cog.qualified_name.lower() == input[0].lower():
                    selected_cog = cog
                    break
            else:
                emb = nextcord.Embed(title="Ты совсем бака?:anger: ",
                    description=f"Они-чан, только не туда! Я никогда не слышала о `{input[0]}`. Не думаю что такая группа существует."
                    "Спроси у меня справочку если забыл что я умею.",
                    color=nextcord.Color.orange())
            if selected_cog:
                for command in selected_cog.walk_commands():
                    aliases = command.aliases[:]
                    aliases.insert(0,command.name)
                    emb.add_field(name="/".join(aliases), value=f"`{command.brief}`", inline=False)
                emb.set_footer(text=f"Чтобы узнать подробнее о команде введите: !help <команда>")

        elif len(input) == 2:
            selected_cog = None
            for cog in self.bot.cogs.values():
                if cog.qualified_name.lower() == input[0].lower():
                    selected_cog = cog
                    break
            else:
                emb = nextcord.Embed(title="Ты совсем бака?:anger: ",
                    description=f"Они-чан, только не туда! Я никогда не слышала о `{input[0]}`. Не думаю что такая группа существует."
                    "Спроси у меня справочку если забыл что я умею.",
                    color=nextcord.Color.orange())
            if selected_cog:
                for command in selected_cog.walk_commands():
                    aliases = command.aliases[:]
                    aliases.insert(0,command.name)
                    if input[1].lower() in aliases:

                        emb = nextcord.Embed(title=f'{"/".join(aliases)} - помощч', description=f"`{command.description}`",
                                            color=nextcord.Color.green())#TODO color from cfg
                        break
                else:
                    emb = nextcord.Embed(title="Ты совсем бака?:anger: ",
                                        description=f"Братик, ты дурашка? Я никогда не слышала о `{input[1]}`. Не думаю что такая команда существует."
                                        "Спроси у меня справочку если забыл команды. Сестренка всегда здесь, сестренка всегда с тобой.:heartpulse: ",
                                        color=nextcord.Color.orange())

        elif len(input) > 2:
            emb = nextcord.Embed(title="Нет, семпай, не так сильно",
                                description="Слишком много аргументов, братик:sweat_drops:",
                                color=nextcord.Color.orange())

        else:
            emb = nextcord.Embed(title="Неожиданно.",
                                description="Я не знаю как ты увидел это сообщение, но ты победил.\n"
                                            "Напиши разработчикам в ЛС и на GitHub чтобы мы вместе отметили твою удачу\n"
                                            "https://github.com/reven-n1/DiscordBot",
                                color=nextcord.Color.red())

        await ctx.message.channel.send(embed=emb, delete_after=self.options.get_chat_misc_cooldown_sec)#TODO заменить на загрузку из файла
        try:
            await ctx.message.delete(delay=self.options.get_chat_misc_cooldown_sec)
        except Exception as e:
            print(e)


def setup(bot):
    bot.add_cog(Help(bot))