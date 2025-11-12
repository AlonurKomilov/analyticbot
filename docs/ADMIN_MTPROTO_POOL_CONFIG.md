# Admin MTProto Connection Pool Configuration 🎛️

## Overview

The MTProto connection pool is now **fully configurable** by system administrators through environment variables and Admin API endpoints. This allows you to scale the system based on server capacity without code changes.

---

## 🎯 Key Configuration Settings

### 1. **MTPROTO_MAX_CONCURRENT_USERS** (System-Wide Limit)
**Most Important Setting for Scaling**

- **Description**: Maximum number of users that can collect data simultaneously
- **Default**: 10 users
- **Range**: 1-200 users
- **Impact**: Each active user consumes ~850MB RAM during collection

#### Recommended Values by Server Size:

| Server Type | RAM | CPU | Recommended Value | Expected Peak RAM |
|-------------|-----|-----|-------------------|-------------------|
| Small VPS   | 2GB | 2   | 5-10 users       | 2-4GB            |
| Medium VPS  | 4GB | 4   | 10-20 users      | 4-6GB            |
| Large VPS   | 8GB | 8   | 20-50 users      | 6-10GB           |
| Dedicated   | 16GB+ | 16+ | 50-100+ users   | 10-20GB          |

**Formula**: `(Available RAM - 2GB for system) / 850MB = Max Users`

---

### 2. **MTPROTO_MAX_CONNECTIONS_PER_USER**
- **Description**: Maximum connections per user (prevents duplicate workers)
- **Default**: 1
- **Recommended**: Keep at 1 to prevent resource conflicts
- **Range**: 1-5

---

### 3. **MTPROTO_SESSION_TIMEOUT**
- **Description**: Force close sessions exceeding this duration
- **Default**: 600 seconds (10 minutes)
- **Range**: 60-3600 seconds
- **Purpose**: Prevents hung connections from consuming resources

---

### 4. **MTPROTO_CONNECTION_TIMEOUT**
- **Description**: Time allowed to establish Telegram connection
- **Default**: 300 seconds (5 minutes)
- **Range**: 30-600 seconds

---

### 5. **MTPROTO_IDLE_TIMEOUT**
- **Description**: Disconnect if no activity for this duration
- **Default**: 180 seconds (3 minutes)
- **Range**: 30-600 seconds

---

## 🔧 Configuration Methods

### Method 1: Environment Variables (Recommended for Production)

Edit `.env.development` or `.env.production`:

```bash
# Current Dev/Test VPS (2GB RAM)
MTPROTO_MAX_CONCURRENT_USERS=10
MTPROTO_MAX_CONNECTIONS_PER_USER=1
MTPROTO_SESSION_TIMEOUT=600
MTPROTO_CONNECTION_TIMEOUT=300
MTPROTO_IDLE_TIMEOUT=180
```

**After changing**: Restart MTProto worker for changes to take effect:
```bash
make -f Makefile.dev dev-stop
make -f Makefile.dev dev-start
```

---

### Method 2: Admin API (Runtime Configuration)

#### Get Current Configuration
```bash
GET /admin/system/mtproto/pool/config
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "max_concurrent_users": 10,
  "max_connections_per_user": 1,
  "session_timeout": 600,
  "connection_timeout": 300,
  "idle_timeout": 180
}
```

#### Update Configuration
```bash
PUT /admin/system/mtproto/pool/config
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "max_concurrent_users": 30,
  "max_connections_per_user": 1,
  "session_timeout": 600,
  "connection_timeout": 300,
  "idle_timeout": 180
}
```

**Note**: Changes are written to `.env.development` and require worker restart.

#### Get Pool Status
```bash
GET /admin/system/mtproto/pool/status
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "active_sessions": 2,
  "max_concurrent_users": 10,
  "max_connections_per_user": 1,
  "session_timeout": 600,
  "connection_timeout": 300,
  "idle_timeout": 180,
  "metrics": {
    "total_sessions": 150,
    "recent_sessions": 50,
    "avg_duration_seconds": 78.5,
    "avg_messages_per_session": 2763,
    "avg_channels_per_session": 1.2,
    "total_errors": 3
  }
}
```

---

## 📈 Scaling Examples

### Example 1: Current Dev/Test VPS (2GB RAM)
```bash
MTPROTO_MAX_CONCURRENT_USERS=10
```
- **Memory**: Peak 3-4GB (only few users active simultaneously)
- **Capacity**: Suitable for 10-20 total users
- **Status**: ✅ **Current Configuration**

---

### Example 2: Production Server (8GB RAM)
```bash
MTPROTO_MAX_CONCURRENT_USERS=30
```
- **Memory**: Peak 6-8GB (staggered collection cycles)
- **Capacity**: Suitable for 50-100 total users
- **Throughput**: 3x current capacity

**How to Apply:**
1. Update `.env.production` with new value
2. Deploy to production server
3. Restart MTProto worker
4. Monitor memory usage: `free -h`

---

### Example 3: High-Load Server (16GB+ RAM)
```bash
MTPROTO_MAX_CONCURRENT_USERS=50
```
- **Memory**: Peak 10-12GB (intelligent scheduling)
- **Capacity**: Suitable for 100-200+ total users
- **Throughput**: 5x current capacity

**Additional Optimizations for High Load:**
- Deploy multiple MTProto workers with load balancing
- Use read replicas for database queries
- Implement Redis caching for frequently accessed data
- Consider message queue (RabbitMQ/Kafka) for async processing

---

## 🔍 Monitoring & Debugging

### Check Current Pool Status

**Command Line:**
```bash
python -m apps.mtproto.worker --status

# Output includes:
📊 Connection Pool Metrics:
   total_sessions: 150
   avg_duration_seconds: 78.5
   avg_messages_per_session: 2763
   active_sessions: 2
   max_connections: 10
```

**Logs:**
```bash
tail -f logs/dev_mtproto_worker.log | grep -E "Acquired|Released"

# Shows:
📡 Acquired MTProto session for user 844338517 (active: 2/10)
✅ Released MTProto session for user 844338517 (duration: 78.0s, channels: 1, messages: 2763, errors: 0)
```

---

### Monitor System Resources

**Memory Usage:**
```bash
# Real-time memory monitoring
watch -n 2 'free -h'

# Check MTProto worker memory
ps aux | grep "mtproto.worker" | awk '{print $6/1024 " MB"}'
```

**Database Connections:**
```bash
PGPASSWORD=change_me psql -h localhost -p 10100 -U analytic -d analytic_bot \
  -c "SELECT count(*), state FROM pg_stat_activity WHERE datname = 'analytic_bot' GROUP BY state;"
```

**Active Sessions:**
```bash
# Count active MTProto workers
ps aux | grep "apps.mtproto.worker" | grep -v grep | wc -l
```

---

## ⚠️ Important Considerations

### 1. **Memory Requirements**
- Each concurrent user: ~850MB during active collection
- System overhead: ~2GB for OS and other services
- **Formula**: Total RAM needed = (Max Users × 850MB) + 2GB

### 2. **Restart Required**
- Configuration changes require MTProto worker restart
- Active collections will be interrupted
- **Best Practice**: Schedule restarts during low-usage periods

### 3. **Database Connections**
- Connection pool auto-adjusts based on load
- Default: 15 connections per MTProto worker
- Monitor with: `SELECT count(*) FROM pg_stat_activity`

### 4. **CPU Considerations**
- Each collection uses 1-2 CPU cores during active processing
- Recommended: 1 CPU core per 5-10 concurrent users
- Monitor with: `top` or `htop`

---

## 🚀 Migration Path: Dev VPS → Production Server

When moving to a bigger server, follow these steps:

### Step 1: Assess New Server Capacity
```bash
# Check available RAM
free -h

# Check CPU cores
nproc

# Calculate max users
echo "scale=0; ($(free -m | grep Mem | awk '{print $7}') - 2048) / 850" | bc
```

### Step 2: Update Production Configuration
```bash
# Edit .env.production
nano .env.production

# Example for 8GB server:
MTPROTO_MAX_CONCURRENT_USERS=30
```

### Step 3: Deploy and Test
```bash
# Deploy to production
git pull origin main
make -f Makefile.dev dev-stop
make -f Makefile.dev dev-start

# Monitor for 10-15 minutes
tail -f logs/dev_mtproto_worker.log
watch -n 5 'free -h'
```

### Step 4: Gradual Scaling
Start conservative and increase gradually:
- **Day 1**: Set to 50% of calculated max
- **Day 2-3**: Monitor performance, adjust if needed
- **Day 4-7**: Scale to 75% if stable
- **Week 2+**: Scale to 100% if no issues

---

## 📊 Performance Benchmarks

Based on current system measurements:

| Metric | Value |
|--------|-------|
| **Collection Duration** | 78 seconds average |
| **Messages per Session** | 2,763 average |
| **Throughput** | 35 messages/second |
| **Memory per User** | 850MB during collection |
| **Database Writes** | 57 messages/second |
| **Connection Lifetime** | Auto-closed after completion |

---

## 🛠️ Troubleshooting

### Issue: "Maximum concurrent users reached"

**Symptoms**: Users queued, collections delayed

**Solutions**:
1. Increase `MTPROTO_MAX_CONCURRENT_USERS`
2. Check for stuck sessions: `python -m apps.mtproto.worker --status`
3. Restart worker if sessions stuck

---

### Issue: High memory usage

**Symptoms**: System slow, OOM errors

**Solutions**:
1. Reduce `MTPROTO_MAX_CONCURRENT_USERS`
2. Reduce `MTPROTO_HISTORY_LIMIT_PER_RUN` (fewer messages per run)
3. Increase collection interval (less frequent runs)
4. Upgrade server RAM

---

### Issue: Database connection pool exhausted

**Symptoms**: "Could not acquire connection" errors

**Solutions**:
1. Reduce `MTPROTO_MAX_CONCURRENT_USERS`
2. Check idle connections: `SELECT * FROM pg_stat_activity`
3. Increase database max_connections in PostgreSQL config

---

## 📝 Best Practices

1. **Start Conservative**: Begin with lower limits, scale up gradually
2. **Monitor First**: Watch memory/CPU for 24-48 hours before increasing
3. **Schedule Restarts**: Apply config changes during low-usage periods
4. **Use Admin API**: Check pool status regularly via `/admin/system/mtproto/pool/status`
5. **Document Changes**: Keep log of configuration changes and their impact
6. **Set Alerts**: Monitor memory usage and set alerts at 80% capacity

---

## 🎯 Quick Reference

### Environment Variables
```bash
MTPROTO_MAX_CONCURRENT_USERS=10      # System-wide user limit
MTPROTO_MAX_CONNECTIONS_PER_USER=1   # Per-user limit
MTPROTO_SESSION_TIMEOUT=600          # 10 minutes
MTPROTO_CONNECTION_TIMEOUT=300       # 5 minutes
MTPROTO_IDLE_TIMEOUT=180             # 3 minutes
```

### Admin API Endpoints
```
GET    /admin/system/mtproto/pool/config   # Get configuration
PUT    /admin/system/mtproto/pool/config   # Update configuration
GET    /admin/system/mtproto/pool/status   # Get current status
```

### Monitoring Commands
```bash
python -m apps.mtproto.worker --status     # Pool status
free -h                                    # Memory usage
ps aux | grep mtproto                      # Active workers
tail -f logs/dev_mtproto_worker.log        # Real-time logs
```

---

**Status**: ✅ Fully Implemented and Configurable
**Date**: November 11, 2025
**Ready for Production Scaling**: Yes, with admin control
