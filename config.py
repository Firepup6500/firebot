# pylint: disable=missing-module-docstring,missing-class-docstring,too-few-public-methods
from os import environ as env
import re
from typing import Any
from dotenv import load_dotenv
from pydnsbl import DNSBLIpChecker, DNSBLDomainChecker, providers as BL
import pylast


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

hardbl: list[str] = ["146.70.59.36"]

load_dotenv()
__version__ = "v3.0.23"
npbase: str = (
    "\\[\x0303last\\.fm\x03\\] [A-Za-z0-9_[\\]{}\\|\\-^]{1,$MAX} (is listening|last listened) to: \x02.+ - .*\x02( \\([0-9]+ plays\\)( \\[.*\\])?)?"
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
admin_hosts: list[str] = ["firepup.firepi", "69.8.95.218"]
noAdmins = ["ircnow", "backupbox"]
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
