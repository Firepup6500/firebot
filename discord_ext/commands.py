# pylint: disable=missing-module-docstring,missing-function-docstring,redefined-builtin,duplicate-code
from subprocess import run, PIPE
import random as r
import re, logging
from sys import exit
from typing import Any, Callable
from traceback import format_exc
from urllib.parse import unquote
import discord
from discord.ext.commands import Context
from utils import decodeEscapes
from .shared import handler

logger = logging.getLogger(__name__)
logger.addHandler(handler)


async def fpmpDiscord(ctx: Context) -> None:
    await ctx.send(
        "Firepup's master playlist\nhttps://open.spotify.com/playlist/4ctNy3O0rOwhhXIKyLvUZM"
    )


async def fplqDiscord(ctx: Context) -> None:
    await ctx.send(
        "Firepup's listen queue\nhttps://open.spotify.com/playlist/20PLdgeBNrCC63Bufg50eK"
    )


async def fpoDiscord(ctx: Context) -> None:
    await ctx.send(
        "Firepup's obsessions playlist\nhttps://open.spotify.com/playlist/5kdR1GsT0gG6ISvskpHyMS"
    )


async def versionDiscord(ctx: Context) -> None:
    await ctx.send("Version: " + ctx.bot.__version__ + " (Discord)")


async def botlistDiscord(ctx: Context) -> None:
    await ctx.send(
        f"Hi! I'm FireBot (<https://git.firepup650.com/firepup650/firebot>)! My admins on discord are {str(ctx.bot.owner_ids)}."
    )


async def bugsDiscord(ctx: Context) -> None:
    await ctx.send(
        f"_realizes <@{ctx.author.id}> looks like a bug and squashes <@{ctx.author.id}>_"
    )


async def hiDiscord(ctx: Context) -> None:
    await ctx.send(f"Hello <@{ctx.author.id}>!")


async def pingDiscord(ctx: Context) -> None:
    await ctx.send(
        f"<@{ctx.author.id}>: pong ({round(ctx.bot.latency * 1000)}ms server latency)"
    )


async def uptimeDiscord(ctx: Context) -> None:
    uptime = run(["uptime", "-p"], stdout=PIPE, check=False).stdout.decode().strip()
    await ctx.send(f"Uptime: {uptime}")


async def helpDiscord(ctx: Context, *, category: str = None) -> None:
    # pylint: disable=unreachable
    await ctx.send("Command list needs rework")
    return
    match category:
        case None:
            await ctx.send("Categories of commands: gen, dbg, adm, fun, msc")
        case "gen":
            await ctx.send("Commands in the General category: ")
        case "dbg":
            await ctx.send("Commands in the [DEBUG] category: ")
        case "adm":
            await ctx.send("Commands in the Admin category: ")
        case "fun":
            await ctx.send("Commands in the Fun category: ")
        case "msc":
            await ctx.send("Commands in the Misc. category: ")
        case _:
            await ctx.send("Unknown commands category.")


async def quoteDiscord(ctx: Context, *, regex: str = "") -> None:
    qfilter = regex.replace(
        " ", r"\s"
    )  # pyright: ignore [reportInvalidStringEscapeSequence]
    r.seed()
    with open("mastermessages.txt", "r", encoding="utf-8") as mm:
        q = []
        try:
            q = list(filter(lambda x: re.search(qfilter, x), mm.readlines()))
        except re.error:
            q = ["Sorry, your query is invalid regex. Please try again."]
        if not q:
            q = [f'No results for "{regex}" ']
        sel = decodeEscapes(
            r.sample(q, 1)[0]
            .replace("\\n", "")
            .replace("\n", "")
            .replace("_", "\\_")
            .replace("*", "\\*")
            .replace("||", "\\|\\|")
            .replace("\\", "\\\\"),
            True,
        )
        await ctx.send(sel)
        if ctx.interaction and await ctx.bot.is_owner(ctx.author):
            await ctx.send(sel.encode(), ephemeral=True)


async def eballDiscord(ctx: Context, *, question: str = "") -> None:
    if question.endswith("?"):
        with open("eightball.txt", "r", encoding="utf-8") as eb:
            q = eb.readlines()
            sel = str(r.sample(q, 1)).strip("[]'").replace("\\n", "").strip('"')
            await ctx.send(f"User asked: {question}\nThe magic eightball says: {sel}")
    else:
        await ctx.send("Please pose a Yes or No question.")


async def debugDiscord(ctx: Context) -> None:
    debugOutput = {
        "VERSION": ctx.bot.__version__ + " (Discord)",
        "NICKLEN": "N/A on discord",
        "NICK": ctx.guild.me.nick if ctx.guild.me.nick else ctx.guild.me.name,
        "ADMINS": ctx.bot.owner_ids,
        "CHANNELS": "N/A on discord",
    }
    await ctx.send(f"[DEBUG] {debugOutput}")


async def debugInternalDiscord(ctx: Context, thing: str = "") -> None:
    things = dir(ctx.bot)
    if thing == "":
        await ctx.send("You can't just ask me to lookup nothing.")
        return
    if thing in things:
        await ctx.send(f"self.{thing} = {getattr(ctx.bot, thing)}")
    else:
        await ctx.send(f'I have nothing called "{thing}"')


async def debugEvalDiscord(ctx: Context, *, code: str = "") -> None:
    # pylint: disable=broad-exception-caught,eval-used
    try:
        out = (
            str(eval(code))
            .replace("_", "\\_")
            .replace("*", "\\*")
            .replace("||", "\\|\\|")
        )
        if len(out) == 0:
            await ctx.send("<No Output>")
        while len(out) > 0:
            chunk = out[:2000]
            out = out[2000:]
            await ctx.send(chunk, allowed_mentions=discord.AllowedMentions.none())
    except Exception:
        exception = format_exc()
        await ctx.send(f"Exception:\n{exception}")


async def debugEvalRawDiscord(ctx: Context, *, code: str = "") -> None:
    # pylint: disable=broad-exception-caught,eval-used
    try:
        out = str(eval(code))
        if len(out) == 0:
            await ctx.send("<No Output>")
        while len(out) > 0:
            chunk = out[:2000]
            out = out[2000:]
            await ctx.send(chunk, allowed_mentions=discord.AllowedMentions.none())
    except Exception:
        exception = format_exc()
        await ctx.send(f"Exception:\n{exception}")


async def rebootDiscord(ctx: Context) -> None:
    await ctx.send("Rebooting")
    exit("Reboot")


async def fmpullDiscord(ctx: Context, user: str = "Firepup650") -> None:
    # pylint: disable=broad-exception-caught,fixme
    song = None
    try:
        song = ctx.bot.lastfmLink.get_user(user).get_now_playing()
    except Exception:  # TODO: Proper catch
        await ctx.send(
            "Sorry, the last.fm api isn't cooperating, please try again in a minute",
        )
        logger.error("Failed to fetch from last.fm", exc_info=True)
        return
    if song:
        await ctx.send(
            f"{user} is currently listening to: ["
            + str(song)
            + "]("
            + unquote(song.get_url())
            + ")",
        )
    else:
        await ctx.send(f"{user} currently has their music stopped")


async def whoamiDiscord(ctx: Context) -> None:
    await ctx.send(
        f"I think you are {ctx.author.nick if ctx.author.nick else ctx.author.name} (discord)",
    )


async def markovDiscord(ctx: Context, word: str = None) -> None:
    if word is not None and " " in word:
        word = word.split()[0]
    proposed = ctx.bot.markov.generate_text(word)
    if proposed == word:
        proposed = f'Chain failed. (Firepup has never been recorded saying "{word}")'
    await ctx.send(
        proposed.replace("\\n", "")
        .replace("\n", "")
        .replace("_", "\\_")
        .replace("*", "\\*")
        .replace("||", "\\|\\|")
        .replace("\\", "\\\\")
    )


async def slapDiscord(ctx: Context, *, target: str = "") -> None:
    name = f"<@{ctx.author.id}>"
    nick = ctx.guild.me.nick if ctx.guild.me.nick else ctx.guild.me.name
    ping = f"<@{ctx.guild.me.id}>"
    if target:
        msg = target.strip()
        if (
            msg.lower().strip()
            in [nick.lower().strip(), ctx.guild.me.name.lower().strip(), ping]
            or not msg
        ):
            msg = name
    else:
        msg = name
    await ctx.send(
        f"_slaps {msg} around a bit with {r.choice(['a firewall', 'a fireball', 'a large trout', 'a computer', 'an rpi4', 'an rpi5', 'firepi', name])}_",
    )


# Discord-only commands


async def errorTester(ctx: Context) -> None:
    # pylint: disable=broad-exception-raised
    raise Exception("Intentional Error, for testing")


async def ready(ctx: Context) -> None:
    await ctx.send("Yeah I'm ready, what?")


async def reinit(ctx: Context) -> None:
    await ctx.bot.database.delete(ctx.guild.id)
    await ctx.bot.database.set(ctx.guild.id, {"init": True})
    await ctx.send("Re-initalized guild config")


async def dropDatabase(ctx: Context, iAmSure=None) -> None:
    if iAmSure:
        await ctx.bot.database.deleteAll()
        await ctx.send("Dropped the database!")
    else:
        await ctx.send("No.")


VALID_SETTINGS = [
    "welcome_channel",
    "on_user_join_role",
    "on_bot_join_role",
    "leave_channel",
]
VALID_SETTINGS_STRING = ", ".join(VALID_SETTINGS)


async def setSetting(ctx: Context, setting: str = None, value: str = None) -> None:
    if setting is None:
        await ctx.send(f"Valid settings are: `{VALID_SETTINGS_STRING}`")
        return
    if setting not in VALID_SETTINGS:
        await ctx.send(
            f"`{setting}` is not a valid setting. Valid settings are: `{VALID_SETTINGS_STRING}`"
        )
        return
    data = await ctx.bot.database.get(ctx.guild.id)
    oldValue = data.get(setting)
    valueString = f"`{value}`"
    if value is not None:
        if setting.endswith("_channel"):
            value = value[2:-1]
            if not value.isdigit():
                await ctx.send(f"`{setting}` must be a channel.")
                return
            val = ctx.guild.get_channel(int(value))
            if not isinstance(val, discord.TextChannel):
                await ctx.send(f"`{setting}` must be a text channel.")
                return
            valueString = val.mention
        elif setting.endswith("_role"):
            value = value[3:-1]
            if not value.isdigit():
                await ctx.send(f"`{setting}` must be a role.")
                return
            val = ctx.guild.get_role(int(value))
            if not isinstance(val, discord.Role):
                await ctx.send(f"`{setting}` must be a role.")
                return
            valueString = val.mention
    if oldValue == value:
        await ctx.send(f"`{setting}` unchanged")
    elif not oldValue:
        await ctx.send(
            f"Set `{setting}` to {valueString}",
            allowed_mentions=discord.AllowedMentions.none(),
        )
    elif not value:
        await ctx.send(f"`{setting}` has been unset")
    else:
        await ctx.send(
            f"Changed `{setting}` to {valueString}",
            allowed_mentions=discord.AllowedMentions.none(),
        )
    data[setting] = value
    await ctx.bot.database.set(ctx.guild.id, data)


async def getSetting(ctx: Context, setting: str = None) -> None:
    if setting is None:
        data = await ctx.bot.database.get(ctx.guild.id)
        resp = "Settings in this guild:"
        for settingName in VALID_SETTINGS:
            value = data.get(settingName)
            if value is None:
                value = "<Not set>"
            elif settingName.endswith("_channel"):
                val = ctx.guild.get_channel(int(value))
                value = val.mention
            elif settingName.endswith("_role"):
                val = ctx.guild.get_role(int(value))
                value = val.mention
            resp = resp + f"\n\\- {settingName} = {value}"
        await ctx.send(resp, allowed_mentions=discord.AllowedMentions.none())
        return
    if setting not in VALID_SETTINGS:
        await ctx.send(
            f"`{setting}` is not a valid setting. Valid settings are: `{VALID_SETTINGS_STRING}`"
        )
        return
    data = await ctx.bot.database.get(ctx.guild.id)
    value = data.get(setting)
    valueString = value
    if value is not None:
        if setting.endswith("_channel"):
            val = ctx.guild.get_channel(int(value))
            valueString = val.mention
        elif setting.endswith("_role"):
            val = ctx.guild.get_role(int(value))
            valueString = val.mention
    if not value:
        await ctx.send(f"`{setting}` is not set for this guild")
    else:
        await ctx.send(
            f"`{setting}` is set to {valueString} in this guild",
            allowed_mentions=discord.AllowedMentions.none(),
        )


# Data dicts


# Metadata dict
dataDiscord: dict[str, dict[str, Any]] = {
    "botlist": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": [],
        "desc": "Info about the bot",
        "params": {},
    },
    "bugs": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": [],
        "desc": "Say... you kinda look like a bug...",
        "params": {},
    },
    "hi": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["hello"],
        "desc": "Hiya!",
        "params": {},
    },
    "restart": {
        "owner": True,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["reboot", "stop", "hardreload", "hr"],
        "desc": "Owners only - Kill the bot",
        "params": {},
    },
    "uptime": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["u"],
        "desc": "Uptime of the system the bot is running on",
        "params": {},
    },
    "debug": {
        "owner": True,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["dbg", "d"],
        "desc": "Owners only - Debug info",
        "params": {},
    },
    "debuginternal": {
        "owner": True,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["dbgint", "di"],
        "desc": "Owners only - Lookup internal bot components",
        "params": {"thing": "The name of the object you want to pull from the bot"},
    },
    "debugeval": {
        "owner": True,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["dbgeval", "de"],
        "desc": "Owners only - Literally just eval(code)",
        "params": {"code": "eval(code)"},
    },
    "debugevalraw": {
        "owner": True,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["dbgevalraw", "der"],
        "desc": "Owners only - Literally just eval(code)",
        "params": {"code": "eval(code)"},
    },
    "8ball": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["eightball", "8b"],
        "desc": "Ask the magic 8ball a question",
        "params": {
            "question": "The question to ask the magic eightball, must end in a ?"
        },
    },
    "quote": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["q"],
        "desc": "Get something random that firepup has said before",
        "params": {"regex": "Regex filter to use to filter the quote list for"},
    },
    "help": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["list", "h"],
        "desc": "Help command",
        "params": {
            "category": "The category of commands to view help for, if not given lists categories"
        },
    },
    "ping": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": [],
        "desc": "Pingy Pongy (includes latency)",
        "params": {},
    },
    "whoami": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": [],
        "desc": "Who are you? I know! So ask! :3",
        "params": {},
    },
    "fpmp": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["playlist"],
        "desc": "Get the link to Firepup's master playlist on Spotify",
        "params": {},
    },
    "fplq": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["fprq", "queue"],
        "desc": "Get the link to Firepup's listen queue on Spotify",
        "params": {},
    },
    "fpo": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["obsessions"],
        "desc": "Get the link to Firepup's obessions playlist on Spotify",
        "params": {},
    },
    "version": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["ver", "v"],
        "desc": "Check the bot's version",
        "params": {},
    },
    "np": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": [],
        "desc": "Check what Firepup is listening to right now",
        "params": {},
    },
    "markov": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["m"],
        "desc": "markov needs to me on a large ping me just cause it a tilde server, you'd stop spamming IRC Relay",
        "params": {
            "word": 'word "BLACK" in the same for commands to contact for issuing CTCP actually modify that the FBI action picks up maubot'
        },
    },
    "slap": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": ["s"],
        "desc": "Slap someone with something random!",
        "params": {
            "target": "What/Whom I should slap with one of the things I keep in storage"
        },
    },
    "errorTester": {
        "owner": True,
        "server_owner": False,
        "server_admin": False,
        "aliases": [],
        "desc": "Owners only - Cause an error to test the bot",
        "params": {},
    },
    "ready": {
        "owner": False,
        "server_owner": False,
        "server_admin": False,
        "aliases": [],
        "desc": "Test command to see if the bot is ready for commands",
        "params": {},
    },
    "reinit": {
        "owner": True,
        "server_owner": False,
        "server_admin": False,
        "aliases": [],
        "desc": "Onwers only - Reset all settings for the guild this is run in",
        "params": {},
    },
    "dropDatabase": {
        "owner": True,
        "server_owner": False,
        "server_admin": False,
        "aliases": [],
        "desc": "Onwers only - !! DANGER !! Drop ALL settings for all guilds!",
        "params": {"i_am_sure": "Are you SURE you want to drop it?"},
    },
    "set": {
        "owner": False,
        "server_owner": False,
        "server_admin": True,
        "aliases": [],
        "desc": "Server Admins only - Set one of the settings for your guild",
        "params": {"setting": "Setting name", "value": "Setting value"},
    },
    "get": {
        "owner": False,
        "server_owner": False,
        "server_admin": True,
        "aliases": [],
        "desc": "Server Admins only - Get one of the settings for your guild",
        "params": {"setting": "Setting name"},
    },
}
# Call dict
callDiscord: dict[str, Callable[Any, None]] = {
    "botlist": botlistDiscord,
    "bugs": bugsDiscord,
    "hi": hiDiscord,
    "restart": rebootDiscord,
    "uptime": uptimeDiscord,
    "debug": debugDiscord,
    "debuginternal": debugInternalDiscord,
    "debugeval": debugEvalDiscord,
    "debugevalraw": debugEvalRawDiscord,
    "8ball": eballDiscord,
    "quote": quoteDiscord,
    "help": helpDiscord,
    "ping": pingDiscord,
    "whoami": whoamiDiscord,
    "fpmp": fpmpDiscord,
    "fplq": fplqDiscord,
    "version": versionDiscord,
    "np": fmpullDiscord,
    "markov": markovDiscord,
    "slap": slapDiscord,
    "errorTester": errorTester,
    "ready": ready,
    "reinit": reinit,
    "dropDatabase": dropDatabase,
    "set": setSetting,
    "get": getSetting,
}
