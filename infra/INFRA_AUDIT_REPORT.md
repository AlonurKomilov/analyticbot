# 📋 Infrastructure Folder Audit Report

**Date:** December 24, 2025  
**Scope:** `/home/abcdev/projects/analyticbot/infra/`

---

## 🔴 CRITICAL: Duplicate/Overlapping Components Found

### 1. Redis/Cache Implementations - **7 DIFFERENT IMPLEMENTATIONS!**

| Location | Class/Purpose |
|----------|---------------|
| `cache/redis_cache.py` | `RedisJSONCache` - JSON caching with TTL |
| `cache/redis_cache_service.py` | `RedisCacheService` - CacheService port |
| `cache/redis_cache_adapter.py` | `RedisCacheAdapter` - AsyncCachePort |
| `cache/redis_client.py` | Global `redis_client` placeholder |
| `cache/async_redis_client.py` | `AsyncRedisClient` - RedisClientProtocol |
| `cache/advanced_decorators.py` | `CacheDecorators` - caching decorators |
| `security/adapters.py` | `RedisCache` - another CachePort implementation! |

**Impact:** Code duplication, inconsistent caching, maintenance nightmare

---

### 2. MarketplaceServiceRepository - **2 DIFFERENT FILES**

| Location | Status |
|----------|--------|
| `infra/db/repositories/marketplace_service_repository.py` | Active, used by apps |
| `infra/marketplace/repositories/services.py` | Duplicate with slight differences |

**Impact:** Confusion about which to use, both have similar but slightly different implementations

---

### 3. Telegram Analytics Adapter - **EXACT DUPLICATE**

| File | Lines |
|------|-------|
| `adapters/analytics/telegram_analytics_adapter.py` | 549 lines |
| `adapters/analytics/tg_analytics_adapter.py` | 549 lines (IDENTICAL!) |

**Impact:** Complete code duplication - 1098 wasted lines

---

### 4. Kubernetes Manifests - **RAW K8S + HELM DUPLICATION**

| Raw K8s (`k8s/`) | Helm Template (`helm/templates/`) |
|------------------|-----------------------------------|
| `api-deployment.yaml` | `api-deployment.yaml` |
| `bot-deployment.yaml` | `bot-deployment.yaml` |
| `configmap.yaml` | `configmap.yaml` |
| `secrets.yaml` | `secret.yaml` |
| `ingress.yaml` | `ingress.yaml` |

**Impact:** Must update both when making changes, risk of configuration drift

---

### 5. Process Management - **SUPERVISOR + SYSTEMD DUPLICATION**

Both manage the SAME THREE services:

| Supervisor (`supervisor/`) | Systemd (`systemd/`) |
|---------------------------|----------------------|
| `analyticbot-api` program | `analyticbot-api.service` |
| `analyticbot-bot` program | `analyticbot-bot.service` |
| `analyticbot-mtproto-worker` | `analyticbot-mtproto-worker.service` |

**Impact:** Confusion about deployment method

---

### 6. Health Check Duplication

| Location | Class |
|----------|-------|
| `health/adapters.py` | `PostgreSQLHealthAdapter`, `RedisHealthAdapter` |
| `db/health_utils.py` | `check_db_health()`, `PostgreSQLHealthAdapter` |

**Impact:** Two different health check implementations

---

### 7. Notification Services Overlap

| Location | Purpose |
|----------|---------|
| `notifications/simple_notification_service.py` | `SimpleNotificationService`, `EmailNotificationService` |
| `adapters/telegram_alert_adapter.py` | `TelegramAlertAdapter` - Also sends notifications |

---

### 8. Observability Scattered

| Folder | Purpose |
|--------|---------|
| `logging/` | Structured JSON logging |
| `obs/` | OpenTelemetry tracing |
| `monitoring/` | Prometheus metrics, Grafana dashboards |
| `health/` | Health check adapters |

**Impact:** Related observability code spread across 4 folders

---

## 📁 Current Structure vs Proposed Structure

### Current (Problematic):
```
infra/
├── adapters/                    # Mixed adapters
│   ├── analytics/
│   │   ├── telegram_analytics_adapter.py
│   │   └── tg_analytics_adapter.py    # ❌ DUPLICATE
│   ├── payment/
│   └── telegram_alert_adapter.py
├── bot/                         # ❌ Empty placeholder
├── cache/                       # ❌ 6 Redis implementations
├── common/                      # Rate limiting
├── db/                          # Database + repositories
├── factories/                   # Analytics factory
├── health/                      # ❌ Should be in monitoring
├── helm/                        # ❌ Duplicates k8s/
├── k8s/                         # Raw K8s manifests
├── logging/                     # ❌ Should be in observability
├── marketplace/                 # ❌ Duplicates db/repositories
├── monitoring/                  # Prometheus/Grafana
├── nginx/                       # ✅ OK (already consolidated)
├── notifications/               # Notification services
├── obs/                         # ❌ Should be in observability
├── rendering/                   # Chart rendering
├── scripts/                     # Deployment scripts
├── security/                    # ❌ Has another Redis impl
├── services/                    # Payment services
├── supervisor/                  # ❌ OR systemd, not both
├── systemd/                     # ❌ OR supervisor, not both
├── telegram/                    # Telegram/MTProto infra
├── terraform/                   # IaC
└── ansible/                     # Configuration management
```

### Proposed (Clean):
```
infra/
├── adapters/                    # All infrastructure adapters
│   ├── analytics/
│   │   └── telegram_analytics_adapter.py  # ✅ Single file
│   ├── payment/
│   ├── notifications/           # Move from notifications/
│   └── security/                # Move from security/
├── cache/                       # ✅ Single unified Redis implementation
│   ├── __init__.py
│   ├── redis_client.py          # Single async client
│   └── decorators.py            # Caching decorators
├── db/                          # Database layer
│   ├── repositories/            # All repositories here
│   │   └── marketplace_service_repository.py  # Single file
│   ├── migrations/
│   └── models/
├── observability/               # ✅ All observability consolidated
│   ├── logging/                 # Structured logging
│   ├── tracing/                 # OpenTelemetry (from obs/)
│   ├── metrics/                 # Prometheus (from monitoring/)
│   ├── health/                  # Health checks
│   └── dashboards/              # Grafana dashboards
├── deploy/                      # ✅ All deployment consolidated
│   ├── k8s/                     # OR helm/, not both
│   ├── scripts/
│   ├── terraform/
│   └── ansible/
├── process/                     # Choose ONE
│   └── systemd/                 # OR supervisor/, not both
├── nginx/                       # ✅ Already consolidated
├── telegram/                    # Telegram infra
├── rendering/                   # Chart generation
└── services/                    # Business services
    └── payment/
```

---

## 🎯 Action Plan

### Phase 1: Delete Exact Duplicates (IMMEDIATE)

```bash
# Delete exact duplicate file
rm infra/adapters/analytics/tg_analytics_adapter.py
```

### Phase 2: Consolidate Cache (HIGH PRIORITY)

1. Choose ONE Redis implementation (recommend `redis_cache_adapter.py`)
2. Delete others:
   - `cache/redis_cache.py`
   - `cache/redis_cache_service.py`  
   - `cache/async_redis_client.py`
   - `cache/redis_client.py`
   - `security/adapters.py` → Move JWT code, delete Redis

### Phase 3: Consolidate Repositories (HIGH PRIORITY)

1. Keep: `infra/db/repositories/marketplace_service_repository.py`
2. Delete: `infra/marketplace/repositories/services.py`
3. Update imports in `infra/marketplace/__init__.py`

### Phase 4: Choose K8s Strategy (MEDIUM PRIORITY)

**Option A: Keep Helm only (RECOMMENDED)**
- Delete `infra/k8s/` folder
- Helm is more flexible for multi-environment

**Option B: Keep raw K8s only**
- Delete `infra/helm/` folder
- Use Kustomize for overlays

### Phase 5: Choose Process Manager (MEDIUM PRIORITY)

For VM deployment:
- **If using systemd (modern):** Delete `infra/supervisor/`
- **If using supervisor:** Delete `infra/systemd/`

For K8s deployment:
- Delete BOTH (K8s manages processes)

### Phase 6: Consolidate Observability (MEDIUM PRIORITY)

Create new structure:
```bash
mkdir -p infra/observability/{logging,tracing,metrics,health,dashboards}
mv infra/logging/* infra/observability/logging/
mv infra/obs/* infra/observability/tracing/
mv infra/monitoring/prometheus infra/observability/metrics/
mv infra/monitoring/grafana infra/observability/dashboards/
mv infra/health/* infra/observability/health/
```

### Phase 7: Delete Empty Placeholders (LOW PRIORITY)

```bash
# bot/ only contains empty __init__.py
rm -rf infra/bot/
```

---

## 📊 Impact Summary

| Category | Files Affected | Lines Saved | Priority |
|----------|---------------|-------------|----------|
| Duplicate analytics adapter | 1 file | ~549 lines | 🔴 IMMEDIATE |
| Redis implementations | 5+ files | ~800 lines | 🔴 HIGH |
| Marketplace repo duplicate | 1 file | ~200 lines | 🔴 HIGH |
| K8s/Helm duplication | 12+ files | ~500 lines | 🟡 MEDIUM |
| Process manager duplication | 3-4 files | ~100 lines | 🟡 MEDIUM |
| Observability scatter | 4 folders | 0 (reorg) | 🟡 MEDIUM |
| Empty placeholders | 1 folder | 0 | 🟢 LOW |

**Total estimated cleanup:** ~2,000+ lines of duplicate code

---

## ✅ Next Steps

1. **Review this report** and confirm which consolidations to proceed with
2. **Start with Phase 1** - delete exact duplicates (safe, immediate)
3. **Test thoroughly** after each phase before proceeding
4. **Update imports** across the codebase for moved/deleted files

---

*Generated by infrastructure audit on December 24, 2025*
