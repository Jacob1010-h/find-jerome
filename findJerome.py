import io
import json
import aiohttp
import discord
from discord.ext import commands

from debugUtils import print_to_c


class ScoreboardEmbed(discord.Embed):
    def __init__(self, bot, found):
        super().__init__(
            title="Scoreboard",
            url=None,
            description="Who is winning?! It's every person for themselves! With that being said...here are the scores:",
            color=0xFF8000,
        )

    @classmethod
    async def create(cls, bot, ctx, found):
        self = ScoreboardEmbed(bot, found)
        
        print_to_c("INFO", "Creating scoreboard embed")
        
        all_data = []
        images = []
        foundUser = ""
        
        for data in found.values():
            self.user = await self.getUser(bot, ctx, data["user"])
            if self.user is None:
                continue

            # add user and score to all_data to sort later
            all_data.append((self.user, int(data["score"])))

            for image in data["image"]:
                images.append(image)

        # keep the user with the highest score at the top
        all_data.sort(key=lambda a: a[1], reverse=True)

        # add all_data to embed
        for data in all_data:
            self.add_field(name=data[0], value=f"Score: {data[1]}", inline=False)

        for data in found.values():
            for image in data["image"]:
                if image == images[-1]:
                    foundUser = data["user"]

        print_to_c("INFO", "Adding fields to embed")
        if len(images) > 0:
            self.add_field(
                name=f"Last Found | {await self.getUser(bot, ctx, foundUser)}",
                value="",
                inline=False,
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
            color=0xFF8000,
        )

    @classmethod
    async def create(cls, bot, ctx, found):
        self = JustFoundEmbed(bot, found)
        
        print_to_c("INFO", "Creating just found embed")
        
        images = []
        for data in found.values():
            self.user = await self.getUser(bot, ctx, data["user"])
            if self.user is None:
                continue
            self.add_field(
                name=self.user, value=f"Score: {data['score']}", inline=False
            )

        for data in found.values():
            for image in data["image"]:
                images.append(image)

        print_to_c("INFO", "Adding fields to just found embed")
        if len(images) > 0:
            self.add_field(
                name=f"Last Found | {await self.getUser(bot, ctx, ctx.author.id)}",
                value="",
                inline=False,
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

    @commands.hybrid_command(
        name="gallery", help="Shows the gallery of everyone who has found Jerome"
    )
    async def getGallery(self, ctx):
        """
        Shows the gallery of everyone who has found Jerome by sending image URLs
        with aiohttp
        <p>
        Parameters:
        - ctx (discord.Context): The context object representing the invocation of the command.
        """
        discord_files = []
        count = 0
        limit = -1
        await print_to_c("EVENT", f"Gallery requested by {ctx.author}!")
        for data in self.found_count.values():  # changed this line
            for image_url in reversed(data["image"]):
                if limit != -1 and count >= limit:
                    break
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as resp:
                        if resp.status != 200:
                            await print_to_c(
                                "ERROR",
                                f"Could not download image {image_url} for {data['user']}",
                            )
                            continue  # Skip this image if the download failed
                        image_data = await resp.read()
                discord_files.append(
                    discord.File(
                        io.BytesIO(image_data),
                        filename=f"{data['user']}_{data['score']}.png",
                    )
                )
                count += 1
                if len(discord_files) == 10:
                    await ctx.send(files=discord_files)
                    discord_files = []
        if discord_files:  # Send any remaining files
            await ctx.send(files=discord_files)
            discord_files = []

        await print_to_c("COMMAND", f"Gallery has been sent to {ctx.author}!")

    @commands.hybrid_command(
        name="score", help="Shows the scoreboard for everyone who has found Jerome"
    )
    async def getScoreBoard(self, ctx):
        await print_to_c("EVENT", f"Scoreboard requested by {ctx.author}!")
        
        embed = await ScoreboardEmbed.create(self.bot, ctx, self.found_count)
        await ctx.send(embed=embed)

        await print_to_c("COMMAND", f"Scoreboard has been sent to {ctx.author}!")

    @commands.hybrid_command(
        name="found", help="Found Jerome! Increases your score by 1"
    )
    async def found(self, ctx, image: discord.Attachment):
        """
        Increments the score and stores the image attachment when a user finds Jerome.
        <p>
        Parameters:
        - ctx (discord.Context): The context object representing the invocation of the command.
        - image (discord.Attachment): The image attachment submitted by the user.
        """
        await print_to_c("EVENT", f"{ctx.author} has requested to find Jerome!")
        
        user = ctx.author
        user_id_str = str(user.id)
        if user_id_str not in self.found_count:
            self.found_count[user_id_str] = {
                "score": 0,
                "image": [],
                "user": user_id_str,
            }
        self.found_count[user_id_str]["score"] += 1
        self.found_count[user_id_str]["image"].append(image.url)
        embed = await JustFoundEmbed.create(self.bot, ctx, self.found_count)
        await ctx.send(embed=embed)

        await print_to_c("COMMAND", f"{ctx.author} has found Jerome!")

    def sync(self):
        """
        Syncs the scoreboard with the file.
        """
        with open("found.json", "w") as f:
            json.dump({"inputs": list(self.found_count.values())}, f)
            print_to_c("SYNC", "Scoreboard has been synced!")

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
                print_to_c("LOAD", "Scoreboard has been loaded from file!")
                return found_count
        except FileNotFoundError:
            return {}

    @commands.hybrid_command(name="reset", help="Resets the scoreboard")
    @commands.has_permissions(administrator=True)
    async def resetData(self, ctx):
        """
        Resets the scoreboard.
        <p>
        Parameters:
        - ctx (discord.Context): The context object representing the invocation of the command.
        """
        await print_to_c("EVENT", f"Scoreboard reset requested by {ctx.author}!")
        
        self.found_count = {}
        self.sync()
        await ctx.send("Scoreboard has been reset!")

        await print_to_c("COMMAND", f"Scoreboard has been reset by {ctx.author}!")

    @commands.hybrid_command(name="delete", help="Deletes the last found image")
    @commands.has_permissions(administrator=True)
    async def deleteLast(self, ctx, user: discord.Member):
        """
        Deletes the last found image.
        <p>
        Parameters:
        - ctx (discord.Context): The context object representing the invocation of the command.
        """
        await print_to_c( "EVENT", f"Last found image delete requested by {ctx.author}!")
        
        user_id_str = str(user.id)
        if user_id_str not in self.found_count:
            await ctx.send("You haven't found Jerome yet!")
            return
        if len(self.found_count[user_id_str]["image"]) == 0:
            await ctx.send("You haven't found Jerome yet!")
            return
        self.found_count[user_id_str]["image"].pop()
        self.found_count[user_id_str]["score"] -= 1
        await ctx.send("Last found image has been deleted!")
        self.sync()

        await print_to_c("COMMAND", f"Last found image has been deleted by {ctx.author}!")

    @commands.hybrid_command(name="add", help="Adds a user to the scoreboard")
    @commands.has_permissions(administrator=True)
    async def addUser(self, ctx, user: discord.Member, image: str):
        """
        Adds a user to the scoreboard.
        <p>
        Parameters:
        - ctx (discord.Context): The context object representing the invocation of the command.
        - user (discord.Member): The user to add to the scoreboard.
        - score (int): The score of the user.
        - image (str): The image URL of the user.
        """
        await print_to_c("EVENT", f"{user} has been requested to be added to the scoreboard by {ctx.author}!")
        
        user_id_str = str(user.id)
        if user_id_str not in self.found_count:
            self.found_count[user_id_str] = {
                "score": 0,
                "image": [],
                "user": user_id_str,
            }
        self.found_count[user_id_str]["score"] += 1
        self.found_count[user_id_str]["image"].append(image)
        self.sync()
        await ctx.send(f"Added {user} to the scoreboard!")

        await print_to_c(
            "COMMAND", f"{user} has been added to the scoreboard by {ctx.author}!"
        )
