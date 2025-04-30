# pylint: disable=missing-module-docstring,missing-function-docstring
from os import environ as env
from importlib import reload
import logging
import traceback, discord
from discord.ext.commands import Bot, is_owner, Context
from dotenv import load_dotenv
import config as conf
from markov import MarkovBot
from discord_ext import checks
from discord_ext import events
from discord_ext import utils
from discord_ext import shared

load_dotenv()


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.getLogger("discord.http").setLevel(logging.INFO)
logging.getLogger("discord.gateway").setLevel(logging.INFO)
logging.getLogger("discord_ext").setLevel(logging.DEBUG)
discord.utils.setup_logging(level=logging.DEBUG, root=False)
bot = Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None)
with open("mastermessages.txt", encoding="utf-8") as f:
    TMFeed = []
    for line in f.readlines():
        TMFeed.extend([line.strip().split()])
    bot.markov = MarkovBot(TMFeed)
bot.init = False
logger.addHandler(shared.handler)
bot.logger = logger
bot.__version__ = conf.__version__
bot.lastfmLink = conf.lastfmLink

events.register_events(bot, env)
utils.register_commands(bot)


@bot.hybrid_command(
    name="reload", description="Owners only - hot reload the bot from disk"
)
@is_owner()
@checks.is_ready()
async def rel(ctx: Context):
    # pylint: disable=broad-exception-caught
    bot.init = False
    try:
        reload(utils)
        reload(checks)
        reload(events)
        reload(conf)
        bot.__version__ = conf.__version__
        bot.lastfmLink = conf.lastfmLink
        events.register_events(bot, env)
        utils.deregister_commands(bot)
        utils.register_commands(bot)
        bot.init = True
        await ctx.send("Reloaded")
    except Exception as E:
        bot.init = True
        await ctx.send("Error during reload")
        logger.error("".join(traceback.format_exception(E)))


bot.run(env["DISCORD_TOKEN"], log_handler=None)
print()
