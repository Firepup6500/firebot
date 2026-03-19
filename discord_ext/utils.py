# pylint: disable=missing-module-docstring,missing-function-docstring
import logging
from discord.ext import commands
from discord.app_commands import describe
from .commands import data_discord, call_discord
from .checks import isReady, isServerOwner, isServerAdmin
from .shared import handler, withTyping

logger = logging.getLogger(__name__)
logger.addHandler(handler)


def registerCommands(bot):
    logger.info("Registering commands")
    for name, func in call_discord.items():
        logger.debug("Registering command main : %s", name)
        if data_discord[name]["owner"]:
            bot.hybrid_command(name=name, description=data_discord[name]["desc"])(
                commands.is_owner()(
                    isReady()(
                        describe(**data_discord[name]["params"])(withTyping()(func))
                    )
                )
            )
            for _, alias in enumerate(data_discord[name]["aliases"]):
                logger.debug("Registering command alias: %s", alias)
                bot.hybrid_command(name=alias, description=data_discord[name]["desc"])(
                    commands.is_owner()(
                        isReady()(
                            describe(**data_discord[name]["params"])(
                                withTyping()(func)
                            )
                        )
                    )
                )
        elif data_discord[name]["server_owner"]:
            bot.hybrid_command(name=name, description=data_discord[name]["desc"])(
                isServerOwner()(
                    isReady()(
                        describe(**data_discord[name]["params"])(withTyping()(func))
                    )
                )
            )
            for _, alias in enumerate(data_discord[name]["aliases"]):
                logger.debug("Registering command alias: %s", alias)
                bot.hybrid_command(name=alias, description=data_discord[name]["desc"])(
                    isServerOwner()(
                        isReady()(
                            describe(**data_discord[name]["params"])(
                                withTyping()(func)
                            )
                        )
                    )
                )
        elif data_discord[name]["server_admin"]:
            bot.hybrid_command(name=name, description=data_discord[name]["desc"])(
                isServerAdmin()(
                    isReady()(
                        describe(**data_discord[name]["params"])(withTyping()(func))
                    )
                )
            )
            for _, alias in enumerate(data_discord[name]["aliases"]):
                logger.debug("Registering command alias: %s", alias)
                bot.hybrid_command(name=alias, description=data_discord[name]["desc"])(
                    isServerAdmin()(
                        isReady()(
                            describe(**data_discord[name]["params"])(
                                withTyping()(func)
                            )
                        )
                    )
                )
        else:
            bot.hybrid_command(name=name, description=data_discord[name]["desc"])(
                isReady()(
                    describe(**data_discord[name]["params"])(withTyping()(func))
                )
            )
            for _, alias in enumerate(data_discord[name]["aliases"]):
                logger.debug("Registering command alias: %s", alias)
                bot.hybrid_command(name=alias, description=data_discord[name]["desc"])(
                    isReady()(
                        describe(**data_discord[name]["params"])(withTyping()(func))
                    )
                )
    logger.info("Registered commands")


def deregisterCommands(bot):
    logger.info("Deregistering commands")
    for name in call_discord:
        if bot.get_command(name):
            logger.debug("Deregistering command main : %s", name)
            bot.remove_command(name)
        for _, alias in enumerate(data_discord[name]["aliases"]):
            if bot.get_command(alias):
                logger.debug("Deregistering command alias: %s", alias)
                bot.remove_command(alias)
    logger.info("Deregistered commands")
