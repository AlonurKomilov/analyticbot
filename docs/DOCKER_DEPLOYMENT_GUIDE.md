# AnalyticBot Docker Deployment Guide

This guide explains how to run the complete AnalyticBot application stack using Docker, including the newly added frontend.

## Quick Start

```bash
# Start all production services (recommended)
./scripts/docker-manager.sh prod

# Or start development environment
./scripts/docker-manager.sh dev
```

## Available Services

The Docker setup includes the following services:

### Core Services
- **db** (PostgreSQL 16): Database server on port 5432
- **redis** (Redis 7): Cache and message broker on port 6379
- **api** (FastAPI): Backend API on port 8000
- **bot** (Telegram Bot): Telegram bot service
- **frontend** (React + Nginx): Production frontend on port 3000

### Development Services
- **frontend-dev** (Vite): Development frontend with hot reload on port 5173

### Optional Services (--profile full)
- **worker** (Celery): Background task worker
- **beat** (Celery): Task scheduler
- **mtproto** (MTProto): Telegram MTProto service

## Service Access Points

### Production Mode
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432
- **Redis**: localhost:6379

### Development Mode
- **Frontend**: http://localhost:5173 (with hot reload)
- **API**: http://localhost:8000
- **Database**: localhost:5432
- **Redis**: localhost:6379

## Docker Manager Script

The `./scripts/docker-manager.sh` script provides easy management of the Docker environment:

### Basic Commands
```bash
# Start services
./scripts/docker-manager.sh start                # All production services
./scripts/docker-manager.sh start frontend       # Specific service

# Stop services
./scripts/docker-manager.sh stop                 # All services
./scripts/docker-manager.sh stop frontend        # Specific service

# View logs
./scripts/docker-manager.sh logs                 # All services
./scripts/docker-manager.sh logs api             # Specific service

# Check status
./scripts/docker-manager.sh status
```

### Environment Commands
```bash
# Development environment (with hot reload)
./scripts/docker-manager.sh dev

# Production environment
./scripts/docker-manager.sh prod

# Full environment (including workers)
./scripts/docker-manager.sh full
```

### Utility Commands
```bash
# Build services
./scripts/docker-manager.sh build
./scripts/docker-manager.sh build frontend

# Health check
./scripts/docker-manager.sh health

# Open shell in container
./scripts/docker-manager.sh shell frontend

# Clean up everything
./scripts/docker-manager.sh clean
```

## Frontend Helper Script

The `./scripts/frontend-helper.sh` script provides frontend-specific commands:

```bash
# Development
./scripts/frontend-helper.sh setup               # Install dependencies
./scripts/frontend-helper.sh dev                 # Start dev server
./scripts/frontend-helper.sh build               # Build for production

# Testing
./scripts/frontend-helper.sh test                # Run tests
./scripts/frontend-helper.sh test-a11y           # Accessibility tests
./scripts/frontend-helper.sh lint                # Code linting

# Docker operations
./scripts/frontend-helper.sh docker-dev          # Start in Docker dev mode
./scripts/frontend-helper.sh docker-prod         # Start in Docker prod mode
```

## Environment Configuration

### Environment Files
- `.env.docker`: Docker-specific environment variables
- `apps/frontend/.env`: Frontend environment variables
- `config/settings.py`: Backend configuration

### Key Environment Variables
```bash
# Database
POSTGRES_DB=analyticbot
POSTGRES_USER=analyticbot
POSTGRES_PASSWORD=your_password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# API
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://localhost:8000

# Frontend
VITE_API_BASE_URL=http://localhost:8000
VITE_ENVIRONMENT=production
```

## Development Workflow

### 1. First Time Setup
```bash
# Clone and setup
git clone <repository>
cd analyticbot

# Start development environment
./scripts/docker-manager.sh dev

# Install frontend dependencies (if developing locally)
./scripts/frontend-helper.sh setup
```

### 2. Daily Development
```bash
# Start dev environment
./scripts/docker-manager.sh dev

# View logs
./scripts/docker-manager.sh logs

# Make changes to code...

# Restart specific service if needed
./scripts/docker-manager.sh restart api
```

### 3. Testing Changes
```bash
# Run frontend tests
./scripts/frontend-helper.sh test

# Run accessibility tests
./scripts/frontend-helper.sh test-a11y

# Build and test production
./scripts/frontend-helper.sh build
./scripts/docker-manager.sh build frontend
./scripts/docker-manager.sh prod
```

## Production Deployment

### 1. Build Images
```bash
./scripts/docker-manager.sh build
```

### 2. Start Production
```bash
./scripts/docker-manager.sh prod
```

### 3. Health Check
```bash
./scripts/docker-manager.sh health
```

## Troubleshooting

### Common Issues

#### Port Conflicts
If ports are already in use:
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000

# Stop conflicting services
./scripts/docker-manager.sh stop
```

#### Permission Issues
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Fix Docker permissions (if needed)
sudo usermod -aG docker $USER
newgrp docker
```

#### Database Issues
```bash
# Reset database
./scripts/docker-manager.sh stop db
docker volume rm analyticbot_postgres_data
./scripts/docker-manager.sh start db
```

#### Frontend Build Issues
```bash
# Clean and rebuild
./scripts/frontend-helper.sh clean
./scripts/docker-manager.sh build frontend --no-cache
```

### Viewing Logs
```bash
# All services
./scripts/docker-manager.sh logs

# Specific service
./scripts/docker-manager.sh logs frontend
./scripts/docker-manager.sh logs api

# Follow logs in real-time
docker-compose logs -f frontend
```

### Performance Monitoring
```bash
# Container stats
docker stats

# Service status
./scripts/docker-manager.sh status

# Health check
./scripts/docker-manager.sh health
```

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │      API        │    │   Database      │
│   (React)       │────│   (FastAPI)     │────│  (PostgreSQL)   │
│   Port 3000     │    │   Port 8000     │    │   Port 5432     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │     Redis       │              │
         └──────────────│  (Cache/Queue)  │──────────────┘
                        │   Port 6379     │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │  Telegram Bot   │
                        │   (Worker)      │
                        └─────────────────┘
```

## Security Considerations

- All services run in isolated Docker containers
- Frontend uses Nginx with security headers
- Database and Redis are not exposed externally in production
- Environment variables are used for sensitive configuration
- HTTPS should be configured via reverse proxy in production

## Next Steps

1. **Production HTTPS**: Configure SSL/TLS certificates
2. **Monitoring**: Add application monitoring (Prometheus, Grafana)
3. **Backup**: Implement database backup strategy
4. **CI/CD**: Set up automated deployment pipeline
5. **Scaling**: Configure horizontal scaling for API and workers
