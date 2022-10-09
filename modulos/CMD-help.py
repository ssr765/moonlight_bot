import discord
from discord.ext import commands
from discord import app_commands

# Comando que muestra la latencia del bot.
class help(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client
    
        # Lista de comandos/módulos
        self.comandos = {"comandos": [], "modulos": []}

    @app_commands.command(name="help", description=f"Muestra ayuda sobre los comandos de moonlight🌙.")
    @app_commands.rename(modulo="módulo")
    @app_commands.describe(modulo="Introduce el módulo sobre el que quieres obtener ayuda.")
    async def help(self, interaction: discord.Interaction, modulo: str = None):
        # Separamos los comandos y los grupos.
        for item in self.client.tree.get_commands():
            # Identificar el tipo de cada cosa en la lista para separarlos.
            if type(item) == app_commands.commands.Command:
                self.comandos["comandos"].append({"name": item.name, "description": item.description})
            
            elif type(item) == app_commands.commands.Group:
                self.comandos["modulos"].append({"name": item.name, "description": item.description, "comandos": [{"name": command.name, "description": command.description} for command in item.commands]})

        # Crear embed
        embed = discord.Embed(color=self.client.config.embed_color)

        # Si no se especifica ningún módulo muestra todos los comandos y los módulos.
        if modulo == None:
            embed.set_author(name="Ayuda", icon_url=self.client.user.display_avatar)
        
            # Generamos la información de los comandos disponibles.
            msg_comandos = ""
            for comando in self.comandos["comandos"]:
                msg_comandos += f"``{comando['name']}`` - {comando['description']}\n"
            embed.add_field(name="Comandos principales", value=msg_comandos, inline=False)
            
            # Generamos la información de los módulos disponibles.
            msg_grupos = ""
            for grupo in self.comandos["modulos"]:
                msg_grupos += f"``{grupo['name']}`` - {grupo['description']}\n"
            embed.add_field(name="Módulos", value=msg_grupos, inline=False)
        
        # Si se especifica un módulo lo busca en una lista con los nombres de los módulos.
        elif modulo.lower() in [grupo["name"] for grupo in self.comandos["modulos"]]:
            embed.set_author(name=f"Ayuda de {modulo}", icon_url=self.client.user.display_avatar)
        
            # Generamos la información de los comandos disponibles.
            msg_comandos = ""

            # Para encontrar a que módulo pertenecen los comandos busca el índice de una lista con los nombres de los módulos
            # y busca en los comandos de este.
            for comando in self.comandos["modulos"][[grupo["name"] for grupo in self.comandos["modulos"]].index(modulo)]["comandos"]:
                msg_comandos += f"``{comando['name']}`` - {comando['description']}\n"
            embed.add_field(name="Comandos principales", value=msg_comandos, inline=False)

        # Si el módulo especificado es incorrecto lo dice.
        else:
            embed.color = 0xff0000 # Rojo
            embed.set_author(name=f"{modulo} no es un módulo válido.", icon_url=self.client.user.display_avatar)

        # Manda el embed.
        await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot):
    await client.add_cog(help(client))