# MTProto Port 9091 & Process Management Analysis

**Date**: November 23, 2025
**Issue**: Zombie process holding port 9091, missing health checks in dev-start script

---

## ✅ Question 1: Is Port 9091 Only for MTProto Worker?

**YES** - Port 9091 is **exclusively** for the MTProto worker health server.

### Port Assignment Evidence:

```bash
# From .env.development
PROMETHEUS_PORT=9091  # ⚠️ MISLEADING NAME - This is actually MTProto health port

# From apps/mtproto/worker.py (line 95-100)
parser.add_argument(
    "--health-port",
    type=int,
    default=9091,
    help="Health check HTTP server port (default: 9091, 0 = disabled)",
)

# From scripts/dev-start.sh (line 195)
start_service "mtproto_worker" 'python -m apps.mtproto.worker --interval 10 --max-runtime 24 --memory-limit 2048 --cpu-limit 80 --health-port 9091' ""
```

### Port Verification:
```bash
$ lsof -i :9091
COMMAND     PID         USER   FD   TYPE    DEVICE SIZE/OFF NODE NAME
python  3852150 abcdeveloper   13u  IPv4 103653445      0t0  TCP *:9091 (LISTEN)

$ ps aux | grep 3852150
python -m apps.mtproto.worker --interval 10  # ✅ Confirmed: MTProto worker only
```

### No Port Conflicts:
- **Bot**: Uses polling mode (no port needed)
- **Webhook**: Uses API server port (11400 in dev, shared with FastAPI)
- **MTProto Worker**: Uses port 9091 for health checks

---

## ❌ Question 2: Why Zombie Process Not Killed by dev-start?

**PROBLEM**: The `dev-stop` command in `scripts/dev-start.sh` does **NOT** kill MTProto workers properly.

### Current Stop Logic (lines 442-483):

```bash
"stop")
    # Stop all development services
    echo "🛑 Stopping all development services..."

    # Stop services by PID file (safer approach)
    for pid_file in logs/dev_*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            service_name=$(basename "$pid_file" .pid | sed 's/dev_//')
            if kill -0 $pid 2>/dev/null; then
                echo "🔄 Stopping ${service_name} (PID: ${pid})"
                kill $pid
                # ... graceful shutdown logic
            fi
            rm -f "$pid_file"  # ⚠️ REMOVES PID FILE EVEN IF KILL FAILED
        fi
    done

    # More selective port cleanup - only kill our specific processes
    echo "🔍 Checking for remaining development processes..."

    # ❌ MISSING: No check for mtproto_worker processes!

    # Check for uvicorn (API) processes specifically
    if pgrep -f "uvicorn.*11400" > /dev/null; then
        pkill -f "uvicorn.*11400" || true
    fi

    # Check for npm/vite (Frontend) processes specifically
    if pgrep -f "vite.*11300" > /dev/null; then
        pkill -f "vite.*11300" || true
    fi

    # Check for bot processes
    if pgrep -f "apps.bot.run_bot" > /dev/null; then
        pkill -f "apps.bot.run_bot" || true
    fi

    # ❌ MISSING: Should check for "apps.mtproto.worker" here!

    # Check for multiprocessing spawn/resource_tracker (orphaned child processes)
    if pgrep -f "multiprocessing" > /dev/null; then
        pkill -f "multiprocessing.spawn" || true
        pkill -f "multiprocessing.resource_tracker" || true
    fi
```

### Why Zombie Process Survived:

1. **Scenario**: Old MTProto worker (PID 2056150) was started manually or from old session
2. **No PID file**: Process didn't have `logs/dev_mtproto_worker.pid` (file deleted or never created)
3. **Missed by cleanup**: Line 472-475 only checks for `apps.bot.run_bot`, not `apps.mtproto.worker`
4. **Port held**: Process stayed alive, holding port 9091
5. **New worker crash**: When new worker tried to start, port already in use → crash

### Root Cause Timeline:
```
Nov 20: Old MTProto worker started (PID 2056150)
Nov 23: User runs "make dev-stop" → PID file doesn't exist → Not killed
Nov 23: User runs "make dev-start" → New worker starts (PID 3845403)
Nov 23: New worker tries to bind port 9091 → EADDRINUSE → Crashes
Nov 23: Fix applied: Manually killed PID 2056150 → Port freed → New worker succeeds
```

---

## 🔍 Question 3: Why No Health Check for MTProto Worker in Make Status?

**PROBLEM**: The `dev-status` command shows infrastructure and services, but **NOT MTProto worker health**.

### Current Status Check (lines 504-560):

```bash
"status")
    echo "📊 Development Services Status:"
    echo "=================================="
    echo ""
    echo "🐳 Infrastructure (Docker):"

    # Check PostgreSQL (port 10100)
    if nc -z localhost 10100 2>/dev/null; then
        echo "PostgreSQL (10100): ✅ Running"
    else
        echo "PostgreSQL (10100): ❌ Stopped"
    fi

    # Check Redis (port 10200)
    if nc -z localhost 10200 2>/dev/null; then
        echo "Redis (10200):      ✅ Running"
    else
        echo "Redis (10200):      ❌ Stopped"
    fi

    echo ""
    echo "🔥 Development Services (venv):"

    # Check API - Development Environment Port 11400
    if curl -s http://localhost:11400/health >/dev/null 2>&1; then
        echo "API (11400):        ✅ Running"
    else
        echo "API (11400):        ❌ Stopped"
    fi

    # Check Frontend - Development Environment Port 11300
    if curl -s http://localhost:11300 >/dev/null 2>&1; then
        echo "Frontend (11300):   ✅ Running"
    else
        echo "Frontend (11300):   ❌ Stopped"
    fi

    # Check Bot (by PID file)
    if [ -f "logs/dev_bot.pid" ] && kill -0 $(cat logs/dev_bot.pid) 2>/dev/null; then
        echo "Bot:                ✅ Running"
    else
        echo "Bot:                ❌ Stopped"
    fi

    # ❌ MISSING: No check for MTProto Worker!
    # ❌ MISSING: No health endpoint checks!

    echo ""
    echo "🌐 Public Access (CloudFlare Tunnel):"
    # ... tunnel checks ...
```

### What's Missing:

1. **MTProto Worker Status**: Not checked at all
2. **Health Endpoints**: API has /health but not checked for actual health data
3. **Database Health**: Not checked (only port connectivity)
4. **Redis Health**: Not checked (only port connectivity)
5. **Worker Metrics**: No display of CPU, memory, uptime, etc.

### Current Health Data Available:

```bash
# MTProto Worker (port 9091)
$ curl http://localhost:9091/health
{
  "status": "unhealthy",
  "reason": "heartbeat_timeout_447s",
  "timestamp": "2025-11-23T12:01:55.521846Z"
}

$ curl http://localhost:9091/metrics
{
  "metrics": {
    "pid": 3852150,
    "uptime_seconds": 454.64,
    "cpu_percent": 0.0,
    "memory_mb": 832.28,
    "memory_percent": 6.96,
    "status": "sleeping"
  },
  "health": {
    "is_healthy": false,
    "reason": "heartbeat_timeout_447s"
  }
}

# API Server (port 11400)
$ curl http://localhost:11400/health
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

---

## 🛠️ Recommended Fixes

### Fix 1: Add MTProto Worker Cleanup to Stop Command

**Location**: `scripts/dev-start.sh` line 472 (after bot check)

**Add**:
```bash
# Check for mtproto worker processes
if pgrep -f "apps.mtproto.worker" > /dev/null; then
    echo -e "${YELLOW}🔄 Stopping remaining mtproto worker processes${NC}"
    pkill -f "apps.mtproto.worker" || true
fi
```

### Fix 2: Add Comprehensive Health Checks to Status Command

**Location**: `scripts/dev-start.sh` line 543 (after Bot check)

**Add**:
```bash
# Check MTProto Worker (by PID file and health endpoint)
if [ -f "logs/dev_mtproto_worker.pid" ] && kill -0 $(cat logs/dev_mtproto_worker.pid) 2>/dev/null; then
    # Check health endpoint
    MTPROTO_HEALTH=$(curl -s http://localhost:9091/health 2>/dev/null | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    if [ "$MTPROTO_HEALTH" = "healthy" ]; then
        echo -e "MTProto Worker:     ${GREEN}✅ Running & Healthy${NC}"
    else
        echo -e "MTProto Worker:     ${YELLOW}⚠️  Running but ${MTPROTO_HEALTH}${NC}"
        echo -e "                    ${BLUE}Check: curl http://localhost:9091/health${NC}"
    fi
else
    echo -e "MTProto Worker:     ${RED}❌ Stopped${NC}"
fi

echo ""
echo -e "${BLUE}🏥 Service Health Details:${NC}"

# API Health
if curl -s http://localhost:11400/health >/dev/null 2>&1; then
    API_HEALTH=$(curl -s http://localhost:11400/health 2>/dev/null)
    DB_STATUS=$(echo $API_HEALTH | grep -o '"database":"[^"]*"' | cut -d'"' -f4)
    REDIS_STATUS=$(echo $API_HEALTH | grep -o '"redis":"[^"]*"' | cut -d'"' -f4)
    echo -e "  Database:         ${GREEN}✅ ${DB_STATUS}${NC}"
    echo -e "  Redis:            ${GREEN}✅ ${REDIS_STATUS}${NC}"
fi

# MTProto Metrics
if curl -s http://localhost:9091/metrics >/dev/null 2>&1; then
    MTPROTO_METRICS=$(curl -s http://localhost:9091/metrics 2>/dev/null)
    CPU=$(echo $MTPROTO_METRICS | grep -o '"cpu_percent":[0-9.]*' | cut -d':' -f2)
    MEM=$(echo $MTPROTO_METRICS | grep -o '"memory_mb":[0-9.]*' | cut -d':' -f2)
    UPTIME=$(echo $MTPROTO_METRICS | grep -o '"uptime_seconds":[0-9.]*' | cut -d':' -f2)
    if [ ! -z "$CPU" ]; then
        echo -e "  MTProto CPU:      ${GREEN}${CPU}%${NC}"
        echo -e "  MTProto Memory:   ${GREEN}${MEM} MB${NC}"
        echo -e "  MTProto Uptime:   ${GREEN}$((${UPTIME%.*}/60)) minutes${NC}"
    fi
fi
```

### Fix 3: Rename Misleading Environment Variable

**Location**: `.env.development` line 187

**Change**:
```bash
# Before:
PROMETHEUS_PORT=9091  # ❌ Misleading - not actually Prometheus

# After:
MTPROTO_HEALTH_PORT=9091  # ✅ Clear purpose
```

### Fix 4: Add Pre-Start Port Cleanup

**Location**: `scripts/dev-start.sh` line 423 (in "all" case, before starting mtproto)

**Add**:
```bash
echo ""
echo -e "${BLUE}🚀 Starting MTProto data collection worker...${NC}"

# Clean up any zombie processes holding the health port
if lsof -ti:9091 >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 9091 already in use - cleaning up...${NC}"
    ZOMBIE_PID=$(lsof -ti:9091)
    if ps -p $ZOMBIE_PID > /dev/null; then
        echo -e "${YELLOW}🧟 Killing zombie process (PID: ${ZOMBIE_PID})${NC}"
        kill -9 $ZOMBIE_PID 2>/dev/null || true
        sleep 2
    fi
fi

start_service "mtproto_worker" 'python -m apps.mtproto.worker --interval 10' ""
```

---

## 📊 Current Health Status

**MTProto Worker (PID 3852150)**:
- ✅ Process running (uptime: 7.6 minutes)
- ✅ Port 9091 bound successfully
- ⚠️ Health status: **unhealthy** (heartbeat timeout)
- ⚠️ Last heartbeat: 447 seconds ago
- ℹ️ Status: sleeping (waiting for next collection cycle)
- 📊 Metrics: 0% CPU, 832 MB RAM (6.96%)

**Why "unhealthy" despite collecting data?**

The health server reports "unhealthy" because the heartbeat mechanism hasn't been updated. The worker is actually functioning - it's actively collecting messages from Telegram channels. The heartbeat timeout is a monitoring issue, not a functional issue.

**Current Collection Status**:
```
2025-11-23 12:54:47 - Fetched 2,000/5,000 messages (40.0%) - 104.2 msg/s
```
✅ Data collection is working!

---

## 🎯 Summary

### Answers to Your Questions:

1. **Port 9091 Usage**: ✅ **MTProto worker ONLY** (health server)
   - Bot uses polling (no port)
   - Webhook uses API port 11400
   - No conflicts

2. **Zombie Process Issue**: ❌ **dev-stop doesn't kill MTProto workers**
   - Missing `pkill -f "apps.mtproto.worker"` in cleanup
   - Old process (PID 2056150 from Nov 20) held port 9091
   - Manual kill required: `kill -9 2056150`

3. **Missing Health Checks**: ❌ **dev-status only shows process state, not health**
   - No MTProto worker check
   - No health endpoint interrogation
   - No metrics display (CPU, RAM, uptime)
   - Only checks: PostgreSQL port, Redis port, API port, Frontend port, Bot PID

### Priority Fixes:
1. 🔴 **HIGH**: Add MTProto worker cleanup to stop command
2. 🟡 **MEDIUM**: Add comprehensive health checks to status command
3. 🟡 **MEDIUM**: Add pre-start port cleanup
4. 🟢 **LOW**: Rename PROMETHEUS_PORT → MTPROTO_HEALTH_PORT
