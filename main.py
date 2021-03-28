import os
from dotenv import load_dotenv
from enum import Enum

import requests
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_NAME')

class ControllerType(Enum):
    NONE = 0
    HUMAN = 1
    AI = 2

class TurnState(Enum):
    WAITING = 0
    UNKNOWN = 1
    DONE = 2

def update_cache():
    response = requests.get('https://dom5.snek.earth/api/games/2579/status')
    json_data = response.json()
    nations = json_data['nations']

    cache = ""

    for nation in nations:
        if ControllerType(int(nation['controller'])) is ControllerType.HUMAN:
            current = nation['name'] + ': ' + TurnState(int(nation['turnplayed'])).name
            cache += current + "\n"
    return cache

client = discord.Client()
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if (guild.name == GUILD):
            channel = discord.utils.get(guild.text_channels, name="general")
            print(
                f'{bot.user} is connected to the following guild:\n'
                f'{guild.name}(id: {guild.id})'
            )

@bot.command()
async def status(ctx):
    for guild in bot.guilds:
        if (guild.name == GUILD):
            channel = discord.utils.get(guild.text_channels, name="los_amigos_del_dominion")
            await channel.send(update_cache())

bot.run(TOKEN)