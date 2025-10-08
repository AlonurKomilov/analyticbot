# 🚀 AnalyticBot Development Workflow

## Overview

This project uses a **hybrid development approach** to optimize developer productivity:

- **Development (Fast)**: Virtual environment with hot reload (~1-2 second startup)
- **Production (Robust)**: Docker containers with full isolation

## Quick Start

### Development Environment (Recommended)

```bash
# Start development services
make dev-start

# Your services will be available at:
# • API: http://localhost:8001
# • Frontend: http://localhost:5174
# • Database: localhost:5432 (Docker)
# • Redis: localhost:6379 (Docker)
```

### Production Environment

```bash
# Start Docker services
make up

# Services available at:
# • API: http://localhost:8000
# • Frontend: http://localhost:3000
```

## Development Workflow

1. **Start Development**: `make dev-start`
2. **Code Changes**: Edit files (auto-reload enabled)
3. **Run Tests**: `make dev-test`
4. **Sync to Docker**: `make sync` (when ready)
5. **Deploy**: `make up`

## Commands Reference

### 🔥 Development (Fast)
- `make dev-start` - Start development servers
- `make dev-stop` - Stop development services
- `make dev-status` - Check service status
- `make dev-logs` - View development logs
- `make dev-test` - Run tests in venv
- `make dev-install` - Install dependencies

### 🐳 Production (Docker)
- `make up` - Start Docker services
- `make down` - Stop Docker services
- `make logs` - Follow Docker logs
- `make ps` - List Docker services
- `make migrate` - Run database migrations

### 🔄 Sync & Quality
- `make sync` - Sync dev changes to Docker
- `make lint` - Run code linting
- `make typecheck` - Run type checking
- `make test` - Run unit tests
- `make test-all` - Run all tests

## Performance Comparison

| Environment | Startup Time | Rebuild Time | Hot Reload |
|-------------|--------------|--------------|------------|
| Development (venv) | 1-2 seconds | N/A | ✅ Instant |
| Docker | 30-45 seconds | 3-8 minutes | ❌ Full rebuild |

## Port Configuration

### Development Ports (8001-8010)
- API: 8001
- Frontend: 5174
- Database: 5432 (Docker)
- Redis: 6379 (Docker)

### Production Ports (8000, 3000)
- API: 8000
- Frontend: 3000
- Database: 5432
- Redis: 6379

## Environment Files

- `.env.production` - Production configuration (10xxx ports, Docker internal)
- `.env.development` - Development configuration (11xxx ports, external Docker access)
- `.env.production.example` - Production template with CHANGE_ME placeholders
- `.env.development.example` - Development template with CHANGE_ME placeholders

## Database & Redis

Both development and production use Docker containers for:
- **PostgreSQL**: Consistent database engine
- **Redis**: Session storage and caching

This ensures data consistency while keeping development fast.

## Troubleshooting

### Port Conflicts
```bash
# Check what's using a port
netstat -tlnp | grep :8001

# Kill process on port
kill -9 $(lsof -t -i:8001)
```

### Service Status
```bash
# Check development status
make dev-status

# Check Docker status
make ps
```

### Logs
```bash
# Development logs
make dev-logs

# Docker logs
make logs
```

## IDE Setup

### VS Code
- Install Python extension
- Set Python interpreter to `.venv/bin/python`
- Enable auto-reload in launch.json

### PyCharm
- Configure Python interpreter: `.venv/bin/python`
- Enable auto-reload in run configurations

## Best Practices

1. **Use development environment** for coding and testing
2. **Sync to Docker** before major commits
3. **Run full test suite** before deployment
4. **Keep environment files in sync** when adding new variables
5. **Use production Docker** for integration testing

## Migration from Docker-only

If you were previously using Docker for development:

1. Stop Docker services: `make down`
2. Install development environment: `make dev-install`
3. Start development: `make dev-start`
4. Enjoy faster development! 🚀

## Architecture Benefits

- **Fast Development**: No container overhead, instant reloads
- **Production Parity**: Same database, Redis, and environment variables
- **Flexible Testing**: Test in venv for speed, Docker for integration
- **Easy Deployment**: Docker for production, proven and reliable
