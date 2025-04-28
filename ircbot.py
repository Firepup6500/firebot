#!/usr/bin/python3
# pylint: disable=missing-module-docstring,broad-exception-caught,redefined-builtin
from sys import argv as args, exit
from traceback import format_exc
from bot import bot
from logs import log

server = args[1] if args else "UNSTABLE"


if __name__ == "__main__":
    instance = bot(server)
    try:
        instance.mainloop()
    except Exception:
        Err = format_exc()
        for line in Err.split("\n"):
            log(line, server, "CRASH")
    exit(1)
