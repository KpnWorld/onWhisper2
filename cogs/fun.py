import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import aiohttp
import logging


# Set up logging for the Fun Cog
logger = logging.getLogger(__name__)

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Rolls a dice in NdN format.")
    async def roll(self, interaction: discord.Interaction, dice: str):
        try:
            rolls, limit = map(int, dice.lower().split('d'))
            if rolls <= 0 or limit <= 0:
                raise ValueError  # Prevent negative or zero values
        except ValueError:
            await interaction.response.send_message("❌ Format must be `NdN` (e.g., `2d6`).", ephemeral=True)
            return

        results = ', '.join(str(random.randint(1, limit)) for _ in range(rolls))
        embed = discord.Embed(title="🎲 Dice Roll", description=f"{interaction.user.mention}, you rolled: **{results}**", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="choose", description="Chooses between multiple choices.")
    async def choose(self, interaction: discord.Interaction, choices: str):
        options = [choice.strip() for choice in choices.split(",") if choice.strip()]
        if len(options) < 2:
            await interaction.response.send_message("❌ Provide at least two choices, separated by commas.", ephemeral=True)
            return

        selected = random.choice(options)
        embed = discord.Embed(title="🎯 Choice", description=f"{interaction.user.mention}, I choose: **{selected}**", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Flips a coin.")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["Heads", "Tails"])
        embed = discord.Embed(title="🪙 Coin Flip", description=f"{interaction.user.mention}, it's **{result}**!", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rps", description="Plays rock-paper-scissors.")
    async def rps(self, interaction: discord.Interaction, choice: str):
        choices = ["rock", "paper", "scissors"]
        user_choice = choice.lower().strip()

        if user_choice not in choices:
            await interaction.response.send_message("❌ Choose either 'rock', 'paper', or 'scissors'.", ephemeral=True)
            return

        bot_choice = random.choice(choices)
        if user_choice == bot_choice:
            result = "It's a tie!"
        elif (user_choice == "rock" and bot_choice == "scissors") or (user_choice == "paper" and bot_choice == "rock") or (user_choice == "scissors" and bot_choice == "paper"):
            result = "You win! 🎉"
        else:
            result = "I win! 😈"

        embed = discord.Embed(title="🗿 Rock-Paper-Scissors", description=f"{interaction.user.mention}, you chose: **{user_choice}**\n🤖 I chose: **{bot_choice}**\n🏆 {result}", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="joke", description="Tell a random joke.")
    async def joke(self, interaction: discord.Interaction):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://official-joke-api.appspot.com/random_joke") as response:
                    if response.status == 200:
                        joke_data = await response.json()
                        joke = f"{joke_data['setup']} - {joke_data['punchline']}"
                    else:
                        joke = f"❌ Failed to fetch a joke. API error {response.status}."
        except Exception as e:
            logger.error(f"❌ Error fetching joke: {e}")
            joke = f"❌ Error fetching joke: {e}"

        embed = discord.Embed(title="😂 Joke", description=f"{interaction.user.mention}, here's a joke for you: {joke}", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="countdown", description="Start a countdown timer.")
    async def countdown(self, interaction: discord.Interaction, seconds: int):
        if seconds < 1 or seconds > 3600:
            await interaction.response.send_message("❌ Please enter a time between 1 and 3600 seconds.", ephemeral=True)
            return

        await interaction.response.defer()
        message = await interaction.followup.send(f"⏳ {interaction.user.mention}, countdown started for {seconds} seconds...")

        while seconds > 0:
            await asyncio.sleep(1)
            seconds -= 1
            if seconds % 10 == 0 or seconds <= 5:  # Update every 10 seconds, and last 5 seconds
                await message.edit(content=f"⏳ {interaction.user.mention}, {seconds} seconds remaining...")

        await message.edit(content=f"🎉 {interaction.user.mention}, countdown has ended!")

    
async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))

