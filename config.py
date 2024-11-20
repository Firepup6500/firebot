#!/usr/bin/python3
from os import environ as env
from dotenv import load_dotenv  # type: ignore
import re, codecs
from typing import Optional, Any, Union
import bare, pylast
from pydnsbl import DNSBLIpChecker, DNSBLDomainChecker, providers as BL


class droneBL(BL.Provider):
    def process_response(self, response):
        reasons = set()
        for result in response:
            reason = result.host
            if reason in ["127.0.0.3"]:
                reasons.add("IRC Spambot")
            elif reason in ["127.0.0.19"]:
                reasons.add("Abused VPN")
            elif reason in ["127.0.0.9", "127.0.0.8"]:
                reasons.add("Open Proxy")
            elif reason in ["127.0.0.13"]:
                reasons.add("Automated Attacks")
            else:
                print("Unknown dnsbl reason: " + reason, flush=True)
                reasons.add("unknown")
        return reasons


providers = BL.BASE_PROVIDERS + [droneBL("dnsbl.dronebl.org")]

ipbl = DNSBLIpChecker(providers=providers)
hsbl = DNSBLDomainChecker(providers=providers)

hardbl = ["146.70.59.36"]

load_dotenv()
__version__ = "v3.0.22"
npbase: str = (
    "\[\x0303last\.fm\x03\] [A-Za-z0-9_[\]{}\\|\-^]{1,$MAX} (is listening|last listened) to: \x02.+ - .*\x02( \([0-9]+ plays\)( \[.*\])?)?"  # pyright: ignore [reportInvalidStringEscapeSequence]
)
su = "^(su|sudo|(su .*|sudo .*))$"
servers: dict[str, dict[str, Any]] = {
    "ircnow": {
        "address": "127.0.0.1",
        "port": 6601,
        "interval": 200,
        "pass": env["ircnow_pass"],
        "channels": {"#random": 0, "#dice": 0, "#offtopic": 0, "#main/replirc": 0},
        "ignores": ["#main/replirc"],
        "hosts": ["9pfs.repl.co"],
        "dnsblMode": "kickban",
    },
    "efnet": {
        "address": "irc.underworld.no",
        "channels": {"#random": 0, "#dice": 0},
        "hosts": ["154.sub-174-251-241.myvzw.com"],
        "threads": ["pingMon"],
        "dnsblMode": "kickban",
    },
    "replirc": {
        "address": "127.0.0.1",
        "pass": env["replirc_pass"],
        "channels": {
            "#random": 0,
            "#dice": 0,
            "#main": 0,
            "#bots": 0,
            "#firebot": 0,
            "#sshchat": 0,
            "#firemc": 0,
            "#fp-radio": 0,
            "#fp-radio-debug": 0,
            "#hardfork": 0,
            "#opers": 0,
        },
        "ignores": ["#fp-radio"],
        "admins": ["h-tl"],
        "hosts": ["owner.firepi"],
        "threads": ["radio"],
        "autoMethod": "MARKOV",
        "dnsblMode": "akill",
    },
    "backupbox": {
        "address": "127.0.0.1",
        "port": 6607,
        "channels": {"#default": 0, "#botrebellion": 0, "#main/replirc": 0},
        "ignores": ["#main/replirc"],
        "hosts": [
            "172.20.171.225",
            "169.254.253.107",
            "2600-6c5a-637f-1a85-0000-0000-0000-6667.inf6.spectrum.com",
        ],
        "onIdntCmds": ["OPER e e"],
        "dnsbl-mode": "gline",
    },
    "twitch": {
        "nick": "fireschatbot",
        "address": "irc.chat.twitch.tv",
        "serverPass": env["twitch_pass"],
        "channels": {
            "#firepup650": 0,
        },
        "admins": ["firepup650"],
        "prefix": "!",
    },
}
admin_hosts: list[str] = ["firepup.firepi", "47.221.98.52"]
ESCAPE_SEQUENCE_RE = re.compile(
    r"""
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )""",
    re.UNICODE | re.VERBOSE,
)
prefix = "."
lastfmLink = pylast.LastFMNetwork(env["FM_KEY"], env["FM_SECRET"])
npallowed: list[str] = ["FireBitBot"]


def decode_escapes(s: str) -> str:
    def decode_match(match):
        return codecs.decode(match.group(0), "unicode-escape")

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)


def cmdFind(message: str, find: list, usePrefix: bool = True) -> bool:
    cmd = message.split(" ")
    if not cmd:
        return False
    if usePrefix:
        for match in find:
            sMatch = (prefix + match).split(" ")
            try:
                if all(cmd[i] == sMatch[i] for i in range(len(sMatch))):
                    return True
            except IndexError:
                ...
    else:
        for match in find:
            sMatch = match.split(" ")
            try:
                if all(cmd[i] == sMatch[i] for i in range(len(sMatch))):
                    return True
            except IndexError:
                ...
    return False


def mfind(message: str, find: list, usePrefix: bool = True) -> bool:
    if usePrefix:
        return any(message[: len(match) + 1] == prefix + match for match in find)
    else:
        return any(message[: len(match)] == match for match in find)


def sub(
    message: str, bot: bare.bot, chan: Optional[str] = "", name: Optional[str] = ""
) -> str:
    result = message.replace("$BOTNICK", bot.nick).replace("$NICK", bot.nick)
    result = result.replace("$NICKLEN", str(bot.nicklen)).replace(
        "$MAX", str(bot.nicklen)
    )
    if chan:
        result = result.replace("$CHANNEL", chan).replace("$CHAN", chan)
    if name:
        result = result.replace("$SENDER", name).replace("$NAME", name)
    return result


def dnsbl(hostname: str) -> tuple[str, dict[str, list[str]]]:
    hosts = []
    hstDT = {}
    try:
        hstDT = ipbl.check(hostname).detected_by
    except ValueError:  # It's not an IP
        try:
            hstDT = hsbl.check(hostname).detected_by
        except ValueError:  # It's also not a hostname
            hstDT = {}
    if hostname in hardbl:
        hstDT["hardcoded"] = ["Known bad host"]
    for host in hstDT:
        if hstDT[host] != ["unknown"]:
            hosts.append(host)
    if not hosts:
        return "", hstDT
    hostStr = None
    if len(hosts) >= 3:
        hostStr = ", and ".join((", ".join(hosts)).rsplit(", ", 1))
    else:
        hostStr = " and ".join(hosts)
    return hostStr, hstDT


def dnsblHandler(
    bot: bare.bot, nick: str, hostname: str, chan: str
) -> tuple[str, dict[str, list[str]]]:
    dnsblStatus = "Not enabled"
    dnsblResps = {}
    if bot.dnsblMode != "none":
        dnsblStatus, dnsblResps = (
            dnsbl(hostname)
            if not hostname in bot.dns
            else (bot.dns[hostname]["status"], bot.dns[hostname]["resps"])
        )
        bot.dns[hostname] = {"status": dnsblStatus, "resps": dnsblResps}
        if dnsblStatus:
            match bot.dnsblMode:
                case "kickban":
                    bot.sendraw(
                        f"KICK {chan} {nick} :Sorry, but you're on the {dnsblStatus} blacklist(s)."
                    )
                    bot.sendraw(f"MODE {chan} +b *!*@{hostname}")
                case "akill":
                    bot.sendraw(
                        f"OS AKILL ADD *@{hostname} !P Sorry, but you're on the {dnsblStatus} blacklist(s)."
                    )
                case "kline":
                    bot.sendraw(
                        f"KILL {nick} :Sorry, but you're on the {dnsblStatus} blacklist(s)."
                    )
                    bot.sendraw(
                        f"KLINE 524160 *@{hostname} :Sorry, but you're on the {dnsblStatus} blacklist(s)."
                    )
                    bot.sendraw(
                        f"KLINE *@{hostname} :Sorry, but you're on the {dnsblStatus} blacklist(s)."
                    )
                case "gline":
                    bot.sendraw(
                        f"KILL {nick} :Sorry, but you're on the {dnsblStatus} blacklist(s)."
                    )
                    bot.sendraw(
                        f"GLINE *@{hostname} 524160 :Sorry, but you're on the {dnsblStatus} blacklist(s)."
                    )
                    bot.sendraw(
                        f"GLINE *@{hostname} :Sorry, but you're on the {dnsblStatus} blacklist(s)."
                    )
                case _:
                    bot.log(f'Unknown dnsbl Mode "{bot.dnsblMode}"!', "WARN")
    return dnsblStatus, dnsblResps
