# Server Health Monitor

A simple Discord bot that reports CPU, memory, and disk usage from a personal server or PC at regular intervals. 

Also includes moderation commands like !ping, !uptime, !top, !shutdown, and !restart.

## Setup

1. Install dependencies:
   pip install -r requirements.txt

2. Open server_monitor_bot.py:
   - Set your bot token
   - Set the channel ID
   - Optionally configure thresholds and interval

3. Run the bot:
   python server_monitor_bot.py

## How It Works

The bot collects system stats using psutil and sends a snapshot to a Discord channel at a fixed interval. 
It displays potential warnings when CPU, memory, or disk usage exceeds configured thresholds. 

Additional commands provide control and visibility into the system, including uptime tracking, active process usage, and optional shutdown or restart functionality.

## Requirements

- Python 3.8+
- discord.py >= 2.3.0
- psutil >= 5.9.0
