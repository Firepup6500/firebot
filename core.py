#!/usr/bin/python3
# pylint: disable=missing-module-docstring,missing-function-docstring
import sys
from subprocess import Popen
from logs import log
from threads import threadManager


def launch(server: str) -> Popen:
    with Popen(["python3", "-u", "ircbot.py", server]) as proc:
        proc.wait()


def launchDiscord() -> Popen:
    with Popen(["python3", "-u", "discordBot.py"]) as proc:
        proc.wait()


servers = {
    "ircnow": {"noWrap": True, "func": launch, "args": ["ircnow"]},
    "libera": {"noWrap": True, "func": launch, "args": ["libera"]},
    #    "fireirc": {"noWrap": True, "func": launch, "args": ["fireirc"]},
    #    "efnet": {"noWrap": True, "func": launch, "args": ["efnet"]},
    #    "backupbox": {"noWrap": True, "func": launch, "args": ["backupbox"]},
    #    "twitch": {"noWrap": True, "func": launch, "args": ["twitch"]},
    "discord": {"noWrap": True, "func": launchDiscord, "args": []},
}


if __name__ == "__main__":
    try:
        threadManager(servers, True, "CORE")
    except KeyboardInterrupt:
        log("Terminating from ^C", "CORE", "EXIT")
        sys.exit(0)
