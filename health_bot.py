import discord
from discord.ext import commands, tasks
import json
import os

TOKEN = "YOUR_DISCORD_BOT_TOKEN"  # Replace with bot's token
CHANNEL_ID = 123456789012345678   # Replace with target channel ID
LOG_FILE = "server_health_log.json"
INTERVAL_SECONDS = 300  # interval in seconds

# Thresholds for warnings
CPU_WARN = 85.0
MEM_WARN = 90.0
DISK_WARN = 90.0

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def read_latest_snapshot():
    """
    Reads the latest snapshot from the log file.
    Returns the most recent data entry as a dictionary.
    """
    if not os.path.exists(LOG_FILE):
        return None
    with open(LOG_FILE, "r") as f:
        data = json.load(f)
        if data:
            return data[-1]
    return None

def get_status_color(cpu, mem, disk):
    """
    Determines the color and warning messages for the embed
    based on current system metrics and thresholds.
    Returns a tuple: (color, list of warning strings)
    """
    warnings = []
    if cpu >= CPU_WARN:
        warnings.append("High CPU usage")
    if mem >= MEM_WARN:
        warnings.append("High Memory usage")
    if disk >= DISK_WARN:
        warnings.append("High Disk usage")

    if warnings:
        return discord.Color.red(), warnings
    return discord.Color.green(), ["All systems normal"]

@bot.event
async def on_ready():
    """
    Called when the bot has successfully connected.
    Starts the health reporting task.
    """
    print(f"Logged in as {bot.user.name}")
    health_ping.start()

@tasks.loop(seconds=INTERVAL_SECONDS)
async def health_ping():
    """
    Scheduled task that reads the latest system health snapshot
    and sends it as an embed message to the configured channel.
    """
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Channel not found.")
        return

    snapshot = read_latest_snapshot()
    if not snapshot:
        await channel.send("No health data available.")
        return

    cpu = snapshot["cpu_percent"]
    mem = snapshot["memory_percent"]
    disk = snapshot["disk_percent"]
    color, warnings = get_status_color(cpu, mem, disk)

    embed = discord.Embed(title="Server Health Report", color=color)
    embed.add_field(name="Time", value=snapshot["timestamp"], inline=False)
    embed.add_field(name="CPU Usage", value=f"{cpu}%", inline=True)
    embed.add_field(name="Memory Usage", value=f"{mem}%", inline=True)
    embed.add_field(name="Disk Usage", value=f"{disk}%", inline=True)
    embed.add_field(name="Status", value="\n".join(warnings), inline=False)

    await channel.send(embed=embed)

# Run
bot.run(TOKEN)
