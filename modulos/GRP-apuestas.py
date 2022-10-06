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

    async def actualizar_puntos(self, servidor, usuario, puntos_disponibles, puntos):
        await self.client.cursor.execute(f"""
            UPDATE puntos
            SET puntos = {puntos_disponibles + puntos}
            WHERE servidorID = (
                SELECT ID FROM servidores
                WHERE servidor = '{servidor}')
            AND usuarioID = (
                SELECT ID FROM usuarios
                WHERE usuario = '{usuario}');""")
        await self.client.database.connection.commit()

    class lado_moneda:
        def __init__(self, lado):
            self.lado = lado

            if self.lado == "cara":
                self.emoji = "⭕"
            
            elif self.lado == "cruz":
                self.emoji = "❌"
        
        def mostrar(self):
            return f"Es ``{self.emoji} {self.lado.capitalize()}``."

    @app_commands.command(name="moneda", description="Lanza una moneda. Ganar duplica los puntos apostados!")
    @app_commands.rename(cara_elegida="lado")
    @app_commands.choices(cara_elegida=[
        app_commands.Choice(name='⭕ Cara', value="cara"),
        app_commands.Choice(name='❌ Cruz', value="cruz")])
    @app_commands.describe(cara_elegida="Elige una de las dos caras de la moneda.", apuesta="Cantidad de puntos que quieres apostar. Apuesta mínima: 1.")
    async def moneda(self, interaction: discord.Interaction, cara_elegida: app_commands.Choice[str], apuesta: app_commands.Range[int, 1]):
        # Hacer la consulta.
        puntos_disponibles = await self.consultar_puntos(interaction.guild_id, interaction.user.id)

        if apuesta > puntos_disponibles:
            await interaction.response.send_message("No tienes suficientes puntos para jugar.")
            return

        cara_ganadora = self.lado_moneda(random.choice(["cara", "cruz"]))

        if cara_elegida.value == cara_ganadora.lado:
            await self.actualizar_puntos(interaction.guild_id, interaction.user.id, puntos_disponibles, apuesta)
            await interaction.response.send_message(f"{cara_ganadora.mostrar()} Ganas {apuesta} puntos!")

        else:
            await self.actualizar_puntos(interaction.guild_id, interaction.user.id, puntos_disponibles, apuesta * -1)
            await interaction.response.send_message(f"{cara_ganadora.mostrar()} Pierdes {apuesta} puntos.")

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

    class numero_ruleta:
        def __init__(self, numero):
            NUMEROS_ROJOS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
            NUMEROS_NEGROS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]

            self.numero = numero

            # Color
            if self.numero in NUMEROS_ROJOS:
                self.color = "rojo"
                self.emoji = "🔴"

            elif self.numero in NUMEROS_NEGROS:
                self.color = "negro"
                self.emoji = "⚫"

            else:
                self.color = "verde"
                self.emoji = "🟢"
            
            # par/impar
            if self.numero % 2 == 0:
                self.tipo = "par"
            
            else:
                self.tipo = "impar"
            
        def mostrar(self):
            return f"El número premiado és el ``{self.emoji} {self.numero} ({self.tipo.capitalize()})``."

    @app_commands.command(name="ruleta", description="Juega a la ruleta.")
    @app_commands.rename(numero="número")
    @app_commands.choices(color=[
        app_commands.Choice(name="🟢 Verde", value="verde"),
        app_commands.Choice(name="🔴 Rojo", value="rojo"),
        app_commands.Choice(name="⚫ Negro", value="negro")])
    @app_commands.describe(
        apuesta="Cantidad de puntos que quieres apostar. Apuesta mínima: 1.",
        color="Escoje un color al que apostar. El verde da x36 puntos!",
        tipo="Escoje si apostar al par o al impar (x2).",
        numero="Escoje un número al que apostar (x36).")
    async def ruleta(
        self,
        interaction: discord.Interaction,
        apuesta: app_commands.Range[int, 1],
        color: app_commands.Choice[str] = None,
        tipo: Literal["par", "impar"] = None,
        numero: app_commands.Range[int, 0, 36] = None):
        # Hacer la consulta.
        puntos_disponibles = await self.consultar_puntos(interaction.guild_id, interaction.user.id)
        numero_premiado = self.numero_ruleta(random.randint(0, 36))


        if apuesta > puntos_disponibles:
            await interaction.response.send_message("No tienes suficientes puntos para jugar.")
            return
        
        # Jugada por color 
        if color != None and tipo == None and numero == None:
            if color.value == numero_premiado.color and color.value != "verde":
                await self.actualizar_puntos(interaction.guild_id, interaction.user.id, puntos_disponibles, apuesta)
                await interaction.response.send_message(f"{numero_premiado.mostrar()} Has ganado {apuesta} puntos.")

            elif color.value == numero_premiado.color and color.value == "verde":
                await self.actualizar_puntos(interaction.guild_id, interaction.user.id, puntos_disponibles, apuesta * 36)
                await interaction.response.send_message(f"{numero_premiado.mostrar()} HAS GANADO {apuesta * 36} puntos.")

            else:
                await self.actualizar_puntos(interaction.guild_id, interaction.user.id, puntos_disponibles, apuesta * -1)
                await interaction.response.send_message(f"{numero_premiado.mostrar()} Has perdido {apuesta} puntos.")
        
        # Jugada por par/impar
        elif color == None and tipo != None and numero == None:
            if tipo == numero_premiado.tipo:
                await self.actualizar_puntos(interaction.guild_id, interaction.user.id, puntos_disponibles, apuesta)
                await interaction.response.send_message(f"{numero_premiado.mostrar()} Has ganado {apuesta} puntos.")

            else:
                await self.actualizar_puntos(interaction.guild_id, interaction.user.id, puntos_disponibles, apuesta * -1)
                await interaction.response.send_message(f"{numero_premiado.mostrar()} Has perdido {apuesta} puntos.")

        # Jugada por número
        elif color == None and tipo == None and numero != None:
            if numero == numero_premiado.numero and numero != 0:
                await self.actualizar_puntos(interaction.guild_id, interaction.user.id, puntos_disponibles, apuesta)
                await interaction.response.send_message(f"{numero_premiado.mostrar()} Has ganado {apuesta} puntos.")

            elif numero == numero_premiado.numero and numero == 0:
                await self.actualizar_puntos(interaction.guild_id, interaction.user.id, puntos_disponibles, apuesta * 36)
                await interaction.response.send_message(f"{numero_premiado.mostrar()} HAS GANADO {apuesta * 36} puntos.")

            else:
                await self.actualizar_puntos(interaction.guild_id, interaction.user.id, puntos_disponibles, apuesta * -1)
                await interaction.response.send_message(f"{numero_premiado.mostrar()} Has perdido {apuesta} puntos.")
        
        # No se eligió nada
        elif color == None and tipo == None and numero == None:
            await interaction.response.send_message(f"Debes seleccionar alguna opción (color, tipo o número) para jugar, o si no la banca se quedará tus {apuesta} puntos.")

        # Se eligió más de una opción
        else:
            await interaction.response.send_message(f"Has seleccionado demasiadas opciones, elige solo una, o si no la banca se quedará tus {apuesta} puntos.")

async def setup(client: commands.Bot):
    await client.add_cog(apuestas(client))