import discord
from discord.ext import commands
import os
import json
import welcomer

#load JSON file
with open('config.json') as config_file:
    config = json.load(config_file)

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

#setup welcomer module
welcomer.setup_welcomer(bot)

bot.run(config['bot_token'])
