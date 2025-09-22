# 🔄 Port Restructuring Plan - AnalyticBot

**Current Date:** September 18, 2025  
**Status:** Planning Phase

## 📋 Current vs Proposed Port Architecture

### 🔴 Current Port Assignment Issues

**Development (.env.development):**
```
API_PORT=11300          # API Service
FRONTEND_PORT=11400     # Frontend Service
POSTGRES_PORT=10100     # Mixed series!
REDIS_PORT=10200        # Mixed series!
PROMETHEUS_PORT=9091    # Outside series!
SMTP_PORT=1025          # Outside series!
```

**Production (.env.production):**
```
API_PORT=10300                    # API Service
FRONTEND_PORT=10400               # Frontend Service  
POSTGRES_PORT=5432                # Not in 10xxx series!
POSTGRES_EXTERNAL_PORT=10100      # Correct
REDIS_PORT=6379                   # Not in 10xxx series!
REDIS_EXTERNAL_PORT=10200         # Correct
PROMETHEUS_PORT=9090              # Outside series!
SMTP_PORT=587                     # Outside series!
```

## 🎯 NEW PROPOSED PORT ARCHITECTURE

### 🟢 Development Environment (11xxx Series)
```
FRONTEND_PORT=11300               # Frontend (moved from 11400)
API_PORT=11400                    # API (moved from 11300)
POSTGRES_PORT=10100               # PostgreSQL (moved from 10100)
REDIS_PORT=10200                  # Redis (moved from 10200)
PROMETHEUS_PORT=11500             # Prometheus (moved from 9091)
SMTP_PORT=11600                   # SMTP (moved from 1025)
```

### 🟢 Production Environment (10xxx Series)
```
FRONTEND_PORT=10300               # Frontend (moved from 10400)
API_PORT=10400                    # API (moved from 10300)
POSTGRES_PORT=5432                # Internal (unchanged)
POSTGRES_EXTERNAL_PORT=10100      # External (unchanged)
REDIS_PORT=6379                   # Internal (unchanged)  
REDIS_EXTERNAL_PORT=10200         # External (unchanged)
PROMETHEUS_PORT=10500             # Prometheus (moved from 9090)
SMTP_PORT=10600                   # SMTP (was variable 587)
```

## 🔧 Required Changes Summary

### 1. Environment Files
- **`.env.development`**: Update 6 port variables
- **`.env.production`**: Update 4 port variables

### 2. Docker Configuration
- **`docker-compose.yml`**: Update port mappings for all services

### 3. Development Scripts
- **`scripts/dev-start.sh`**: Update hardcoded ports (11300→11400, 11400→11300)

### 4. Application Code
- **Frontend configs**: Update API URL references
- **API configs**: Update any hardcoded ports
- **Health checks**: Update port references

### 5. Documentation
- **README files**: Update port references
- **Documentation**: Update all port examples

## ⚠️ CRITICAL CONSIDERATIONS

### 1. Service Dependencies
- Frontend needs to know new API port (11300→11400 in dev)
- Health checks need updated port references
- Docker internal networking may be affected

### 2. External Integrations
- Dev tunnels currently pointing to 11400 (frontend)
- External monitoring tools
- Load balancers or reverse proxies

### 3. Breaking Changes
- **Development workflows** will break temporarily
- **Running services** need to be restarted
- **Local configurations** need updates

## 🚨 RISKS IDENTIFIED

### High Risk
1. **Frontend-API communication** could break if not updated together
2. **Docker container networking** could fail
3. **Development tunnels** will need reconfiguration

### Medium Risk
1. **Health check failures** during transition
2. **Monitoring disruption** from Prometheus port change
3. **Email service disruption** from SMTP port change

### Low Risk
1. **Documentation inconsistency**
2. **Log file references**

## 📝 RECOMMENDED IMPLEMENTATION PLAN

### Phase 1: Preparation
1. ✅ **Backup current configuration**
2. ✅ **Document all current port usages**
3. ✅ **Identify all files requiring changes**

### Phase 2: Environment Updates
1. 🔄 **Update .env.development**
2. 🔄 **Update .env.production**
3. 🔄 **Update example files**

### Phase 3: Configuration Updates
1. 🔄 **Update docker-compose.yml**
2. 🔄 **Update development scripts**
3. 🔄 **Update application settings**

### Phase 4: Code Updates
1. 🔄 **Search and replace hardcoded ports**
2. 🔄 **Update frontend API URLs**
3. 🔄 **Update health check configurations**

### Phase 5: Validation
1. 🔄 **Test development environment**
2. 🔄 **Test production environment**
3. 🔄 **Verify all services communicate**

## 🔍 FILES REQUIRING CHANGES

### Environment Files
- `.env.development` - 6 port updates
- `.env.production` - 4 port updates
- `.env.development.example` - 6 port updates
- `.env.production.example` - 4 port updates

### Docker Configuration
- `docker-compose.yml` - Multiple port mappings

### Scripts
- `scripts/dev-start.sh` - Port references and commands
- `scripts/*tunnel*.sh` - Tunnel configurations

### Application Code
- `apps/frontend/vite.config.ts` - API URL configuration
- `apps/api/main.py` - Server port configuration
- Health check endpoints - Port references

### Documentation
- `README.md` - Port examples
- `COMPREHENSIVE_PORT_AUDIT.md` - Update with new scheme
- Various `.md` files with port references

## ⏱️ ESTIMATED IMPLEMENTATION TIME

- **Planning & Analysis**: ✅ Complete
- **Environment Updates**: ~15 minutes
- **Configuration Updates**: ~20 minutes  
- **Code Updates**: ~30 minutes
- **Testing & Validation**: ~45 minutes
- **Documentation Updates**: ~15 minutes

**Total Estimated Time: ~2 hours**

## 🎯 SUCCESS CRITERIA

1. ✅ All services start on new ports
2. ✅ Frontend communicates with API on new ports
3. ✅ Docker containers work with new port mappings
4. ✅ Development and production environments isolated
5. ✅ All documentation updated
6. ✅ No hardcoded old port references remain

---

**Ready to proceed?** This is a significant change that will require careful coordination to avoid breaking the system during the transition.