import discord
from discord import Interaction
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

bot = commands.Bot(command_prefix="?", intents=discord.Intents.all())

load_dotenv(".env")
BOT_TOKEN = os.getenv("TESTBOT_TOKEN")

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        synced_cmds = await bot.tree.sync()
        print(f"Sycned {len(synced_cmds)} Commands")
    except Exception as e:
        print("Error in syncing commands", e)

@bot.tree.command(name="ping",description="Sends the bots latency")
async def ping(interaction: Interaction):
    await interaction.response.send_message(f"Ping {round(bot.latency*1000)} ms")  

@bot.command(name="sync", description="Syncs slash commands")
@commands.is_owner()
async def sync(ctx):
    print("in sync")
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} command(s)")
    except Exception as e:
        await ctx.send(f"An error occurred while syncing commands: {e}")

async def load():
    ## LOADS THE COGS
    for filename in os.listdir('cogs'):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    ## LOADS COGS
    ## RUNS BOT
    async with bot:
        await load()
        await bot.start(BOT_TOKEN)


asyncio.run(main())