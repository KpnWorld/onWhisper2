import discord
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Displays help for available commands.")
    async def help(self, interaction: discord.Interaction):
        """Slash command help menu for onWhisper."""
        embed = discord.Embed(
            title="🗯 onWhisper Command Guide 🗯",
            description="Here is a list of available commands organized by category.",
            color=discord.Color.gold()
        )

        # Whisper Commands
        embed.add_field(
            name="🤖 Whisper Commands",
            value=(
                "• **/whisper** - Send a whispered message.\n"
                "• **/admin_whisper** - Whisper command for moderators/admins.\n"
            ),
            inline=False
        )

        # Info Commands
        embed.add_field(
            name="ℹ️ Info Commands",
            value=(
                "• **/help** - Displays this help menu.\n"
                "• **/info** - Shows information about the bot.\n"
                "• **/ping** - Displays the bot's latency.\n"
                "• **/uptime** - Shows how long the bot has been online.\n"
                "• **/server_info** - Displays server details.\n"
                "• **/user_info** - Provides info about a user."
            ),
            inline=False
        )

        # Voting Commands
        embed.add_field(
            name="🗳 Voting",
            value=(
                "• **/vote_reward** - Claim your reward for voting on Top.gg.\n"
                "  *Vote for the bot here:* [Top.gg Link](https://top.gg)"
            ),
            inline=False
        )

        embed.set_footer(text="Use these commands to enhance your onWhisper experience!")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))

