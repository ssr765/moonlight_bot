import discord
from discord.ext import commands

class error(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignorar los comandos clasicos no encontrados y el comando sync usado
        # por otra persona.
        ignorados = (commands.CommandNotFound, commands.NotOwner)

        if isinstance(error, ignorados):
            return

async def setup(client: commands.Bot):
    await client.add_cog(error(client))