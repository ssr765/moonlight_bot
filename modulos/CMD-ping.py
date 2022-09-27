import discord
from discord.ext import commands
from discord import app_commands

# Comando que muestra la latencia del bot.
class ping(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client

    @app_commands.command(
        name="ping",
        description="Muestra la latencia del bot."
        )
    async def ping(self, interaction: discord.Interaction):
        embed = discord.Embed(color=0xdcdcdc)
        embed.set_author(
            name=f"Ping: {round(self.client.latency * 1000)} ms",
            icon_url=self.client.user.display_avatar
            )
            
        await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot):
    await client.add_cog(ping(client))