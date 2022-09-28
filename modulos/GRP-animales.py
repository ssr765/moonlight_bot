import discord
from discord.ext import commands
from discord import app_commands

class animales(commands.GroupCog, name="animales"):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client

    @app_commands.command(name="gato", description="Envía una imagen de un gato.")
    async def gato(self, interaction: discord.Interaction):
        # Request de la imágen
        async with self.client.session.get("https://api.thecatapi.com/v1/images/search") as resp:
            source = await resp.json()
        # Creación del embed
        embed = discord.Embed(color=self.client.config.embed_color)
        embed.set_image(url=source[0]['url'])
        embed.set_footer(text=self.client.user, icon_url=self.client.user.display_avatar)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="perro", description="Envía una imagen de un perro.")
    async def perro(self, interaction: discord.Interaction):
        # Request de la imágen
        async with self.client.session.get("https://dog.ceo/api/breeds/image/random") as resp:
            source = await resp.json()
        # Creación del embed
        embed = discord.Embed(color=self.client.config.embed_color)
        embed.set_image(url=source['message'])
        embed.set_footer(text=self.client.user, icon_url=self.client.user.display_avatar)
        await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot):
    await client.add_cog(animales(client))