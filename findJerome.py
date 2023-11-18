
import discord
from discord.ext import commands

class ScoreboardEmbed(discord.Embed):
    def __init__(self, bot, found):
        super().__init__(
            title="Scoreboard",
            url = None,
            description="Who is winning?! It's every person for themselves! With that being said...here are the scores:", 
            color=0xff8000
        )
        
        images = []
        for user_id, score in found.items():
            user = bot.get_user(user_id)
            if user is None:
                continue
            self.add_field(
                name=user.name, 
                value=f"Score: {score['score']}",
                inline=False
            )
            if score["image"] is not None:
                images.append(score["image"][-1])

        if len(images) > 0:
            self.add_field(
                name="Last Found",
                value="",
                inline=False
            )
            self.set_image(url=images[-1])


class FindJerome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.found_count = {}

    @commands.hybrid_command(name="score" , help="Shows the scoreboard for everyone who has found Jerome", with_app_command=True)
    async def getScoreBoard(self, ctx):
        embed = ScoreboardEmbed(self.bot, self.found_count)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="found", help="Found Jerome! Increases your score by 1", with_app_command=True)
    async def found(self, ctx, image: discord.Attachment):
        user = ctx.author
        if user.id not in self.found_count:
            self.found_count[user.id] = {"score": 0, "image": []}
        self.found_count[user.id]["score"] += 1
        self.found_count[user.id]["image"].append(image)
        
        await ctx.send(f"{user.name} has found Jerome {self.found_count[user.id]['score']} times!")
