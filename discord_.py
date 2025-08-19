# pylint: disable=missing-module-docstring,missing-function-docstring
from os import environ as env
from importlib import reload
import logging, warnings, sys
import discord
from discord.ext.commands import Bot, is_owner, Context
from dotenv import load_dotenv
from fpsql.asyncio import sql as asyncSql
import config as conf
import utils as global_utils
from markov import MarkovBot
from discord_ext import checks
from discord_ext import events
from discord_ext import exceptions
from discord_ext import utils
from discord_ext import shared
from discord_ext import commands

load_dotenv()

warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"discord\..*")
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
bot.database = asyncSql("discord-data.db")


async def maybe_defer(ctx: Context):
    if (
        ctx.interaction
        and not ctx.interaction.response.is_done()
        and not ctx.command_failed
    ):
        await ctx.interaction.response.defer()


bot.before_invoke(maybe_defer)

events.register_events(bot, env)
utils.register_commands(bot)


@bot.hybrid_command(
    name="reload", description="Owners only - hot reload the bot from disk"
)
@is_owner()
@checks.is_ready()
@shared.with_typing()
async def rel(ctx: Context):
    logger.info("Reloading")
    # pylint: disable=broad-exception-caught
    bot.init = False
    try:
        reload(conf)
        reload(global_utils)
        reload(exceptions)
        reload(checks)
        reload(commands)
        reload(events)
        reload(utils)
        logger.debug("Reloaded components")
        bot.__version__ = conf.__version__
        bot.lastfmLink = conf.lastfmLink
        events.register_events(bot, env)
        utils.deregister_commands(bot)
        utils.register_commands(bot)
        logger.debug("Syncing commands")
        await bot.tree.sync()
        bot.init = True
        logger.info("Reloaded")
        await ctx.send("Reloaded")
    except Exception:
        bot.init = True
        await ctx.send("Error during reload")
        logger.error("Failed to reload", exc_info=True)


if __name__ == "__main__":
    bot.run(env["DISCORD_TOKEN"], log_handler=None)
    logger.error("Recieved ^C, cleaning up asyncio before ternmination")
    loop = conf.loop
    if not loop.is_closed():
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
    logger.error("Terminating.")
    sys.exit(0)
