# bot.py
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

@bot.hybrid_command(name='clear', help='Clears the chat of n messages', with_app_command=True)
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)

@bot.hybrid_command(name='test', help='Tests the discord app', with_app_command=True)
async def test(ctx):
    await ctx.send("Hello!! I am Jerome!")


bot.run(TOKEN)