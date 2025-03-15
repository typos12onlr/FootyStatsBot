import discord
from discord import app_commands
from discord.ext import commands
import asyncpraw as praw
from random import choice
from dotenv import load_dotenv
import os

load_dotenv(".env")
SECRET = os.getenv("REDDIT_API_KEY")


class Reddit(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.reddit = praw.Reddit(client_id="8GCZU-u1z6eh8iDUuYJWoA",
                                  client_secret=SECRET,
                                  user_agent="script:randommemegen:v1.0 (by u/typos_onlr)")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is ready")

    @app_commands.command(name="meme", description="generates random meme from reddit")
    async def meme(self, interaction: discord.Interaction):

        print("in meme command")
        subreddit = await self.reddit.subreddit("memes")

        posts_list = []
        print("Fetching posts...")

        # Fetch posts first
        submissions = [post async for post in subreddit.hot(limit=10)]  # Increase limit

        for post in submissions:
            print("Checking post:", post.title)  # Debugging print

            if not post.over_18 and post.author and any(post.url.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif"]):
                author_name = post.author.name if post.author else "Unknown"
                posts_list.append((post.url, author_name))

        print("Posts fetched:", len(posts_list))

        if posts_list:
            random_post = choice(posts_list)
            meme_embed = discord.Embed(title="Random Meme", description="Random Meme from Reddit", color=discord.Color.random())
            meme_embed.set_author(name=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar)
            meme_embed.set_image(url=random_post[0])
            meme_embed.set_footer(text=f"Post created by {random_post[1]}")

            await interaction.response.send_message(embed=meme_embed)
        else:
            await interaction.response.send_message("Unable to fetch a random meme.")

    def cog_unload(self):
        self.bot.loop.create_task(self.reddit.close())

async def setup(bot):
    await bot.add_cog(Reddit(bot))
