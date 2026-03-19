#!/usr/bin/python3
# pylint: disable=missing-module-docstring,missing-function-docstring
from typing import Optional
import bare
import config as conf


def admin(
    bot: bare.Bot,
    name: str,
    host: Optional[str] = "",
    chan: Optional[str] = "",
    cmd: Optional[str] = "",
) -> bool:
    # pylint: disable=too-many-return-statements
    if bot.server in conf.noAdmins:
        if not chan:
            return False
        bot.msg(
            f"Sorry {name}, {cmd} is an admin only command, and this network has had admin perms explicitly disabled.",
            chan,
        )
        return False
    if (
        name.lower() in bot.adminnames
        or (host or bot.tmpHost) in conf.admin_hosts
        or (host or bot.tmpHost) in conf.servers[bot.server]["hosts"]
    ):
        if bot.current != "bridge":
            return True
        if not chan:
            return False
        bot.msg(f"Sorry {name}, bridged users can't use admin commands.", chan)
        return False
    if not chan:
        return False
    bot.msg(f"Sorry {name}, {cmd} is an admin only command.", chan)
    return False
