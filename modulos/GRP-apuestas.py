import random
from typing import Literal
import discord
from discord.ext import commands
from discord import app_commands
from aiomysql import IntegrityError

class apuestas(commands.GroupCog, name="apuestas", description="Juegos para apostar puntos del servidor."):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client

    async def registrar(self, servidor, usuario):
        # Bloques try/except para ignorar las entradas duplicadas.
        try:
            await self.client.cursor.execute(f"INSERT INTO servidores (servidor) VALUE ('{servidor}');")
            print(f"> {servidor} ha sido añadido a la base de datos.")
        
        except IntegrityError:
            print(f"> El servidor {servidor} ya estaba registrado en la base de datos. Ignorando...")

        try:
            await self.client.cursor.execute(f"INSERT INTO usuarios (usuario) VALUE ('{usuario}');")
            print(f"> {usuario} ha sido añadido a la base de datos.")
        
        except IntegrityError:
            print(f"> El usuario {usuario} ya estaba registrado en la base de datos. Ignorando...")

        # Se guardan los cambios para que pueda encontrar el servidor y el usuario.
        await self.client.database.connection.commit()
        await self.client.cursor.execute(f"""
            INSERT INTO puntos (
                servidorID,
                usuarioID,
                puntos)
            VALUE (
                (
                    SELECT ID FROM servidores
                    WHERE servidor = '{servidor}'),
                (
                    SELECT ID FROM usuarios
                    WHERE usuario = '{usuario}'),
                {self.client.config.apuestas.puntos_iniciales});""")
        await self.client.database.connection.commit()

    @app_commands.command(name="coinflip", description="Lanza una moneda. Ganar duplica los puntos apostados!")
    @app_commands.describe(cara_elegida="Elige una de las dos caras de la moneda.", apuesta="Cantidad de puntos que quieres apostar. Apuesta mínima: 1.")
    async def coinflip(self, interaction: discord.Interaction, cara_elegida: Literal["Cara", "Cruz"], apuesta: app_commands.Range[int, 1]):
        # Hacer la consulta.
        await self.client.cursor.execute(f"""
            SELECT puntos FROM puntos
            WHERE servidorID = (
                SELECT ID FROM servidores
                WHERE servidor = '{interaction.guild_id}')
            AND usuarioID = (
                SELECT ID FROM usuarios
                WHERE usuario = '{interaction.user.id}');""")
        consulta = self.client.cursor.fetchall()

        # Si la consulta no devuelve nada registra al usuario en la base de datos y vuelve a hacer la consulta.
        while len(consulta.result()) == 0:
            await self.registrar(interaction.guild_id, interaction.user.id)
            await self.client.cursor.execute(f"""
                SELECT puntos FROM puntos
                WHERE servidorID = (
                    SELECT ID FROM servidores
                    WHERE servidor = '{interaction.guild_id}')
                AND usuarioID = (
                    SELECT ID FROM usuarios
                    WHERE usuario = '{interaction.user.id}');""")
            consulta = self.client.cursor.fetchall()

        # consulta.result() devuelve ((puntos,),)
        puntos_disponibles = consulta.result()[0][0]
        if apuesta > puntos_disponibles:
            await interaction.response.send_message("No tienes suficientes puntos.")
        
        else:
            cara_ganadora = random.choice(["Cara", "Cruz"])
            if cara_elegida == cara_ganadora:
                await self.client.cursor.execute(f"""
                    UPDATE puntos
                    SET puntos = {puntos_disponibles + apuesta}
                    WHERE servidorID = (
                        SELECT ID FROM servidores
                        WHERE servidor = '{interaction.guild_id}')
                    AND usuarioID = (
                        SELECT ID FROM usuarios
                        WHERE usuario = '{interaction.user.id}');""")
                await self.client.database.connection.commit()
                await interaction.response.send_message(f"Es {cara_ganadora}! Ganas {apuesta} puntos.")

            else:
                await self.client.cursor.execute(f"""
                    UPDATE puntos
                    SET puntos = {puntos_disponibles - apuesta}
                    WHERE servidorID = (
                        SELECT ID FROM servidores
                        WHERE servidor = '{interaction.guild_id}')
                    AND usuarioID = (
                        SELECT ID FROM usuarios
                        WHERE usuario = '{interaction.user.id}');""")
                await self.client.database.connection.commit()
                await interaction.response.send_message(f"Es {cara_ganadora}. Pierdes {apuesta} puntos.")

    @app_commands.command(name="puntos", description="Consulta tus puntos.")
    async def puntos(self, interaction: discord.Interaction):
        # Hacer la consulta.
        await self.client.cursor.execute(f"""
            SELECT puntos FROM puntos
            WHERE servidorID = (
                SELECT ID FROM servidores
                WHERE servidor = '{interaction.guild_id}')
            AND usuarioID = (
                SELECT ID FROM usuarios
                WHERE usuario = '{interaction.user.id}');""")
        consulta = self.client.cursor.fetchall()

        # consulta.result() devuelve ((puntos,),)
        puntos_disponibles = consulta.result()[0][0]
        if len(consulta.result()) == 0:
            await interaction.response.send_message(f"No estás registrado en el servidor, juega a cualquier juego para recibir {self.client.config.apuestas.puntos_iniciales} puntos iniciales.")
        
        else:
            await interaction.response.send_message(f"Tienes {puntos_disponibles} puntos.")

async def setup(client: commands.Bot):
    await client.add_cog(apuestas(client))