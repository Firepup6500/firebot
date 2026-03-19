#!/usr/bin/python3
# pylint: disable=missing-module-docstring,broad-exception-caught,redefined-builtin
import asyncio
from socket import SHUT_RDWR
from sys import argv as args, exit
from traceback import format_exc
from bot import Bot
from logs import log

SERVER = args[1] if args else "UNSTABLE"

exception = "" # IT IS NOT A CONSTANT PYLINT

if __name__ == "__main__":
    instance = Bot(SERVER)
    try:
        instance.mainloop()
    except Exception:
        exception = format_exc()
        for line in exception.split("\n"):
            log(line, SERVER, "CRASH")
    except KeyboardInterrupt:
        log("Recieved ^C", SERVER, "EXIT")
        log("Cleaning up asyncio before ternmination", SERVER, "EXIT")
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        log("Cleaning up socket before termination", SERVER, "EXIT")
        instance.sock.shutdown(SHUT_RDWR)
        instance.sock.close()
        log("Terminating.", SERVER, "EXIT")
        exit(0)
    exit(1)
