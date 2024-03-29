# bot.py
import asyncio
import os
from discord import Intents
from discord.ext import commands
from discord.ext.commands import CommandNotFound

from dotenv import load_dotenv
from debugUtils import print_to_c

from findJerome import FindJerome


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

findJerome = FindJerome(bot)


@bot.event
async def on_ready():
    await bot.add_cog(findJerome)
    print_to_c("EVENT", f"{bot.user.name} has connected to Discord!")
    await bot.tree.sync()


@bot.event
async def on_command_error(ctx, error):
    """
    If the command is not found, send a message to the user saying that the command is not available.

    :param ctx: The context of where the command was used
    :param error: The error that was raised
    """
    if isinstance(error, CommandNotFound):
        await print_to_c("ERROR", f"Command not found: {ctx.message.content} in {ctx.message.channel} by {ctx.message.author}")


try:
    bot.run(TOKEN)
finally:
    findJerome.sync()
