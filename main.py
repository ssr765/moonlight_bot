import os
import aiohttp
import discord
from discord.ext import commands
from colorama import Fore
from dotenv import load_dotenv

from load_config import config
from config.asciiart_generator import asciiart

# Obtener token.
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class client(commands.Bot):
    def __init__(self, config):
        super().__init__(
            command_prefix = commands.when_mentioned_or(config.prefix),
            intents = discord.Intents.all(),
            activity = discord.Streaming(
            name="una nueva era",
            url="http://www.twitch.tv/ssr765"
            )
        )

        self.config = config

        # Eliminar comando antiguo "help".
        self.remove_command("help")

        # Generar lista de modulos.
        self.initial_modules = os.listdir("modulos")
        if "__pycache__" in self.initial_modules:
            self.initial_modules.remove("__pycache__")
        else:
            pass

        # Lista para mostrar los modulos que no se han cargado.
        # Estos se mostrarán después de borrar la pantalla con el ASCII art.
        self.uncharged_modules = []

    async def on_ready(self):
        asciiart.crear()
        print(f"> {self.user} {Fore.GREEN}conectado{Fore.RESET}")
        print(f"> Discord.py version: {discord.__version__}")
        for x in self.uncharged_modules:
            print(f"> {Fore.RED}⚠  {x} no se ha podido cargar. {Fore.RESET}")
    
    async def setup_hook(self):
        self.session = aiohttp.ClientSession()

        # Cargar modulos.
        for cog in [cog[:-3] for cog in self.initial_modules]:
            try:
                await ssr765client.load_extension(f"modulos.{cog}")

            except:
                print(f"{Fore.RED}⚠  {cog} no se ha podido cargar."
                    f"{Fore.RESET}")
                self.uncharged_modules.append(cog)

            else:
                print(f"{Fore.GREEN}✔  {cog} se ha cargado correctamente."
                    f"{Fore.RESET}")

ssr765client = client(config())
ssr765client.run(TOKEN)