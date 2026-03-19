#!/usr/bin/python3
# pylint: disable=missing-module-docstring,missing-function-docstring
import sys
from subprocess import Popen
from logs import log
from threads import threadManager


def launchIrc(server: str) -> Popen:
    with Popen(["python3", "-u", "ircBot.py", server]) as proc:
        proc.wait()


def launchDiscord() -> Popen:
    with Popen(["python3", "-u", "discordBot.py"]) as proc:
        proc.wait()


servers = {
    "ircnow": {"noWrap": True, "func": launchIrc, "args": ["ircnow"]},
    "libera": {"noWrap": True, "func": launchIrc, "args": ["libera"]},
    #    "fireirc": {"noWrap": True, "func": launchIrc, "args": ["fireirc"]},
    #    "efnet": {"noWrap": True, "func": launchIrc, "args": ["efnet"]},
    #    "backupbox": {"noWrap": True, "func": launchIrc, "args": ["backupbox"]},
    #    "twitch": {"noWrap": True, "func": launchIrc, "args": ["twitch"]},
    "discord": {"noWrap": True, "func": launchDiscord, "args": []},
}


if __name__ == "__main__":
    try:
        threadManager(servers, True, "CORE")
    except KeyboardInterrupt:
        log("Terminating from ^C", "CORE", "EXIT")
        sys.exit(0)
