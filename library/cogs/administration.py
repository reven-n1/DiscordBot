from nextcord.ext.commands import command, has_permissions
from nextcord.errors import HTTPException, NotFound
from nextcord.ext.commands.core import guild_only
from nextcord.ext.commands import Cog
from library import Amia
import nextcord.member


class Admin(Cog):
    qualified_name = 'Admin'
    description = 'Администраторские команды, кек'
    def __init__(self, bot):
        self.bot = bot

    @command(name="ban", aliases=["бан"], brief='Забанить говножуя', 
    description='Забанить челика на серве, только для админов, ну ну а ты что думал.')
    @guild_only()
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: nextcord.Member, reason=None):
        """
        Ban command
        """
        try:
            reason = ctx.message.content.split()[2]
        except IndexError:
            pass

        await ctx.message.delete()
        await member.ban(reason=reason)
        await ctx.message.channel.send(f"{member} забанен", delete_after=15)


    @command(name="kick", aliases=["кик"],
    brief='Кикнуть лоха', description='Кикнуть челика с сервера, только для админов, ну ну а ты что думал.')
    @guild_only()
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: nextcord.Member, reason=None):
        """
        Kick command
        """
        try:
            reason = ctx.message.content.split()[2]
        except IndexError:
            pass

        await ctx.message.delete()
        await member.kick(reason=reason)
        await ctx.message.channel.send(f"{member} кикнут, нах.", delete_after=15)


    @command(name="unban", aliases=["разбан"],
    brief='Разбанить невиновного', description='Разбанить невиновного, что он тебе плохого сделал, бака?')
    @guild_only()
    @has_permissions(administrator=True)
    async def unban(self, ctx, user:nextcord.User):
        """
        Unban command
        """
        await ctx.message.delete()
        try:
            await ctx.guild.unban(user)
            await ctx.message.channel.send(f"{user} - разбанен")
        except NotFound:
            await ctx.message.channel.send("***А он и так не забанен, ти шо. Проверь имя, мб опечатался, дурашка.***", delete_after=10) 


    @command(name="ban_list", aliases=["бан_лист"],
    brief='Вывести всех забаненых лошков', description='Вывести всех забаненых лошков')
    @guild_only()
    @has_permissions(ban_members=True)
    async def ban_list(self, ctx):
        """
        Returns ban_list
        """
        await ctx.message.delete()
        banned_list = list()
        for _ in await ctx.guild.bans():
            banned_list.append(f"{_.user.name} - {_.user.id} ")
            print(f"{_.user.name} - {_.user.id} ")
        try:
            await ctx.message.channel.send(*banned_list, delete_after=60)
        except HTTPException:
            await ctx.message.channel.send("***Никто не забанен, амнистия!***", delete_after=10) 


    @command(name="give_role", aliases=["повысить"],
    brief='Выдать роль', description='Выдать роль')
    @guild_only()
    @has_permissions(administrator=True)
    async def give_role(self, ctx, member:nextcord.Member, role:nextcord.Role):
        """
        Gives role to person

        Args:
            ctx (Any): context
            member (nextcord.Member): target member
            role (nextcord.Role): chosen role
        """
        await ctx.message.delete()
        await member.add_roles(role)
    

    @command(name="remove_role", aliases=["понизить"],
    brief='Убрать роль', description='Убрать роль с человека, потому что ты его ненавидишь')
    @guild_only()
    @has_permissions(administrator=True)
    async def remove_role(self, ctx, member:nextcord.Member, role:nextcord.Role):
        """
        Remove role from person

        Args:
            ctx (Any): context
            member (nextcord.Member): target member
            role (nextcord.Role): role to remove
        """
        await ctx.message.delete()
        await member.remove_roles(role)


    @command(name="clear", aliases=["очистить"],
    brief='Удаляет N последних сообщений в этом канале', description='Удаляет N последних сообщений в этом канале.')
    @guild_only()
    async def clear(self, ctx):
        """
        Clears channel from messages(takes quantity to delete)(in default 1000)
        """
        await ctx.message.delete()
        message_text = ctx.message.content.split()
        if len(message_text) == 2 and message_text[1].isdigit():
            await ctx.message.channel.purge(limit=int(ctx.message.content.split()[1]))
        else:
            clear_limit = await Amia.server_delete_quantity
            await ctx.message.channel.purge(limit=clear_limit)


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Admin(bot))
