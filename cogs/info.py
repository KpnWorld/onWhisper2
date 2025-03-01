# cogs/info.py 🎉 V1.0.0
import discord
from discord.ext import commands
from discord import app_commands
import time
import logging

# Initialize logger with timestamp formatting
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

