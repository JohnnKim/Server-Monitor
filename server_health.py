import psutil
import json
import os
from datetime import datetime

# Config
LOG_FILE = "server_health_log.json" # Path to the log file
MAX_ENTRIES = 100  # Keep last 100 entries

def get_health_snapshot():
    """
    Collect current system health metrics.
    - CPU usage (%)
    - Memory usage (%)
    - Disk usage (%)
    """
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Current timestamp
        "cpu_percent": psutil.cpu_percent(interval=1),             # Average CPU usage over 1 second
        "memory_percent": psutil.virtual_memory().percent,         # RAM usage
        "disk_percent": psutil.disk_usage("/").percent             # Disk usage on root partition
    }

def load_log():
    """
    Load existing log from file if it exists.
    Returns a list of previous snapshots.
    """
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []   # Return empty list if log file doesn't exist

def save_log(log):
    """
    Save the updated list of snapshots to the log file in JSON format.
    """
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

def main():
    """
    Main execution:
    - Load previous log entries
    - Append new snapshot
    - Trim log to keep only the last MAX_ENTRIES
    - Save updated log
    """
    log = load_log()
    snapshot = get_health_snapshot()
    log.append(snapshot)

    # Keep only the last MAX_ENTRIES
    if len(log) > MAX_ENTRIES:
        log = log[-MAX_ENTRIES:]

    save_log(log)
    print(f"Logged system health at {snapshot['timestamp']}")

# Run
if __name__ == "__main__":
    main()
