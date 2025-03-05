# cogs/whisper.py 🎉 V1.0.0

```
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import logging
import re

logger = logging.getLogger(__name__)

class Whisper(commands.Cog):
    """Cog for whisper commands."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info("Whisper cog initialized.")

    @app_commands.command(name="admin_whisper", description="Send a secret message to a specified channel (admins/mods).")
    @app_commands.describe(channel="The channel to send the whisper to")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def admin_whisper(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Command to send a whisper to a specified channel."""
        try:
            # Pass the chosen channel's ID to the modal.
            await interaction.response.send_modal(WhisperModal(self.bot, channel_select=False, default_channel=channel.id))
        except Exception as err:
            logger.error("[Whisper] Unexpected error: %s", err)
            await interaction.response.send_message("❌ Could not open whisper modal.", ephemeral=True)

    @app_commands.command(name="whisper", description="Send a secret message in this channel.")
    async def whisper(self, interaction: discord.Interaction):
        """Command to send a whisper in the current channel."""
        try:
            await interaction.response.send_modal(WhisperModal(self.bot, channel_select=False, default_channel=interaction.channel.id))
        except Exception as err:
            logger.error("[Whisper] Unexpected error: %s", err)
            await interaction.response.send_message("❌ Could not open whisper modal.", ephemeral=True)

class WhisperModal(discord.ui.Modal):
    """Modal for sending a whisper message."""
    def __init__(self, bot: commands.Bot, channel_select: bool = True, default_channel: int = None):
        # The modal title remains the same.
        super().__init__(title="Send a Whisper")
        self.bot = bot
        self.channel_select = channel_select
        self.default_channel = default_channel  # ID of the channel chosen before submission

    message = discord.ui.TextInput(
        label="Secret Message",
        placeholder="Enter your whisper... You can @mention someone.",
        max_length=200
    )
    duration = discord.ui.TextInput(
        label="Delete After (Seconds)",
        placeholder="e.g., 10",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        """Callback for when the modal is submitted."""
        try:
            if not interaction.guild:
                await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
                return

            await interaction.response.defer(ephemeral=True)
            delete_after = int(self.duration.value)
            if delete_after < 1 or delete_after > 3600:
                raise ValueError("Invalid duration")

            # If channel selection is not needed, use the default channel.
            channel = self.bot.get_channel(self.default_channel)
            if not isinstance(channel, discord.TextChannel):
                await interaction.followup.send("❌ The selected channel is invalid.", ephemeral=True)
                return

            await self.send_whisper(interaction, channel, self.message.value, delete_after)
        except ValueError:
            await interaction.followup.send("⚠️ Invalid duration. Please enter a number between 1 and 3600.", ephemeral=True)
            logger.warning("[WhisperModal] Invalid duration entered: %s", self.duration.value)
        except Exception as err:
            logger.error("[WhisperModal] Unexpected error: %s", err)
            await interaction.followup.send("❌ Something went wrong.", ephemeral=True)

    async def send_whisper(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str, delete_after: int):
        """Sends a whisper message to the specified channel."""
        try:
            # Check bot permissions in the channel.
            guild = interaction.guild
            bot_member = guild.get_member(self.bot.user.id)
            if not bot_member or not channel.permissions_for(bot_member).send_messages:
                await interaction.followup.send("❌ I don't have permission to send messages in the selected channel.", ephemeral=True)
                return

            msg = await channel.send(f"💬 **Secret Message:** {message}")
            logger.info("[WhisperModal] Whisper sent to #%s: %s", channel.name, message)
            if delete_after > 0:
                await asyncio.sleep(delete_after)
                try:
                    await msg.delete()
                    logger.info("[WhisperModal] Whisper deleted in #%s after %s seconds.", channel.name, delete_after)
                except Exception as e:
                    logger.error("[WhisperModal] Failed to delete whisper in #%s: %s", channel.name, e)
            await interaction.followup.send("✅ Whisper sent!", ephemeral=True)
        except Exception as err:
            logger.error("[WhisperModal] Failed to send whisper: %s", err)
            await interaction.followup.send("❌ Failed to send the whisper message.", ephemeral=True)

async def setup(bot: commands.Bot):
    """Adds the Whisper cog to the bot."""
    await bot.add_cog(Whisper(bot))


```
# cogs/owner.py 🎉V1.0.0
```
import os
import discord
import asyncio
import logging
from discord import app_commands
from discord.ext import commands
from bot import change_activity 
import sys

owner_id = int(os.environ.get('OWNER_ID', 0))

logger = logging.getLogger(__name__)

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()

    async def is_owner(self, interaction: discord.Interaction):
        """Checks if the command user is the bot owner"""
        return interaction.user.id == owner_id

    async def send_unauthorized_response(self, interaction: discord.Interaction):
        """Sends an unauthorized response to the user"""
        embed = discord.Embed(title="🔒 Unauthorized", description="You are not authorized to use this command.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="set_status", description="Set a custom bot status.")
    async def set_status(self, interaction: discord.Interaction, *, status: str):
        """Sets a custom status for the bot and pauses the status loop"""
        if await self.is_owner(interaction):
            await self.bot.change_presence(activity=discord.Game(name=status))
            logger.info(f"Custom status set by {interaction.user}: {status}")
            change_activity.stop() 

            embed = discord.Embed(title="✅ Status Updated", 
                                  description=f"Custom status set to: `{status}`", 
                                  color=discord.Color.green())
            await interaction.response.send_message(embed=embed)
        else:
            await self.send_unauthorized_response(interaction)

    @app_commands.command(name="delete_status", description="Remove custom status and resume normal activity.")
    async def delete_status(self, interaction: discord.Interaction):
        """Removes custom status and resumes normal activity change"""
        if await self.is_owner(interaction):
            await self.bot.change_presence(activity=None)
            change_activity.start() 

            logger.info(f"Custom status deleted by {interaction.user}. Resuming normal activity change.")
            embed = discord.Embed(title="🔄 Status Cleared", 
                                  description="Custom status cleared. Resuming normal status changes.", 
                                  color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)
        else:
            await self.send_unauthorized_response(interaction)

    @app_commands.command(name="restart", description="Restart the bot.")
    async def restart(self, interaction: discord.Interaction):
        """Restarts the bot"""
        if await self.is_owner(interaction):
            async with self.lock:
                logger.info(f"Bot restart command received by {interaction.user}")
                embed = discord.Embed(title="🔄 Restarting Bot", 
                                      description="The bot is restarting...", 
                                      color=discord.Color.orange())
                await interaction.response.send_message(embed=embed)


                python = sys.executable
                os.execl(python, python, *sys.argv)  
        else:
            await self.send_unauthorized_response(interaction)

    @app_commands.command(name="shutdown", description="Shut down the bot.")
    async def shutdown(self, interaction: discord.Interaction):
        """Shuts down the bot"""
        if await self.is_owner(interaction):
            logger.info(f"Bot shutdown command received by {interaction.user}")
            embed = discord.Embed(title="🔒 Shutting Down", 
                                  description="Shutting down...", 
                                  color=discord.Color.orange())
            await interaction.response.send_message(embed=embed)
            await self.bot.close()
        else:
            await self.send_unauthorized_response(interaction)

async def setup(bot):
    await bot.add_cog(Owner(bot))
```
# cogs/info.py 🎉 V1.0.0
```
import discord
from discord.ext import commands
from discord import app_commands
import time
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.start_time = time.time()  # Store bot start time
        logger.info("Info cog initialized.")

    @app_commands.command(name="ping", description="Check the bot's latency.")
    @commands.cooldown(1, 5, commands.BucketType.user)  # Prevent spamming
    async def ping(self, interaction: discord.Interaction):
        try:
            start_time = time.time()
            await interaction.response.send_message("Pinging...")
            end_time = time.time()
            latency = round((end_time - start_time) * 1000, 2)

            embed = discord.Embed(title="Pong!", description=f"Latency: {latency}ms", color=discord.Color.green())
            await interaction.followup.send(embed=embed)
            logger.info(f"Ping command used by {interaction.user}")
        except Exception as e:
            logger.error(f"Error in ping command: {e}")
            await interaction.response.send_message("An error occurred while processing your request.")

    @app_commands.command(name="uptime", description="Check the bot's uptime.")
    @commands.cooldown(1, 10, commands.BucketType.user)  # Prevent spamming
    async def uptime(self, interaction: discord.Interaction):
        try:
            uptime_seconds = round(time.time() - self.bot.start_time, 2)
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            seconds = int(uptime_seconds % 60)

            # Improved human-readable format
            uptime_str = f"{hours} hours, {minutes} minutes, and {seconds} seconds" if hours else f"{minutes} minutes and {seconds} seconds"

            embed = discord.Embed(title="Bot Uptime", 
                                  description=f"Bot has been running for {uptime_str}.", 
                                  color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)
            logger.info(f"Uptime command used by {interaction.user}")
        except Exception as e:
            logger.error(f"Error in uptime command: {e}")
            await interaction.response.send_message("An error occurred while processing your request.")

    @app_commands.command(name="serverinfo", description="Get information about the server.")
    async def serverinfo(self, interaction: discord.Interaction):
        try:
            guild = interaction.guild
            if guild is None:
                await interaction.response.send_message("This command can only be used in a server.")
                return

            embed = discord.Embed(
                title=f"Server Information - {guild.name}",
                color=discord.Color.blue()
            )
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            embed.add_field(name="Server ID", value=guild.id, inline=False)
            embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=False)
            embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S") if guild.created_at else "Unknown", inline=False)
            embed.add_field(name="Members", value=guild.member_count, inline=False)
            embed.add_field(name="Roles", value=len(guild.roles), inline=False)
            embed.add_field(name="Channels", value=len(guild.channels), inline=False)
            await interaction.response.send_message(embed=embed)
            logger.info(f"Server info command used by {interaction.user}")
        except Exception as e:
            logger.error(f"Error in serverinfo command: {e}")
            await interaction.response.send_message("An error occurred while processing your request.")

    @app_commands.command(name="userinfo", description="Get information about a user.")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        try:
            user = user or interaction.user
            if user is None:
                await interaction.response.send_message("Could not find the user.")
                return

            embed = discord.Embed(
                title=f"User Information - {user.name}",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.add_field(name="User ID", value=user.id, inline=False)
            embed.add_field(name="Nickname", value=user.nick or "None", inline=False)
            embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S") if user.joined_at else "Unknown", inline=False)
            embed.add_field(name="Created Account", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "Unknown", inline=False)
            embed.add_field(name="Roles", value=", ".join(role.mention for role in user.roles[1:]) or "None", inline=False)
            await interaction.response.send_message(embed=embed)
            logger.info(f"User info command used by {interaction.user}")
        except Exception as e:
            logger.error(f"Error in userinfo command: {e}")
            await interaction.response.send_message("An error occurred while processing your request.")

    @app_commands.command(name="botinfo", description="Get information about the bot.")
    async def botinfo(self, interaction: discord.Interaction):
        try:
            # Read the version dynamically from a file
            with open("version.txt", "r") as version_file:
                bot_version = version_file.read().strip()

            embed = discord.Embed(
                title="Bot Information",
                color=discord.Color.gold()
            )
            embed.add_field(name="onWhisper", value=self.bot.user.name, inline=False)
            embed.add_field(name="Bot Version", value=bot_version, inline=False)
            embed.add_field(name="Bot Owner", value="@og.kpnworld", inline=False)
            embed.add_field(name="Suport Server", value="https://discord.gg/64bGK2SQpX", inline=False)
            embed.add_field(name="Bot Language", value="Python / discord.py", inline=False)
            await interaction.response.send_message(embed=embed)
            logger.info(f"Bot info command used by {interaction.user}")
        except Exception as e:
            logger.error(f"Error in botinfo command: {e}")
            await interaction.response.send_message("An error occurred while processing your request.")

async def setup(bot):
    await bot.add_cog(Info(bot))
```
# bot.py 🎉 V1.10.0
```
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
```
