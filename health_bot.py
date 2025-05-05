import psutil
import discord
from discord.ext import commands, tasks
from datetime import datetime
import os
from dotenv import load_dotenv
from threading import Thread
from flask import Flask, jsonify, render_template_string

# Load .env variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
TARGET_CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))

# Thresholds
INTERVAL_SECONDS = 60
CPU_WARN = 85.0
MEM_WARN = 90.0
DISK_WARN = 90.0

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def get_health_snapshot():
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent
    }

def get_status_color(cpu, mem, disk):
    warnings = []
    if cpu >= CPU_WARN: warnings.append("High CPU usage")
    if mem >= MEM_WARN: warnings.append("High Memory usage")
    if disk >= DISK_WARN: warnings.append("High Disk usage")
    return (discord.Color.red(), warnings) if warnings else (discord.Color.green(), ["All systems normal"])

def get_uptime():
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    return str(uptime).split(".")[0]

def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    health_ping.start()

@tasks.loop(seconds=INTERVAL_SECONDS)
async def health_ping():
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel: return

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

@bot.command(name="uptime")
async def uptime(ctx):
    await ctx.send(f"Uptime: `{get_uptime()}`")

@bot.command(name="shutdown")
@is_admin()
async def shutdown(ctx):
    await ctx.send("Shutting down system...")
    os.system("shutdown /s /t 5")

@bot.command(name="restart")
@is_admin()
async def restart(ctx):
    await ctx.send("Restarting system...")
    os.system("shutdown /r /t 5")

@bot.command(name="top")
async def top_processes(ctx, count: int = 5):
    processes = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']),
                       key=lambda p: p.info['cpu_percent'], reverse=True)[:count]
    msg = "\n".join(f"PID {p.info['pid']}: {p.info['name']} ({p.info['cpu_percent']}%)" for p in processes)
    await ctx.send(f"Top {count} CPU Processes:\n```{msg}```")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! Latency: `{round(bot.latency * 1000)}ms`")

@bot.command(name="net")
async def net(ctx):
    io = psutil.net_io_counters()
    conns = len(psutil.net_connections())
    await ctx.send(f"**Network I/O**\nSent: `{io.bytes_sent / 1_000_000:.2f} MB`\nReceived: `{io.bytes_recv / 1_000_000:.2f} MB`\nActive Connections: `{conns}`")

# Flask App
app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu": float(psutil.cpu_percent(interval=0.2)),
        "memory": float(psutil.virtual_memory().percent),
        "disk": float(psutil.disk_usage("/").percent),
        "uptime": get_uptime()
    })

dashboard_template = """
<!DOCTYPE html>
<html>
<head>
  <title>Server Health Dashboard</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    canvas { max-height: 200px; }
  </style>
  <script>
    let cpuChart, memoryChart, diskChart;

    function getColor(value) {
      if (value >= 90) return '#e74c3c';    // red
      if (value >= 70) return '#f1c40f';    // yellow
      return '#27ae60';                     // darker green
    }

    async function fetchStats() {
      const res = await fetch('/health');
      const data = await res.json();

      document.getElementById('cpu').innerText = data.cpu + '%';
      document.getElementById('memory').innerText = data.memory + '%';
      document.getElementById('disk').innerText = data.disk + '%';
      document.getElementById('uptime').innerText = data.uptime;
      document.getElementById('timestamp').innerText = data.time;

      const updateChart = (chart, value) => {
        const dataset = chart.data.datasets[0];
        chart.data.labels.push('');
        dataset.data.push(value);
        dataset.borderColor = getColor(value);
        if (dataset.data.length > 20) {
          dataset.data.shift();
          chart.data.labels.shift();
        }
        chart.update();
      };

      updateChart(cpuChart, parseFloat(data.cpu));
      updateChart(memoryChart, parseFloat(data.memory));
      updateChart(diskChart, parseFloat(data.disk));
    }

    setInterval(fetchStats, 5000);

    window.onload = () => {
      const createChart = (id, label) => {
        const ctx = document.getElementById(id).getContext('2d');
        return new Chart(ctx, {
          type: 'line',
          data: {
            labels: [],
            datasets: [{
              label,
              data: [],
              borderColor: '#27ae60',
              backgroundColor: 'transparent',
              tension: 0.1
            }]
          },
          options: {
            animation: false,
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
                max: 100,
                ticks: {
                  color: '#ccc',
                  font: { size: 14 }
                }
              },
              x: {
                ticks: {
                  color: '#ccc',
                  font: { size: 14 }
                }
              }
            },
            plugins: {
              legend: {
                display: true,
                labels: {
                  color: '#eee',
                  font: { size: 16 }
                }
              }
            }
          }
        });
      };

      cpuChart = createChart('cpuChart', 'CPU Usage (%)');
      memoryChart = createChart('memoryChart', 'Memory Usage (%)');
      diskChart = createChart('diskChart', 'Disk Usage (%)');
      fetchStats();
    };
  </script>
</head>
<body class="bg-dark text-white">
  <div class="container py-4">
    <h2 class="mb-3">Server Health Dashboard</h2>
    <div class="row mb-2">
      <div class="col-sm-6 col-md-3"><strong>CPU:</strong> <span id="cpu">-</span></div>
      <div class="col-sm-6 col-md-3"><strong>Memory:</strong> <span id="memory">-</span></div>
      <div class="col-sm-6 col-md-3"><strong>Disk:</strong> <span id="disk">-</span></div>
      <div class="col-sm-6 col-md-3"><strong>Uptime:</strong> <span id="uptime">-</span></div>
    </div>
    <div class="mb-3"><strong>Timestamp:</strong> <span id="timestamp">-</span></div>
    <div class="mb-4">
      <h5>CPU Usage</h5>
      <canvas id="cpuChart" class="w-100 my-3"></canvas>
      <h5>Memory Usage</h5>
      <canvas id="memoryChart" class="w-100 my-3"></canvas>
      <h5>Disk Usage</h5>
      <canvas id="diskChart" class="w-100 my-3"></canvas>
    </div>
  </div>
</body>
</html>
"""

@app.route("/dashboard")
def dashboard():
    return render_template_string(dashboard_template)

def run_flask():
    app.run(host="0.0.0.0", port=5000)

# Start Flask app in thread
flask_thread = Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# Start bot
bot.run(TOKEN)
