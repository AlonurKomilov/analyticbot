# Database Scaling Guide: 100,000+ Users

## Current State (Optimized for ~10K users)

```
┌─────────────────┐
│   Application   │
│   (50 conns)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   (Primary)     │
│   64 tables     │
│   36 indexes    │
└─────────────────┘
```

**Current Limits:**
- Connection pool: 10-50 connections
- Max concurrent users: ~1,000
- Database size: < 50GB
- Query latency: ~10-50ms average

---

## Phase 1: 10K → 50K Users

### 1.1 Add PgBouncer (Connection Multiplexing)

```
┌─────────────────┐
│   Application   │
│ (200 app conns) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PgBouncer     │
│   (50 DB conns) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
└─────────────────┘
```

**Configuration:**
```ini
# pgbouncer.ini
[databases]
analyticbot = host=localhost port=5432 dbname=analyticbot

[pgbouncer]
pool_mode = transaction
max_client_conn = 200
default_pool_size = 50
reserve_pool_size = 10
reserve_pool_timeout = 3
```

**Code Usage:**
```python
from infra.db.scaling import PgBouncerPool, SCALE_CONFIGS

# Use medium config for 50K users
pool = await PgBouncerPool.create(
    host="pgbouncer-host",
    port=6432,  # PgBouncer port
    database="analyticbot",
    config=SCALE_CONFIGS["medium"]  # 200 connections
)
```

### 1.2 Enable Aggressive Caching

```python
from infra.db.scaling import QueryCacheManager, CacheTier

cache = QueryCacheManager(redis_client)

# Cache user data (5 min TTL)
@cache.cached(namespace="user", tier=CacheTier.STANDARD)
async def get_user(user_id: int) -> User:
    return await db.fetch_user(user_id)

# Cache channel stats (30 sec TTL)
@cache.cached(namespace="stats", tier=CacheTier.HOT)
async def get_channel_stats(channel_id: int) -> ChannelStats:
    return await db.fetch_stats(channel_id)
```

**Expected Cache Hit Rate:** 70-80%

---

## Phase 2: 50K → 100K Users

### 2.1 Add Read Replicas

```
                    ┌─────────────────┐
                    │   Application   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ ReadReplicaRouter│
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│    Primary      │ │   Replica 1     │ │   Replica 2     │
│  (WRITES only)  │ │   (READS)       │ │   (READS)       │
│   Weight: 0     │ │   Weight: 50    │ │   Weight: 50    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

**Configuration:**
```python
from infra.db.scaling import ReadReplicaRouter, ReadReplicaRouterConfig

config = ReadReplicaRouterConfig(
    primary_dsn="postgresql://user:pass@primary:5432/db",
    replicas=[
        ReplicaConfig(
            dsn="postgresql://user:pass@replica1:5432/db",
            weight=50,
            max_lag_seconds=30
        ),
        ReplicaConfig(
            dsn="postgresql://user:pass@replica2:5432/db", 
            weight=50,
            max_lag_seconds=30
        ),
    ]
)

router = await ReadReplicaRouter.create(config)

# Automatic routing
users = await router.fetch("SELECT * FROM users")  # → Replica
await router.execute("INSERT INTO users ...")       # → Primary
```

### 2.2 Table Partitioning

Partition large time-series tables:

```python
from infra.db.scaling import PartitionManager

pm = PartitionManager(pool)

# Create monthly partitions for post_metrics
await pm.create_monthly_partitions(
    table_name="post_metrics",
    months_ahead=3,   # Future partitions
    months_behind=12  # Historical partitions
)

# Auto-cleanup old partitions
await pm.drop_old_partitions(
    table_name="post_metrics",
    retention_months=12
)
```

**Tables to Partition:**
| Table | Partition Key | Retention |
|-------|--------------|-----------|
| post_metrics | snapshot_time | 12 months |
| service_usage_log | created_at | 6 months |
| credit_transactions | created_at | 24 months |
| mtproto_audit_log | created_at | 12 months |

---

## Phase 3: 100K+ Users

### 3.1 Enterprise Configuration

```
┌─────────────────────────────────────────────────────────┐
│                      Application                        │
│  (Multiple instances with load balancer)                │
└────────────────────────┬────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
┌─────────────────────┐   ┌─────────────────────┐
│ QueryCacheManager   │   │   ReadReplicaRouter │
│ (Redis Cluster)     │   └──────────┬──────────┘
└─────────────────────┘              │
                         ┌───────────┼───────────┐
                         ▼           ▼           ▼
              ┌──────────────┐ ┌──────────┐ ┌──────────┐
              │  PgBouncer   │ │ Replica1 │ │ Replica2 │
              │  (Primary)   │ │          │ │          │
              └──────┬───────┘ └──────────┘ └──────────┘
                     │
                     ▼
              ┌──────────────┐
              │   Primary    │
              │  (Writes)    │
              └──────────────┘
```

**PgBouncer Enterprise Config:**
```python
from infra.db.scaling import PgBouncerPool, SCALE_CONFIGS

pool = await PgBouncerPool.create(
    config=SCALE_CONFIGS["enterprise"]  # 500 connections
)
```

### 3.2 Index Optimization for Scale

```sql
-- Partial indexes for active data only
CREATE INDEX CONCURRENTLY idx_users_active 
ON users (id) 
WHERE is_active = true;

-- Covering indexes to avoid table lookups
CREATE INDEX CONCURRENTLY idx_posts_covering 
ON posts (channel_id, created_at) 
INCLUDE (msg_id, views, forwards);

-- BRIN indexes for time-series data
CREATE INDEX CONCURRENTLY idx_metrics_time_brin 
ON post_metrics USING BRIN (snapshot_time);
```

### 3.3 Connection Pool Settings

| Scale | App Connections | DB Connections | PgBouncer Mode |
|-------|----------------|----------------|----------------|
| 10K   | 50             | 50             | Direct         |
| 50K   | 200            | 50             | Transaction    |
| 100K  | 500            | 100            | Transaction    |
| 500K  | 1000           | 200            | Transaction    |

---

## Phase 4: 500K+ Users (Future)

### 4.1 Horizontal Sharding

Consider sharding by `user_id`:

```
┌─────────────┐
│   Router    │
└──────┬──────┘
       │
┌──────┼──────┬──────┐
│      │      │      │
▼      ▼      ▼      ▼
Shard1 Shard2 Shard3 Shard4
(0-25) (26-50)(51-75)(76-99)
 hash   hash   hash   hash
```

### 4.2 Multiple PgBouncer Instances

```yaml
# docker-compose.scale.yml
services:
  pgbouncer-1:
    image: edoburu/pgbouncer
    ports:
      - "6432:6432"
  
  pgbouncer-2:
    image: edoburu/pgbouncer
    ports:
      - "6433:6432"
```

### 4.3 Redis Cluster

```python
from redis.cluster import RedisCluster

redis = RedisCluster(
    startup_nodes=[
        {"host": "redis-1", "port": 6379},
        {"host": "redis-2", "port": 6379},
        {"host": "redis-3", "port": 6379},
    ]
)
```

---

## Monitoring at Scale

### Key Metrics to Watch

```python
# Database metrics
- Active connections / Max connections (keep < 80%)
- Query latency p99 (keep < 100ms)
- Cache hit rate (keep > 80%)
- Replication lag (keep < 30s)
- Disk usage growth rate

# Application metrics
- Request latency p99
- Error rate
- Queue depth (Celery)
```

### Alerting Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Connection usage | 70% | 90% |
| Query latency p99 | 100ms | 500ms |
| Cache hit rate | < 70% | < 50% |
| Replication lag | 30s | 60s |
| Disk usage | 70% | 85% |

---

## Quick Start Commands

### Deploy PgBouncer
```bash
# Docker
docker run -d \
  --name pgbouncer \
  -e DATABASE_URL="postgresql://user:pass@db:5432/analyticbot" \
  -e POOL_MODE=transaction \
  -e MAX_CLIENT_CONN=200 \
  -e DEFAULT_POOL_SIZE=50 \
  -p 6432:6432 \
  edoburu/pgbouncer

# Update app config
export DATABASE_URL="postgresql://user:pass@localhost:6432/analyticbot"
```

### Add Read Replica (AWS RDS example)
```bash
aws rds create-db-instance-read-replica \
  --db-instance-identifier analyticbot-replica-1 \
  --source-db-instance-identifier analyticbot-primary \
  --db-instance-class db.r6g.large
```

### Create Partitions
```bash
# Run migration
alembic upgrade head

# Or manual
python -c "
from infra.db.scaling import PartitionManager
import asyncio
asyncio.run(pm.create_monthly_partitions('post_metrics'))
"
```

---

## Summary: Scaling Roadmap

| Users | Infrastructure Changes | Estimated Cost |
|-------|----------------------|----------------|
| 10K → 50K | + PgBouncer, + Redis cache | +$50/mo |
| 50K → 100K | + 2 Read replicas, + Partitioning | +$200/mo |
| 100K → 500K | + More replicas, + Redis cluster | +$500/mo |
| 500K+ | + Sharding, + Multiple PgBouncer | +$1000+/mo |

Your current database architecture is **ready for 100K+ users** with these additions:
1. ✅ Indexes optimized
2. ✅ Query caching framework
3. ✅ Connection pooling ready
4. ✅ Read replica router ready
5. ✅ Partition manager ready
