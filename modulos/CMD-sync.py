import discord
from discord.ext import commands

# Comando para actualizar los comandos en todos los servidores en los que este
# el bot, solo lo pueden usar los owners del bot.
class sync(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client

    @commands.command(name="sync")
    @commands.is_owner()
    async def sync(self, ctx):
        self.client.synced = True
        for server in self.client.guilds:
            self.client.tree.copy_global_to(guild=server)
            await self.client.tree.sync(guild=server)
        await ctx.send("Comandos sincronizados con Discord.")
        print("> Comandos sincronizados con Discord.")

async def setup(client: commands.Bot):
    await client.add_cog(sync(client))