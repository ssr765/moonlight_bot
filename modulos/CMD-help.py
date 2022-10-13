import discord
from discord.ext import commands
from discord import app_commands

# Comando que muestra la latencia del bot.
class help(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client
    
    def generar_comandos(self, arbol_comandos):
        comandos = []
        modulos = []
        # get_commands() devuelve una lista de comandos y módulos del servidor.
        # Si se especifica guild devuelve los comandos y módulos EXCLUSIVOS del
        # servidor especificado.
        for item in arbol_comandos:
            if type(item) == app_commands.commands.Command:
                comandos.append(item)

            elif type(item) == app_commands.commands.Group:
                modulos.append(item)
                for c in item.commands:
                    comandos.append(c)

        return comandos, modulos

    async def comandos_autocompletado(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        comandos, modulos = self.generar_comandos(self.client.tree.get_commands() + self.client.tree.get_commands(guild=interaction.guild))
        comandos = [c.name for c in comandos]
        return [app_commands.Choice(name=comando, value=comando) for comando in comandos if current.lower() in comando.lower()]

    async def modulos_autocompletado(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        comandos, modulos = self.generar_comandos(self.client.tree.get_commands() + self.client.tree.get_commands(guild=interaction.guild))
        modulos = [m.name for m in modulos]
        return [app_commands.Choice(name=modulo, value=modulo) for modulo in modulos if current.lower() in modulo.lower()]

    @app_commands.command(name="help", description=f"Muestra ayuda sobre los comandos de moonlight🌙.")
    @app_commands.autocomplete(comando_deseado=comandos_autocompletado, modulo_deseado=modulos_autocompletado)
    @app_commands.rename(modulo_deseado="módulo", comando_deseado="comando")
    @app_commands.describe(comando_deseado="Introduce el comando sobre el que quieres obtener más detalles.", modulo_deseado="Introduce el módulo sobre el que quieres obtener ayuda.")
    async def help(self, interaction: discord.Interaction, comando_deseado: str = None, modulo_deseado: str = None):
        comandos, modulos = self.generar_comandos(self.client.tree.get_commands() + self.client.tree.get_commands(guild=interaction.guild))

        if comando_deseado == None and modulo_deseado == None or comando_deseado != None and modulo_deseado != None:
            embed = discord.Embed(description="Usa ``/help [módulo: nombre del módulo]`` para ver los comandos que contiene un módulo.\nUsa ``/help [comando: nombre del comando]`` para obtener detalles acerca de este.", color=self.client.config.embed_color)
            embed.set_author(name="Ayuda de moonlight🌙", icon_url=self.client.user.display_avatar)
            embed.add_field(name="Comandos generales", value=f"```{', '.join([command.name for command in comandos if command.parent == None])}```", inline=False)
            embed.add_field(name="Módulos disponibles", value=f"```{', '.join([cog.name for cog in modulos])}```", inline=False)

        # Mensaje de comandos
        elif comando_deseado != None and modulo_deseado == None:
            try:
                # Escoje el comando que está en la posición donde coincide el nombre del comando.
                comando = comandos[[command.name for command in comandos].index(comando_deseado)]

            except ValueError:
                embed = discord.Embed(color=0xff0000)
                embed.set_author(name=f"El comando {comando_deseado.lower()} no existe.", icon_url=self.client.user.display_avatar)
                await interaction.response.send_message(embed=embed)
                return

            embed = discord.Embed(color=self.client.config.embed_color)
            embed.set_author(name=f"Ayuda de /{comando.parent.name + ' ' if comando.parent != None else ''}{comando.name}", icon_url=self.client.user.display_avatar)
            embed.add_field(name="Descripción", value=f"> {comando.description}", inline=False)
            
            if comando.parent != None:
                embed.set_footer(text=f"Para más información del módulo {comando.parent.name} usa /help módulo:{comando.parent.name}.")

            if len(comando.parameters) >= 1:
                parametros = ""
                for parameter in comando.parameters:
                    if parameter.required:
                        parametros += "```" + parameter.display_name + " - " + parameter.description + "```\n"

                    else:
                        parametros += "```(Opcional) " + parameter.display_name + " - " + parameter.description + "```\n"

                embed.add_field(name="Parametros", value=parametros)
            
            if comando.nsfw == True:
                embed.add_field(name="Comando con restricción de edad", value="> \\✅", inline=False)

        # Mensaje de módulos
        elif comando_deseado == None and modulo_deseado != None:
            try:
                # Escoje el módulo que está en la posición donde coincide el nombre del módulo.
                modulo = modulos[[cog.name for cog in modulos].index(modulo_deseado)]

            except ValueError:
                embed = discord.Embed(color=0xff0000)
                embed.set_author(name=f"El modulo {modulo_deseado.lower()} no existe.", icon_url=self.client.user.display_avatar)
                await interaction.response.send_message(embed=embed)
                return

            embed = discord.Embed(color=self.client.config.embed_color)
            embed.set_author(name=f"Ayuda de /{modulo.name} (comando)", icon_url=self.client.user.display_avatar)
            embed.add_field(name="Descripción", value=f"> {modulo.description}", inline=False)
            embed.set_footer(text=f"Para ver detalles de un comando usa /help comando:(comando deseado).")
            
            if len(modulo.commands) >= 1:
                lista_de_comandos = ""
                for comando in modulo.commands:
                    lista_de_comandos += "```" + comando.name + " - " + comando.description + "```\n"

                embed.add_field(name=f"Comandos de {modulo.name}", value=lista_de_comandos)
            
            else:
                embed.add_field(name=f"Comandos de {modulo.name}", value="> *Todavía no hay comandos en este módulo.*")

        await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot):
    await client.add_cog(help(client))