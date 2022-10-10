import json
import random
import discord
from discord.ext import commands
from discord import app_commands

class acciones(commands.GroupCog, name="accion"):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client

        with open("config/frases_acciones.json", "r", encoding="UTF-8") as f:
            d = json.load(f)

        self.acciones = d["acciones"]
        self.negaciones = d["negaciones"]

    # Comando de acción propia.
    @app_commands.command(name="expresion", description="Muestra tu expresión.")
    @app_commands.describe(expresion="Usuario al que quieres lanzarle el beso.")
    @app_commands.rename(expresion="expresión")
    @app_commands.choices(expresion=[
        app_commands.Choice(name="Enrojecerse", value="blush"),
        app_commands.Choice(name="Celebrar", value="celebrate"),
        app_commands.Choice(name="Aplaudir", value="clap"),
        app_commands.Choice(name="Confuso", value="confused"),
        app_commands.Choice(name="Llorar", value="cry"),
        app_commands.Choice(name="Bailar", value="dance"),
        app_commands.Choice(name="Babear", value="drool"),
        app_commands.Choice(name="Risa maligna", value="evillaugh"),
        app_commands.Choice(name="Facepalm", value="facepalm"),
        app_commands.Choice(name="Feliz", value="happy"),
        app_commands.Choice(name="Darse cabezazos", value="headbang"),
        app_commands.Choice(name="Reir", value="laugh"),
        app_commands.Choice(name="Enfadado", value="mad"),
        app_commands.Choice(name="Nervioso", value="nervous"),
        app_commands.Choice(name="Negarse", value="no"),
        app_commands.Choice(name="Asomarse", value="peek"),
        app_commands.Choice(name="Triste", value="sad"),
        app_commands.Choice(name="Sorber", value="sip"),
        app_commands.Choice(name="Dormir", value="sleep"),
        app_commands.Choice(name="Pedir disculpas", value="sorry"),
        app_commands.Choice(name="Bostezar", value="yawn"),
        app_commands.Choice(name="Afirmar", value="yes"),
        ])
    async def expresion(self, interaction: discord.Interaction, expresion: app_commands.Choice[str]):
        # Imágen de una acción propia.
        async with self.client.session.get(f"https://api.otakugifs.xyz/gif?reaction={expresion.value}") as resp:
            source = await resp.json()

        embed = discord.Embed(description=f"**{interaction.user.name}** {self.acciones[expresion.value]}.", color=0xdcdcdc)
        embed.set_image(url=source["url"])
        embed.set_footer(text=self.client.user, icon_url=self.client.user.avatar.url)
        await interaction.response.send_message(embed=embed)


    # Comando de acción conjunta.
    @app_commands.command(name="interactuar", description="Interactua con otro usuario.")
    @app_commands.describe(user="Usuario con el que quieres interactuar.")
    @app_commands.rename(accion="acción")
    @app_commands.choices(accion=[
        app_commands.Choice(name="Lanzar beso", value="airkiss"),
        app_commands.Choice(name="Morder", value="bite"),
        app_commands.Choice(name="Chocar puños", value="brofist"),
        app_commands.Choice(name="Brindar", value="cheers"),
        app_commands.Choice(name="Dar mimos", value="cuddle"),
        app_commands.Choice(name="Cojer de la mano", value="handhold"),
        app_commands.Choice(name="Abrazar", value="hug"),
        app_commands.Choice(name="Besar", value="kiss"),
        app_commands.Choice(name="Chupar", value="lick"),
        app_commands.Choice(name="Dar cariño", value="love"),
        app_commands.Choice(name="Hacer pat pat", value="pat"),
        app_commands.Choice(name="Abofetear", value="slap"),
        app_commands.Choice(name="Golpear", value="smack"),
        ])
    async def interactuar(self, interaction: discord.Interaction, accion: app_commands.Choice[str], user: discord.Member):
        # Imágen de una acción conjunta.
        async with self.client.session.get(f"https://api.otakugifs.xyz/gif?reaction={accion.value}") as resp:
            source = await resp.json()

        embed = discord.Embed(description=f"**{interaction.user.name}** {self.acciones[accion.value]} **{user.name}**.", color=0xdcdcdc)
        embed.set_image(url=source["url"])
        embed.set_footer(text=self.client.user, icon_url=self.client.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    """
    Acciones disponibles de otakugifs.xyz no añadidas:
        angrystare, bleh, nyah, nom, nosebleed, nuzzle,
        pinch, poke, pout, punch, roll, run, ,scared,
        shrug, shy, sigh, slowclap, smile, smug,
        sneeze, stare, stop, surprised, sweat, thumbsup,
        tickle, tired, wave, wink, woah, yay."""

async def setup(client: commands.Bot):
    await client.add_cog(acciones(client))