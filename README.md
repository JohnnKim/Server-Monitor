# Server Health Monitor

A simple Discord bot that reports CPU, memory, and disk usage from a personal server or PC at regular intervals.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Open `server_monitor_bot.py`:
   - Set your bot token
   - Set the channel ID
   - Optionally configure thresholds and interval

3. Run:
   ```
   python server_monitor_bot.py
   ```

## How It Works

The bot collects system stats using `psutil` and sends the most recent snapshot to a Discord channel on a loop. Status is color-coded and warnings are listed if usage exceeds defined limits.

## Requirements

- Python 3.8+
- `discord.py` ≥ 2.3.0
- `psutil` ≥ 5.9.0
