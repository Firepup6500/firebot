# pylint: disable=missing-module-docstring,missing-function-docstring
from discord.ext.commands import Context, check
from .exceptions import NotReady, NotServerOwner, NotServerAdmin


def isReady():
    def predicate(ctx: Context):
        if ctx.bot.init:
            return True
        raise NotReady

    return check(predicate)


def isServerOwner():
    def predicate(ctx: Context):
        if ctx.author.id in ctx.bot.owner_ids or ctx.author == ctx.guild.owner:
            return True
        raise NotServerOwner

    return check(predicate)


def isServerAdmin():
    def predicate(ctx: Context):
        if (
            ctx.author.id in ctx.bot.owner_ids
            or ctx.author == ctx.guild.owner
            or any(
                role.permissions.administrator
                for _, role in enumerate(ctx.author.roles)
            )
        ):
            return True
        raise NotServerAdmin

    return check(predicate)
