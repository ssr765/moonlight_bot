import random
from typing import Literal
import datetime
import discord
from discord.ext import commands
from discord import app_commands
from aiomysql import IntegrityError

class apuestas(commands.GroupCog, name="apuestas", description="Juegos para apostar puntos del servidor."):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client

    async def consultar_puntos(self, servidor, usuario):
        sql_query = f"""
            SELECT puntos FROM puntos
            WHERE servidorID = (
                SELECT ID FROM servidores
                WHERE servidor = '{servidor}')
            AND usuarioID = (
                SELECT ID FROM usuarios
                WHERE usuario = '{usuario}');"""
        await self.client.cursor.execute(sql_query)

        # consulta.result() devuelve ((puntos,),)
        consulta = self.client.cursor.fetchall()

        # Si no está registrado lo registra.
        if len(consulta.result()) == 0:
            await self.registrar(servidor, usuario)
            await self.client.cursor.execute(sql_query)
            consulta = self.client.cursor.fetchall()
        
        consulta = consulta.result()[0][0]

        return consulta

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
        puntos_disponibles = await self.consultar_puntos(interaction.guild_id, interaction.user.id)

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
        puntos_disponibles = await self.consultar_puntos(interaction.guild_id, interaction.user.id)
        await interaction.response.send_message(f"Tienes {puntos_disponibles} puntos.")

    @app_commands.command(name="diario", description=f"Consigue puntos diariamente.")
    @app_commands.checks.cooldown(1, 86400, key=lambda i: (i.guild_id, i.user.id))
    async def diario(self, interaction: discord.Interaction):
        # Consulta
        puntos_disponibles = await self.consultar_puntos(interaction.guild_id, interaction.user.id)

        # Puntos diarios aleatorios
        puntos = random.randint(self.client.config.apuestas.puntos_diarios_min, self.client.config.apuestas.puntos_diarios_max)

        # Añadir los puntos.
        await self.client.cursor.execute(f"""
            UPDATE puntos
            SET puntos = {puntos_disponibles + puntos}
            WHERE servidorID = (
                SELECT ID FROM servidores
                WHERE servidor = '{interaction.guild_id}')
            AND usuarioID = (
                SELECT ID FROM usuarios
                WHERE usuario = '{interaction.user.id}');""")
        await self.client.database.connection.commit()

        await interaction.response.send_message(f"Hoy has conseguido {puntos}! Vuelve mañana para obtener más puntos.")
    
    @diario.error
    async def on_test_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"Todavía no puedes reclamar el bonus diario, queda {str(datetime.timedelta(seconds=error.retry_after)).split('.')[0]} para que puedas volver a hacerlo.", ephemeral=True)

async def setup(client: commands.Bot):
    await client.add_cog(apuestas(client))