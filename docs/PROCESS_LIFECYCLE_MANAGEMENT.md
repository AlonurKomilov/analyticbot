# Process Lifecycle Management System

## Overview

Comprehensive process management system with:
- **Max runtime enforcement** - Workers auto-shutdown after configurable hours
- **Graceful shutdown** - Proper signal handling (SIGTERM/SIGINT)
- **Resource monitoring** - CPU and memory limits with auto-restart
- **Health checks** - HTTP endpoints for monitoring
- **Process cleanup** - Prevents duplicate instances

## Architecture

### Core Components

1. **ProcessManager** (`apps/shared/process_manager.py`)
   - Lifecycle management
   - Resource monitoring
   - Signal handling
   - Cleanup callbacks

2. **HealthCheckServer** (`apps/shared/health_server.py`)
   - HTTP health endpoints
   - Metrics API
   - Readiness checks

3. **Worker Integration** (`apps/mtproto/worker.py`, `apps/bot/run_bot.py`)
   - ProcessManager integration
   - Configurable limits
   - Health monitoring

## Usage

### Development Mode

#### Start with Process Management

```bash
# Start MTProto worker with lifecycle management
./scripts/dev-start.sh mtproto

# Start bot with cleanup
./scripts/dev-start.sh bot

# Start both workers
./scripts/dev-start.sh workers

# Start all services
./scripts/dev-start.sh
```

#### Manual Worker Startup

```bash
# MTProto worker with custom limits
python -m apps.mtproto.worker \
    --interval 10 \
    --max-runtime 24 \
    --memory-limit 2048 \
    --cpu-limit 80 \
    --health-port 9091 \
    --log-level INFO

# Single user collection (one-time)
python -m apps.mtproto.worker \
    --user-id 123 \
    --once

# Infinite runtime (for testing)
python -m apps.mtproto.worker \
    --max-runtime 0 \
    --memory-limit 0 \
    --cpu-limit 0
```

### Production Mode

#### Using Systemd (Recommended)

```bash
# Install service files
sudo cp infra/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable analyticbot-api
sudo systemctl enable analyticbot-bot
sudo systemctl enable analyticbot-mtproto-worker

# Start services
sudo systemctl start analyticbot-api
sudo systemctl start analyticbot-bot
sudo systemctl start analyticbot-mtproto-worker

# Check status
sudo systemctl status analyticbot-*

# View logs
sudo journalctl -u analyticbot-mtproto-worker -f
sudo journalctl -u analyticbot-bot -f

# Restart services
sudo systemctl restart analyticbot-mtproto-worker
```

#### Using Supervisord (Alternative)

```bash
# Install supervisor
sudo apt install supervisor

# Copy configuration
sudo cp infra/supervisor/analyticbot.conf /etc/supervisor/conf.d/

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Manage services
sudo supervisorctl status analyticbot:*
sudo supervisorctl restart analyticbot:*
sudo supervisorctl stop analyticbot:analyticbot-mtproto-worker

# View logs
sudo supervisorctl tail -f analyticbot:analyticbot-mtproto-worker stdout
```

## Health Monitoring

### HTTP Endpoints

Workers expose health check endpoints (default port 9091):

```bash
# Health status
curl http://localhost:9091/health

# Detailed metrics
curl http://localhost:9091/metrics

# Readiness check
curl http://localhost:9091/ready
```

### Response Examples

**Healthy Response** (`/health`):
```json
{
  "status": "healthy",
  "reason": "healthy",
  "timestamp": "2025-11-19T10:30:00Z"
}
```

**Metrics Response** (`/metrics`):
```json
{
  "metrics": {
    "pid": 12345,
    "name": "mtproto_worker_all",
    "uptime_seconds": 3600.5,
    "cpu_percent": 45.2,
    "memory_mb": 856.3,
    "memory_percent": 8.1,
    "num_threads": 12,
    "status": "running",
    "heartbeat_age_seconds": 5.2
  },
  "health": {
    "is_healthy": true,
    "reason": "healthy"
  },
  "runtime": {
    "uptime_hours": 1.0,
    "remaining_hours": 23.0
  },
  "limits": {
    "max_runtime_hours": 24.0,
    "memory_limit_mb": 2048,
    "cpu_limit_percent": 80.0
  },
  "timestamp": "2025-11-19T10:30:00Z"
}
```

## Configuration

### Worker Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--interval` | 10 | Collection interval in minutes |
| `--max-runtime` | 24 | Max runtime in hours (0 = infinite) |
| `--memory-limit` | 2048 | Memory limit in MB (0 = no limit) |
| `--cpu-limit` | 80 | CPU limit % (0 = no limit) |
| `--health-port` | 9091 | Health check port (0 = disabled) |
| `--once` | false | Run once and exit |
| `--user-id` | null | Specific user ID to collect |

### Systemd Resource Limits

Service files include resource controls:

```ini
# Memory limits
MemoryMax=2.5G          # Hard limit
MemoryHigh=2G           # Soft limit (triggers pressure)

# CPU limits
CPUQuota=90%            # Max 90% of one core

# Restart policy
Restart=always
RestartSec=10
StartLimitBurst=5       # Max 5 restarts
StartLimitIntervalSec=600  # In 10 minutes
```

## Monitoring & Alerts

### Prometheus Integration

Health endpoints are compatible with Prometheus scraping:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'analyticbot-workers'
    static_configs:
      - targets:
        - 'localhost:9091'  # MTProto worker
        - 'localhost:9092'  # Additional workers
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### Grafana Dashboard

Key metrics to monitor:
- `uptime_hours` - Worker uptime
- `cpu_percent` - CPU usage
- `memory_mb` - Memory usage
- `heartbeat_age_seconds` - Time since last heartbeat
- Worker restart count (from systemd/supervisor)

### Alerting Rules

**High Memory Usage:**
```
memory_percent > 85% for 5 minutes
```

**Worker Down:**
```
health status != "healthy" for 2 minutes
```

**Frequent Restarts:**
```
restart_count > 3 in 1 hour
```

## Troubleshooting

### Check Process Status

```bash
# Find running workers
ps aux | grep "apps.mtproto.worker"
ps aux | grep "apps.bot.run_bot"

# Check health endpoint
curl http://localhost:9091/health

# View logs
tail -f logs/dev_mtproto.log
```

### Kill Stuck Processes

```bash
# Kill specific process
kill -TERM <PID>  # Graceful
kill -9 <PID>     # Force

# Kill all workers (using dev-start.sh cleanup)
./scripts/dev-start.sh cleanup_workers all
```

### Common Issues

**Issue: Workers not stopping**
- Check if SIGTERM handler is working
- Force kill with `kill -9` if stuck
- Review shutdown timeout settings

**Issue: High memory usage**
- Check `memory_limit_mb` setting
- Review connection pool sizes
- Monitor for memory leaks

**Issue: Duplicate processes**
- Run cleanup before starting: `./scripts/dev-start.sh mtproto`
- Check for orphan `multiprocessing.spawn` processes
- Verify systemd `KillMode=mixed` setting

## Migration Guide

### From Old Workers (Infinite Loops)

**Before:**
```python
while True:
    # Do work
    await asyncio.sleep(60)
```

**After:**
```python
from apps.shared.process_manager import ProcessManager

manager = ProcessManager(name="my_worker", max_runtime_hours=24)
manager.start()

while manager.should_continue():
    manager.heartbeat()
    # Do work
    await asyncio.sleep(60)

manager.shutdown()
```

### From Manual Scripts to Systemd

1. Stop manual processes
2. Install service files
3. Enable and start services
4. Verify health endpoints
5. Monitor logs for issues

## Best Practices

1. **Always use ProcessManager** - Don't write custom infinite loops
2. **Set reasonable limits** - Max runtime prevents runaway processes
3. **Monitor health endpoints** - Integrate with monitoring stack
4. **Use systemd in production** - Better than supervisor for production
5. **Cleanup on startup** - dev-start.sh now handles this automatically
6. **Log to files** - Easier debugging than stdout only
7. **Test graceful shutdown** - Send SIGTERM and verify cleanup

## Security Considerations

- Health endpoints bind to 0.0.0.0 - restrict with firewall
- Resource limits prevent DoS
- Systemd security options (ProtectSystem, PrivateTmp)
- Non-root user execution
- Read-only filesystem where possible

## Performance Tuning

### Memory Optimization
- Reduce connection pool size
- Lower history limit per run
- Increase collection interval
- Monitor GC with `gc.get_stats()`

### CPU Optimization
- Reduce worker count
- Use connection pooling
- Batch database operations
- Profile with `cProfile`

## References

- [Systemd service management](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Supervisor documentation](http://supervisord.org/)
- [Python signal handling](https://docs.python.org/3/library/signal.html)
- [psutil resource monitoring](https://psutil.readthedocs.io/)
