# pylint: disable=missing-module-docstring,missing-class-docstring
from discord.ext.commands import CheckFailure


class NotReady(CheckFailure): ...


class NotServerOwner(CheckFailure): ...


class NotServerAdmin(CheckFailure): ...
