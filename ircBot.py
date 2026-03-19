#!/usr/bin/python3
# pylint: disable=missing-module-docstring,broad-exception-caught,redefined-builtin
import asyncio
from socket import SHUT_RDWR
from sys import argv as args, exit
from traceback import format_exc
from bot import Bot
from logs import log

server = args[1] if args else "UNSTABLE"


if __name__ == "__main__":
    instance = Bot(server)
    try:
        instance.mainloop()
    except Exception:
        Err = format_exc()
        for line in Err.split("\n"):
            log(line, server, "CRASH")
    except KeyboardInterrupt:
        log("Recieved ^C", server, "EXIT")
        log("Cleaning up asyncio before ternmination", server, "EXIT")
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        log("Cleaning up socket before termination", server, "EXIT")
        instance.sock.shutdown(SHUT_RDWR)
        instance.sock.close()
        log("Terminating.", server, "EXIT")
        exit(0)
    exit(1)
