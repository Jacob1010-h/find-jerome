# bot.py
import asyncio
import os

from discord import Intents
from discord.ext import commands

from dotenv import load_dotenv

from findJerome import FindJerome


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

findJerome = FindJerome(bot)

@bot.event
async def on_ready():
    await bot.add_cog(findJerome)
    print(f'{bot.user.name} has connected to Discord!')
    await bot.tree.sync()

# if admin
@bot.hybrid_command(name='clear', help='Clears the chat of n messages')
@commands.has_permissions(administrator=True)
async def clear(ctx, amount=5):
    await ctx.send(f'{amount} messages have been deleted.')
    await asyncio.sleep(1)
    await ctx.channel.purge(limit=amount+1)

try:
    bot.run(TOKEN)
finally:
    findJerome.sync()