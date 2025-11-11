# AnalyticBot - Automated Resource Management

This document explains the automated cleanup and monitoring system to prevent orphaned processes and resource leaks.

## 🎯 Problem

Multiprocessing workers can become orphaned when:
- Process crashes without cleanup
- SIGKILL instead of graceful SIGTERM
- Parent process dies unexpectedly
- No signal handlers registered

**Result**: Processes stay in memory for days, wasting 500+ MB RAM

---

## ✅ Solution: 3-Layer Defense

### Layer 1: **Graceful Shutdown** (Prevention)
Prevents orphans from being created in the first place.

**File**: `apps/shared/graceful_shutdown.py`

**Usage in MTProto Worker**:
```python
from apps.shared.graceful_shutdown import get_shutdown_handler, register_cleanup_callback

# Initialize handler
shutdown_handler = get_shutdown_handler()

# Register cleanup callbacks
def cleanup_session():
    logger.info("Closing Telethon session...")
    # Your cleanup code

register_cleanup_callback(cleanup_session)

# When creating workers
from multiprocessing import Process
worker = Process(target=my_task)
shutdown_handler.register_child_process(worker)
worker.start()
```

**What it does**:
- Catches SIGTERM/SIGINT signals
- Runs cleanup callbacks
- Terminates all child processes
- Prevents orphans on shutdown

---

### Layer 2: **Automated Cleanup** (Detection & Removal)
Automatically kills orphaned processes.

**File**: `scripts/cleanup_orphaned_processes.sh`

**What it does**:
- Runs every hour (via systemd timer)
- Finds multiprocessing workers older than 1 day
- Kills orphaned processes
- Frees up memory
- Logs all actions to `/tmp/analyticbot_cleanup.log`

**Manual run**:
```bash
./scripts/cleanup_orphaned_processes.sh
```

---

### Layer 3: **Resource Monitoring** (Alerting)
Monitors resources and alerts when thresholds exceeded.

**File**: `scripts/monitor_resources.py`

**What it monitors**:
- Memory usage (alerts at 75%, critical at 85%)
- CPU usage (alerts at 80%, critical at 90%)
- Disk usage (alerts at 80%, critical at 90%)
- Orphaned processes (> 24 hours old)
- High memory processes (> 500 MB)

**Manual run**:
```bash
python3 scripts/monitor_resources.py
```

---

## 🚀 Setup Instructions

### Step 1: Install Systemd Services

```bash
# Copy systemd files
sudo cp scripts/systemd/analyticbot-cleanup.service /etc/systemd/system/
sudo cp scripts/systemd/analyticbot-cleanup.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start timer
sudo systemctl enable analyticbot-cleanup.timer
sudo systemctl start analyticbot-cleanup.timer

# Check status
sudo systemctl status analyticbot-cleanup.timer
```

### Step 2: Setup Resource Limits (Optional)

```bash
# Copy limits config
sudo cp scripts/systemd/resource_limits.conf /etc/security/limits.d/analyticbot.conf

# Reload limits (requires re-login)
logout
```

### Step 3: Setup Monitoring Cron (Optional)

```bash
# Add to crontab (runs every 30 minutes)
crontab -e

# Add this line:
*/30 * * * * /home/abcdeveloper/projects/analyticbot/scripts/monitor_resources.py
```

---

## 📊 Monitoring & Logs

### Check Cleanup Logs
```bash
tail -f /tmp/analyticbot_cleanup.log
```

### Check Monitoring Logs
```bash
tail -f /tmp/analyticbot_monitor.log
```

### Check Systemd Timer Status
```bash
# Check timer status
sudo systemctl status analyticbot-cleanup.timer

# Check last cleanup run
sudo journalctl -u analyticbot-cleanup.service -n 50
```

### Manual Cleanup
```bash
# Run cleanup immediately
./scripts/cleanup_orphaned_processes.sh

# Or trigger via systemd
sudo systemctl start analyticbot-cleanup.service
```

---

## 🔧 Configuration

### Cleanup Script Thresholds

Edit `scripts/cleanup_orphaned_processes.sh`:

```bash
MAX_PROCESS_AGE_DAYS=1  # Kill processes older than 1 day
MAX_MEMORY_PERCENT=85   # Trigger cleanup if memory exceeds 85%
```

### Monitoring Thresholds

Edit `scripts/monitor_resources.py`:

```python
MEMORY_WARNING_PERCENT = 75
MEMORY_CRITICAL_PERCENT = 85
CPU_WARNING_PERCENT = 80
CPU_CRITICAL_PERCENT = 90
MAX_PROCESS_AGE_HOURS = 24
```

---

## 📝 Integration Checklist

To integrate graceful shutdown into MTProto worker:

- [ ] Import `get_shutdown_handler` in `apps/mtproto/worker.py`
- [ ] Call `get_shutdown_handler()` at startup
- [ ] Register cleanup callbacks for:
  - [ ] Telethon session cleanup
  - [ ] Database connection cleanup
  - [ ] File handle cleanup
- [ ] Register all multiprocessing workers with `register_child_process()`
- [ ] Test graceful shutdown: `kill -TERM <pid>`

---

## 🎯 Expected Results

### Before:
- ❌ Orphaned processes accumulate over days
- ❌ Memory leaks up to 87%+
- ❌ Manual cleanup required
- ❌ No visibility into issues

### After:
- ✅ Orphans automatically cleaned every hour
- ✅ Memory stays below 75%
- ✅ No manual intervention needed
- ✅ Alerts when thresholds exceeded
- ✅ Graceful shutdowns prevent orphans

---

## 🧪 Testing

### Test Cleanup Script
```bash
# Create a test orphan (for testing only)
python3 -c "import time; time.sleep(999999)" &

# Run cleanup (should NOT kill recent process)
./scripts/cleanup_orphaned_processes.sh

# Check logs
cat /tmp/analyticbot_cleanup.log
```

### Test Monitoring
```bash
# Run monitoring
python3 scripts/monitor_resources.py

# Should show current resource usage and any alerts
```

### Test Graceful Shutdown
```bash
# Start MTProto worker
python3 -m apps.mtproto.worker --once

# In another terminal, send SIGTERM
pkill -TERM -f "apps.mtproto.worker"

# Check logs - should see graceful shutdown messages
```

---

## 📚 Files Created

1. **scripts/cleanup_orphaned_processes.sh** - Automated cleanup script
2. **scripts/monitor_resources.py** - Resource monitoring script
3. **apps/shared/graceful_shutdown.py** - Graceful shutdown handler
4. **scripts/systemd/analyticbot-cleanup.service** - Systemd service
5. **scripts/systemd/analyticbot-cleanup.timer** - Systemd timer (runs hourly)
6. **scripts/systemd/resource_limits.conf** - Resource limits config

---

## 🎉 Summary

Your system now has:

1. **Prevention**: Graceful shutdown handlers prevent orphans
2. **Detection**: Hourly automatic cleanup removes orphans
3. **Monitoring**: Resource monitoring alerts on issues
4. **Limits**: Process/memory limits prevent runaway processes

**No more manual cleanup needed!** The system manages itself. 🚀
