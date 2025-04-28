# pylint: disable=missing-module-docstring,missing-function-docstring
from os import environ as env
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
# intents.guild_members = True
bot = commands.Bot(command_prefix=".", intents=intents)
# print(dir(bot))


@bot.hybrid_command()
async def ping(ctx):
    "Pingy Pongy"
    await ctx.send("pong")


@bot.hybrid_command()
@commands.is_owner()
async def owner_test(ctx):
    "Woag owner only stuff"
    await ctx.send("Hai owner!")


@owner_test.error
async def owner_test_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You're not my owner!")


@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Ready!")


bot.run(env["DISCORD_TOKEN"])
print()
