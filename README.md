# Server Health Monitor

[![Downloads](https://img.shields.io/github/downloads/JohnnKim/Server-Monitor/total.svg)](https://github.com/JohnnKim/Server-Monitor/releases)
[![Repo Size](https://img.shields.io/github/repo-size/JohnnKim/Server-Monitor.svg)](https://github.com/JohnnKim/Server-Monitor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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

- Uses `psutil` to monitor:
  - CPU usage (%)
  - Memory usage (%)
  - Disk usage (%)

- Sends a report to your configured Discord channel every `60` seconds.

- Provides a **live dashboard** at `http://localhost:5000/dashboard`  
  → Includes labeled charts with color-coded usage levels (green/yellow/red).

- Thresholds:
  - CPU ≥ 85%
  - Memory ≥ 90%
  - Disk ≥ 90%

---

## Commands

| Command     | Description                                |
|-------------|--------------------------------------------|
| `!ping`     | Check if the bot is online                 |
| `!uptime`   | Get system uptime                          |
| `!top`      | List top CPU-consuming processes           |
| `!shutdown` | Shut down the system (admin only)          |
| `!restart`  | Restart the system (admin only)            |
| `!net`      | Show network traffic and connections       |

---

## Requirements

- Python 3.8+
- `discord.py` ≥ 2.3.0
- `psutil` ≥ 5.9.0
- `python-dotenv`
- `flask` (for dashboard)

Install all dependencies:
```
pip install -r requirements.txt
```

---

## Security Disclaimer

This bot includes commands that can shut down or restart your machine. It is meant for private/local use only.

NEVER share or commit your `.env` file. Treat your DISCORD_TOKEN as a secret key, anyone with it can control your bot and potentially your system.

If distributing the bot, make sure the token is only used on trusted machines and servers.
