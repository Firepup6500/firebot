# pylint: disable=missing-module-docstring,missing-function-docstring
import codecs
from typing import Optional
import bare
from config import ESCAPE_SEQUENCE_RE, prefix, ipbl, hsbl, hardbl, IRC_ESCAPE_CODES


def replace_irc(s: str) -> str:
    for code in IRC_ESCAPE_CODES:
        s = s.replace(chr(code), f"\\x{code:02x}")
    return s


def decode_escapes(s: str, replaceControls=False) -> str:
    s = s.replace("\n", "").replace("\\n", "")

    def decode_match(match):
        return codecs.decode(match.group(0), "unicode-escape")

    s = ESCAPE_SEQUENCE_RE.sub(decode_match, s)

    if replaceControls:
        s = replace_irc(s)

    return s


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
