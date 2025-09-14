# 🚨 DOCKER API URL CONFIGURATION ISSUE

## Problem Identified
The system has mixed API URL configurations that will cause connectivity issues in Docker:

### ❌ Current Issues:
1. **docker-compose.yml**: `VITE_API_URL: http://173.212.236.167:8000` (external IP)
2. **config/settings.py**: `API_HOST_URL: http://173.212.236.167:8000` (external IP) 
3. **Health checks**: `http://localhost:8000` (container-internal)

### 🔧 Why This Is Wrong:
- **Frontend containers** cannot reach external IPs when they should communicate via Docker's internal network
- **Service discovery** should use Docker service names (`api:8000` not external IPs)
- **Mixed configurations** cause different behavior in development vs Docker

## ✅ Solution: Environment-Based Configuration

### 1. Docker Internal Communication
```yaml
# docker-compose.yml
environment:
  VITE_API_URL: ${VITE_API_URL:-http://api:8000}  # Use service name
```

### 2. External Access (Production)
```yaml
# For external access
environment:
  VITE_API_URL: ${VITE_API_URL:-http://173.212.236.167:8000}
```

### 3. Development vs Production
```bash
# .env (development)
VITE_API_URL=http://localhost:8000

# .env.production (Docker/Production)  
VITE_API_URL=http://api:8000
```

## 🔧 Recommended Fix:
1. Use Docker service names for internal communication
2. Use external IPs only for browser-based access
3. Environment-specific configuration files