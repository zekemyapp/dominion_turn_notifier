import os
import datetime
from dotenv import load_dotenv
from enum import Enum

import requests
import discord
from discord.ext import commands, timers

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_NAME')
URL_PATTERN_STATE = 'https://dom5.snek.earth/api/games/%s/status'
URL_PATTERN_GAME = 'https://dom5.snek.earth/api/games/%s'

GAME_ID = None

cached_state = {}

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
def fetch_game_status():
    response = requests.get(URL_PATTERN_STATE % GAME_ID)
    return response.json()

def fetch_game_info():
    response = requests.get(URL_PATTERN_GAME % GAME_ID)
    return response.json()

def error_no_id():
    return 'Please asign a game id using !set_id'

'''
@return string with the current state of human players
'''
def get_status():
    if GAME_ID is None:
        return (True, True, error_no_id())
    json_data = fetch_game_status()
    nations = json_data['nations']
    cache = ""
    changed = False
    all_done = False
    for nation in nations:
        is_done = (TurnState(int(nation['turnplayed'])) == TurnState.DONE)
        if ControllerType(int(nation['controller'])) is ControllerType.HUMAN:
            if nation['nationid'] in cached_state :
                if cached_state[nation['nationid']] != is_done:
                    changed = True
            else:
                changed = True

            if cached_state[nation['nationid']] and not is_done:
                all_done = True

            cached_state[nation['nationid']] = is_done    
            current = nation['name'] + ': ' + TurnState(int(nation['turnplayed'])).name
            cache += current + "\n"
    return (changed, all_done, cache)

'''
@return user friendly string of players with pending turns
'''
def get_pending_turns():
    if GAME_ID is None:
        return "Please asign a game id using !set_id"
    json_data = fetch_game_status()
    nations = json_data['nations']
    cache = "Waiting for:\n"
    for nation in nations:
        if (ControllerType(int(nation['controller'])) is ControllerType.HUMAN
                and TurnState(int(nation['turnplayed'])) is not TurnState.DONE):
            current = '\t- ' + nation['name']
            cache += current + "\n"
    return cache

def get_game_name():
    if GAME_ID is None:
        return error_no_id()
    json_data = fetch_game_info()
    return json_data['name']


client = discord.Client()
bot = commands.Bot(command_prefix='!')
bot.timer_manager = timers.TimerManager(bot)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if (guild.name == GUILD):
            print(bot.user.name + ' is connected to the following guild:\n' + guild.name)

@bot.command()
async def help_dom(ctx):
    cache = "Usage:\n"
    cache += "\t!help: Print current help.\n"
    cache += "\t!set_id: Set the id of the game.\n"
    cache += "\t!status <id>: Show the status of a game.\n"
    cache += "\t!set_reminder: Not implemented.\n"
    await ctx.send(cache)

@bot.command()
async def set_id(ctx, id):
    global GAME_ID
    GAME_ID = id
    await ctx.send("ID set to " + GAME_ID)
    await ctx.send("Welcome to " + get_game_name() + "!")

@bot.command()
async def status(ctx):
    for guild in bot.guilds:
        if (guild.name == GUILD):
            await ctx.send(get_pending_turns())

@bot.command()
async def set_reminder(ctx):
    time_now = datetime.datetime.utcnow()
    time_dt = datetime.timedelta(seconds = 10)
    time_now += time_dt
    bot.timer_manager.clear()
    bot.timer_manager.create_timer("reminder", time_now, args=(ctx.channel.id, ctx.author.id, 600))
    await ctx.send("Turn notifier started.")


@bot.command()
async def stop_reminder(ctx):
    bot.timer_manager.clear()
    await ctx.send("Turn notifier stopped.")

@bot.event
async def on_reminder(channel_id, author_id, seconds):
    time_now = datetime.datetime.utcnow()
    time_dt = datetime.timedelta(seconds = seconds)
    time_now += time_dt
    bot.timer_manager.create_timer("reminder", time_now, args=(channel_id, author_id, seconds))

    is_changed, all_done, cache = get_status()
    print("timer is running:\n"+str(is_changed)+"\n"+str(all_done)+"\n"+cache)
    channel = bot.get_channel(channel_id)
    if (is_changed and all_done):
        await channel.send("Attention Pretenders!\nA new turn has started\n")


bot.run(TOKEN)