import datetime
import discord
from discord.ext import commands
from discord import app_commands

from colorama import Fore

class error(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client

        # Handler
        self.client.tree.on_error = self.on_app_command_error

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignorar los comandos clasicos no encontrados y el comando sync usado
        # por otra persona.
        ignorados = (commands.CommandNotFound, commands.NotOwner)

        if isinstance(error, ignorados):
            return
        
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        # Comando en cooldown.
        if isinstance(error, app_commands.CommandOnCooldown):
            cooldown_restante = str(datetime.timedelta(seconds=error.retry_after)).split('.')[0]

            # Mensajes personalizados para ciertos comandos.
            if interaction.command.name == "diario":
                await interaction.response.send_message(f"Ya has reclamado el bonus diario de hoy. Volverá a estar disponible en {cooldown_restante}.", ephemeral=True)

            else:
                await interaction.response.send_message(f"El comando ``{interaction.command.name}`` está en cooldown. Vuelve a intentarlo en {cooldown_restante}.", ephemeral=True)

        # Comando fallido por falta de permisos.
        elif isinstance(error, app_commands.BotMissingPermissions):
            embed = discord.Embed(description="Si eres miembro del servidor, informa a algún moderador de este error. Si eres moderador o dueño del servidor asegurate que moonlight\\🌙 tiene los permisos necesarios para funcionar correctamente.", color=0xFF0000)
            embed.set_author(name="moonlight🌙 no tiene suficientes permisos para ejectuar el comando.", icon_url=self.client.user.display_avatar)
            embed.add_field(name="Permisos necesarios faltantes:", value=f"{','.join('``' + permiso + '``' for permiso in error.missing_permissions)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)

        # Comando fallido por otros motivos
        else:
            embed = discord.Embed(description="Si el error persiste puedes reportarlo al servidor oficial de moonlight\\🌙 para ayudar a mejorar el bot.", color=0xFF0000)
            embed.set_author(name="El comando ha fallado.", icon_url=self.client.user.display_avatar)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            print(f"> {Fore.RED}⚠  Error en el comando '{interaction.command.name}': {error}{Fore.RESET}")

async def setup(client: commands.Bot):
    await client.add_cog(error(client))