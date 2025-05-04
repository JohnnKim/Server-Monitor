# Server Health Monitor

A Discord bot for monitoring the health of your personal server or PC.

It reports CPU, RAM, and disk usage at specified intervals, and includes basic moderation and control commands like `!ping`, `!uptime`, `!top`, `!shutdown`, and `!restart`.

---

## Setup

1. Install dependencies:
   pip install -r requirements.txt

2. Create a `.env` file in the root directory (same level as `health_bot.py`):

   DISCORD_TOKEN=your_bot_token_here
   CHANNEL_ID=123456789012345678

   - DISCORD_TOKEN is your bot's secret token from the Discord Developer Portal.
   - CHANNEL_ID is the numeric ID of the channel where health reports will be sent.

3. Run the bot manually:
   python health_bot.py

   Or compile to an `.exe` for standalone use.

---

## How It Works

- The bot uses `psutil` to collect system health data and sends periodic updates to a Discord channel.
- Warnings are shown when CPU, memory, or disk usage exceeds configured thresholds.
- Built-in commands:
  - !ping – Check if the bot is alive
  - !uptime – Display how long the system has been running
  - !top – Show the top CPU-consuming processes
  - !shutdown – Shut down the system (admin only)
  - !restart – Restart the system (admin only)

---

## Requirements

- Python 3.8 or higher
- discord.py >= 2.3.0
- psutil >= 5.9.0
- python-dotenv

Install with:
   pip install -r requirements.txt

---

## Security Disclaimer

This bot includes commands that can shut down or restart your machine. It is meant for private/local use only.

NEVER share or commit your `.env` file. Treat your DISCORD_TOKEN as a secret key, anyone with it can control your bot and potentially your system.

If distributing the bot, make sure the token is only used on trusted machines and servers.
