import random
import discord
from discord.ext import commands
from discord import app_commands

class acciones(commands.GroupCog, name="accion"):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client

        self.acciones = {
            "airkiss": "le lanza un beso a",
            "bite": "mordia a",
            "blush": "se enrojece",
            "brofist": "choca los puños con",
            "celebrate": "lo celebra",
            "cheers": "brinda con",
            "clap": "aplaude",
            "confused": "está confundido/a",
            "cuddle": "le da mimos a",
            "cry": "está llorando",
            "dance": "se ha puesto a bailar",
            "drool": "está babeando",
            "evillaugh": "está tramando algo",
            "facepalm": "está decepcionado/a",
            "handhold": "ha cojido de la mano a",
            "happy": "está contento/a",
            "headbang": "se está dando cabezazos contra la pared",
            "hug": "abraza a",
            "kiss": "besa a",
            "laugh": "se ha puesto a reir",
            "love": "quiere a",
            "pat": "le hace pat pat a",
            "slap": "abofetea a"
            }
        
        self.negaciones = ["no lol", "iugh", "quita quita", "aparta", "dejame",
            "no puedes", "no me toques"]

    # Ambas funciones generan el embed con el gif de la respectiva acción.
    async def embed_accion(self, user_origen, tipo):
        # Imágen de una acción propia.
        async with self.client.session.get(f"https://api.otakugifs.xyz/gif?reaction={tipo}") as resp:
            source = await resp.json()
        embed = discord.Embed(description=f"**{user_origen}** {self.acciones[tipo]}.", color=0xdcdcdc)
        embed.set_image(url=source["url"])
        embed.set_footer(text=self.client.user, icon_url=self.client.user.avatar.url)
        return embed

    async def embed_accion_dospersonas(self, user_origen, user_destino, tipo):
        # Imágen de una acción conjunta.
        async with self.client.session.get(f"https://api.otakugifs.xyz/gif?reaction={tipo}") as resp:
            source = await resp.json()
        embed = discord.Embed(description=f"**{user_origen}** {self.acciones[tipo]} **{user_destino}**.", color=0xdcdcdc)
        embed.set_image(url=source["url"])
        embed.set_footer(text=self.client.user, icon_url=self.client.user.avatar.url)
        return embed

    @app_commands.command(name="airkiss", description="Lánzale un beso a alguien.")
    @app_commands.describe(user="Usuario al que quieres lanzarle el beso.")
    async def airkiss(self, interaction: discord.Interaction, user: discord.User):
        # Solo el owner del bot puede realizarle estas acciones al bot, en caso de no ser el owner se niega.
        if interaction.user.id != self.client.owner_id and user == self.client.user:
            await interaction.response.send_message(embed=discord.Embed(title=random.choice(self.negaciones), color=0xdd0000))
            return

        embed = await self.embed_accion_dospersonas(interaction.user.name, user.name, "airkiss")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="bite", description="Muerde a alguien.")
    @app_commands.describe(user="Usuario al que quieres morder.")
    async def bite(self, interaction: discord.Interaction, user: discord.User):
        # Solo el owner del bot puede realizarle estas acciones al bot, en caso de no ser el owner se niega.
        if interaction.user.id != self.client.owner_id and user == self.client.user:
            await interaction.response.send_message(embed=discord.Embed(title=random.choice(self.negaciones), color=0xdd0000))
            return

        embed = await self.embed_accion_dospersonas(interaction.user.name, user.name, "bite")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="blush", description="Muestra que estás enrojecido.")
    async def blush(self, interaction: discord.Interaction):
        embed = await self.embed_accion(interaction.user.name, "blush")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="brofist", description="Choca los puños con alguien.")
    @app_commands.describe(user="Usuario con el que quieres chocar los puños.")
    async def brofist(self, interaction: discord.Interaction, user: discord.User):
        embed = await self.embed_accion_dospersonas(interaction.user.name, user.name, "brofist")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="celebrate", description="Ponte a celebrar algo.")
    async def celebrate(self, interaction: discord.Interaction):
        embed = await self.embed_accion(interaction.user.name, "celebrate")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cheers", description="Brinda con alguien.")
    @app_commands.describe(user="Usuario con el que quieres brindar.")
    async def cheers(self, interaction: discord.Interaction, user: discord.User):
        embed = await self.embed_accion_dospersonas(interaction.user.name, user.name, "cheers")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clap", description="Ponte a aplaudir.")
    async def clap(self, interaction: discord.Interaction):
        embed = await self.embed_accion(interaction.user.name, "clap")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="confused", description="Muestra que estás confuso.")
    async def confused(self, interaction: discord.Interaction):
        embed = await self.embed_accion(interaction.user.name, "confused")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cuddle", description="Dale mimos a alguien.")
    @app_commands.describe(user="Usuario al que le quieres dar mimos.")
    async def cuddle(self, interaction: discord.Interaction, user: discord.User):
        # Solo el owner del bot puede realizarle estas acciones al bot, en caso de no ser el owner se niega.
        if interaction.user.id != self.client.owner_id and user == self.client.user:
            await interaction.response.send_message(embed=discord.Embed(title=random.choice(self.negaciones), color=0xdd0000))
            return

        embed = await self.embed_accion_dospersonas(interaction.user.name, user.name, "cuddle")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cry", description="Muestra que estás llorando.")
    async def cry(self, interaction: discord.Interaction):
        embed = await self.embed_accion(interaction.user.name, "cry")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="dance", description="Ponte a bailar.")
    async def dance(self, interaction: discord.Interaction):
        embed = await self.embed_accion(interaction.user.name, "dance")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="drool", description="Muestra que estás babeando.")
    async def drool(self, interaction: discord.Interaction):
        embed = await self.embed_accion(interaction.user.name, "drool")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="evillaugh", description="Ponte a tramar algo.")
    async def evillaugh(self, interaction: discord.Interaction):
        embed = await self.embed_accion(interaction.user.name, "evillaugh")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="facepalm", description="Haz un facepalm.")
    async def facepalm(self, interaction: discord.Interaction):
        embed = await self.embed_accion(interaction.user.name, "facepalm")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="handhold", description="Coje de la mano a alguien.")
    async def handhold(self, interaction: discord.Interaction, user: discord.User):
        # Solo el owner del bot puede realizarle estas acciones al bot, en caso de no ser el owner se niega.
        if interaction.user.id != self.client.owner_id and user == self.client.user:
            await interaction.response.send_message(embed=discord.Embed(title=random.choice(self.negaciones), color=0xdd0000))
            return

        embed = await self.embed_accion_dospersonas(interaction.user.name, user.name, "handhold")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="happy", description="Muestra que estás feliz.")
    async def happy(self, interaction: discord.Interaction):
        embed = await self.embed_accion(interaction.user.name, "happy")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="headbang", description="Date cabezazos contra la pared.")
    async def headbang(self, interaction: discord.Interaction):
        embed = await self.embed_accion(interaction.user.name, "headbang")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hug", description="Abraza a alguien.")
    @app_commands.describe(user="Usuario al que quieres abrazar.")
    async def hug(self, interaction: discord.Interaction, user: discord.User):
        # Solo el owner del bot puede realizarle estas acciones al bot, en caso de no ser el owner se niega.
        if interaction.user.id != self.client.owner_id and user == self.client.user:
            await interaction.response.send_message(embed=discord.Embed(title=random.choice(self.negaciones), color=0xdd0000))
            return

        embed = await self.embed_accion_dospersonas(interaction.user.name, user.name, "hug")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="kiss", description="Besa a alguien.")
    @app_commands.describe(user="Usuario al que quieres besar.")
    async def kiss(self, interaction: discord.Interaction, user: discord.User):
        # Solo el owner del bot puede realizarle estas acciones al bot, en caso de no ser el owner se niega.
        if interaction.user.id != self.client.owner_id and user == self.client.user:
            await interaction.response.send_message(embed=discord.Embed(title=random.choice(self.negaciones), color=0xdd0000))
            return
            
        embed = await self.embed_accion_dospersonas(interaction.user.name, user.name, "kiss")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="laugh", description="Muestra que te estás riendo.")
    async def laugh(self, interaction: discord.Interaction):
        embed = await self.embed_accion(interaction.user.name, "laugh")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="love", description="Muestra que quieres a alguien.")
    @app_commands.describe(user="Usuario al que quieres.")
    async def love(self, interaction: discord.Interaction, user: discord.User):
        # Solo el owner del bot puede realizarle estas acciones al bot, en caso de no ser el owner se niega.
        if interaction.user.id != self.client.owner_id and user == self.client.user:
            await interaction.response.send_message(embed=discord.Embed(title=random.choice(self.negaciones), color=0xdd0000))
            return
            
        embed = await self.embed_accion_dospersonas(interaction.user.name, user.name, "love")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pat", description="Hazle pat pat a alguien.")
    @app_commands.describe(user="Usuario al quel le quieres hacer pat pat.")
    async def pat(self, interaction: discord.Interaction, user: discord.User):
        # Solo el owner del bot puede realizarle estas acciones al bot, en caso de no ser el owner se niega.
        if interaction.user.id != self.client.owner_id and user == self.client.user:
            await interaction.response.send_message(embed=discord.Embed(title=random.choice(self.negaciones), color=0xdd0000))
            return

        embed = await self.embed_accion_dospersonas(interaction.user.name, user.name, "pat")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="slap", description="Abofetea a alguien.")
    @app_commands.describe(user="Usuario al que quieres abofetear.")
    async def slap(self, interaction: discord.Interaction, user: discord.User):
        # Solo el owner del bot puede realizarle estas acciones al bot, en caso de no ser el owner se niega.
        # En el caso de la bofetada, también abofetea al que le ha intentado abodetear.
        if interaction.user.id != self.client.owner_id and user == self.client.user:
            embed = await self.embed_accion_dospersonas(user.name, interaction.user.name, "slap")
            await interaction.response.send_message(embeds=[discord.Embed(title="no.", color=0xdd0000), embed])
            return

        embed = await self.embed_accion_dospersonas(interaction.user.name, user.name, "slap")
        await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot):
    await client.add_cog(acciones(client))