import discord
from discord.ext import commands
import os
import json
import welcomer

# Load the JSON configuration file
try:
    with open('config.json') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print("Error: The configuration file 'config.json' was not found.")
    exit(1)
except json.JSONDecodeError:
    print("Error: The configuration file 'config.json' is not a valid JSON.")
    exit(1)

# Initialize bot intents (permissions)
intents = discord.Intents.default()
intents.members = True  # Needed to track member updates (e.g., joins)

# Create the bot instance with the specified command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Setup the welcomer module if it's enabled in the configuration
if config.get('welcomer_module', False):  # Defaults to False if not specified
    try:
        welcomer.setup_welcomer(bot)
        print("Welcomer module has been successfully set up.")
    except Exception as e:
        print(f"Error setting up the welcomer module: {e}")
else:
    print("Welcomer module is disabled in the configuration.")

# Run the bot using the token from the configuration file
try:
    bot.run(config['bot_token'])
except discord.LoginFailure:
    print("Error: The bot token is invalid.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
