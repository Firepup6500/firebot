#!/usr/bin/python3
import config as conf
import random as r
from typing import Any, Callable, Optional
import bare, re


def admin(
    bot: bare.bot,
    name: str,
    host: Optional[str] = "",
    chan: Optional[str] = "",
    cmd: Optional[str] = "",
) -> bool:
    if bot.server in conf.noAdmins:
        if not chan:
            return False
        else:
            bot.msg(
                f"Sorry {name}, {cmd} is an admin only command, and this network has had admin perms explicitly disabled.",
                chan,
            )
    elif (
        name.lower() in bot.adminnames
        or (host or bot.tmpHost) in conf.admin_hosts
        or (host or bot.tmpHost) in conf.servers[bot.server]["hosts"]
    ):
        if bot.current != "bridge":
            return True
        elif not chan:
            return False
        else:
            bot.msg(f"Sorry {name}, bridged users can't use admin commands.", chan)
            return False
    elif not chan:
        return False
    else:
        bot.msg(f"Sorry {name}, {cmd} is an admin only command.", chan)
        return False
