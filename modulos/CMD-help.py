import discord
from discord.ext import commands
from discord import app_commands

# Comando que muestra la latencia del bot.
class help(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client
    
        self.comandos = []
        self.grupos = []

    @app_commands.command(name="help", description="Muestra ayuda sobre los comandos.")
    @app_commands.describe(modulo="Introduce el módulo sobre el que quieres obtener ayuda.")
    async def help(self, interaction: discord.Interaction, modulo: str = None):
        # Separamos los comandos y los grupos.
        for item in self.client.tree.get_commands():
            if type(item) == app_commands.commands.Command:
                self.comandos.append(item)
            
            elif type(item) == app_commands.commands.Group:
                self.grupos.append(item)

        embed = discord.Embed(color=self.client.config.embed_color)

        if modulo == None:
            embed.set_author(name="Ayuda", icon_url=self.client.user.display_avatar)
        
            # Generamos la información de los comandos disponibles.
            msg_comandos = ""
            for comando in self.comandos:
                msg_comandos += f"``{comando.name}`` - {comando.description}\n"
            embed.add_field(name="Comandos principales", value=msg_comandos)
            
            # Generamos la información de los módulos disponibles.
            msg_grupos = ""
            for grupo in self.grupos:
                msg_grupos += f"``{grupo.name}`` - {grupo.description}\n"
            embed.add_field(name="Módulos", value=msg_grupos)
        
        # WIP
        # elif modulo in [grupo.name for grupo in self.grupos]:
        #     embed.set_author(name=f"Ayuda de {modulo}", icon_url=self.client.user.display_avatar)
        
        #     # Generamos la información de los comandos disponibles.
        #     msg_comandos = ""
        #     for comando in grupo.commands:
        #         msg_comandos += f"``{comando.name}`` - {comando.description}\n"
        #     embed.add_field(name="Comandos principales", value=msg_comandos)

        await interaction.response.send_message(embed=embed)

# async def setup(client: commands.Bot):
#     await client.add_cog(help(client))