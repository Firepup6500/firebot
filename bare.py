#!/usr/bin/python3
# pylint: disable=unused-argument,missing-module-docstring,missing-function-docstring,missing-class-docstring,redefined-builtin,invalid-name
from socket import socket
from typing import NoReturn, Union
from pylast import LastFMNetwork
from overrides import bytes, bbytes
from markov import MarkovBot

logs = ...
re = ...
cmds = ...
conf = ...
sleep = ...
reload = ...
r = ...
handlers = ...


def mfind(message: str, find: list, usePrefix: bool = True) -> bool: ...


class Bot:
    gmode: bool
    server: str
    nicklen: int
    address: str
    port: int
    channels: dict[str, int]
    interval: int
    __version__: str
    nick: str
    adminnames: list[str]
    queue: list[bbytes]  # pyright: ignore [reportInvalidTypeForm]
    sock: socket
    npallowed: list[str]
    current: str
    tmpHost: str
    ignores: list[str]
    threads: list[str]
    lastfmLink: LastFMNetwork
    onIdntCmds: list[str]
    onJoinCmds: list[str]
    onStrtCmds: list[str]
    markov: MarkovBot
    autoMethod: str
    dnsblMode: str
    statuses: dict[str, dict[str, str]]
    ops: dict[str, bool]
    dns: dict[str, dict[str, Union[str, list[str]]]]

    def __init__(self, server: str): ...

    def connect(self) -> None: ...

    def join(self, chan: str, origin: str, lock: bool = True) -> None: ...

    def ping(self, ircmsg: str) -> int: ...

    def send(self, command: str) -> int: ...

    def recv(self) -> bytes: ...

    def log(self, message: str, level: str = "LOG") -> None: ...

    def exit(self, message: str) -> NoReturn: ...

    def msg(self, msg: str, target: str) -> None: ...

    def op(self, name: str, chan: str) -> Union[int, None]: ...

    def notice(self, msg: str, target: str, silent: bool = False) -> int: ...

    def sendraw(self, command: str) -> int: ...

    def mainloop(self) -> NoReturn: ...
