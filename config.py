# pylint: disable=missing-module-docstring,missing-class-docstring,too-few-public-methods
import asyncio
from os import environ as env
import re
from typing import Any
from dotenv import load_dotenv
from pydnsbl import DNSBLIpChecker, DNSBLDomainChecker, providers as BL
import pylast


class DroneBl(BL.Provider):
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


providers = BL.BASE_PROVIDERS + [DroneBl("dnsbl.dronebl.org")]

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
ipbl = DNSBLIpChecker(providers=providers)
hsbl = DNSBLDomainChecker(providers=providers)

hardbl: list[str] = ["146.70.59.36"]

load_dotenv()
__version__ = "v3.0.27"
NOWPLAYING_REGEX: str = (
    "\\[\x0303last\\.fm\x03\\] [A-Za-z0-9_[\\]{}\\|\\-^]{1,$MAX} (is listening|last listened) to: \x02.+ - .*\x02( \\([0-9]+ plays\\)( \\[.*\\])?)?"
)
SUDO_REGEX = "^(su|sudo|(su .*|sudo .*))$"
servers: dict[str, dict[str, Any]] = {
    "ircnow": {
        "address": "irc.freeirc.org",
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
        "threads": ["pingMon"],
        "dnsblMode": "kickban",
        "hosts": []
    },
    "hollyhock": {
        "address": "irc.hollyhock.internal",
        "channels": {"#random": 0, "#main": 0, "#radio": 0},
        "ignores": ["#radio"],
        "threads": ["radio"],
        "radioData": {"channel": "#radio", "topic": False, "debug": False},
        "v6": True,
        "autoMethod": "MARKOV",
        "hosts": [],
    },
    "libera": {
        "address": "irc.libera.chat",
        "pass": env["libera_pass"],
        "channels": {"#random": 0, "#dice": 0},
        "dnsblMode": "kickban",
        "hosts": [],
    },
    "fireirc": {
        "address": "127.0.0.1",
        "pass": env["fireirc_pass"],
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
            "#opers": 0,
        },
        "ignores": ["#fp-radio"],
        "hosts": ["owner.irc.firepup650.com"],
        "threads": ["radio"],
        "radioData": {"channel": "#fp-radio", "topic": True, "debug": False},
        "autoMethod": "MARKOV",
        "dnsblMode": "akill",
    },
    "backupbox": {
        "address": "127.0.0.1",
        "port": 6607,
        "channels": {"#default": 0, "#botrebellion": 0, "#main/replirc": 0},
        "ignores": ["#main/replirc"],
        "onIdntCmds": ["OPER e e"],
        "dnsbl-mode": "gline",
        "hosts": [],
    },
    "twitch": {
        "nick": "fireschatbot",
        "address": "irc.chat.twitch.tv",
        "serverPass": "oauth:" + env["twitch_pass"],
        "channels": {
            "#firepup650": 0,
        },
        "admins": ["firepup650"],
        "prefix": "!",
        "hosts": [],
    },
}
GLOBAL_ADMIN_HOSTS: list[str] = ["firepup.firepi", "69.8.95.218"]
noAdmins = ["ircnow", "backupbox", "hollyhock"]
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
IRC_ESCAPE_CODES = [0x02, 0x1F, 0x16, 0x1D, 0x1E, 0x0F, 0x03, 0x07, 0x1B, 0x11]
DEFAULT_PREFIX = "."
lastfmLink = pylast.LastFMNetwork(env["FM_KEY"], env["FM_SECRET"])
npallowed: list[str] = ["FireBitBot"]
