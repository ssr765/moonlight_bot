import discord
from discord.ext import commands
from discord import app_commands

class apuestas(commands.GroupCog, name="apuestas", description="Juegos para apostar puntos del servidor."):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client

    async def registrar(self, servidor, usuario):
        await self.client.cursor.execute(f"INSERT INTO servidores (servidor) VALUE ('{servidor}');")
        await self.client.cursor.execute(f"INSERT INTO usuarios (usuario) VALUE ('{usuario}');")
        await self.client.cursor.execute(f"""INSERT INTO puntos (
                                                servidorID,
                                                usuarioID,
                                                puntos) VALUE (
                                                    (SELECT ID FROM servidores WHERE servidor = '{servidor}'),
                                                    (SELECT ID FROM usuarios WHERE usuario = '{usuario}'),
                                                    1000);""")
        print(f"{usuario} ha sido añadido a la base de datos.")

    @app_commands.command(name="coinflip", description="moneda")
    async def coinflip(self, interaction: discord.Interaction, cara: str, apuesta: int):
        # Hacer la consulta.
        await self.client.cursor.execute(f"""SELECT puntos FROM puntos
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
            await self.client.cursor.execute(f"""SELECT puntos FROM puntos
                                                    WHERE servidorID = (
                                                        SELECT ID FROM servidores
                                                        WHERE servidor = '{interaction.guild_id}')
                                                        AND usuarioID = (
                                                            SELECT ID FROM usuarios
                                                            WHERE usuario = '{interaction.user.id}');""")
            consulta = self.client.cursor.fetchall()

        await interaction.response.send_message(f"{consulta.result()}")

async def setup(client: commands.Bot):
    await client.add_cog(apuestas(client))