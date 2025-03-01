# bot.py 🎉 V1.0.0
import os
import discord
from discord.ext import commands, tasks
import logging
import asyncio
import random
import aiohttp
import traceback

# Custom bot class to include session
class CustomBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: aiohttp.ClientSession = None

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()

    async def close(self):
        await self.session.close()
        await super().close()
        logger.info("Bot session closed.")

# Load environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[
                        logging.FileHandler("bot.log", encoding='utf-8'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Define bot intents
intents = discord.Intents.all()

# Create bot instance
bot = CustomBot(command_prefix="!", intents=intents, help_command=None)

# List of statuses to cycle through
statuses = [
    discord.Game("with the code"),
    discord.Game("moderating the server"),
    discord.Game("helping users"),
    discord.Activity(type=discord.ActivityType.watching, name="the chat"),
    discord.Activity(type=discord.ActivityType.listening, name="commands"),
    discord.Game("Version 1.0.0 is out soon!")
]

# Function to load cogs
async def load_cogs():
    cogs = ["cogs.whisper", "cogs.owner", "cogs.info"]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logger.info(f"{cog} loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load {cog}: {e}")

# Bot startup event
@bot.event
async def on_ready():
    await load_cogs()
    logger.info(
        f"Bot is online as {bot.user} (ID: {bot.user.id if bot.user else 'Unknown'})"
    )
    if not change_activity.is_running():
        change_activity.start()
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} commands.")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")

# Task to change bot presence
@tasks.loop(seconds=280)
async def change_activity():
    activity = random.choice(statuses)
    await bot.change_presence(activity=activity)
    logger.info(f"Changed bot activity to: {activity.name}")

# Updated help command to send an embed
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Available Commands",
                          description="List of commands you can use:",
                          color=discord.Color.blue())
    embed.add_field(name="/ping",
                    value="Test the bot's responsiveness.",
                    inline=False)
    embed.add_field(name="/uptime",
                    value="Check the bot's uptime.",
                    inline=False)
    embed.add_field(name="/serverinfo",
                    value="Get information about the server.",
                    inline=False)
    embed.add_field(name="/userinfo [user]",
                    value="Get information about a user.",
                    inline=False)
    embed.add_field(name="/botinfo",
                    value="Get information about the bot.",
                    inline=False)
    embed.add_field(
        name="/whisper_admin",
        value="Send a secret message to any channel (admins/mods).",
        inline=False)
    embed.add_field(name="/whisper",
                    value="Send a secret message in this channel.",
                    inline=False)

    logger.info(f"Help command used by {ctx.author}")
    await ctx.send(embed=embed)

# Handle errors and log them
@bot.event
async def on_command_error(ctx, error):
    command_name = ctx.command.name if ctx.command else "Unknown"
    logger.error(f"Error in command '{command_name}': {error}\n{traceback.format_exc()}")
    await ctx.send(f"⚠️ An error occurred: {error}")

# Create an aiohttp session in main()
async def main():
    if DISCORD_TOKEN:
        try:
            logger.info("Starting bot...")
            await bot.start(DISCORD_TOKEN)
        except Exception as e:
            logger.critical(f"Error running bot: {e}")
    else:
        logger.critical(
            "No token found. Set DISCORD_TOKEN in your environment variables."
        )

if __name__ == "__main__":
    asyncio.run(main())
