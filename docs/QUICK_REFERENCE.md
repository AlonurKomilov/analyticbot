# Quick Reference: Process Management

## 🚀 Starting Services

### Development

```bash
# Start all services
./scripts/dev-start.sh

# Start specific services (with auto-cleanup)
./scripts/dev-start.sh api
./scripts/dev-start.sh bot
./scripts/dev-start.sh mtproto
./scripts/dev-start.sh workers  # Both bot and mtproto
./scripts/dev-start.sh frontend
```

### Production

```bash
# Using systemd
sudo systemctl start analyticbot-api
sudo systemctl start analyticbot-bot
sudo systemctl start analyticbot-mtproto-worker

# Using supervisord
sudo supervisorctl start analyticbot:*
```

## 🛑 Stopping Services

### Development

```bash
# Graceful stop (recommended)
kill -TERM $(cat logs/dev_mtproto.pid)
kill -TERM $(cat logs/dev_bot.pid)

# Force stop
pkill -9 -f "apps.mtproto.worker"
pkill -9 -f "apps.bot.run_bot"
```

### Production

```bash
# Using systemd
sudo systemctl stop analyticbot-mtproto-worker
sudo systemctl restart analyticbot-mtproto-worker

# Using supervisord
sudo supervisorctl stop analyticbot:analyticbot-mtproto-worker
sudo supervisorctl restart analyticbot:*
```

## 📊 Monitoring

### Health Checks

```bash
# MTProto worker health
curl http://localhost:9091/health

# Detailed metrics
curl http://localhost:9091/metrics | jq

# Readiness check
curl http://localhost:9091/ready
```

### Logs

```bash
# Development logs
tail -f logs/dev_mtproto.log
tail -f logs/dev_bot.log

# Production logs (systemd)
sudo journalctl -u analyticbot-mtproto-worker -f
sudo journalctl -u analyticbot-bot --since "1 hour ago"

# Production logs (supervisord)
sudo supervisorctl tail -f analyticbot:analyticbot-mtproto-worker stdout
```

### Status

```bash
# Development
ps aux | grep "apps.mtproto.worker"
ps aux | grep "apps.bot.run_bot"

# Production (systemd)
sudo systemctl status analyticbot-*

# Production (supervisord)
sudo supervisorctl status analyticbot:*
```

## 🧹 Cleanup

### Kill Duplicate Processes

```bash
# Kill all MTProto workers
pkill -9 -f "apps.mtproto.worker"

# Kill all bot processes
pkill -9 -f "apps.bot.run_bot"

# Kill orphan multiprocessing children
pkill -9 -f "multiprocessing.spawn"

# Kill everything Python (use with caution!)
pkill -9 -f "python"
```

### Check Resources

```bash
# Memory usage
free -h

# Swap usage
swapon --show

# Load average
uptime

# Detailed process info
htop
```

## ⚙️ Configuration

### Worker Limits

```bash
# Custom runtime (6 hours instead of 24)
python -m apps.mtproto.worker --max-runtime 6

# Higher memory limit (4GB instead of 2GB)
python -m apps.mtproto.worker --memory-limit 4096

# Lower CPU limit (50% instead of 80%)
python -m apps.mtproto.worker --cpu-limit 50

# Disable health endpoint
python -m apps.mtproto.worker --health-port 0

# Infinite runtime (testing only)
python -m apps.mtproto.worker --max-runtime 0
```

### One-Time Collection

```bash
# All users, once
python -m apps.mtproto.worker --once

# Specific user, once
python -m apps.mtproto.worker --user-id 123 --once

# Custom message limit
python -m apps.mtproto.worker --once  # Uses MTPROTO_HISTORY_LIMIT_PER_RUN from .env
```

## 🔍 Troubleshooting

### Worker Not Starting

```bash
# Check what's using the health port
lsof -i :9091

# Check logs for errors
tail -50 logs/dev_mtproto.log

# Check dependencies
source .venv/bin/activate
python -c "from apps.shared.process_manager import ProcessManager; print('OK')"
```

### High Memory Usage

```bash
# Check worker metrics
curl http://localhost:9091/metrics | jq '.metrics.memory_mb'

# Kill and restart
pkill -9 -f "apps.mtproto.worker"
./scripts/dev-start.sh mtproto
```

### Worker Stuck / Not Responding

```bash
# Check if responding
curl http://localhost:9091/health
# If times out, worker is stuck

# Force kill
pkill -9 -f "apps.mtproto.worker"

# Check for zombies
ps aux | grep defunct
```

### Database Connection Errors

```bash
# Check PostgreSQL
nc -z localhost 10100 && echo "✅ PostgreSQL reachable" || echo "❌ PostgreSQL down"

# Check Redis
nc -z localhost 10200 && echo "✅ Redis reachable" || echo "❌ Redis down"

# Start infrastructure
docker-compose -f docker/docker-compose.yml up -d db redis
```

## 📝 Common Commands

### Development Workflow

```bash
# 1. Start infrastructure
docker-compose -f docker/docker-compose.yml up -d

# 2. Start all services
./scripts/dev-start.sh

# 3. Check health
curl http://localhost:9091/health
curl http://localhost:11400/health

# 4. View logs
tail -f logs/dev_mtproto.log

# 5. Restart worker
pkill -f "apps.mtproto.worker"
./scripts/dev-start.sh mtproto
```

### Production Workflow

```bash
# 1. Deploy/update code
git pull origin main
source .venv/bin/activate
pip install -r requirements.prod.txt
alembic upgrade head

# 2. Restart services
sudo systemctl restart analyticbot-*

# 3. Verify
sudo systemctl status analyticbot-*
curl http://localhost:9091/health

# 4. Monitor
sudo journalctl -u analyticbot-mtproto-worker -f
```

## 🆘 Emergency Procedures

### System Overloaded

```bash
# 1. Kill all workers immediately
pkill -9 -f "apps.mtproto.worker"
pkill -9 -f "apps.bot.run_bot"
pkill -9 -f "multiprocessing.spawn"

# 2. Check resources
free -h
uptime

# 3. Restart with lower limits
python -m apps.mtproto.worker \
    --max-runtime 2 \
    --memory-limit 1024 \
    --cpu-limit 50
```

### Health Endpoint Down

```bash
# 1. Check if process is running
ps aux | grep "apps.mtproto.worker"

# 2. Check logs
tail -50 logs/dev_mtproto.log

# 3. Restart
pkill -f "apps.mtproto.worker"
./scripts/dev-start.sh mtproto

# 4. Verify
curl http://localhost:9091/health
```

### Production Outage

```bash
# 1. Check all services
sudo systemctl status analyticbot-*

# 2. Restart failed services
sudo systemctl restart analyticbot-mtproto-worker

# 3. Check logs
sudo journalctl -u analyticbot-* --since "10 minutes ago"

# 4. Verify health
curl http://localhost:9091/health
curl http://localhost:8000/health
```

## 📚 Documentation

- Full docs: `docs/PROCESS_LIFECYCLE_MANAGEMENT.md`
- Deployment: `docs/PRODUCTION_DEPLOYMENT.md`
- Implementation: `PROCESS_LIFECYCLE_IMPLEMENTATION_COMPLETE.md`

## 🔗 Quick Links

- Health endpoint: http://localhost:9091/health
- Metrics endpoint: http://localhost:9091/metrics
- API health: http://localhost:11400/health (dev) or http://localhost:8000/health (prod)
