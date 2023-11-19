import io
import json
import deprecation
import aiohttp
import discord
from discord.ext import commands

class ScoreboardEmbed(discord.Embed):
    def __init__(self, bot, found):
        super().__init__(
            title="Scoreboard",
            url=None,
            description="Who is winning?! It's every person for themselves! With that being said...here are the scores:",
            color=0xff8000
        )

    @classmethod
    async def create(cls, bot, ctx, found):
        self = ScoreboardEmbed(bot, found)
        images = []
        foundUser = ""
        for data in found.values():
            self.user = await self.getUser(bot, ctx, data["user"])
            if self.user is None:
                continue
            self.add_field(
                name=self.user,
                value=f"Score: {data['score']}",
                inline=False
            )
        for data in found.values():
            for image in data["image"]:
                images.append(image)

        if len(images) > 0:
            self.add_field(
                name=f"Last Found | {await self.getUser(bot, ctx, ctx.author.id)}",
                value="",
                inline=False
            )
            self.set_image(url=images[-1])

        return self

    async def getUser(self, bot, ctx, user_id):
        guild = bot.get_guild(ctx.guild.id)
        member = await guild.fetch_member(user_id)
        if member.nick is None:
            return member.name
        return member.nick


class JustFoundEmbed(discord.Embed):
    def __init__(self, bot, found):
        super().__init__(
            title="Scoreboard",
            url=None,
            description="Who's the bestest jerome finder?! :eyes:",
            color=0xff8000
        )

    @classmethod
    async def create(cls, bot, ctx, found):
        self = JustFoundEmbed(bot, found)
        images = []
        for data in found.values():
            self.user = await self.getUser(bot, ctx, data["user"])
            if self.user is None:
                continue
            self.add_field(
                name=self.user,
                value=f"Score: {data['score']}",
                inline=False
            )
            
        for data in found.values():
            for image in data["image"]:
                images.append(image)

        if len(images) > 0:
            self.add_field(
                name=f"Last Found | {await self.getUser(bot, ctx, ctx.author.id)}",
                value="",
                inline=False
            )
            self.set_image(url=images[-1])

        return self

    async def getUser(self, bot, ctx, user_id):
        guild = bot.get_guild(ctx.guild.id)
        member = await guild.fetch_member(user_id)
        if member.nick is None:
            return member.name
        return member.nick


class FindJerome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.found_count = self.load_from_file()

    @commands.hybrid_command(name="gallery", help="Shows the gallery of everyone who has found Jerome")
    async def getGallery(self, ctx, limit=-1):
        """
        Shows the gallery of everyone who has found Jerome by sending image URLs
        with aiohttp
        <p>
        Parameters:
        - ctx (discord.Context): The context object representing the invocation of the command.
        - limit (int): The maximum number of images to send.
        """
        discord_files = []
        count = 0
        for data in self.found_count.values():  # changed this line
            for image_url in reversed(data["image"]):
                if (limit != -1 and count >= limit):
                    break
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as resp:
                        if resp.status != 200:
                            print(f"Could not download image {image_url}")
                            continue  # Skip this image if the download failed
                        image_data = await resp.read()
                discord_files.append(discord.File(io.BytesIO(image_data), filename=f"{data['user']}_{data['score']}.png"))
                count += 1
                if len(discord_files) == 10:
                    await ctx.send(files=discord_files)
                    discord_files = []
        if discord_files:  # Send any remaining files
            await ctx.send(files=discord_files)
            discord_files = []

    @commands.hybrid_command(name="score", help="Shows the scoreboard for everyone who has found Jerome")
    async def getScoreBoard(self, ctx):
        embed = await ScoreboardEmbed.create(self.bot, ctx, self.found_count)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="found", help="Found Jerome! Increases your score by 1")
    async def found(self, ctx, image: discord.Attachment):
        """
        Increments the score and stores the image attachment when a user finds Jerome.
        <p>
        Parameters:
        - ctx (discord.Context): The context object representing the invocation of the command.
        - image (discord.Attachment): The image attachment submitted by the user.
        """
        user = ctx.author
        user_id_str = str(user.id)
        if user_id_str not in self.found_count:
            self.found_count[user_id_str] = {"score": 0, "image": [], "user": user_id_str}
        self.found_count[user_id_str]["score"] += 1
        self.found_count[user_id_str]["image"].append(image.url)
        embed = await JustFoundEmbed.create(self.bot, ctx, self.found_count)
        await ctx.send(embed=embed)

    def sync(self):
        """
        Syncs the scoreboard with the file.
        """
        with open("found.json", "w") as f:
            json.dump({"inputs": list(self.found_count.values())}, f)

    def load_from_file(self):
        """
        Loads the scoreboard from the file.
        """
        try:
            with open("found.json", "r") as f:
                data = json.load(f)
                found_count = {}
                for item in data.get("inputs", []):
                    found_count[item["user"]] = item
                return found_count
        except FileNotFoundError:
            return {}

