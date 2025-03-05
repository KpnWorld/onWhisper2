"cogs/whisper.py 🎉 V1.0.0"
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

