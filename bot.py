# bot.py 🎉 V1.4.0
import os
import discord
from discord import app_commands
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
        self.tree.add_command(help_command)  # Register help command properly

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
@bot.tree.command(name="help", description="Current Available Commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="Available Commands", color=discord.Color.blue())
    commands_list = [
        {"name": "admin_whisper", "description": "Send a secret message to a specified channel (admins/mods)."},
        {"name": "whisper", "description": "Send a secret message in this channel."},
        {"name": "ping", "description": "Check the bot's latency."},
        {"name": "uptime", "description": "Check the bot's uptime."},
        {"name": "serverinfo", "description": "Get information about the server."},
        {"name": "userinfo", "description": "Get information about a user."},
        {"name": "help", "description": "Display this help message."},
    ]
    for command in commands_list:
        embed.add_field(name=f"/{command['name']}", value=command['description'], inline=False)

    await interaction.response.send_message(embed=embed)

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
