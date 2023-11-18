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

@bot.event
async def on_ready():
    await bot.add_cog(FindJerome(bot))
    print(f'{bot.user.name} has connected to Discord!')
    await bot.tree.sync()

# if admin
@bot.hybrid_command(name='clear', help='Clears the chat of n messages', with_app_command=True)
@commands.has_permissions(administrator=True)
async def clear(ctx, amount=5):
    await ctx.send(f'{amount} messages have been deleted.')
    await asyncio.sleep(2)
    await ctx.channel.purge(limit=amount)
    await ctx.channel.purge(limit=1)

bot.run(TOKEN)