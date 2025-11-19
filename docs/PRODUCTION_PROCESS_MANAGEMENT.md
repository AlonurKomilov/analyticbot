# Production Process Management Guide

## Problem: Orphaned Child Processes in Production

When parent processes are killed without proper cleanup, child processes (multiprocessing workers) become orphaned and continue consuming RAM indefinitely.

## Professional Solutions

### ⭐ Solution 1: Systemd Services (RECOMMENDED for Production Linux)

Systemd automatically handles process cleanup with proper configuration.

#### Create Service Files

**1. API Service:**
```bash
sudo nano /etc/systemd/system/analyticbot-api.service
```

```ini
[Unit]
Description=AnalyticBot API Service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=abcdeveloper
Group=abcdeveloper
WorkingDirectory=/home/abcdeveloper/projects/analyticbot
Environment="PATH=/home/abcdeveloper/projects/analyticbot/.venv/bin:/usr/local/bin:/usr/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/home/abcdeveloper/projects/analyticbot/.env.production

# Main command
ExecStart=/home/abcdeveloper/projects/analyticbot/.venv/bin/uvicorn apps.api.main:app \
    --host 0.0.0.0 \
    --port 11400 \
    --workers 4

# Graceful shutdown
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
SendSIGKILL=yes

# Restart policy
Restart=always
RestartSec=10

# Resource limits
LimitNOFILE=65536
MemoryMax=2G

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=analyticbot-api

[Install]
WantedBy=multi-user.target
```

**2. Bot Service:**
```bash
sudo nano /etc/systemd/system/analyticbot-bot.service
```

```ini
[Unit]
Description=AnalyticBot Telegram Bot
After=network.target analyticbot-api.service
Wants=analyticbot-api.service

[Service]
Type=simple
User=abcdeveloper
Group=abcdeveloper
WorkingDirectory=/home/abcdeveloper/projects/analyticbot
Environment="PATH=/home/abcdeveloper/projects/analyticbot/.venv/bin:/usr/local/bin:/usr/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/home/abcdeveloper/projects/analyticbot/.env.production

ExecStart=/home/abcdeveloper/projects/analyticbot/.venv/bin/python -m apps.bot.run_bot

# Cleanup child processes properly
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=analyticbot-bot

[Install]
WantedBy=multi-user.target
```

**3. MTProto Worker Service:**
```bash
sudo nano /etc/systemd/system/analyticbot-mtproto.service
```

```ini
[Unit]
Description=AnalyticBot MTProto Data Collection Worker
After=network.target analyticbot-api.service
Wants=analyticbot-api.service

[Service]
Type=simple
User=abcdeveloper
Group=abcdeveloper
WorkingDirectory=/home/abcdeveloper/projects/analyticbot
Environment="PATH=/home/abcdeveloper/projects/analyticbot/.venv/bin:/usr/local/bin:/usr/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/home/abcdeveloper/projects/analyticbot/.env.production

ExecStart=/home/abcdeveloper/projects/analyticbot/.venv/bin/python -m apps.mtproto.worker --interval 10

# CRITICAL: Kill all child processes (multiprocessing workers)
KillMode=control-group
KillSignal=SIGTERM
TimeoutStopSec=60
SendSIGKILL=yes

Restart=always
RestartSec=30

# Resource limits (each multiprocessing child uses ~800MB)
MemoryMax=4G
TasksMax=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=analyticbot-mtproto

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services (start on boot)
sudo systemctl enable analyticbot-api
sudo systemctl enable analyticbot-bot
sudo systemctl enable analyticbot-mtproto

# Start services
sudo systemctl start analyticbot-api
sudo systemctl start analyticbot-bot
sudo systemctl start analyticbot-mtproto

# Check status
sudo systemctl status analyticbot-api
sudo systemctl status analyticbot-bot
sudo systemctl status analyticbot-mtproto

# View logs
sudo journalctl -u analyticbot-mtproto -f
```

#### Key Systemd Features

- **`KillMode=mixed`**: Sends SIGTERM to main process, SIGKILL to children
- **`KillMode=control-group`**: Kills ALL processes in the cgroup (better for multiprocessing)
- **`TimeoutStopSec=60`**: Wait 60s for graceful shutdown before force kill
- **`SendSIGKILL=yes`**: Force kill if graceful shutdown fails
- **`Restart=always`**: Auto-restart on failure
- **`MemoryMax=4G`**: Prevent runaway memory usage
- **`TasksMax=10`**: Limit max child processes

---

### ⭐ Solution 2: Supervisor (Easier, Cross-Platform)

Install Supervisor:
```bash
sudo apt install supervisor  # Debian/Ubuntu
# or
sudo yum install supervisor  # CentOS/RHEL
```

**Configuration:**
```bash
sudo nano /etc/supervisor/conf.d/analyticbot.conf
```

```ini
[program:analyticbot-api]
command=/home/abcdeveloper/projects/analyticbot/.venv/bin/uvicorn apps.api.main:app --host 0.0.0.0 --port 11400 --workers 4
directory=/home/abcdeveloper/projects/analyticbot
user=abcdeveloper
autostart=true
autorestart=true
stopasgroup=true     ; Kills parent AND children
killasgroup=true     ; Force kills entire process group
stopwaitsecs=30
redirect_stderr=true
stdout_logfile=/var/log/analyticbot/api.log
environment=PATH="/home/abcdeveloper/projects/analyticbot/.venv/bin:/usr/bin"

[program:analyticbot-bot]
command=/home/abcdeveloper/projects/analyticbot/.venv/bin/python -m apps.bot.run_bot
directory=/home/abcdeveloper/projects/analyticbot
user=abcdeveloper
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stopwaitsecs=30
redirect_stderr=true
stdout_logfile=/var/log/analyticbot/bot.log

[program:analyticbot-mtproto]
command=/home/abcdeveloper/projects/analyticbot/.venv/bin/python -m apps.mtproto.worker --interval 10
directory=/home/abcdeveloper/projects/analyticbot
user=abcdeveloper
autostart=true
autorestart=true
stopasgroup=true     ; CRITICAL: Kills all multiprocessing children
killasgroup=true     ; CRITICAL: Force kills if needed
stopwaitsecs=60
redirect_stderr=true
stdout_logfile=/var/log/analyticbot/mtproto.log

[group:analyticbot]
programs=analyticbot-api,analyticbot-bot,analyticbot-mtproto
priority=999
```

**Usage:**
```bash
# Create log directory
sudo mkdir -p /var/log/analyticbot
sudo chown abcdeveloper:abcdeveloper /var/log/analyticbot

# Reload config
sudo supervisorctl reread
sudo supervisorctl update

# Control services
sudo supervisorctl start analyticbot:*
sudo supervisorctl stop analyticbot:*
sudo supervisorctl restart analyticbot:*
sudo supervisorctl status

# View logs
sudo supervisorctl tail -f analyticbot-mtproto
```

---

### ⭐ Solution 3: Enhanced Code with Context Managers

Improve your code to guarantee cleanup:

**Update `/home/abcdeveloper/projects/analyticbot/apps/mtproto/worker.py`:**

```python
import signal
import sys
from contextlib import asynccontextmanager

# Add signal handlers at module level
_shutdown_requested = False

def request_shutdown(signum, frame):
    """Handle shutdown signals gracefully"""
    global _shutdown_requested
    _shutdown_requested = True
    logger.info(f"🛑 Shutdown signal received ({signum}), finishing current work...")

# Register handlers
signal.signal(signal.SIGTERM, request_shutdown)
signal.signal(signal.SIGINT, request_shutdown)


@asynccontextmanager
async def managed_service():
    """Context manager that guarantees cleanup"""
    service = MTProtoDataCollectionService()
    pool_config = ConnectionPoolConfig.from_settings(service.settings)

    try:
        # Setup
        await init_connection_pool(pool_config)
        await service.initialize()
        logger.info("✅ Service initialized")

        yield service

    finally:
        # Cleanup ALWAYS runs, even on kill
        logger.info("🧹 Cleaning up resources...")
        try:
            await service.shutdown()
            await shutdown_connection_pool()
            logger.info("✅ Cleanup complete")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")


async def main():
    """Main entry point with guaranteed cleanup"""
    # ... parse args ...

    async with managed_service() as service:
        try:
            if args.once:
                # Run once and exit
                result = await service.collect_all_users()
                sys.exit(0 if result.get("success") else 1)
            else:
                # Continuous mode with graceful shutdown
                while not _shutdown_requested:
                    result = await service.collect_all_users()

                    if _shutdown_requested:
                        break

                    # Sleep with periodic wake-ups to check shutdown flag
                    for _ in range(args.interval * 60):
                        if _shutdown_requested:
                            break
                        await asyncio.sleep(1)

                logger.info("🛑 Graceful shutdown complete")

        except KeyboardInterrupt:
            logger.info("🛑 Interrupted by user")
            sys.exit(130)


if __name__ == "__main__":
    asyncio.run(main())
```

---

### ⭐ Solution 4: Resource Limits with cgroups

Prevent runaway processes from eating all RAM:

```bash
# Create cgroup for analyticbot
sudo cgcreate -g memory,cpu:analyticbot

# Set 6GB memory limit
sudo cgset -r memory.limit_in_bytes=6G analyticbot

# Set CPU limit (80% of 2 cores = 1.6 cores)
sudo cgset -r cpu.cfs_quota_us=160000 analyticbot
sudo cgset -r cpu.cfs_period_us=100000 analyticbot

# Run your service in the cgroup
sudo cgexec -g memory,cpu:analyticbot python -m apps.mtproto.worker
```

---

## Monitoring & Alerts

### 1. Process Monitoring Script

```bash
#!/bin/bash
# /home/abcdeveloper/scripts/monitor-processes.sh

MAX_PYTHON_PROCS=15
MAX_RAM_GB=8

PYTHON_COUNT=$(ps aux | grep -E "python|uvicorn" | grep -v grep | wc -l)
RAM_USAGE=$(free -g | awk '/Mem:/{print $3}')

if [ $PYTHON_COUNT -gt $MAX_PYTHON_PROCS ]; then
    echo "⚠️  WARNING: Too many Python processes ($PYTHON_COUNT > $MAX_PYTHON_PROCS)"
    echo "Orphaned processes detected. Run: pkill -9 -f 'multiprocessing'"
    # Send alert email/Telegram
fi

if [ $RAM_USAGE -gt $MAX_RAM_GB ]; then
    echo "⚠️  WARNING: High RAM usage (${RAM_USAGE}GB > ${MAX_RAM_GB}GB)"
fi
```

Add to crontab:
```bash
crontab -e
# Check every 5 minutes
*/5 * * * * /home/abcdeveloper/scripts/monitor-processes.sh
```

### 2. Prometheus Metrics

Add to your API:
```python
from prometheus_client import Gauge

orphaned_processes = Gauge('orphaned_python_processes', 'Number of orphaned Python processes')

# In monitoring endpoint
import subprocess
proc_count = subprocess.check_output(
    ["ps", "aux"], text=True
).count("multiprocessing.spawn")
orphaned_processes.set(proc_count)
```

---

## Comparison Table

| Solution | Pros | Cons | Best For |
|----------|------|------|----------|
| **Systemd** | ✅ Native Linux<br>✅ Auto-restart<br>✅ Resource limits<br>✅ Logging | ❌ Linux only<br>❌ Requires root | Production servers |
| **Supervisor** | ✅ Cross-platform<br>✅ Easy to use<br>✅ Web UI | ❌ Extra dependency<br>❌ Less powerful | Small deployments |
| **Code Context Managers** | ✅ Always works<br>✅ No dependencies | ❌ Doesn't protect against `kill -9` | Development + backup |
| **cgroups** | ✅ Hard limits<br>✅ Prevents crashes | ❌ Complex setup<br>❌ Requires root | High-security environments |

---

## Recommended Production Stack

1. **Systemd services** (primary process management)
2. **Enhanced code with context managers** (defense in depth)
3. **Monitoring script** (early warning)
4. **Resource limits via systemd** (prevent crashes)

This gives you multiple layers of protection against orphaned processes!

---

## Quick Commands Reference

```bash
# Systemd
sudo systemctl restart analyticbot-mtproto
sudo journalctl -u analyticbot-mtproto -f

# Supervisor
sudo supervisorctl restart analyticbot-mtproto
sudo supervisorctl tail -f analyticbot-mtproto

# Emergency cleanup
pkill -9 -f "multiprocessing"
pkill -9 -f "apps.mtproto.worker"

# Check for orphans
ps aux | grep multiprocessing | grep -v grep | wc -l

# RAM usage
free -h
```
