
import discord
from discord.ext import commands

class FindJerome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.found_count = {}

    @commands.hybrid_command(name="score" , help="Shows the scoreboard for everyone who has found Jerome", with_app_command=True)
    async def getScoreBoard(self, ctx):
        embed = discord.Embed(title="Jerome Scoreboard", description="The number of times each person has found Jerome", color=0x00ff00)
        for user_id, count in self.found_count.items():
            user = self.bot.get_user(user_id)
            embed.add_field(name=user.name, value=count, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="found", help="Found Jerome! Increases your score by 1", with_app_command=True)
    async def found(self, ctx):
        user = ctx.author
        if user.id not in self.found_count:
            self.found_count[user.id] = 1
        else:
            self.found_count[user.id] += 1
        
        await ctx.send(f"{user.name} has found it {self.found_count[user.id]} times!")
