import asyncio
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

    async def consultar_puntos(self, servidor, usuario, registrar = True):
        # Cogiendo una conexión de la pool.
        async with self.client.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql_query = f"""
                    SELECT puntos FROM puntos
                    WHERE servidorID = (
                        SELECT ID FROM servidores
                        WHERE servidor = '{servidor}')
                    AND usuarioID = (
                        SELECT ID FROM usuarios
                        WHERE usuario = '{usuario}');"""
                await cursor.execute(sql_query)

                # consulta.result() devuelve ((puntos,),)
                consulta = cursor.fetchall()

                # Si no está registrado lo registra.
                if len(consulta.result()) == 0 and registrar == True:
                    await self.registrar(servidor, usuario)
                    await cursor.execute(sql_query)
                    consulta = cursor.fetchall()
                
                # En caso de que un usuario intente ver los puntos de un usuario no registrado.
                elif len(consulta.result()) == 0 and registrar == False:
                    return None
                
                consulta = consulta.result()[0][0]

                return consulta

    async def registrar(self, servidor, usuario):
        # Cogiendo una conexión de la pool.
        async with self.client.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Bloques try/except para ignorar las entradas duplicadas.
                try:
                    await cursor.execute(f"INSERT INTO servidores (servidor) VALUE ('{servidor}');")
                    print(f"> {servidor} ha sido añadido a la base de datos.")
                
                except IntegrityError:
                    print(f"> El servidor {servidor} ya estaba registrado en la base de datos. Ignorando...")

                try:
                    await cursor.execute(f"INSERT INTO usuarios (usuario) VALUE ('{usuario}');")
                    print(f"> {usuario} ha sido añadido a la base de datos.")
                
                except IntegrityError:
                    print(f"> El usuario {usuario} ya estaba registrado en la base de datos. Ignorando...")

                # Se guardan los cambios para que pueda encontrar el servidor y el usuario.
                await conn.commit()
                await cursor.execute(f"""
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
                await conn.commit()

    async def actualizar_puntos(self, servidor, usuario, puntos_disponibles, puntos):
        # Cogiendo una conexión de la pool.
        async with self.client.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f"""
                    UPDATE puntos
                    SET puntos = {puntos_disponibles + puntos}
                    WHERE servidorID = (
                        SELECT ID FROM servidores
                        WHERE servidor = '{servidor}')
                    AND usuarioID = (
                        SELECT ID FROM usuarios
                        WHERE usuario = '{usuario}');""")
                await conn.commit()

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
        app_commands.Choice(name="⭕ Cara", value="cara"),
        app_commands.Choice(name="❌ Cruz", value="cruz")])
    @app_commands.describe(cara_elegida="Elige una de las dos caras de la moneda.", apuesta="Cantidad de puntos que quieres apostar. Apuesta mínima: 1.")
    async def moneda(self, interaction: discord.Interaction, apuesta: app_commands.Range[int, 1], cara_elegida: app_commands.Choice[str]):
        # Hacer la consulta.
        puntos_disponibles = await self.consultar_puntos(interaction.guild_id, interaction.user.id)

        if apuesta > puntos_disponibles:
            await interaction.response.send_message("No tienes suficientes puntos para jugar.", ephemeral=True)
            return

        cara_ganadora = self.lado_moneda(random.choice(["cara", "cruz"]))

        if cara_elegida.value == cara_ganadora.lado:
            await self.actualizar_puntos(interaction.guild_id, interaction.user.id, puntos_disponibles, apuesta)
            await interaction.response.send_message(f"{cara_ganadora.mostrar()} Ganas {apuesta} puntos!")

        else:
            await self.actualizar_puntos(interaction.guild_id, interaction.user.id, puntos_disponibles, apuesta * -1)
            await interaction.response.send_message(f"{cara_ganadora.mostrar()} Pierdes {apuesta} puntos.")

    @app_commands.command(name="puntos", description="Consulta tus puntos o los de otro usuario.")
    @app_commands.describe(usuario="Usuario del qual quieres ver sus puntos.")
    async def puntos(self, interaction: discord.Interaction, usuario: discord.Member = None):
        if usuario != None:
            puntos_disponibles = await self.consultar_puntos(interaction.guild_id, usuario.id, False)

            # Habrá devuelto en mensaje de que el usuario no tiene puntos.
            if puntos_disponibles == None:
                await interaction.response.send_message(f"``{self.client.get_user(usuario.id)}`` no tiene puntos en este servidor. ")
                
            else:
                await interaction.response.send_message(f"``{usuario}`` tiene {puntos_disponibles} puntos.")

        else:
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
        await self.actualizar_puntos(interaction.guild_id, interaction.user.id, puntos_disponibles, puntos)

        await interaction.response.send_message(f"Hoy has conseguido {puntos}! Vuelve mañana para obtener más puntos.")
    
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
            await interaction.response.send_message("No tienes suficientes puntos para jugar.", ephemeral=True)
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

    class numero_dados:
        def __init__(self, numero):
            self.numero = numero

            self.COORDENADAS = [
                [(0, 6), (0, 7), (1, 7), (2, 7), (3, 7), (4, 7)],                                                   # 1
                [(0, 6), (0, 7), (0, 8), (1, 8), (2, 6), (2, 7), (2, 8), (3, 6), (4, 6), (4, 7), (4, 8)],           # 2
                [(0, 6), (0, 7), (0, 8), (1, 8), (2, 6), (2, 7), (2, 8), (3, 8), (4, 6), (4, 7), (4, 8)],           # 3
                [(0, 6), (0, 8), (1, 6), (1, 8), (2, 6), (2, 7), (2, 8), (3, 8), (4, 8)],                           # 4
                [(0, 6), (0, 7), (0, 8), (1, 6), (2, 6), (2, 7), (2, 8), (3, 8), (4, 6), (4, 7), (4, 8)],           # 5
                [(0, 6), (0, 7), (0, 8), (1, 6), (2, 6), (2, 7), (2, 8), (3, 6), (3, 8), (4, 6), (4, 7), (4, 8)]    # 6
                ]

        def dibujar(self) -> str:
            # Reiniciar tablero.
            tablero = [["<:vacio:1028722267984769114>"]*15, ["<:vacio:1028722267984769114>"]*15, ["<:vacio:1028722267984769114>"]*15, ["<:vacio:1028722267984769114>"]*15, ["<:vacio:1028722267984769114>"]*15]

            # Poner los dados en las coordenadas.
            for x, y in self.COORDENADAS[self.numero - 1]:
                tablero[x][y] = "\\🎲"

            animacion = ""

            # Crear la cadena con el dibujo.
            for linea in tablero:
                for posicion in linea:
                    animacion += posicion
                animacion += "\n"

            return animacion
            
        def mostrar(self) -> str:
            return f"Ha salido el número: {self.numero}."

    @app_commands.command(name="dado", description="Lanza un dado. Ganar da x6 de los puntos apostados!")
    @app_commands.rename(numero_elegido="número")
    @app_commands.checks.bot_has_permissions(external_emojis=True)
    @app_commands.describe(numero_elegido="Elige un número del dado.", apuesta="Cantidad de puntos que quieres apostar. Apuesta mínima: 1.")
    async def dado(self, interaction: discord.Interaction, apuesta: app_commands.Range[int, 1], numero_elegido: app_commands.Range[int, 1, 6]):
        # Hacer la consulta.
        puntos_disponibles = await self.consultar_puntos(interaction.guild_id, interaction.user.id)

        if apuesta > puntos_disponibles:
            await interaction.response.send_message("No tienes suficientes puntos para jugar.", ephemeral=True)
            return

        lanzamiento = discord.Embed(color=self.client.config.embed_color)
        lanzamiento.set_author(name="Lanzando el dado...", icon_url=self.client.user.display_avatar)
        await interaction.response.send_message(embed=lanzamiento)

        # Animación del dado.
        for x in range(4):
            animacion = ""
            tablero = [["<:vacio:1028722267984769114>"]*15, ["<:vacio:1028722267984769114>"]*15, ["<:vacio:1028722267984769114>"]*15, ["<:vacio:1028722267984769114>"]*15, ["<:vacio:1028722267984769114>"]*15]

            # Dado en una posición aleatoria.
            tablero[random.randint(0, 4)][random.randint(0, 14)] = "\\🎲"

            # Crear la cadena con el dibujo.
            for linea in tablero:
                for posicion in linea:
                    animacion += posicion
                animacion += "\n"
            
            lanzamiento.description = animacion
            await interaction.edit_original_response(embed=lanzamiento)
            await asyncio.sleep(1)

        numero_ganador = self.numero_dados(random.randint(1, 6))

        if numero_elegido == numero_ganador.numero:
            await self.actualizar_puntos(interaction.guild_id, interaction.user.id, puntos_disponibles, apuesta * 6)
            lanzamiento.set_author(name=f"{numero_ganador.mostrar()} Ganas {apuesta * 6} puntos!", icon_url=self.client.user.display_avatar)
            lanzamiento.description = numero_ganador.dibujar()
            await interaction.edit_original_response(embed=lanzamiento)

        else:
            await self.actualizar_puntos(interaction.guild_id, interaction.user.id, puntos_disponibles, apuesta * -1)
            lanzamiento.set_author(name=f"{numero_ganador.mostrar()} Pierdes {apuesta} puntos.", icon_url=self.client.user.display_avatar)
            lanzamiento.description = numero_ganador.dibujar()
            await interaction.edit_original_response(embed=lanzamiento)

    @app_commands.command(name="clasificación", description="Muestra la clasificación de puntos del servidor.")
    async def clasificacion(self, interaction: discord.Interaction):
        # Cogiendo una conexión de la pool.
        async with self.client.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql_query = f"""
                SELECT usuario, puntos
                FROM moonlight.puntos
                INNER JOIN usuarios
                ON puntos.usuarioID = usuarios.ID
                WHERE servidorID = (
                    SELECT ID
                    FROM servidores
                    WHERE servidor = '{interaction.guild_id}'
                )
                ORDER BY puntos DESC
                LIMIT 10;"""
                await cursor.execute(sql_query)
                # ((usuario, puntos), ...)
                consulta = await cursor.fetchall()

            contador = 1
            leaderboard = ""
            for x in consulta:
                # Número de la clasificación.
                if contador == 1:
                    leaderboard += "\\🥇 "

                elif contador == 2:
                    leaderboard += "\\🥈 "

                elif contador == 3:
                    leaderboard += "\\🥉 "

                else:
                    leaderboard += f"{contador}. "
                
                # Usuario.
                leaderboard += f"``{self.client.get_user(int(x[0]))}`` -  {x[1]:,} puntos.\n"
                contador += 1

            embed = discord.Embed(description=leaderboard if leaderboard != "" else "*No hay ningún registro en la clasificación.*", color=self.client.config.embed_color)

            # Añadir icono del server si tiene.
            if interaction.guild.icon != None:
                embed.set_author(icon_url=interaction.guild.icon.url, name=f"Clasificación de {interaction.guild.name}")
            else:
                embed.set_author(name=f"Clasificación de {interaction.guild.name}")

            await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot):
    await client.add_cog(apuestas(client))