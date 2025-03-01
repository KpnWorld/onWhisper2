# cogs/owner.py 🎉V1.0.0
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
