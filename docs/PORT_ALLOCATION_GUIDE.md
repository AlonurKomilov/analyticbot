# 🔌 Port Allocation Guide for AnalyticBot

## 📊 **MASTER PORT ALLOCATION TABLE**

### **Development Environment (docker-compose.yml)**
| Service | Internal Port | External Port | URL | Status |
|---------|---------------|---------------|-----|--------|
| PostgreSQL | 5432 | 5433 | `localhost:5433` | ✅ ACTIVE |
| Redis | 6379 | 6380 | `localhost:6380` | ✅ ACTIVE |
| API Service | 8000 | 8000 | `localhost:8000` | ✅ ACTIVE |
| Frontend (TWA) | 80 | 3000 | `localhost:3000` | ✅ ACTIVE |
| Frontend Dev | 5173 | 5173 | `localhost:5173` | ✅ ACTIVE |

### **Production Environment (docker-compose.prod.yml)**
| Service | Internal Port | External Port | URL | Status |
|---------|---------------|---------------|-----|--------|
| PostgreSQL | 5432 | INTERNAL | `postgres:5432` | ✅ ACTIVE |
| Redis | 6379 | INTERNAL | `redis:6379` | ✅ ACTIVE |
| API Service | 8000 | INTERNAL | `api:8000` | ✅ ACTIVE |
| Nginx Proxy | 80 | 80 | `localhost:80` | ✅ ACTIVE |
| Prometheus | 9090 | COMMENTED | `prometheus:9090` | 💤 DISABLED |
| Grafana | 3000 | **3001** | `localhost:3001` | 💤 DISABLED |

### **MTProto Services (docker-compose.mtproto.scale.yml)**
| Service | Internal Port | External Port | URL | Status |
|---------|---------------|---------------|-----|--------|
| MTProto Updates | 8091 | INTERNAL | `mtproto-updates:8091` | 💤 READY |
| MTProto History | 8092 | INTERNAL | `mtproto-history:8092` | 💤 READY |
| MTProto Stats | 8093 | INTERNAL | `mtproto-stats:8093` | 💤 READY |
| Prometheus (MTProto) | 9090 | **9091** | `localhost:9091` | 💤 READY |
| Grafana (MTProto) | 3000 | **3002** | `localhost:3002` | 💤 READY |
| Nginx (MTProto) | 80 | **8080** | `localhost:8080` | 💤 READY |

### **🔧 FIXED CONFLICTS:**

1. **✅ Grafana Port Updated**: Changed from `3000:3000` to `3001:3000` to avoid conflict with TWA frontend
2. **✅ Production Isolation**: All production services use internal networking only (except Nginx on port 80)
3. **✅ Development Separation**: Development uses offset ports (5433, 6380) to avoid system conflicts

### **🌐 SERVICE ACCESS ENDPOINTS:**

#### **Development Mode:**
```bash
# Core Services
curl http://localhost:8000/health              # API Health Check
curl http://localhost:3000                     # TWA Frontend (Production Build)
curl http://localhost:5173                     # TWA Frontend (Development Mode)

# Database & Cache
psql -h localhost -p 5433 -U analytic analytic_bot    # PostgreSQL
redis-cli -h localhost -p 6380                        # Redis
```

#### **Production Mode:**
```bash
# Public Access (via Nginx)
curl http://localhost/api/health               # API via Nginx
curl http://localhost                          # Will serve frontend when configured

# Internal Access (for debugging)
docker exec analyticbot-api-prod curl http://localhost:8000/health
docker exec analyticbot-postgres-prod psql -U analytic analytic_bot

# Monitoring (when enabled)
curl http://localhost:3001                     # Grafana (if uncommented)
# curl http://localhost:9090                   # Prometheus (if uncommented)
```

### **⚠️ PORT CONFLICT PREVENTION:**

#### **Reserved Port Ranges:**
- **3000-3099**: Frontend services
  - 3000: TWA Frontend (Development)
  - 3001: Grafana (Production, when enabled)
- **5000-5999**: Development tools
  - 5173: Vite dev server
  - 5433: PostgreSQL (Development)
- **6000-6999**: Cache & messaging
  - 6380: Redis (Development)
- **8000-8999**: API services
  - 8000: Main API
- **9000-9999**: Monitoring
  - 9090: Prometheus

#### **NEVER USE THESE PORTS:**
- **80, 443**: Reserved for Nginx reverse proxy
- **22**: SSH
- **25, 587**: Email services
- **53**: DNS
- **3306**: MySQL (if used elsewhere)
- **5432**: PostgreSQL default (conflicts with system)

### **🚀 DEPLOYMENT-SPECIFIC CONFIGURATIONS:**

#### **Development Deployment:**
```bash
# Start all development services
docker-compose up -d

# Access points:
# - API: http://localhost:8000
# - Frontend: http://localhost:3000 (prod build) or http://localhost:5173 (dev)
# - Database: localhost:5433
# - Redis: localhost:6380
```

#### **Production Deployment:**
```bash
# Start production services
docker-compose -f infra/docker/docker-compose.prod.yml up -d

# Access points:
# - Public API: http://localhost/api/*
# - Public Frontend: http://localhost (when configured)
# - Monitoring: http://localhost:3001 (Grafana, if enabled)
```

### **🔍 PORT CONFLICT DEBUGGING:**

#### **Check for conflicts:**
```bash
# Check if ports are in use
sudo netstat -tulpn | grep -E ':(3000|3001|5173|5433|6380|8000|9090)\s'

# Check specific port
sudo lsof -i :3000

# Docker port mappings
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

#### **Quick conflict resolution:**
```bash
# Kill process on specific port
sudo fuser -k 3000/tcp

# Or find and kill by PID
sudo lsof -ti:3000 | xargs sudo kill -9
```

### **📝 UPDATING PORT CONFIGURATIONS:**

When changing ports, update these files:
1. `docker-compose.yml` - Development port mappings
2. `infra/docker/docker-compose.prod.yml` - Production port mappings
3. `.env` - Environment variables
4. `apps/frontend/.env.docker` - Frontend API URLs
5. Documentation and scripts referencing specific ports

### **🎯 CURRENT STATUS:**

- ✅ **Port 3000 Conflict**: RESOLVED (Grafana moved to 3001)
- ✅ **Development Ports**: All properly offset to avoid system conflicts
- ✅ **Production Isolation**: Internal networking only, except Nginx
- ✅ **Monitoring Ports**: Reserved but disabled by default
- ✅ **Documentation**: Updated with clear allocation scheme

**Last Updated**: September 11, 2025
**Next Review**: When adding new services
