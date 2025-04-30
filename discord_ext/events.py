# pylint: disable=missing-module-docstring,missing-function-docstring,unused-argument
import traceback, logging
import discord
from discord.ext import commands
from .exceptions import NotServerOwner, NotServerAdmin, NotReady
from .shared import handler

logger = logging.getLogger(__name__)
logger.addHandler(handler)


def register_events(bot, env):
    @bot.event
    async def on_ready():
        logger.debug("Almost ready")
        await bot.tree.sync()
        bot.home = bot.get_guild(int(env["DISCORD_HOME_GUILD"]))
        bot.error_channel = bot.home.get_channel(int(env["DISCORD_ERROR_CHANNEL"]))
        bot.log_channel = bot.home.get_channel(int(env["DISCORD_LOGS_CHANNEL"]))
        logger.info("Ready")
        bot.init = True

    @bot.event
    async def on_command_error(ctx: commands.Context, error: commands.CommandError):
        embed = discord.Embed(title="Error")
        full_error = error
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f'No such command: {error.args[0].split("\"")[1]}')
            return
        if isinstance(error, commands.errors.NotOwner):
            await ctx.send("Only bot owners can run this command.", ephemeral=True)
            return
        if isinstance(error, NotServerOwner):
            await ctx.send("Only server owners can run this command.", ephemeral=True)
            return
        if isinstance(error, NotServerAdmin):
            await ctx.send("Only server admins can run this command.", ephemeral=True)
            return
        if isinstance(error, NotReady):
            await ctx.send(
                "Woah there buddy! I'm not quite ready to run commands, gimme a little bit to finish loading.",
                ephemeral=True,
            )
            return
        error_data = ("".join(traceback.format_exception(error))).strip()
        embed.description = f"```py\n{error_data}\n```"
        logger.error("An error occured while calling a command:\n", exc_info=full_error)
        await bot.error_channel.send(
            f"{ctx.author.mention} ({ctx.author.id}) broke something :/\nGuild: {ctx.guild.name} ({ctx.guild.id})\nChannel: {ctx.channel.name} ({ctx.channel.id})\nCommand: {ctx.command}",
            embed=embed,
        )
        await ctx.send(
            "I had an error trying to run that command, sorry.\nIt's been logged and should be investigated soon."
        )

    @bot.event
    async def on_member_join(member):
        sys_channel = member.guild.system_channel
        if sys_channel:
            await sys_channel.send(f"Woah {member.mention} has joined :eyes:")

    @bot.event
    async def on_member_remove(member):
        sys_channel = member.guild.system_channel
        if sys_channel:
            await sys_channel.send(f"Woah {member.mention} has left :eyes:")

    @bot.event
    async def on_guild_join(guild):
        await bot.log_channel.send("Woah I added to somewhere :eyes:")

    @bot.event
    async def on_guild_remove(guild):
        await bot.log_channel.send("Woah I got removed from somewhere :eyes:")
