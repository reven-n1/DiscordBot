import logging
from discord.ext.commands import command, cooldown
from discord.errors import Forbidden
from discord.ext.commands import Cog, Command
from library import data, user_channel_cooldown
import discord
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

    @cooldown(10, data.get_chat_misc_cooldown_sec, user_channel_cooldown)
    @command(brief='Показать помощь, ня', description='Показать помощь, ня')
    async def help(self, ctx, *args):
        # TODO: уменьшить кол-во if, aka пофиксить логику, йоу

        emb = discord.Embed(title="Помощь, угу...", color=self.embed_color)
        emb.set_thumbnail(url=self.bot.user.avatar.url)
        if len(args) == 0:
            for cog in self.bot.cogs.values():
                emb.add_field(name=cog.qualified_name, value=cog.description, inline=False)
            emb.set_footer(text="Чтобы узнать подробнее о группе команд введите: !help <группа>")

        elif len(args) == 1:
            selected_cog = None
            for cog in self.bot.cogs.values():
                if cog.qualified_name.lower() == args[0].lower():
                    selected_cog = cog
                    break
            else:
                emb = discord.Embed(title="Ты совсем бака?:anger: ",
                                    description=f"Они-чан, только не туда! Я никогда не слышала о `{args[0]}`. Не думаю что такая группа существует."
                                    "Спроси у меня справочку если забыл что я умею.",
                                    color=discord.Color.orange())
            if selected_cog:
                if len(selected_cog.get_commands()) <= 25:
                    for cmd in selected_cog.walk_commands():
                        aliases = cmd.aliases[:]
                        aliases.insert(0, cmd.qualified_name)
                        emb.add_field(name="/".join(aliases), value=f"`{cmd.brief}`", inline=False)
                    emb.set_footer(text="Чтобы узнать подробнее о команде введите: !help <команда>")
                else:
                    cmd_string = ""
                    for cmd in selected_cog.walk_commands():
                        if not isinstance(cmd, Command):
                            continue
                        aliases = cmd.aliases[:]
                        aliases.insert(0, cmd.qualified_name)
                        cmd_string += f"**{'/'.join(aliases)}**\n`{cmd.brief}`\n\n"
                    emb.add_field(name="Комманды красиво не поместились, ебашим так", value=cmd_string, inline=False)
                    emb.set_footer(text="Чтобы узнать подробнее о команде введите: !help <команда>")

        elif len(args) == 2:
            selected_cog = None
            for cog in self.bot.cogs.values():
                if cog.qualified_name.lower() == args[0].lower():
                    selected_cog = cog
                    break
            else:
                emb = discord.Embed(title="Ты совсем бака?:anger: ",
                                    description=f"Они-чан, только не туда! Я никогда не слышала о `{args[0]}`. Не думаю что такая группа существует."
                                    "Спроси у меня справочку если забыл что я умею.",
                                    color=discord.Color.orange())
            if selected_cog:
                for cmd in selected_cog.walk_commands():
                    aliases = cmd.aliases[:]
                    aliases.insert(0, cmd.name)
                    if args[1].lower() in aliases:

                        emb = discord.Embed(title=f'{"/".join(aliases)} - помощч', description=f"`{cmd.description}`",
                                            color=discord.Color.green())
                        break
                else:
                    emb = discord.Embed(title="Ты совсем бака?:anger: ",
                                        description=f"Братик, ты дурашка? Я никогда не слышала о `{args[1]}`. Не думаю что такая команда существует."
                                        "Спроси у меня справочку если забыл команды. Сестренка всегда здесь, сестренка всегда с тобой.:heartpulse: ",
                                        color=discord.Color.orange())

        elif len(args) > 2:
            emb = discord.Embed(title="Нет, семпай, не так сильно",
                                description="Слишком много аргументов, братик:sweat_drops:",
                                color=discord.Color.orange())

        else:
            emb = discord.Embed(title="Неожиданно.",
                                description="Я не знаю как ты увидел это сообщение, но ты победил.\n"
                                "Напиши разработчикам в ЛС и на GitHub чтобы мы вместе отметили твою удачу\n"
                                "https://github.com/reven-n1/DiscordBot",
                                color=discord.Color.red())

        await ctx.message.channel.send(embed=emb, delete_after=self.options.get_chat_misc_cooldown_sec)
        try:
            await ctx.message.delete(delay=self.options.get_chat_misc_cooldown_sec)
        except Exception as e:
            logging.warning(e)

    @staticmethod
    def find_cog_by_name(cogs, name: str) -> Cog:
        selected_cog = None
        for cog in cogs:
            if cog.qualified_name.lower() == name:
                selected_cog = cog
                break
        return selected_cog

def setup(bot):
    bot.add_cog(Help(bot))
