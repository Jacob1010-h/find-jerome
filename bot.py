# bot.py
import asyncio
from datetime import datetime
import os
from termcolor import colored
from discord import Intents
from discord.ext import commands
from discord.ext.commands import CommandNotFound

from dotenv import load_dotenv

from findJerome import FindJerome


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

async def print_to_c(type, msg):
    """
    It prints a line, the current date and time, the input, another line, and a new line
    
    :param imp: The string to be printed
    """
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(colored(dt_string, 'dark_grey'), end=' ')
    
    if type == "COMMAND":
        print(colored(type + " ", 'cyan'), end=' ')
    elif type == "SYNC":
        print(colored(type + "    ", 'red'), end=' ')
    elif type == "EVENT":
        print(colored(type + "   ", 'yellow'), end=' ')
    elif type == "LOAD":
        print(colored(type + "    ", 'green'), end=' ')
    else:
        print(colored(type + "    ", 'blue'), end=' ')
    
    print(colored("discord.bot", 'magenta'), end=' ')
    print(colored(msg, 'white'))
    
intents = Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

findJerome = FindJerome(bot)

@bot.event
async def on_ready():
    await bot.add_cog(findJerome)
    await print_to_c("EVENT", f'{bot.user.name} has connected to Discord!')
    await bot.tree.sync()

@bot.event
async def on_command_error(ctx, error):
    """
    If the command is not found, send a message to the user saying that the command is not available.
    
    :param ctx: The context of where the command was used
    :param error: The error that was raised
    """
    if isinstance(error, CommandNotFound):
        await ctx.send('This command is not available.')

# if admin
# @bot.hybrid_command(name='clear', help='Clears the chat of n messages')
# @commands.has_permissions(administrator=True)
# async def clear(ctx, amount=0):
#     await ctx.send(f'{amount} messages have been deleted.')
#     await asyncio.sleep(1)
#     await ctx.channel.purge(limit=amount+1)

try:
    bot.run(TOKEN)
finally:
    findJerome.sync()