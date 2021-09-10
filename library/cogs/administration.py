from discord.ext.commands import command, has_permissions
from discord.errors import HTTPException, NotFound
from discord.ext.commands import Cog
from library.__init__ import Amia
import discord.member


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="ban", aliases=["бан"])
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, reason=None):
        """
        Ban command
        """
        try:
            reason = ctx.message.content.split()[2]
        except IndexError:
            pass

        await ctx.message.delete()
        await member.ban(reason=reason)
        await ctx.message.channel.send(f"{member} is banned", delete_after=15)

    @command(name="kick", aliases=["кик"])
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, reason=None):
        """
        Kick command
        """
        try:
            reason = ctx.message.content.split()[2]
        except IndexError:
            pass

        await ctx.message.delete()
        await member.kick(reason=reason)
        await ctx.message.channel.send(f"{member} is kicked", delete_after=15)


    @command(name="unban", aliases=["разбан"])
    @has_permissions(administrator=True)
    async def unban(self, ctx, user:discord.User):
        """
        Unban command
        """
        await ctx.message.delete()
        try:
            await ctx.guild.unban(user)
            await ctx.message.channel.send(f"{user} - unbanned")
        except NotFound:
            await ctx.message.channel.send("***User isn't banned or he isn't not a guild member***", delete_after=10) 


    @command(name="ban_list", aliases=["бан_лист"])
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
            await ctx.message.channel.send("***Ban list is empty***", delete_after=10) 


    @command(name="give_role", aliases=["повысить"])
    @has_permissions(administrator=True)
    async def give_role(self, ctx, member:discord.Member, role:discord.Role):
        """
        Gives role to person

        Args:
            ctx (Any): context
            member (discord.Member): target member
            role (discord.Role): chosen role
        """
        await ctx.message.delete()
        await member.add_roles(role)
    

    @command(name="remove_role", aliases=["понизить"])
    @has_permissions(administrator=True)
    async def remove_role(self, ctx, member:discord.Member, role:discord.Role):
        """
        Remove role from person

        Args:
            ctx (Any): context
            member (discord.Member): target member
            role (discord.Role): role to remove
        """
        await ctx.message.delete()
        await member.remove_roles(role)


    @command(name="clear", aliases=["очистить"])
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
    bot.add_cog(Commands(bot))
