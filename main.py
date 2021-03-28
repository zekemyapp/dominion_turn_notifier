import os
from dotenv import load_dotenv
from enum import Enum

import requests
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_NAME')
URL_PATTERN = 'https://dom5.snek.earth/api/games/%s/status'
GAME_ID = "2579"

class ControllerType(Enum):
    NONE = 0
    HUMAN = 1
    AI = 2

class TurnState(Enum):
    WAITING = 0
    IN_PROGRESS = 1
    DONE = 2

'''
@return json containing game data
'''
def fetch_game_data():
    response = requests.get(URL_PATTERN % GAME_ID)
    return response.json()

'''
@return string with the current state of human players
'''
def get_status():
    json_data = fetch_game_data()
    nations = json_data['nations']
    cache = ""
    for nation in nations:
        if ControllerType(int(nation['controller'])) is ControllerType.HUMAN:
            current = nation['name'] + ': ' + TurnState(int(nation['turnplayed'])).name
            cache += current + "\n"
    return cache

'''
@return user friendly string of players with pending turns
'''
def get_pending_turns():
    json_data = fetch_game_data()
    nations = json_data['nations']
    cache = "Waiting for:\n"
    for nation in nations:
        if (ControllerType(int(nation['controller'])) is ControllerType.HUMAN
                and TurnState(int(nation['turnplayed'])) is not TurnState.DONE):
            current = '\t- ' + nation['name']
            cache += current + "\n"
    return cache

client = discord.Client()
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if (guild.name == GUILD):
            print(
                f'{bot.user} is connected to the following guild:\n'
                f'{guild.name}(id: {guild.id})'
            )

@bot.command()
async def status(ctx):
    for guild in bot.guilds:
        if (guild.name == GUILD):
            await ctx.send(get_pending_turns())

bot.run(TOKEN)