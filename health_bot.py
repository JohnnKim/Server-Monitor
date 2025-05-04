import psutil
import discord
from discord.ext import commands, tasks
from datetime import datetime
import platform
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")  # Bot token
TARGET_CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))  # Discord channel to report to

# Health check configuration
INTERVAL_SECONDS = 60  # Time between health reports in seconds
CPU_WARN = 85.0        # CPU usage warning threshold (%)
MEM_WARN = 90.0        # Memory usage warning threshold (%)
DISK_WARN = 90.0       # Disk usage warning threshold (%)

# Bot setup with necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# System Info Helpers
def get_health_snapshot():
    """Collects current CPU, memory, and disk usage statistics."""
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent
    }

def get_status_color(cpu, mem, disk):
    """Determines the color and warning messages based on usage thresholds."""
    warnings = []
    if cpu >= CPU_WARN:
        warnings.append("High CPU usage")
    if mem >= MEM_WARN:
        warnings.append("High Memory usage")
    if disk >= DISK_WARN:
        warnings.append("High Disk usage")
    return (discord.Color.red(), warnings) if warnings else (discord.Color.green(), ["All systems normal"])

def get_uptime():
    """Calculates how long the system has been running."""
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    now = datetime.now()
    uptime = now - boot_time
    return str(uptime).split(".")[0]  # Remove microseconds

def is_admin():
    """Check if the command caller is a Discord admin."""
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

# Events
@bot.event
async def on_ready():
    """Runs when the bot successfully connects to Discord."""
    print(f"Logged in as {bot.user.name}")
    health_ping.start()  # Start the periodic health check loop

# Periodic Health Check Task
@tasks.loop(seconds=INTERVAL_SECONDS)
async def health_ping():
    """Sends system health reports to the specified Discord channel."""
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        print("Target channel not found.")
        return

    snap = get_health_snapshot()
    cpu, mem, disk = snap["cpu_percent"], snap["memory_percent"], snap["disk_percent"]
    color, warnings = get_status_color(cpu, mem, disk)

    embed = discord.Embed(title="Server Health Report", color=color)
    embed.add_field(name="Time", value=snap["timestamp"], inline=False)
    embed.add_field(name="CPU Usage", value=f"{cpu:.1f}%", inline=True)
    embed.add_field(name="Memory Usage", value=f"{mem:.1f}%", inline=True)
    embed.add_field(name="Disk Usage", value=f"{disk:.1f}%", inline=True)
    embed.add_field(name="Status", value="\n".join(warnings), inline=False)

    await channel.send(embed=embed)

# Commands
@bot.command(name="uptime")
async def uptime(ctx):
    """Shows how long the system has been running."""
    await ctx.send(f"Uptime: `{get_uptime()}`")

@bot.command(name="shutdown")
@is_admin()
async def shutdown(ctx):
    """Shuts down the machine (admin only)."""
    await ctx.send("Shutting down system...")
    os.system("shutdown /s /t 5")  # Windows; use `shutdown -h now` on Linux

@bot.command(name="restart")
@is_admin()
async def restart(ctx):
    """Restarts the machine (admin only)."""
    await ctx.send("Restarting system...")
    os.system("shutdown /r /t 5")  # Windows; use `reboot` on Linux

@bot.command(name="top")
async def top_processes(ctx, count: int = 5):
    """Shows the top N CPU-consuming processes."""
    processes = sorted(
        psutil.process_iter(['pid', 'name', 'cpu_percent']),
        key=lambda p: p.info['cpu_percent'],
        reverse=True
    )[:count]
    msg = "\n".join(f"PID {p.info['pid']}: {p.info['name']} ({p.info['cpu_percent']}%)" for p in processes)
    await ctx.send(f"Top {count} CPU Processes:\n```{msg}```")

@bot.command(name="ping")
async def ping(ctx):
    """Check bot latency."""
    await ctx.send(f"Pong! Latency: `{round(bot.latency * 1000)}ms`")

# run bot
bot.run(TOKEN)
