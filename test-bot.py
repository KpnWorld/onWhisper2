import os

# Check if the bot is running from the test branch
IS_TEST = os.getenv("GITHUB_REF") == "refs/heads/test-bot"

TOKEN = os.getenv("TEST_BOT_TOKEN") if IS_TEST else os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("Bot token is missing!")

# Run the bot
import discord
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (Test Mode: {IS_TEST})")

bot.run(TOKEN)
