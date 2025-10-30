# Multi-Tenant Bot System - Production Deployment Guide

**Version:** 1.0
**Last Updated:** 2025-10-27
**Status:** Production Ready (Backend Complete)

---

## 📋 Prerequisites

### Required Software
- **Python:** 3.10+
- **PostgreSQL:** 14+
- **Redis:** 6+ (for caching and rate limiting)
- **Docker & Docker Compose:** (recommended for deployment)
- **Git:** For version control

### System Requirements
- **CPU:** 2+ cores (4+ recommended)
- **RAM:** 4GB minimum (8GB+ recommended)
- **Disk:** 20GB+ available space
- **Network:** Stable internet connection for Telegram API

---

## 🚀 Quick Start (Development)

### 1. Clone and Setup Environment

```bash
# Clone repository
git clone <your-repo-url> analyticbot
cd analyticbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://analyticbot:password@localhost:5432/analyticbot

# Telegram
TELEGRAM_BOT_TOKEN=<your-bot-token>
TELEGRAM_API_ID=<your-api-id>
TELEGRAM_API_HASH=<your-api-hash>

# Security
BOT_ENCRYPTION_KEY=<generate-with-command-below>
SECRET_KEY=<your-secret-key-for-jwt>
JWT_SECRET_KEY=<your-jwt-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://localhost:6379/0

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### 3. Generate Encryption Key

```bash
# Generate Fernet encryption key for bot credentials
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy output to .env as BOT_ENCRYPTION_KEY
```

### 4. Setup Database

```bash
# Start PostgreSQL (if using Docker)
docker run --name analyticbot-postgres \
  -e POSTGRES_USER=analyticbot \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=analyticbot \
  -p 5432:5432 \
  -d postgres:14

# Wait for database to be ready
sleep 5

# Run migrations
psql -U analyticbot -d analyticbot -h localhost -f infra/db/migrations/001_layered_architecture.sql
psql -U analyticbot -d analyticbot -h localhost -f infra/db/migrations/002_alert_system.sql
psql -U analyticbot -d analyticbot -h localhost -f infra/db/migrations/003_user_bot_credentials.sql

# Verify tables created
psql -U analyticbot -d analyticbot -h localhost -c "\dt user_bot_credentials"
psql -U analyticbot -d analyticbot -h localhost -c "\d user_bot_credentials"
```

### 5. Create Initial Admin User

```bash
# Using Python
python3 << EOF
import asyncio
from apps.di import get_container
from core.security_engine.models import UserRole

async def create_admin():
    container = get_container()
    user_repo = await container.database.user_repo()

    # Check if admin exists
    admin = await user_repo.get_by_username("admin")
    if not admin:
        # Create admin user
        await user_repo.create({
            "username": "admin",
            "email": "admin@example.com",
            "password_hash": "<bcrypt-hashed-password>",
            "role": UserRole.ADMIN.value,
            "is_active": True
        })
        print("Admin user created!")
    else:
        print("Admin user already exists")

asyncio.run(create_admin())
EOF
```

### 6. Start Application

```bash
# Development server
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

# Production server
gunicorn apps.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### 7. Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs

# Login to get JWT token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'

# Use token for authenticated requests
TOKEN="<jwt-token-from-login>"
curl -X GET http://localhost:8000/api/user-bot/status \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🐳 Docker Deployment (Recommended)

### 1. Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    container_name: analyticbot-postgres
    environment:
      POSTGRES_USER: analyticbot
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: analyticbot
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infra/db/migrations:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U analyticbot"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - analyticbot-network

  redis:
    image: redis:7-alpine
    container_name: analyticbot-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - analyticbot-network

  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: analyticbot-app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql+asyncpg://analyticbot:${DB_PASSWORD}@postgres:5432/analyticbot
      - REDIS_URL=redis://redis:6379/0
      - BOT_ENCRYPTION_KEY=${BOT_ENCRYPTION_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - ENVIRONMENT=production
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
    networks:
      - analyticbot-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: analyticbot-nginx
    depends_on:
      - app
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - analyticbot-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  analyticbot-network:
    driver: bridge
```

### 2. Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements.prod.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.prod.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Start application
CMD ["gunicorn", "apps.api.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "/app/logs/access.log", \
     "--error-logfile", "/app/logs/error.log"]
```

### 3. Deploy with Docker

```bash
# Create .env.production file
cp .env .env.production

# Edit with production values
nano .env.production

# Build and start services
docker-compose --env-file .env.production up -d --build

# Check logs
docker-compose logs -f app

# Check service health
docker-compose ps

# Execute migrations (if not auto-applied)
docker-compose exec postgres psql -U analyticbot -d analyticbot -f /docker-entrypoint-initdb.d/003_user_bot_credentials.sql
```

---

## 🔐 Security Checklist

### Before Production Deployment

- [ ] **Change Default Credentials**
  - [ ] Update DATABASE_URL with strong password
  - [ ] Change default admin password
  - [ ] Generate unique JWT_SECRET_KEY

- [ ] **Enable HTTPS**
  - [ ] Obtain SSL certificate (Let's Encrypt recommended)
  - [ ] Configure Nginx with SSL
  - [ ] Redirect HTTP to HTTPS

- [ ] **Encryption Keys**
  - [ ] Generate unique BOT_ENCRYPTION_KEY
  - [ ] Store keys in secure vault (AWS Secrets Manager, HashiCorp Vault)
  - [ ] Never commit keys to Git

- [ ] **Database Security**
  - [ ] Enable PostgreSQL authentication
  - [ ] Use strong database passwords
  - [ ] Enable database connection encryption (SSL)
  - [ ] Backup database regularly

- [ ] **Network Security**
  - [ ] Configure firewall (allow only 80, 443, SSH)
  - [ ] Use private network for database connections
  - [ ] Enable rate limiting at Nginx level
  - [ ] Configure CORS properly

- [ ] **Application Security**
  - [ ] Set DEBUG=false in production
  - [ ] Use secure session cookies (httpOnly, secure, sameSite)
  - [ ] Implement request rate limiting
  - [ ] Enable logging and monitoring

---

## 📊 Monitoring & Logging

### Setup Prometheus Metrics

```python
# Add to apps/api/main.py
from prometheus_client import make_asgi_app, Counter, Histogram

# Metrics
bot_requests_total = Counter('bot_requests_total', 'Total bot requests', ['user_id', 'endpoint'])
bot_request_duration = Histogram('bot_request_duration_seconds', 'Bot request duration')

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

### Logging Configuration

```python
# config/logging.py
import logging
import logging.handlers
import sys

def setup_logging(log_level: str = "INFO", log_file: str = "logs/app.log"):
    """Configure structured logging"""

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10_000_000, backupCount=5
    )
    file_handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
```

---

## 🧪 Testing

### Run Unit Tests

```bash
# All tests
PYTHONPATH=/home/abcdeveloper/projects/analyticbot python3 -m pytest tests/ -v

# Repository tests
PYTHONPATH=/home/abcdeveloper/projects/analyticbot python3 tests/test_user_bot_simple.py

# With coverage
pytest tests/ --cov=core --cov=apps --cov-report=html
open htmlcov/index.html
```

### Integration Tests

```bash
# Start test database
docker run --name test-postgres \
  -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -e POSTGRES_DB=test_analyticbot \
  -p 5433:5432 -d postgres:14

# Run integration tests
DATABASE_URL=postgresql+asyncpg://test:test@localhost:5433/test_analyticbot \
  pytest tests/integration/ -v
```

---

## 🔄 Backup & Recovery

### Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U analyticbot analyticbot > backup_$(date +%Y%m%d).sql

# Automated backups (cron)
0 2 * * * docker-compose exec postgres pg_dump -U analyticbot analyticbot | gzip > /backups/analyticbot_$(date +\%Y\%m\%d).sql.gz
```

### Restore Database

```bash
# Restore from backup
docker-compose exec -T postgres psql -U analyticbot analyticbot < backup_20251027.sql

# Or with gzip
gunzip -c backup_20251027.sql.gz | docker-compose exec -T postgres psql -U analyticbot analyticbot
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Test connection
psql -U analyticbot -h localhost -d analyticbot

# Check DATABASE_URL in .env
```

**2. Bot Manager Not Starting**
```bash
# Check bot manager logs
docker-compose logs app | grep "bot_manager"

# Verify encryption key is set
docker-compose exec app env | grep BOT_ENCRYPTION_KEY

# Check user_bot_credentials table exists
docker-compose exec postgres psql -U analyticbot -d analyticbot -c "\dt user_bot_credentials"
```

**3. Authentication Errors**
```bash
# Check JWT_SECRET_KEY is set
docker-compose exec app env | grep JWT_SECRET_KEY

# Verify admin user exists
docker-compose exec postgres psql -U analyticbot -d analyticbot -c "SELECT * FROM users WHERE role='admin';"

# Test login endpoint
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'
```

**4. Rate Limiting Issues**
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# Check rate limit settings
docker-compose exec postgres psql -U analyticbot -d analyticbot -c "SELECT user_id, rate_limit_rps, max_concurrent_requests FROM user_bot_credentials;"
```

---

## 📈 Performance Tuning

### Database Optimization

```sql
-- Create additional indexes
CREATE INDEX CONCURRENTLY idx_user_bot_credentials_user_status ON user_bot_credentials(user_id, status);
CREATE INDEX CONCURRENTLY idx_admin_actions_timestamp_desc ON admin_bot_actions(timestamp DESC);

-- Analyze tables
ANALYZE user_bot_credentials;
ANALYZE admin_bot_actions;

-- Vacuum
VACUUM ANALYZE user_bot_credentials;
```

### Application Tuning

```python
# config/settings.py
class Settings:
    # Database pool
    DB_POOL_SIZE = 20
    DB_MAX_OVERFLOW = 10
    DB_POOL_TIMEOUT = 30

    # Bot manager
    MAX_BOTS_IN_MEMORY = 100
    BOT_IDLE_TIMEOUT_MINUTES = 30
    CLEANUP_INTERVAL_MINUTES = 5

    # Rate limiting
    DEFAULT_RATE_LIMIT_RPS = 30.0
    DEFAULT_MAX_CONCURRENT = 10
```

---

## 📝 Maintenance Tasks

### Weekly
- [ ] Review application logs for errors
- [ ] Check disk space and database size
- [ ] Verify backups are working
- [ ] Monitor bot usage metrics

### Monthly
- [ ] Update dependencies (`pip list --outdated`)
- [ ] Review and rotate logs
- [ ] Database maintenance (VACUUM, ANALYZE)
- [ ] Security audit (check for vulnerabilities)

### Quarterly
- [ ] Review and update SSL certificates
- [ ] Load testing and performance review
- [ ] Disaster recovery drill
- [ ] Update documentation

---

## 🚧 Roadmap & Future Enhancements

### Planned Features
- [ ] **Frontend UI** (React dashboard for bot management)
- [ ] **Webhook Support** (Handle Telegram webhooks instead of polling)
- [ ] **Multi-Language Support** (i18n for UI and error messages)
- [ ] **Advanced Analytics** (Bot usage statistics and dashboards)
- [ ] **Auto-scaling** (Kubernetes deployment with HPA)

### Nice to Have
- [ ] Bot backup/export functionality
- [ ] Template messages for common bot operations
- [ ] Scheduled bot operations
- [ ] Bot health monitoring and alerts

---

## 📞 Support & Resources

### Documentation
- **API Documentation**: http://localhost:8000/docs
- **Implementation Plan**: `IMPLEMENTATION_PLAN.md`
- **Phase 4 Details**: `PHASE_4_COMPLETE.md`
- **Status Summary**: `IMPLEMENTATION_STATUS.md`

### Getting Help
- **Issues**: Create GitHub issue with logs and error details
- **Logs Location**: `/app/logs/` (in container) or `./logs/` (host)
- **Database Logs**: `docker-compose logs postgres`
- **Application Logs**: `docker-compose logs app`

### Useful Commands

```bash
# View real-time logs
docker-compose logs -f app

# Restart application
docker-compose restart app

# Rebuild and restart
docker-compose up -d --build app

# Execute SQL query
docker-compose exec postgres psql -U analyticbot -d analyticbot -c "SELECT COUNT(*) FROM user_bot_credentials;"

# Access Python shell with app context
docker-compose exec app python3 -c "from apps.di import get_container; print(get_container())"

# Check service health
curl http://localhost:8000/health
```

---

## ✅ Production Deployment Checklist

Before going live:

- [ ] All environment variables configured in `.env.production`
- [ ] Database migration executed successfully
- [ ] Initial admin user created
- [ ] SSL certificates installed and configured
- [ ] Firewall rules configured
- [ ] Backup system tested and working
- [ ] Monitoring and logging configured
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation updated
- [ ] Team trained on deployment process
- [ ] Disaster recovery plan documented
- [ ] Health checks passing
- [ ] API documentation accessible
- [ ] Rate limiting tested

---

**Last Updated:** 2025-10-27
**Version:** 1.0
**Status:** Production Ready (Backend)
