#!/usr/bin/python3
import random as r
import config as conf
import commands as cmds
from typing import Union, Callable
from overrides import bytes, bbytes
from importlib import reload
import bare, re, checks
from traceback import format_exc


def CTCP(bot: bare.bot, msg: str) -> bool:
    sender = msg.split("!", 1)[0][1:]
    kind = msg.split("\x01")[1].split(" ", 1)[0]
    bot.log(f'Responding to CTCP "{kind}" from {sender}')
    if kind == "VERSION":
        bot.notice(
            f"\x01VERSION FireBot {conf.__version__} (https://git.h.hackclub.app/Firepup650/FireBot)\x01",
            sender,
            True,
        )
        return True
    elif kind == "USERINFO":
        bot.notice("\x01USERINFO FireBot (Firepup's bot)\x01", sender, True)
        return True
    elif kind == "SOURCE":
        bot.notice(
            "\x01SOURCE https://git.h.hackclub.app/Firepup650/FireBot\x01",
            sender,
            True,
        )
        return True
    elif kind == "FINGER":
        bot.notice("\x01FINGER Firepup's bot\x01", sender, True)
        return True
    elif kind == "CLIENTINFO":
        bot.notice(
            "\x01CLIENTINFO ACTION VERSION USERINFO SOURCE FINGER\x01", sender, True
        )
        return True
    bot.log(f'Unknown CTCP "{kind}"', "WARN")
    return False


def PRIVMSG(bot: bare.bot, msg: str) -> Union[tuple[None, None], tuple[str, str]]:
    # Format of ":[Nick]![ident]@[host|vhost] PRIVMSG [channel] :[message]”
    name = msg.split("!", 1)[0][1:]
    host = msg.split("@", 1)[1].split(" ", 1)[0]
    bot.tmpHost = host
    bridge = False
    bot.current = "user"
    if (
        (name.startswith("saxjax") and bot.server == "efnet")
        or (name in ["ReplIRC", "sshchat"] and bot.server == "replirc")
        or (
            name in ["FirePyLink_", "FirePyLink"]
            and bot.server in ["ircnow", "backupbox"]
        )
    ):
        if "<" in msg and ">" in msg:
            bridge = True
            bot.current = "bridge"
            Nname = msg.split("<", 1)[1].split(">", 1)[0].strip()
            if name == "ReplIRC":
                name = Nname[4:]
            elif name in ["FirePyLink_", "FirePyLink"]:
                name = Nname.lstrip("@%~+")[3:-1]
            else:
                name = Nname
            message = msg.split(">", 1)[1].strip()
        else:
            message = msg.split("PRIVMSG", 1)[1].split(":", 1)[1].strip()
    elif name == bot.nick:
        return None, None
    else:
        message = msg.split("PRIVMSG", 1)[1].split(":", 1)[1].strip()
    chan = msg.split("PRIVMSG", 1)[1].split(":", 1)[0].strip()
    message = conf.sub(message, bot, chan, name)
    if chan in bot.ignores:
        return None, None
    bot.log(
        f'Got "{bytes(message).lazy_decode()}" from "{name}" in "{chan}" ({bot.current})',
    )
    if len(name) > bot.nicklen:
        bot.log(f"Name too long ({len(name)} > {bot.nicklen})")
        if not bridge:
            return None, None
        else:
            bot.log("This user is a bridge, overriding")
    elif chan not in bot.channels:
        if not chan == bot.nick:
            bot.log(
                f"Channel not in channels ({chan} not in {bot.channels})",
                "WARN",
            )
        if not chan.startswith(("#", "+", "&")):
            chan = name
    else:
        bot.channels[chan] += 1
    if "goat" in name.lower() and bot.gmode == True:
        cmds.goat(bot, chan, name, message)
    handled = False
    for cmd in cmds.data:
        triggers = [cmd]
        triggers.extend(cmds.data[cmd]["aliases"])
        triggers = list(conf.sub(call, bot, chan, name).lower() for call in triggers)
        if conf.cmdFind(
            conf.sub(message, bot, chan, name).lower(),
            triggers,
            cmds.data[cmd]["prefix"],
        ):
            if "check" in cmds.data[cmd] and cmds.data[cmd]["check"]:
                if cmds.data[cmd]["check"](bot, name, host, chan, cmd):
                    try:
                        cmds.call[cmd](bot, chan, name, message)
                    except Exception:
                        Err = format_exc()
                        for line in Err.split("\n"):
                            bot.log(line, "ERROR")
                        bot.msg(
                            "Sorry, I had an error trying to execute that command. Please check error logs.",
                            chan,
                        )
            else:
                try:
                    cmds.call[cmd](bot, chan, name, message)
                except Exception:
                    Err = format_exc()
                    for line in Err.split("\n"):
                        bot.log(line, "ERROR")
                    bot.msg(
                        "Sorry, I had an error trying to execute that command. Please check error logs.",
                        chan,
                    )
            handled = True
            break
    if not handled:
        for check in cmds.regexes:
            if re.search(
                conf.sub(check, bot, chan, name),
                message,
            ):
                cmds.call[check](bot, chan, name, message)
                handled = True
                break
    if not handled and conf.cmdFind(message, ["reload", "r"]):
        if checks.admin(bot, name, host, chan, "reload"):
            return "reload", chan
        handled = True
    if not handled and len(message.split("\x01")) == 3:
        if not CTCP(bot, message):
            kind = message.split("\x01")[1]
            if kind.startswith("ACTION ducks") and len(kind.split(" ", 2)) == 3:
                bot.msg(
                    f"\x01ACTION gets hit by {kind.split(' ', 2)[2]}\x01",
                    chan,
                )
            elif kind == "ACTION ducks":
                bot.msg("\x01ACTION gets hit by a duck\x01", chan)
    if chan in bot.channels and bot.channels[chan] >= bot.interval:
        sel = ""
        bot.channels[chan] = 0
        if bot.autoMethod == "QUOTE":
            r.seed()
            with open("mastermessages.txt", "r") as mm:
                sel = conf.decode_escapes(
                    r.sample(mm.readlines(), 1)[0].replace("\\n", "").replace("\n", "")
                )
        else:
            sel = bot.markov.generate_from_sentence(message)
        bot.msg(f"[{bot.autoMethod}] {sel}", chan)
    return None, None


def NICK(bot: bare.bot, msg: str) -> tuple[None, None]:
    name = msg.split("!", 1)[0][1:]
    if name == bot.nick:
        bot.nick = msg.split("NICK", 1)[1].split(":", 1)[1].strip()
    return None, None


def KICK(bot: bare.bot, msg: str) -> tuple[None, None]:
    important = msg.split("KICK", 1)[1].split(":", 1)[0].strip().split(" ")
    channel = important[0]
    kicked = important[1]
    if kicked == bot.nick:
        bot.channels.pop(channel, None)
    return None, None


def PART(bot: bare.bot, msg: str) -> tuple[None, None]:
    parted = msg.split("!", 1)[0][1:]
    channel = msg.split("PART", 1)[1].split(":", 1)[0].strip()
    if parted == bot.nick:
        bot.channels.pop(channel, None)
    return None, None


def QUIT(bot: bare.bot, msg: str) -> tuple[None, None]:
    if bot.server == "replirc":
        quitter = msg.split("!", 1)[0][1:]
        if quitter == "FireMCbot":
            bot.send("TOPIC #firemc :FireMC Relay channel (offline)\n")
    return None, None


def JOIN(bot: bare.bot, msg: str) -> tuple[None, None]:
    nick = msg.split("!", 1)[0][1:]
    hostname = msg.split("@", 1)[1].split(" ", 1)[0].strip()
    chan = msg.split("#")[-1].strip()
    conf.dnsblHandler(bot, nick, hostname, chan)
    return None, None


def MODE(bot: bare.bot, msg: str) -> tuple[None, None]:
    try:
        chan = msg.split("#", 1)[1].split(" ", 1)[0]
        add = True if msg.split("#", 1)[1].split(" ", 2)[1][0] == "+" else False
        modes = msg.split("#", 1)[1].split(" ", 2)[1][1:]
        users = ""
        try:
            users = msg.split("#", 1)[1].split(" ", 2)[2].split()
        except IndexError:
            ...
        if len(modes) != len(users):
            bot.log("Refusing to handle modes that do not have corresponding users.")
            return None, None
        for i in range(len(modes)):
            if users[i] == bot.nick:
                if modes[i] == "o":
                    bot.ops[chan] = add
                    bot.log(f"{'Got' if add else 'Lost'} ops in {chan}")
    except IndexError:  # *our* modes are changing, not a channel
        bot.log("Not handling changing of my modes")
    return None, None


def NULL(bot: bare.bot, msg: str) -> tuple[None, None]:
    return None, None


handles: dict[
    str, Callable[[bare.bot, str], Union[tuple[None, None], tuple[str, str]]]
] = {
    "PRIVMSG": PRIVMSG,
    "NICK": NICK,
    "KICK": KICK,
    "PART": PART,
    "MODE": MODE,
    "TOPIC": NULL,
    "QUIT": QUIT,
    "JOIN": JOIN,
    "NOTICE": NULL,
    "INVITE": NULL,
}
