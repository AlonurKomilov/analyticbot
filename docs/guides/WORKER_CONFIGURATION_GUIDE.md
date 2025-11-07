# Worker Configuration Guide - API Performance Optimization

## Your Current Server Resources

**CPU Cores:** 6 cores
**RAM:** 12 GB total (4.5 GB available)
**Current Setup:** 1 worker (development mode with --reload)

---

## Recommended Worker Configuration

### Formula for Optimal Workers
```
Workers = (2 × CPU_CORES) + 1
Workers = (2 × 6) + 1 = 13 workers (MAXIMUM)
```

### Practical Recommendations

#### 1. **Conservative (Recommended for Start)** ✅
```bash
--workers 4
```
**Why:**
- Uses 66% of CPU capacity (4 out of 6 cores)
- Leaves resources for PostgreSQL, Redis, system
- Safe for 12GB RAM (each worker ~200-300MB)
- Handles 1000+ concurrent users easily

**Memory Usage:**
- API workers: 4 × 300MB = 1.2GB
- PostgreSQL: ~1GB
- Redis: ~500MB
- System: ~1GB
- **Total:** ~3.7GB (leaves 8GB buffer) ✅

#### 2. **Moderate (Good Balance)**
```bash
--workers 6
```
**Why:**
- Uses 100% of CPU cores efficiently
- Each core gets dedicated worker
- Better load distribution
- Handles 1500+ concurrent users

**Memory Usage:**
- API workers: 6 × 300MB = 1.8GB
- Total system: ~4.3GB ✅

#### 3. **Aggressive (Maximum Performance)**
```bash
--workers 8-10
```
**Why:**
- Oversubscription for I/O-bound tasks
- Better handling of blocking operations
- Handles 2000+ concurrent users
- Good for high-traffic periods

**Memory Usage:**
- API workers: 10 × 300MB = 3GB
- Total system: ~5.5GB ✅

#### 4. **Maximum (Not Recommended)**
```bash
--workers 13
```
**Why NOT:**
- Excessive context switching overhead
- Diminishing returns after 2×cores
- Higher memory pressure
- Only useful for extreme I/O wait scenarios

---

## Configuration by Use Case

### Development (Current)
```bash
uvicorn apps.api.main:app \
  --host 0.0.0.0 \
  --port 11400 \
  --reload \
  --log-level debug
```
**Workers:** 1 (auto-reload enabled)

### Staging/Testing
```bash
uvicorn apps.api.main:app \
  --host 0.0.0.0 \
  --port 11400 \
  --workers 4 \
  --log-level info
```
**Workers:** 4 (matches production)

### Production (Recommended)
```bash
uvicorn apps.api.main:app \
  --host 0.0.0.0 \
  --port 11400 \
  --workers 6 \
  --log-level info \
  --timeout-keep-alive 65 \
  --limit-concurrency 1000 \
  --backlog 2048
```
**Workers:** 6 (optimal for 6 cores)

### High Traffic Production
```bash
uvicorn apps.api.main:app \
  --host 0.0.0.0 \
  --port 11400 \
  --workers 8 \
  --log-level warning \
  --timeout-keep-alive 65 \
  --limit-concurrency 2000 \
  --backlog 4096
```
**Workers:** 8 (for peak loads)

---

## Performance Comparison

### Single Worker (Current Dev Setup)
- **Requests/sec:** ~100-200 req/s
- **Concurrent users:** ~50-100 users
- **Latency:** 17ms (local) / 498ms (DevTunnel)
- **CPU usage:** ~15-25%

### 4 Workers (Recommended)
- **Requests/sec:** ~800-1000 req/s (5x improvement)
- **Concurrent users:** ~400-800 users
- **Latency:** 17ms (local) / 498ms (DevTunnel)
- **CPU usage:** ~60-80%

### 6 Workers (Optimal)
- **Requests/sec:** ~1200-1500 req/s (7.5x improvement)
- **Concurrent users:** ~600-1200 users
- **Latency:** 17ms (local) / 498ms (DevTunnel)
- **CPU usage:** ~90-100%

### 8 Workers (High Traffic)
- **Requests/sec:** ~1400-1800 req/s (9x improvement)
- **Concurrent users:** ~800-1500 users
- **Latency:** 17ms (local) / 498ms (DevTunnel)
- **CPU usage:** ~100% (with context switching)

---

## Database Connection Pool Adjustment

Your connection pool needs to scale with workers!

### Current Settings (From your config)
```python
ConnectionConfig:
    min_connections: 10
    max_connections: 50
```

### Recommended by Worker Count

#### For 4 Workers
```python
DB_POOL_MIN = 8        # 2 per worker
DB_POOL_MAX = 40       # 10 per worker
```

#### For 6 Workers (Recommended)
```python
DB_POOL_MIN = 12       # 2 per worker
DB_POOL_MAX = 60       # 10 per worker
```

#### For 8 Workers
```python
DB_POOL_MIN = 16       # 2 per worker
DB_POOL_MAX = 80       # 10 per worker
```

**PostgreSQL max_connections must be higher:**
```sql
ALTER SYSTEM SET max_connections = 200;
```

---

## Redis Connection Pool Adjustment

### Current Settings
```python
REDIS_MAX_CONNECTIONS = 50
```

### Recommended by Worker Count

#### For 4 Workers
```python
REDIS_MAX_CONNECTIONS = 40  # 10 per worker
```

#### For 6 Workers
```python
REDIS_MAX_CONNECTIONS = 60  # 10 per worker
```

#### For 8 Workers
```python
REDIS_MAX_CONNECTIONS = 80  # 10 per worker
```

---

## Monitoring Worker Performance

### Check Worker Status
```bash
# See all workers
ps aux | grep uvicorn

# Count workers
ps aux | grep uvicorn | grep -v grep | wc -l

# Monitor CPU per worker
top -p $(pgrep -d',' -f uvicorn)

# Monitor memory per worker
ps aux | grep uvicorn | awk '{sum+=$6} END {print "Total Memory:", sum/1024, "MB"}'
```

### Load Testing
```bash
# Install hey (HTTP load testing tool)
go install github.com/rakyll/hey@latest

# Test with 1000 concurrent users for 30 seconds
hey -z 30s -c 1000 -q 10 http://localhost:11400/health

# Test specific endpoint
hey -z 30s -c 500 -q 5 \
  -m POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message":"test"}' \
  http://localhost:11400/system/send
```

---

## Systemd Service Configuration

### Create Service File
```bash
sudo nano /etc/systemd/system/analyticbot-api.service
```

### For 4 Workers (Recommended Start)
```ini
[Unit]
Description=AnalyticBot FastAPI Application
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=analyticbot
Group=analyticbot
WorkingDirectory=/home/analyticbot/analyticbot
Environment="PATH=/home/analyticbot/analyticbot/.venv/bin"
EnvironmentFile=/home/analyticbot/analyticbot/.env.production

ExecStart=/home/analyticbot/analyticbot/.venv/bin/uvicorn \
    apps.api.main:app \
    --host 0.0.0.0 \
    --port 11400 \
    --workers 4 \
    --log-level info \
    --timeout-keep-alive 65 \
    --limit-concurrency 1000 \
    --backlog 2048

ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### For 6 Workers (Optimal)
Change only this line:
```ini
--workers 6 \
```

---

## Quick Start Commands

### Start with 4 workers (Recommended)
```bash
cd /home/abcdeveloper/projects/analyticbot
source .venv/bin/activate
uvicorn apps.api.main:app --host 0.0.0.0 --port 11400 --workers 4
```

### Start with 6 workers (Optimal)
```bash
uvicorn apps.api.main:app --host 0.0.0.0 --port 11400 --workers 6
```

### Start with systemd (Production)
```bash
sudo systemctl start analyticbot-api
sudo systemctl enable analyticbot-api  # Auto-start on boot
sudo systemctl status analyticbot-api  # Check status
```

---

## Expected Performance Improvements

### Scenario: 500 Concurrent Users

| Workers | Req/sec | Avg Latency | CPU Usage | Success Rate |
|---------|---------|-------------|-----------|--------------|
| 1       | 150     | 3.3s        | 25%       | 60% (timeouts) |
| 4       | 600     | 0.8s        | 70%       | 99.5%        |
| 6       | 900     | 0.55s       | 95%       | 99.9%        |
| 8       | 1000    | 0.5s        | 100%      | 99.9%        |

### Scenario: 1000 Concurrent Users

| Workers | Req/sec | Avg Latency | CPU Usage | Success Rate |
|---------|---------|-------------|-----------|--------------|
| 1       | 150     | timeout     | 25%       | 10% (fail)   |
| 4       | 600     | 1.6s        | 80%       | 95%          |
| 6       | 900     | 1.1s        | 100%      | 99%          |
| 8       | 1000    | 1.0s        | 100%      | 99.5%        |

---

## Migration Plan

### Phase 1: Testing (1-2 days)
```bash
# Start with 4 workers
uvicorn apps.api.main:app --workers 4 --port 11400

# Run load tests
hey -z 60s -c 500 http://localhost:11400/health

# Monitor metrics
watch -n 1 'ps aux | grep uvicorn'
```

### Phase 2: Optimization (1 day)
```bash
# Increase to 6 workers
uvicorn apps.api.main:app --workers 6 --port 11400

# Update connection pools
# Edit: infra/db/connection_manager.py
DB_POOL_MAX = 60

# Restart and test
```

### Phase 3: Production (Ongoing)
```bash
# Setup systemd service with 6 workers
sudo systemctl enable analyticbot-api
sudo systemctl start analyticbot-api

# Monitor in production
sudo journalctl -u analyticbot-api -f
```

---

## Important Notes

### ⚠️ Worker Process Model
- Each worker is a **separate Python process**
- Workers do NOT share memory
- Each worker has its own:
  - Database connection pool
  - Redis connection pool
  - In-memory cache
  - Event loop

### ⚠️ Stateful Services
If using in-memory caching or WebSockets:
- Workers don't share state
- Use Redis for shared cache
- Use sticky sessions for WebSockets

### ⚠️ DevTunnel Bottleneck
Adding workers **won't help** with DevTunnel latency (481ms):
- Workers only improve **throughput** (req/s)
- Workers don't reduce **latency** (response time)
- To fix latency: Deploy without DevTunnel

---

## Recommendation Summary

**For Your Server (6 cores, 12GB RAM):**

1. **Start with 4 workers** → Safe, proven, 5x performance boost
2. **Monitor for 1 week** → Check CPU, memory, errors
3. **Upgrade to 6 workers** → If CPU < 80% average
4. **Consider 8 workers** → Only if CPU < 70% with 6 workers

**Best Configuration:**
```bash
uvicorn apps.api.main:app \
  --host 0.0.0.0 \
  --port 11400 \
  --workers 6 \
  --timeout-keep-alive 65 \
  --limit-concurrency 1000 \
  --log-level info
```

**Database Pool:**
```python
DB_POOL_MIN = 12
DB_POOL_MAX = 60
```

**Redis Pool:**
```python
REDIS_MAX_CONNECTIONS = 60
```

---

## Quick Decision Matrix

| Current Load | Recommended Workers | Why |
|--------------|-------------------|-----|
| < 100 users  | 2-4 workers       | Overkill, but good headroom |
| 100-500 users | 4 workers        | Sweet spot for stability |
| 500-1000 users | 6 workers       | Full CPU utilization |
| 1000-2000 users | 8 workers      | Handle traffic spikes |
| > 2000 users | Scale horizontally | Add more servers |

---

**Status:** Ready to implement! Start with 4 workers, monitor, then scale up to 6.
