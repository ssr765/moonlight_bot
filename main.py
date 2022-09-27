import os
import asyncio
import json
import discord
from discord.ext import commands
from colorama import Fore
from dotenv import load_dotenv

from config.asciiart_generator import asciiart

# Obtener token.
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Lista para mostrar los modulos que no se han cargado.
# Estos se mostrarán después de borrar la pantalla con el ASCII art.
no_cargados = []

# Cargar configuración.
with open("config/bot_config.json", "r") as f:
    d = json.load(f)

PREFIX = d["prefix"]

class client(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = commands.when_mentioned_or(PREFIX),
            intents = discord.Intents.all(),
            activity = discord.Streaming(
                name = "una nueva era",
                url = "http://www.twitch.tv/ssr765"
                )
        )

        # Eliminar comando antiguo "help".
        self.remove_command("help")

    async def on_ready(self):
        asciiart.crear()
        print(f"> {self.user} {Fore.GREEN}conectado{Fore.RESET}")
        print(f"> Discord.py version: {discord.__version__}")
        for x in no_cargados:
            print(f"> {Fore.RED}⚠  {x} no se ha podido cargar. {Fore.RESET}")

ssr765client = client()

# Cargar los modulos.
async def cargar_extensiones():
    modulos = os.listdir("modulos")
    modulos.remove("__pycache__") if "__pycache__" in modulos else None
    for cog in [cog[:-3] for cog in modulos]:
        try:
            await ssr765client.load_extension(f"modulos.{cog}")

        except:
            print(f"{Fore.RED}⚠  {cog} no se ha podido cargar. {Fore.RESET}")
            no_cargados.append(cog)

        else:
            print(f"{Fore.GREEN}✔  {cog} se ha cargado correctamente. {Fore.RESET}")

asyncio.run(cargar_extensiones())

ssr765client.run(TOKEN)