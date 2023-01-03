import discord
from discord.ext import commands
from discord import app_commands

import random
import asyncio

class decidir(commands.GroupCog, name="decidir", description="Preguntale algo al bot, el responderá."):
    def __init__(self, client: commands.Bot) -> None:
        super().__init__()
        self.client = client

    @app_commands.command(name="elegir", description="Elige entre las opciones introducidas.")
    @app_commands.describe(opciones="Introduce las opciones que quieras separadas por ';'.")
    async def elegir(self, interaction: discord.Interaction, opciones: str):
        # Generar la elección y la lista de opciones.
        opciones = opciones.split(";")
        eleccion = random.choice(opciones)
        opciones_posibles = []
        for opcion in opciones:
            if opcion == eleccion:
                opciones_posibles.append(f"*``{opcion}``*")
            
            else:
                opciones_posibles.append(f"``{opcion}``")

        # El bot "piensa" la respuesta.
        embed = discord.Embed(color=self.client.config.embed_color)
        embed.set_author(icon_url=self.client.user.display_avatar, name="Pensando...")
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(random.randint(1, 15))

        # Mandar la elección.
        embed = discord.Embed(description=f"Mi elección ha sido: *``{eleccion}``*", color=self.client.config.embed_color)
        embed.set_author(icon_url=self.client.user.display_avatar, name="He elegido")
        embed.add_field(name="**Opciones posibles:**", value=f"> {', '.join(opciones_posibles)}")
        await interaction.edit_original_response(embed=embed)

    @app_commands.command(name="preguntar", description="El bot responderá a tu pregunta.")
    @app_commands.describe(pregunta="Introduce tu pregunta.")
    async def preguntar(self, interaction: discord.Interaction, pregunta: str):
        # Añadir ¿? si no lo tiene
        if pregunta[0] != "¿":
            pregunta = "¿" + pregunta
        
        if pregunta[-1] != "?":
            pregunta += "?"

        # Listas de respuestas.
        afirmaciones = ["sí", "no lo dudes", "100%", "confirmo"]
        negaciones = ["no", "para nada", "ni se te ocurra", "fumas porros"]
        res_neutra = ["puede", "depende", "a lo mejor", "no estoy seguro", "no sé"]

        principio = ["definitivamente ", "probablemente "]
        final = [", la verdad", ", no te voy a mentir", "..."]

        # Escojer la respuesta.
        opcion = random.randint(1, 10)

        if opcion >= 1 and opcion <= 4:
            opciones = afirmaciones

        elif opcion >= 5 and opcion <= 8:
            opciones = negaciones

        elif opcion >= 9 and opcion <= 10:
            opciones = res_neutra

        # Generar la respuesta.
        respuesta = opciones[random.randint(0, len(opciones) - 1)]

        if random.randint(1, 4) == 1 and respuesta not in res_neutra:
            respuesta = principio[random.randint(0, len(principio) - 1)] + respuesta

        if random.randint(1, 4) == 1 and respuesta not in res_neutra:
            respuesta += final[random.randint(0, len(final) - 1)]

        if random.randint(1,10) == 1:
            respuesta = respuesta.upper()

        # El bot "piensa" la respuesta.
        embed = discord.Embed(color=self.client.config.embed_color)
        embed.set_author(icon_url=self.client.user.display_avatar, name="Pensando...")
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(random.randint(1, 15))

        # Mandar la respuesta.
        embed = discord.Embed(title=pregunta, description=respuesta, color=self.client.config.embed_color)
        embed.set_author(icon_url=self.client.user.display_avatar, name="Tengo la respuesta")
        await interaction.edit_original_response(embed=embed)

async def setup(client: commands.Bot) -> None:
    """Configura el módulo en el bot."""
    await client.add_cog(decidir(client))