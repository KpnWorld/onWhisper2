import os
import discord
from discord.ext import commands, tasks
import logging
import asyncio
import random
import aiohttp
import traceback

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


DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[
                        logging.FileHandler("bot.log", encoding='utf-8'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

intents = discord.Intents.all()

bot = CustomBot(command_prefix="!", intents=intents, help_command=None)

statuses = [
    discord.Game("with the code"),
    discord.Game("moderating the server"),
    discord.Game("helping users"),
    discord.Activity(type=discord.ActivityType.watching, name="the chat"),
    discord.Activity(type=discord.ActivityType.listening, name="commands"),
    discord.Game("Version 1.0.0 is out now!")
]

async def load_cogs():
    cogs = ["cogs.whisper", "cogs.owner", "cogs.info", "cogs.help"]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logger.info(f"{cog} loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load {cog}: {e}")

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

@tasks.loop(seconds=280)
async def change_activity():
    activity = random.choice(statuses)
    await bot.change_presence(activity=activity)
    logger.info(f"Changed bot activity to: {activity.name}")


@bot.event
async def on_command_error(ctx, error):
    command_name = ctx.command.name if ctx.command else "Unknown"
    logger.error(f"Error in command '{command_name}': {error}\n{traceback.format_exc()}")
    await ctx.send(f"⚠️ An error occurred: {error}")

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