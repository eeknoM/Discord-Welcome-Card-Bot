import discord
from discord.ext import commands
import os
import json
import welcomer

with open('config.json') as config_file:
    config = json.load(config_file)

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

welcomer.setup_welcomer(bot)

bot.run(config['bot_token'])
