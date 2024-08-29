# Discord Welcomer Bot

A module based Discord bot that welcomes new members to your server with a custom GIF and assigns them a role. The bot uses the `discord.py` library and supports dynamic configuration via a JSON file.

## Features

- **Welcomes New Members:** Sends a personalized welcome message with a custom GIF to new members who join your server.
- **Role Assignment:** Automatically assigns a specified role to new members.
- **Customizable Configuration:** Easily configurable using a JSON file.
- **Font and Image Handling:** Utilizes custom fonts and processes user avatars for a personalized welcome card.

## Prerequisites

- Python 3.8 or higher
- `discord.py` library
- `Pillow` library for image processing
- `requests` library for HTTP requests

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/discord-welcomer-bot.git
   cd discord-welcomer-bot
