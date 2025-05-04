import psutil
import discord
from discord.ext import commands, tasks
from datetime import datetime

# Config
TOKEN = "YOUR_DISCORD_BOT_TOKEN"  # Replace with your actual bot token
CHANNEL_ID = 123456789012345678   # Replace with your target Discord channel ID
INTERVAL_SECONDS = 300            # Send update every 5 minutes

# Warning thresholds
CPU_WARN = 85.0
MEM_WARN = 90.0
DISK_WARN = 90.0

# Discord bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Health Snapshot
def get_health_snapshot():
    """
    Collect and return current system health metrics.
    - CPU usage (%)
    - Memory usage (%)
    - Disk usage (%)
    """
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent
    }

def get_status_color(cpu, mem, disk):
    """
    Determines embed color and warning messages based on thresholds.
    Returns a tuple: (discord.Color, list of warning strings)
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

# Bot events
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    health_ping.start()

# Health Report
@tasks.loop(seconds=INTERVAL_SECONDS)
async def health_ping():
    """
    Runs every INTERVAL_SECONDS to check system health and send a report.
    """
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Channel not found.")
        return

    snapshot = get_health_snapshot()
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

# run bot
bot.run(TOKEN)
