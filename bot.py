#!/usr/bin/python3
# pylint: disable=missing-module-docstring,missing-class-docstring,too-many-instance-attributes,broad-exception-caught,redefined-builtin
from socket import socket, AF_INET, AF_INET6, SOCK_STREAM, SHUT_RDWR
from sys import exit
from typing import NoReturn, Union
from time import sleep
from importlib import reload
import random as r
from threading import Thread
from traceback import format_exc
import ircCommands as cmds
import config as conf
import utils
import threads
import logs
import handlers
import bare
from markov import MarkovBot


class Bot(bare.Bot):
    def __init__(self, server: str):
        bare.Bot.__init__(self, server)
        self.gmode = False
        self.server = server
        self.nicklen = 30
        self.address = conf.servers[server]["address"]
        self.port = (
            conf.servers[server]["port"] if "port" in conf.servers[server] else 6667
        )
        self.channels = conf.servers[server]["channels"]
        self.adminnames = (
            conf.servers[server]["admins"] if "admins" in conf.servers[server] else []
        )
        self.ignores = (
            conf.servers[server]["ignores"] if "ignores" in conf.servers[server] else []
        )
        self.__version__ = conf.__version__
        self.npallowed = conf.npallowed
        self.interval = (
            conf.servers[server]["interval"]
            if "interval" in conf.servers[server]
            else 50
        )
        self.nick = (
            conf.servers[server]["nick"]
            if "nick" in conf.servers[server]
            else "FireBot"
        )
        self.queue: list[bytes] = []
        self.statuses = {"firepup": {}}
        self.ops = {}
        inetFamily = (
            AF_INET6
            if "v6" in conf.servers[server] and conf.servers[server]["v6"]
            else AF_INET
        )
        self.sock = socket(inetFamily, SOCK_STREAM)
        self.current = "user"
        self.threads = (
            conf.servers[server]["threads"] if "threads" in conf.servers[server] else []
        )
        self.radioData = (
            conf.servers[server]["radioData"]
            if "radioData" in conf.servers[server]
            else {}
        )
        self.onIdntCmds = (
            conf.servers[server]["onIdntCmds"]
            if "onIdntCmds" in conf.servers[server]
            else []
        )
        self.onJoinCmds = (
            conf.servers[server]["onJoinCmds"]
            if "onJoinCmds" in conf.servers[server]
            else []
        )
        self.onStrtCmds = (
            conf.servers[server]["onStrtCmds"]
            if "onStrtCmds" in conf.servers[server]
            else []
        )
        self.autoMethod = (
            conf.servers[server]["autoMethod"]
            if "autoMethod" in conf.servers[server]
            else "QUOTE"
        )
        self.dnsblMode = (
            conf.servers[server]["dnsblMode"]
            if "dnsblMode" in conf.servers[server]
            else "none"
        )
        self.dns = {}
        self.lastfmLink = conf.lastfmLink
        with open("mastermessages.txt", encoding="utf-8") as f:
            markovFeed = []
            for line in f.readlines():
                markovFeed.extend([line.strip().split()])
            self.markov = MarkovBot(markovFeed)
        self.prefix = (
            conf.servers[server]["prefix"]
            if "prefix" in conf.servers[server]
            else conf.DEFAULT_PREFIX
        )
        self.log(f"Start init for {self.server}")

    def connect(self) -> None:
        self.log(f"Joining {self.server}...")
        self.sock.connect((self.address, self.port))
        self.send("\n")  # Just for sanity
        if self.onStrtCmds:
            for cmd in self.onStrtCmds:
                self.send(cmd + "\n")
        if "serverPass" in conf.servers[self.server]:
            self.send(f"PASS {conf.servers[self.server]['serverPass']}\n")
        self.send(f"NICK {self.nick}\n")
        self.send(f"USER {self.nick} {self.nick} {self.nick} {self.nick}\n")
        ircmsg = ""
        while True:
            ircmsg = utils.safeDecode(self.recv())
            if ircmsg != "":
                code = 0
                try:
                    code = int(ircmsg.split(" ", 2)[1].strip())
                except (IndexError, ValueError):
                    pass
                print(utils.lazyDecode(ircmsg))
                if "NICKLEN" in ircmsg:
                    self.nicklen = int(ircmsg.split("NICKLEN=")[1].split(" ")[0])
                    self.log(f"NICKLEN set to {self.nicklen}")
                if code == 433:
                    self.log("Nickname in use", "WARN")
                    self.nick = f"{self.nick}{r.randint(0,1000)}"
                    self.send(f"NICK {self.nick}\n")
                    self.log(f"nick is now {self.nick}")
                if code in [376, 422]:
                    self.log(f"Success by code: {code}")
                    break
                if " MODE " in ircmsg or " PRIVMSG " in ircmsg:
                    self.log("Success by MSG/MODE")
                    break
                if ircmsg.startswith("PING "):
                    self.ping(ircmsg)
                if len(ircmsg.split("\x01")) == 3:
                    handlers.ctcp(self, ircmsg)
                if "Closing link" in ircmsg:
                    self.exit("Closing Link")
            else:
                self.exit("Lost connection to the server")
        self.log(f"Joined {self.server} successfully!")

    def join(self, chan: str, origin: str, lock: bool = True) -> None:
        self.log(f"Joining {chan}...")
        chan = chan.replace(" ", "").lower()
        if "," in chan:
            chans = chan.split(",")
            for subchan in chans:
                self.join(subchan, origin)
            return
        if chan.startswith("0") or (
            chan == "#main" and lock and self.server != "replirc"
        ):
            if origin != "null":
                self.msg(f"Refusing to join channel {chan} (protected)", origin)
            return
        if chan in self.channels and lock:
            if origin != "null":
                self.msg(f"I'm already in {chan}.", origin)
            return
        self.send(f"JOIN {chan}\n")
        while True:
            ircmsg = utils.safeDecode(self.recv())
            if ircmsg != "":
                code = 0
                joinedChan = ""
                try:
                    code = int(ircmsg.split(" ", 2)[1].strip())
                    joinedChan = ircmsg.split(" ", 4)[3].strip().lower()
                except (IndexError, ValueError):
                    pass
                print(utils.lazyDecode(ircmsg))
                if ircmsg.startswith("PING "):
                    self.ping(ircmsg)
                elif ircmsg.startswith("ERROR "):
                    self.exit("Lost connection to the server while joining a channel")
                elif len(ircmsg.split("\x01")) == 3:
                    handlers.ctcp(self, ircmsg)
                elif code == 403 and chan == joinedChan:
                    self.log(f"Joining {chan} failed", "WARN")
                    if origin != "null":
                        self.msg(f"{chan} is an invalid channel", origin)
                    break
                elif code == 473 and chan == joinedChan:
                    self.log(f"Joining {chan} failed (+i)", "WARN")
                    if origin != "null":
                        self.msg(f"{chan} is +i, and I'm not invited.", origin)
                    break
                elif code == 474 and chan == joinedChan:
                    self.log(f"Joining {chan} failed (+b)", "WARN")
                    if origin != "null":
                        self.msg(f"I'm banned from {chan}.", origin)
                    break
                elif code == 475 and chan == joinedChan:
                    self.log(f"Joining {chan} failed (+k without/with bad key)")
                    if origin != "null":
                        self.msg(
                            f"{chan} is +k, and either you didn't give me a key, or you gave me the wrong one.",
                            origin,
                        )
                    break
                elif code == 480 and chan == joinedChan:
                    self.log(f"Joining {chan} failed (+S)", "WARN")
                    if origin != "null":
                        self.msg(
                            f"{chan} is +S, and I'm not connected over SSL.", origin
                        )
                    break
                elif code == 519 and chan == joinedChan:
                    self.log(f"Joining {chan} failed (+A)", "WARN")
                    if origin != "null":
                        self.msg(f"{chan} is +A, and I'm not an admin.", origin)
                    break
                elif code == 520 and chan == joinedChan:
                    self.log(f"Joining {chan} failed (+O)", "WARN")
                    if origin != "null":
                        self.msg(f"{chan} is +O, and I'm not an operator.", origin)
                    break
                elif code == 405 and chan == joinedChan:
                    self.log(f"Joining {chan} failed (too many channels)", "WARN")
                    if origin != "null":
                        self.msg(f"I'm in too many channels to join {chan}", origin)
                    break
                elif code == 471 and chan == joinedChan:
                    self.log(f"Joining {chan} failed (+l)", "WARN")
                    if origin != "null":
                        self.msg(f"{chan} is +l, and is full", origin)
                    break
                elif code == 366:
                    if chan == joinedChan:
                        self.log(f"Joining {chan} succeeded")
                        if origin != "null":
                            self.msg(f"Joined {chan}", origin)
                        self.channels[chan] = 0
                        break
                    self.log(f"Unpexpectedly joined {joinedChan}")
                    if origin != "null":
                        self.msg(f"Joined {joinedChan} (?????)", origin)
                    self.channels[joinedChan] = 0

    def ping(self, ircmsg: str) -> int:
        pong = f"PONG :{ircmsg.split('PING :')[1]}\n"
        print(pong, end="")
        return self.send(pong)

    def send(self, command: str) -> int:
        return self.sock.send(command.encode())

    def recv(self) -> bytes:
        if self.queue:
            return self.queue.pop(0)
        data = self.sock.recv(2048)
        if utils.lazyDecode(data) == "":
            return data
        while not data.endswith(b"\r\n"):
            data += self.sock.recv(2048)
        data = data.strip(b"\r\n")
        if b"\r\n" in data:
            self.queue.extend(data.split(b"\r\n"))
            return self.queue.pop(0)
        return data

    def log(self, message: str, level: str = "LOG") -> None:
        logs.log(message, self.server, level)

    def exit(self, message: str) -> NoReturn:
        logs.log(message, self.server, "EXIT")
        logs.log("Cleaning up asyncio before ternmination", self.server, "EXIT")
        loop = conf.loop
        if not loop.is_closed():
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        logs.log("Cleaning up socket before termination", self.server, "EXIT")
        self.sock.shutdown(SHUT_RDWR)
        self.sock.close()
        logs.log("Terminating.", self.server, "EXIT")
        exit(1)

    def msg(self, msg: str, target: str) -> None:
        if not (target == "NickServ" and utils.mfind(msg, ["IDENTIFY"])):
            self.log(f"Sending {utils.lazyDecode(msg)} to {target}")
        else:
            self.log("Identifying myself...")
        self.send(f"PRIVMSG {target} :{msg}\n")

    def op(self, name: str, chan: str) -> Union[int, None]:
        if name != "":
            self.log(f"Attempting op of {name} in {chan}...")
            return self.send(f"MODE {chan} +o {name}\n")
        return None

    def notice(self, msg: str, target: str, silent: bool = False) -> int:
        if not silent:
            self.log(f"Sending {utils.lazyDecode(msg)} to {target} (NOTICE)")
        return self.send(f"NOTICE {target} :{msg}\n")

    def sendraw(self, command: str) -> int:
        self.log(f"RAW sending {command}")
        command = f"{command}\n"
        return self.send(command.replace("$BOTNICK", self.nick))

    def mainloop(self) -> NoReturn:
        self.log("Starting connection..")
        self.connect()
        if "pass" in conf.servers[self.server]:
            self.msg(
                f"IDENTIFY FireBot {conf.servers[self.server]['pass']}", "NickServ"
            )
        sleep(0.5)
        if self.onIdntCmds:
            for cmd in self.onIdntCmds:
                self.send(cmd + "\n")
        for chan in list(self.channels):
            self.join(chan, "null", False)
        if self.onJoinCmds:
            for cmd in self.onJoinCmds:
                self.send(cmd + "\n")
        tMgr = None
        if self.threads:
            tdict = {}
            for thread in self.threads:
                tdict[thread] = threads.data[thread]
                if tdict[thread]["passInstance"]:
                    tdict[thread]["args"] = [self]
            tMgr = Thread(target=threads.threadManager, args=(tdict,))
            tMgr.daemon = True
            tMgr.start()
        while 1:
            raw = self.recv()
            ircmsg = utils.safeDecode(raw)
            if ircmsg == "":
                self.exit("Probably a netsplit")
            else:
                print(utils.lazyDecode(raw), sep="\n")
                action = "Unknown"
                try:
                    action = ircmsg.split(" ", 2)[1].strip()
                except IndexError:
                    pass
                self.tmpHost = ""
                if action in handlers.handles:
                    res, chan = handlers.handles[action](self, ircmsg)
                    if res == "reload" and isinstance(chan, str):
                        try:
                            reload(conf)
                            reload(utils)
                            self.adminnames = (
                                conf.servers[self.server]["admins"]
                                if "admins" in conf.servers[self.server]
                                else []
                            )
                            self.ignores = (
                                conf.servers[self.server]["ignores"]
                                if "ignores" in conf.servers[self.server]
                                else []
                            )
                            self.__version__ = conf.__version__
                            self.npallowed = conf.npallowed
                            self.interval = (
                                conf.servers[self.server]["interval"]
                                if "interval" in conf.servers[self.server]
                                else 50
                            )
                            self.prefix = (
                                conf.servers[self.server]["prefix"]
                                if "prefix" in conf.servers[self.server]
                                else conf.DEFAULT_PREFIX
                            )
                            reload(cmds)
                            reload(handlers)
                            self.msg("Reloaded successfully", chan)
                        except Exception:
                            exception = format_exc()
                            for line in exception.split("\n"):
                                self.log(line, "ERROR")
                            self.msg(
                                "Reload failed, likely partially reloaded. Please check error logs.",
                                chan,
                            )
                else:
                    if ircmsg.startswith("PING "):
                        self.ping(ircmsg)
                    elif ircmsg.startswith("ERROR :Closing Link"):
                        self.exit("I got killed :'(")
                    elif ircmsg.startswith("ERROR :Ping "):
                        self.exit("Ping timeout")
                    else:
                        self.log("Unrecognized server request!", "WARN")
        self.exit("While loop broken")
