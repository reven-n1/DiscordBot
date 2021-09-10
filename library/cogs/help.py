import discord
from discord.errors import Forbidden
from discord.ext.commands import command
from discord.ext.commands import Cog
import discord
from json import load

"""This custom help command is a perfect replacement for the default one on any Discord Bot written in Discord.py!
However, you must put "bot.remove_command('help')" in your bot, and the command must be in a cog for it to work.
Original concept by Jared Newsom (AKA Jared M.F.)
[Deleted] https://gist.github.com/StudioMFTechnologies/ad41bfd32b2379ccffe90b0e34128b8b
Rewritten and optimized by github.com/nonchris
https://gist.github.com/nonchris/1c7060a14a9d94e7929aa2ef14c41bc2
You need to set three variables to make that cog run.
Have a look at line 51 to 57
"""


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


class Commands(Cog):
    """
    Sends this help message
    """

    def __init__(self, bot):
        self.bot = bot
        with open("bot/config/config.json","rb") as json_config_file:
            data = load(json_config_file)
            try:
                self.embed_color = int(data["default_settings"]["embed_color"],16)
            except KeyError:
                exit("'config.json' is damaged!")

    @command()
    async def help(self, ctx, *input):
        if not input:

            # starting to build embed
            emb = discord.Embed(title="Помощь, угу...", color=self.embed_color)
            emb.set_thumbnail(url="https://media.discordapp.net/attachments/595920342141370381/596022380628017173/O7_12.png")
            for command in self.bot.walk_commands():
                aliases = command.aliases
                aliases.insert(0,command.name)
                emb.add_field(name="/".join(aliases), value=f"`{command.help}`", inline=False)
            emb.set_footer(text=f"Спасибо за вашу преданость, принимаем донаты на лечение")

        elif len(input) == 1:

            for command in self.bot.walk_commands():
                aliases = command.aliases
                aliases.insert(0,command.name)
                if input[0].lower() in aliases:

                    emb = discord.Embed(title=f'{command.name} - помощч', description=f"`{command.description}`",
                                        color=discord.Color.green())#TODO color from cfg
                    break
            else:
                emb = discord.Embed(title="Ты совсем бака?:anger: ",
                                    description=f"Братик, ты дурашка? Я никогда не слышала о `{input[0]}`. Не думаю что такая команда существует."
                                    "Спроси у меня справочку если забыл команды. Сестренка всегда здесь, сестренка всегда с тобой.:heartpulse: ",
                                    color=discord.Color.orange())

        elif len(input) > 1:
            emb = discord.Embed(title="Нет, семпай, не так сильно",
                                description="Слишком много аргументов, братик:sweat_drops:",
                                color=discord.Color.orange())

        else:
            emb = discord.Embed(title="Неожиданно.",
                                description="Я не знаю как ты увидел это сообщение, но ты победил.\n"
                                            "Напиши разработчикам в ЛС и на GitHub чтобы мы вместе отметили твою удачу\n"
                                            "https://github.com/reven-n1/DiscordBot",
                                color=discord.Color.red())

        # sending reply embed using our own function defined above
        await send_embed(ctx, emb)


def setup(bot):
    bot.add_cog(Commands(bot))