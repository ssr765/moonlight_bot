import os
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord import app_commands
from pantheon.pantheon import Pantheon
from pantheon.utils.exceptions import NotFound

load_dotenv()
API_KEY = os.getenv("LOL_KEY")

RANKS = {
    "IRON": {"nombre": "Hierro", "color": 0x6C6C6C},
    "BRONZE": {"nombre": "Bronce", "color": 0x9E4F00},
    "SILVER": {"nombre": "Plata", "color": 0xC0C0C0},
    "GOLD": {"nombre": "Oro", "color": 0xB38000},
    "PLATINUM": {"nombre": "Platino", "color": 0x66EEEE},
    "DIAMOND": {"nombre": "Diamante", "color": 0x0049FF},
    "MASTER": {"nombre": "Maestro", "color": 0x8F00FF},
    "GRANDMASTER": {"nombre": "Gran Maestro", "color": 0xCB0000},
    "CHALLENGER": {"nombre": "Aspirante", "color": 0xDAFFFA}
}

COLAS = {
    "RANKED_SOLO_5x5": "Solo/Dúo",
    "RANKED_FLEX_SR": "Flexible"
}

class invocador:
    """Contiene la información del jugador."""
    def __init__(self, data) -> None:
        self.nombre = data['name']
        self.icono = data['profileIconId']
        self.nivel = data['summonerLevel']
        self.url_icono = f"https://raw.communitydragon.org/latest/game/assets/ux/summonericons/profileicon{self.icono}.png"
        self.id = data['id']

class clasificacion:
    """Contiene toda la información de la clasificación del jugador."""
    def __init__(self, data: dict) -> None:
        self.division = RANKS[data['tier']]['nombre']

        if self.division not in ("Maestro", "Gran Maestro", "Aspirante"):
            self.liga = data['rank']
        
        else:
            self.liga = ""

        self.lp = data['leaguePoints']
        self.victorias = data['wins']
        self.derrotas = data['losses']
        self.winrate = round(self.victorias / (self.victorias + self.derrotas) * 100)
        self.racha = data['hotStreak']
        self.cola = COLAS[data['queueType']]
        self.color = RANKS[data['tier']]['color']
        self.imagen = fr"img/lol/Emblem_{data['tier'].title()}.png"

        self.nombre_liga = None

class lol(commands.GroupCog, name="lol", description="..."):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client
        self.panth = Pantheon('euw1', API_KEY)
    
    @app_commands.command(name="elo", description="Manda datos sobre tu clasificación en el lol.")
    @app_commands.choices(server=[
        app_commands.Choice(name="EUW", value="euw1"),
        app_commands.Choice(name="BR", value="br1"),
        app_commands.Choice(name="EUNE", value="eun1"),
        app_commands.Choice(name="JP", value="jp1"),
        app_commands.Choice(name="KR", value="kr"),
        app_commands.Choice(name="LAN", value="la1"),
        app_commands.Choice(name="LAS", value="la2"),
        app_commands.Choice(name="NA", value="na1"),
        app_commands.Choice(name="OCE", value="oc1"),
        app_commands.Choice(name="RU", value="ru"),
        app_commands.Choice(name="TR", value="tr1")],
    cola=[
        app_commands.Choice(name="Solo/Dúo", value="RANKED_SOLO_5x5"),
        app_commands.Choice(name="Flexible", value="RANKED_FLEX_SR")])
    @app_commands.rename(server="servidor", summoner="invocador")
    @app_commands.describe(server="Servidor en el que juegas", summoner="Tu nombre de invocador", cola="Sobre qué cola quieres saber tu rango?")
    @app_commands.checks.cooldown(2, 5, key=lambda i: (i.guild_id, i.user.id))
    async def elo(self, interaction: discord.Interaction, server: app_commands.Choice[str], summoner: str, cola: app_commands.Choice[str]):
        await interaction.response.defer(thinking=True)
        # Peticiones a la API
        self.panth.set_server(server.value)
        try:
            player_data = await self.panth.get_summoner_by_name(summoner)
        
        except NotFound:
            await interaction.followup.send(f"No se ha encontrado el invocador {summoner} en {server.name}.")
        
        else:
            player = invocador(player_data)
            ranked_data = await self.panth.get_league_position(player.id)
            clasificado = False
            for queue in ranked_data:
                if cola.value == queue['queueType']:
                    clasificado = True
                    ranked = clasificacion(queue)
                    liga_data = await self.panth.get_league_by_id(queue['leagueId'])
                    ranked.nombre_liga = liga_data['name']

                    file = discord.File(ranked.imagen, "rank.png")
                    embed = discord.Embed(color=ranked.color)
                    embed.set_author(name=f"{player.nombre}", icon_url=player.url_icono)
                    embed.set_thumbnail(url="attachment://rank.png")
                    embed.add_field(name=f"{ranked.cola}", value=f"> **{ranked.division} {ranked.liga}** - {ranked.lp} LP\n> {ranked.nombre_liga}", inline=True)
                    embed.add_field(name="Winrate", value=f"> {ranked.victorias}V {ranked.derrotas}D\n> {ranked.winrate}% WR", inline=True)
                    embed.set_footer(text=f"Nivel del invocador: {player.nivel}")
                    await interaction.followup.send(embed=embed, file=file)
            
            if not clasificado:
                file = discord.File("img/lol/Emblem_Unranked.png", "rank.png")
                embed = discord.Embed(color=0xFF0000)
                embed.set_author(name=f"{player.nombre}", icon_url=player.url_icono)
                embed.set_thumbnail(url="attachment://rank.png")
                embed.add_field(name=f"{cola.name}", value=f"> *Sin clasificar*", inline=True)
                embed.set_footer(text=f"Nivel del invocador: {player.nivel}")
                await interaction.followup.send(embed=embed, file=file)

async def setup(client: commands.Bot):
    await client.add_cog(lol(client))