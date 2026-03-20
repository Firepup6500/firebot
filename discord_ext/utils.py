# pylint: disable=missing-module-docstring,missing-function-docstring
import logging
from discord.ext import commands
from discord.app_commands import describe
from .commands import dataDiscord, callDiscord
from .checks import isReady, isServerOwner, isServerAdmin
from .shared import handler, withTyping

logger = logging.getLogger(__name__)
logger.addHandler(handler)


def registerCommands(bot):
    logger.info("Registering commands")
    for name, func in callDiscord.items():
        logger.debug("Registering command main : %s", name)
        if dataDiscord[name]["owner"]:
            bot.hybrid_command(name=name, description=dataDiscord[name]["desc"])(
                commands.is_owner()(
                    isReady()(
                        describe(**dataDiscord[name]["params"])(withTyping()(func))
                    )
                )
            )
            for _, alias in enumerate(dataDiscord[name]["aliases"]):
                logger.debug("Registering command alias: %s", alias)
                bot.hybrid_command(name=alias, description=dataDiscord[name]["desc"])(
                    commands.is_owner()(
                        isReady()(
                            describe(**dataDiscord[name]["params"])(withTyping()(func))
                        )
                    )
                )
        elif dataDiscord[name]["server_owner"]:
            bot.hybrid_command(name=name, description=dataDiscord[name]["desc"])(
                isServerOwner()(
                    isReady()(
                        describe(**dataDiscord[name]["params"])(withTyping()(func))
                    )
                )
            )
            for _, alias in enumerate(dataDiscord[name]["aliases"]):
                logger.debug("Registering command alias: %s", alias)
                bot.hybrid_command(name=alias, description=dataDiscord[name]["desc"])(
                    isServerOwner()(
                        isReady()(
                            describe(**dataDiscord[name]["params"])(withTyping()(func))
                        )
                    )
                )
        elif dataDiscord[name]["server_admin"]:
            bot.hybrid_command(name=name, description=dataDiscord[name]["desc"])(
                isServerAdmin()(
                    isReady()(
                        describe(**dataDiscord[name]["params"])(withTyping()(func))
                    )
                )
            )
            for _, alias in enumerate(dataDiscord[name]["aliases"]):
                logger.debug("Registering command alias: %s", alias)
                bot.hybrid_command(name=alias, description=dataDiscord[name]["desc"])(
                    isServerAdmin()(
                        isReady()(
                            describe(**dataDiscord[name]["params"])(withTyping()(func))
                        )
                    )
                )
        else:
            bot.hybrid_command(name=name, description=dataDiscord[name]["desc"])(
                isReady()(describe(**dataDiscord[name]["params"])(withTyping()(func)))
            )
            for _, alias in enumerate(dataDiscord[name]["aliases"]):
                logger.debug("Registering command alias: %s", alias)
                bot.hybrid_command(name=alias, description=dataDiscord[name]["desc"])(
                    isReady()(
                        describe(**dataDiscord[name]["params"])(withTyping()(func))
                    )
                )
    logger.info("Registered commands")


def deregisterCommands(bot):
    logger.info("Deregistering commands")
    for name in callDiscord:
        if bot.get_command(name):
            logger.debug("Deregistering command main : %s", name)
            bot.remove_command(name)
        for _, alias in enumerate(dataDiscord[name]["aliases"]):
            if bot.get_command(alias):
                logger.debug("Deregistering command alias: %s", alias)
                bot.remove_command(alias)
    logger.info("Deregistered commands")
