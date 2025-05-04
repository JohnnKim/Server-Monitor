import psutil
import discord
from discord.ext import commands, tasks
from datetime import datetime
import platform
import asyncio
import os

# Config
TOKEN = "YOUR_DISCORD_BOT_TOKEN"  # Replace with your bot token
CHANNEL_ID = 123456789012345678   # Replace with your Discord channel ID
INTERVAL_SECONDS = 300            # Health report interval (seconds)

# Warning thresholds
CPU_WARN = 85.0
MEM_WARN = 90.0
DISK_WARN = 90.0

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# System info
def get_health_snapshot():
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent
    }

def get_status_color(cpu, mem, disk):
    warnings = []
    if cpu >= CPU_WARN:
        warnings.append("High CPU usage")
    if mem >= MEM_WARN:
        warnings.append("High Memory usage")
    if disk >= DISK_WARN:
        warnings.append("High Disk usage")
    return (discord.Color.red(), warnings) if warnings else (discord.Color.green(), ["All systems normal"])

def get_uptime():
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    now = datetime.now()
    uptime = now - boot_time
    return str(uptime).split(".")[0]

# Check if user is an admin
def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

# Events
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    health_ping.start()

# Looped Task
@tasks.loop(seconds=INTERVAL_SECONDS)
async def health_ping():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Channel not found.")
        return

    snap = get_health_snapshot()
    cpu, mem, disk = snap["cpu_percent"], snap["memory_percent"], snap["disk_percent"]
    color, warnings = get_status_color(cpu, mem, disk)

    embed = discord.Embed(title="Server Health Report", color=color)
    embed.add_field(name="Time", value=snap["timestamp"], inline=False)
    embed.add_field(name="CPU Usage", value=f"{cpu}%", inline=True)
    embed.add_field(name="Memory Usage", value=f"{mem}%", inline=True)
    embed.add_field(name="Disk Usage", value=f"{disk}%", inline=True)
    embed.add_field(name="Status", value="\n".join(warnings), inline=False)

    await channel.send(embed=embed)

# Commands

@bot.command(name="uptime")
async def uptime(ctx):
    """Show how long the system has been running."""
    await ctx.send(f"Uptime: `{get_uptime()}`")

@bot.command(name="shutdown")
@is_admin()
async def shutdown(ctx):
    """Shutdown the server (admin only)."""
    await ctx.send("Shutting down system...")
    os.system("shutdown /s /t 5")  # Windows. Use `shutdown -h now` for Linux

@bot.command(name="restart")
@is_admin()
async def restart(ctx):
    """Restart the server (admin only)."""
    await ctx.send("Restarting system...")
    os.system("shutdown /r /t 5")  # Windows. Use `reboot` for Linux

@bot.command(name="top")
async def top_processes(ctx, count: int = 5):
    """Show top CPU-consuming processes."""
    processes = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']), key=lambda p: p.info['cpu_percent'], reverse=True)[:count]
    msg = "\n".join(f"PID {p.info['pid']}: {p.info['name']} ({p.info['cpu_percent']}%)" for p in processes)
    await ctx.send(f"Top {count} CPU Processes:\n```{msg}```")

@bot.command(name="ping")
async def ping(ctx):
    """Bot latency check."""
    await ctx.send(f"Pong! Latency: `{round(bot.latency * 1000)}ms`")

# Run
bot.run(TOKEN)
