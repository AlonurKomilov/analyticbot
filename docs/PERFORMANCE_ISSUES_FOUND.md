# 🐌 Performance Issues Detected - November 11, 2025

## Critical Issues Found

### 1. ❌ **DUPLICATE MTPROTO WORKERS** (HIGH PRIORITY)
**Problem**: Multiple MTProto workers running simultaneously
```
PID 2419626: 850MB memory (running since 08:14)
PID 2423118: 832MB memory (running since 08:30)
```

**Impact**:
- Wasting ~1.7GB memory
- Duplicate message collection
- Database connection pool saturation
- Potential data duplication/conflicts

**Solution**: Kill old workers and ensure only one runs

---

### 2. ⚠️ **HIGH MEMORY USAGE**
**Current State**:
- Total: 11GB
- Used: 8.9GB (81% used)
- Available: 2.8GB
- Swap: 73MB in use

**Top Memory Consumers**:
1. VSCode Extension Host: 14% (1.5GB)
2. Python MTProto Workers: 12.5% + 10.4% + 7.2% + 6.9% (multiple instances)
3. VSCode TypeScript Server: 5.3% (580MB)

**Impact**: System slowdown when memory is full

---

### 3. ⚠️ **TELETHON CONNECTION ISSUES**
**Problem**: Repeated "Server closed the connection" warnings

**Evidence**:
```
[WARNING] telethon.network.connection.connection: Server closed the connection:
0 bytes read on a total of 8 expected bytes
```
(Repeated 20+ times in recent logs)

**Impact**:
- Failed data collection attempts
- Retries consuming CPU/memory
- Slower overall performance

---

### 4. ⚠️ **DATABASE CONNECTION POOL**
**Current State**:
- 26 idle connections
- 1 active connection
- Total: 27 connections

**Issue**: Too many idle connections may indicate:
- Connection leaks
- Pool not being released properly
- Multiple worker instances not cleaned up

---

## Performance Metrics

### API Response Times ✅
- Health endpoint: **12ms** (Good)
- Frontend load: **22ms** (Good)

### System Load ⚠️
- Load Average: 0.72, 0.96, 1.08
- Status: **Moderate load** for 4-core system

### Disk Usage ✅
- Used: 34GB / 96GB (36%)
- Status: **Healthy**

---

## Immediate Actions Required

### 1. Kill Duplicate MTProto Workers
```bash
# Keep only the newest worker, kill the old one
kill 2419626

# Or restart all services cleanly
make -f Makefile.dev dev-stop
make -f Makefile.dev dev-start
```

### 2. Monitor Memory After Cleanup
```bash
free -h
ps aux --sort=-%mem | head -10
```

### 3. Check Telethon Session Health
The repeated connection closures suggest:
- Invalid/corrupted session file
- Rate limiting from Telegram
- Network instability
- Need to recreate MTProto session

### 4. Optimize Database Connections
Consider reducing pool size in configuration:
```python
# Current: Too many idle connections
# Recommended: 10-15 connections max for this workload
```

---

## Root Causes

### Why Duplicate Workers?
When running `make -f Makefile.dev dev-start` multiple times without stopping:
1. Old processes don't get killed properly
2. New workers start while old ones still running
3. Each worker holds database connections
4. Memory usage doubles/triples

### Why Telethon Warnings?
1. **Old sessions active**: Multiple workers using same session causes conflicts
2. **Telegram rate limits**: Too many concurrent requests
3. **Network issues**: Connection interrupted mid-request

---

## Recommended Fixes

### A. Clean Restart Script
Create: `scripts/clean-restart.sh`
```bash
#!/bin/bash
# Stop all services
make -f Makefile.dev dev-stop

# Wait for processes to terminate
sleep 3

# Kill any remaining python processes
pkill -f "apps.mtproto.worker" || true
pkill -f "apps.bot.run_bot" || true
pkill -f "uvicorn apps.api.main" || true

# Clean stale PIDs
rm -f logs/*.pid

# Start fresh
make -f Makefile.dev dev-start
```

### B. Add Process Health Check
Modify `dev-start.sh` to check for existing processes before starting:
```bash
check_existing_process() {
    local service=$1
    local count=$(ps aux | grep "$service" | grep -v grep | wc -l)
    if [ $count -gt 0 ]; then
        echo "⚠️  Found $count existing $service processes"
        echo "Run 'make -f Makefile.dev dev-stop' first"
        return 1
    fi
}
```

### C. Reduce Database Connection Pool
File: `.env.development` or `config/settings.py`
```python
# Current: Default (likely 20-30)
# Recommended:
DATABASE_POOL_MIN_SIZE=5
DATABASE_POOL_MAX_SIZE=15
```

### D. Add Connection Retry Logic for Telethon
File: `apps/mtproto/services/data_collection_service.py`
```python
# Add exponential backoff for reconnections
# Catch connection errors and retry with delay
# Log warnings but continue operation
```

---

## Monitoring Commands

### Quick Health Check
```bash
# Check duplicate processes
ps aux | grep -E "(mtproto.worker|run_bot|uvicorn)" | grep -v grep | wc -l

# Should be: 3 (one of each)
# If more: duplicates exist

# Check memory
free -h | grep Mem | awk '{print "Used:", $3, "/", $2, "("int($3/$2*100)"%)"}'

# Check database connections
PGPASSWORD=change_me psql -h localhost -p 10100 -U analytic -d analytic_bot \
  -c "SELECT count(*), state FROM pg_stat_activity WHERE datname = 'analytic_bot' GROUP BY state;"
```

### Real-time Monitoring
```bash
# Watch memory usage
watch -n 2 'free -h && echo "---" && ps aux --sort=-%mem | head -5'

# Monitor API response times
while true; do
  curl -o /dev/null -s -w "API: %{time_total}s\n" http://localhost:11400/health
  sleep 5
done
```

---

## Expected Performance After Fixes

### Memory Usage
- Before: 8.9GB / 11GB (81%)
- After: ~6.5GB / 11GB (59%)
- Saved: ~2.4GB

### Database Connections
- Before: 27 connections (26 idle)
- After: ~10-12 connections (8-10 idle)

### CPU Load
- Before: 1.08 (high for background tasks)
- After: 0.3-0.5 (normal)

### Telethon Warnings
- Before: 20+ per minute
- After: 0-2 per hour (only on real network issues)

---

## Long-term Optimizations

1. **Add Process Manager**: Use supervisord or systemd instead of custom scripts
2. **Implement Health Checks**: Auto-restart crashed workers
3. **Add Metrics Dashboard**: Prometheus + Grafana for monitoring
4. **Optimize Queries**: Add database query logging to find slow queries
5. **Implement Caching**: Redis cache for frequently accessed data
6. **Code Splitting**: Frontend bundle optimization (if pages are slow)

---

## Status: 🔴 ACTION REQUIRED

The duplicate MTProto workers are the primary cause of slowness. Clean restart recommended immediately.
