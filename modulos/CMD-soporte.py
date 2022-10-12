import discord
from discord.ext import commands
from discord import app_commands

# Comando que muestra la latencia del bot.
class soporte(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client

    @app_commands.command(name="soporte", description="Invitación al servidor de soporte de moonlight🌙.")
    async def soporte(self, interaction: discord.Interaction):
        embed = discord.Embed(description="Si tienes alguna sugerencia, has encontrado un fallo o tienes alguna duda, entra al servidor de soporte de moonlight\\🌙\n\n> https://discord.gg/X569K45f6r", color=self.client.config.embed_color)
        embed.set_author(name=f"Soporte de moonlight🌙", url="https://discord.gg/X569K45f6r", icon_url=self.client.user.display_avatar)
        await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot):
    await client.add_cog(soporte(client))