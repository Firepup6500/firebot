#!/usr/bin/python3
# pylint: disable=missing-module-docstring,missing-function-docstring,redefined-builtin
from sys import exit
from typing import Any, NoReturn
from threading import Thread
from time import sleep
from traceback import format_exc
from pylast import WSError
import bare
from logs import log


def isDead(thr: Thread) -> bool:
    thr.join(timeout=0)
    return not thr.is_alive()


def threadWrapper(threadData: dict) -> NoReturn:
    # pylint: disable=broad-exception-caught
    if not threadData["noWrap"]:
        while 1:
            if threadData["ignoreErrors"]:
                try:
                    threadData["func"](*threadData["args"])
                except Exception:
                    exception = format_exc()
                    for line in exception.split("\n"):
                        log(line, "Thread", "WARN")
            else:
                try:
                    threadData["func"](*threadData["args"])
                except Exception:
                    exception = format_exc()
                    for line in exception.split("\n"):
                        log(line, "Thread", "CRASH")
                    exit(1)
            sleep(threadData["interval"])
        log("Threaded loop broken", "Thread", "FATAL")
    else:
        threadData["func"](*threadData["args"])
    exit(1)


def startThread(threadData: dict) -> Thread:
    t = Thread(target=threadWrapper, args=(threadData,))
    t.daemon = True
    t.start()
    return t


def threadManager(
    threads: dict[str, dict[str, Any]],
    output: bool = False,
    mgr: str = "TManager",
    interval: int = 60,
) -> NoReturn:
    if output:
        log("Begin init of thread manager", mgr)
    running = {}
    for name in threads:
        threadData = threads[name]
        running[name] = startThread(threadData)
    if output:
        log("All threads running, starting checkup loop", mgr)
    while 1:
        sleep(interval)
        if output:
            log("Checking threads", mgr)
        for name, t in running.items():
            if isDead(t):
                if output:
                    log(f"Thread {name} has died, restarting", mgr, "WARN")
                threadData = threads[name]
                running[name] = startThread(threadData)
    log("Thread manager loop broken", mgr, "FATAL")
    exit(1)


def radio(instance: bare.Bot) -> NoReturn:
    # pylint: disable=broad-exception-caught
    lastTrack = ""
    complained = False
    misses = 0
    missChunk = 0
    missCap = -5
    perChunk = 10
    channel = instance.radioData["channel"]
    topic = instance.radioData["topic"]
    debug = instance.radioData["debug"]
    while 1:
        try:
            newTrack = instance.lastfmLink.get_user("Firepup650").get_now_playing()
            if newTrack:
                if complained:
                    complained = False
                    misses = 0
                    missChunk = 0
                elif misses > missCap:
                    missChunk += 1
                    if missChunk >= perChunk:
                        misses -= 1
                        missChunk = 0
                thisTrack = str(newTrack)
                if thisTrack != lastTrack:
                    lastTrack = thisTrack
                    instance.msg(thisTrack, channel)
                    if topic:
                        instance.sendraw(
                            f"TOPIC {channel} :Firepup radio ({thisTrack}) - https://open.spotify.com/playlist/4ctNy3O0rOwhhXIKyLvUZM"
                        )
            elif not complained:
                missChunk = 0
                if misses < 0:
                    misses += 1
                    if debug:
                        instance.msg(
                            str(
                                {
                                    "misses": misses,
                                    "missChunk": missChunk,
                                    "misses exceed or meet limit": misses <= missCap,
                                }
                            ),
                            "#fp-radio-debug",
                        )
                    sleep(2)
                    continue
                instance.msg(
                    "Firepup's music seems to have stopped :/",
                    channel,
                )
                if topic:
                    instance.sendraw(
                        f"TOPIC {channel} :Firepup radio (Offline) - https://open.spotify.com/playlist/4ctNy3O0rOwhhXIKyLvUZM"
                    )
                complained = True
                lastTrack = "null"
        except WSError as pylastError:
            instance.log(f"Pylast is fucking stupid: {pylastError}", "WARN")
        except Exception:
            exception = format_exc()
            for line in exception.split("\n"):
                instance.log(line, "WARN")
        if debug:
            instance.msg(
                str(
                    {
                        "misses": misses,
                        "missChunk": missChunk,
                        "misses exceed or meet limit": misses <= missCap,
                    }
                ),
                "#fp-radio-debug",
            )
        sleep(2)
    instance.log("Thread while loop broken", "FATAL")
    exit(1)


def ping(instance: bare.Bot) -> NoReturn:
    while 1:
        instance.sendraw("PING :keepalive")
        sleep(30)


data: dict[str, dict[str, Any]] = {
    "radio": {"noWrap": True, "func": radio, "passInstance": True},
    "pingMon": {"noWrap": True, "func": ping, "passInstance": True},
}
