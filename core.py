#!/usr/bin/python3
# pylint: disable=missing-module-docstring,missing-function-docstring
from os import system
from threads import threadManager


def launch(server: str) -> None:
    system(f"python3 -u ircbot.py {server}")


def launch_discord() -> None:
    system("python3 -u discord_.py")


servers = {
    "ircnow": {"noWrap": True, "func": launch, "args": ["ircnow"]},
    "replirc": {"noWrap": True, "func": launch, "args": ["replirc"]},
    "efnet": {"noWrap": True, "func": launch, "args": ["efnet"]},
    "backupbox": {"noWrap": True, "func": launch, "args": ["backupbox"]},
    "twitch": {"noWrap": True, "func": launch, "args": ["twitch"]},
    "discord": {"noWrap": True, "func": launch_discord, "args": []},
}


if __name__ == "__main__":
    threadManager(servers, True, "CORE")
