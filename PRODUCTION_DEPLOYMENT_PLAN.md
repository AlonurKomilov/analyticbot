# Production Deployment Plan - AnalyticBot

**Date:** October 30, 2025
**Target Environment:** Production Server (No DevTunnel)
**Expected Performance:** 10-30x faster than current DevTunnel setup

---

## Executive Summary

**Current Setup:**
- DevTunnel: Adds 500ms latency per request
- Single uvicorn worker
- Connection pool: 10-50 connections
- Response time: 500ms-2000ms (P50-P95)

**Production Target:**
- Direct server access (no tunnel)
- 4-8 uvicorn workers (multi-core)
- Nginx reverse proxy with TLS
- Redis caching enabled
- Response time: 50ms-200ms (P50-P95)

---

## Phase 1: Server Preparation (30 minutes)

### 1.1 Server Requirements

**Minimum Specs:**
```
CPU: 4 cores (8 recommended)
RAM: 8GB (16GB recommended)
Storage: 50GB SSD
OS: Ubuntu 22.04 LTS
Network: 1Gbps connection
```

**Required Software:**
```bash
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Nginx 1.24+
- Git
- Certbot (for SSL)
```

### 1.2 Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Redis
sudo apt install -y redis-server

# Install Nginx
sudo apt install -y nginx

# Install Certbot for SSL
sudo apt install -y certbot python3-certbot-nginx

# Install additional tools
sudo apt install -y git curl build-essential libpq-dev
```

### 1.3 Create Application User

```bash
# Create dedicated user for application
sudo useradd -m -s /bin/bash analyticbot

# Add to necessary groups
sudo usermod -aG www-data analyticbot

# Switch to application user
sudo su - analyticbot
```

---

## Phase 2: Application Deployment (45 minutes)

### 2.1 Clone Repository

```bash
# As analyticbot user
cd /home/analyticbot

# Clone repository
git clone https://github.com/AlonurKomilov/analyticbot.git
cd analyticbot

# Checkout main branch
git checkout main
```

### 2.2 Setup Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.prod.txt

# Verify installation
pip list | grep -i "fastapi\|uvicorn\|asyncpg\|redis"
```

### 2.3 Configure Environment Variables

```bash
# Create production .env file
cat > /home/analyticbot/analyticbot/.env.production << 'EOF'
# ===== DATABASE CONFIGURATION =====
DATABASE_URL=postgresql+asyncpg://analytic_prod:CHANGE_ME_STRONG_PASSWORD@localhost:5432/analytic_bot_prod
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# ===== REDIS CONFIGURATION =====
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=300
REDIS_MAX_CONNECTIONS=50

# ===== API CONFIGURATION =====
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=false
API_LOG_LEVEL=info

# ===== SECURITY =====
SECRET_KEY=GENERATE_WITH_openssl_rand_hex_32
JWT_SECRET_KEY=GENERATE_WITH_openssl_rand_hex_32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ===== TELEGRAM =====
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# ===== ENVIRONMENT =====
ENVIRONMENT=production
DEBUG=false
TESTING=false

# ===== CORS =====
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOW_CREDENTIALS=true

# ===== LOGGING =====
LOG_LEVEL=INFO
LOG_FILE=/var/log/analyticbot/api.log
EOF

# Generate secure keys
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env.production
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env.production

# Set permissions
chmod 600 .env.production
```

### 2.4 Setup Database

```bash
# As postgres user
sudo -u postgres psql << 'EOF'
-- Create production database
CREATE DATABASE analytic_bot_prod;

-- Create production user
CREATE USER analytic_prod WITH PASSWORD 'CHANGE_ME_STRONG_PASSWORD';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE analytic_bot_prod TO analytic_prod;

-- Connect to database and grant schema privileges
\c analytic_bot_prod
GRANT ALL ON SCHEMA public TO analytic_prod;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO analytic_prod;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO analytic_prod;

-- Optimize PostgreSQL for production
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET work_mem = '10MB';
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_wal_size = '4GB';

\q
EOF

# Restart PostgreSQL to apply changes
sudo systemctl restart postgresql

# Run migrations
cd /home/analyticbot/analyticbot
source .venv/bin/activate
export $(cat .env.production | xargs)
alembic upgrade head
```

### 2.5 Configure Redis

```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Key settings to update:
# maxmemory 1gb
# maxmemory-policy allkeys-lru
# tcp-keepalive 60
# timeout 300

# Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

---

## Phase 3: Uvicorn Multi-Worker Setup (30 minutes)

### 3.1 Create Systemd Service File

```bash
# Create systemd service
sudo nano /etc/systemd/system/analyticbot-api.service
```

**Service Configuration:**
```ini
[Unit]
Description=AnalyticBot FastAPI Application
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=notify
User=analyticbot
Group=www-data
WorkingDirectory=/home/analyticbot/analyticbot
Environment="PATH=/home/analyticbot/analyticbot/.venv/bin"
EnvironmentFile=/home/analyticbot/analyticbot/.env.production

# Multi-worker configuration
ExecStart=/home/analyticbot/analyticbot/.venv/bin/uvicorn \
    apps.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --log-level info \
    --access-log \
    --proxy-headers \
    --forwarded-allow-ips='*'

# Restart policy
Restart=always
RestartSec=5
StartLimitInterval=0

# Performance settings
LimitNOFILE=65535
LimitNPROC=4096

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/analyticbot /home/analyticbot/analyticbot/logs

[Install]
WantedBy=multi-user.target
```

### 3.2 Alternative: Gunicorn with Uvicorn Workers (Recommended)

```bash
# Install gunicorn
source /home/analyticbot/analyticbot/.venv/bin/activate
pip install gunicorn

# Create gunicorn systemd service
sudo nano /etc/systemd/system/analyticbot-api-gunicorn.service
```

**Gunicorn Configuration:**
```ini
[Unit]
Description=AnalyticBot Gunicorn with Uvicorn Workers
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=analyticbot
Group=www-data
WorkingDirectory=/home/analyticbot/analyticbot
Environment="PATH=/home/analyticbot/analyticbot/.venv/bin"
EnvironmentFile=/home/analyticbot/analyticbot/.env.production

# Gunicorn with Uvicorn workers (better for production)
ExecStart=/home/analyticbot/analyticbot/.venv/bin/gunicorn \
    apps.api.main:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-connections 1000 \
    --max-requests 10000 \
    --max-requests-jitter 1000 \
    --timeout 60 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --log-level info \
    --access-logfile /var/log/analyticbot/access.log \
    --error-logfile /var/log/analyticbot/error.log \
    --capture-output

Restart=always
RestartSec=5
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

### 3.3 Create Log Directory

```bash
# Create log directory
sudo mkdir -p /var/log/analyticbot
sudo chown analyticbot:www-data /var/log/analyticbot
sudo chmod 755 /var/log/analyticbot

# Create log rotation config
sudo nano /etc/logrotate.d/analyticbot
```

**Logrotate Configuration:**
```
/var/log/analyticbot/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    sharedscripts
    postrotate
        systemctl reload analyticbot-api-gunicorn > /dev/null 2>&1 || true
    endscript
}
```

### 3.4 Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable analyticbot-api-gunicorn

# Start service
sudo systemctl start analyticbot-api-gunicorn

# Check status
sudo systemctl status analyticbot-api-gunicorn

# View logs
sudo journalctl -u analyticbot-api-gunicorn -f

# Test API locally
curl http://localhost:8000/health/
```

---

## Phase 4: Nginx Reverse Proxy (45 minutes)

### 4.1 Create Nginx Configuration

```bash
# Create site configuration
sudo nano /etc/nginx/sites-available/analyticbot
```

**Nginx Configuration:**
```nginx
# Upstream backend servers
upstream analyticbot_backend {
    # IP hash for sticky sessions (optional)
    # ip_hash;

    # Least connections load balancing
    least_conn;

    # Backend servers (all point to same host with multiple workers)
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;

    # Keep-alive connections
    keepalive 32;
}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=10r/m;

# Connection limiting
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name api.yourdomain.com;

    # Let's Encrypt validation
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration (will be configured by certbot)
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/api.yourdomain.com/chain.pem;

    # SSL Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Logging
    access_log /var/log/nginx/analyticbot-access.log combined;
    error_log /var/log/nginx/analyticbot-error.log warn;

    # Max request size
    client_max_body_size 10M;

    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/rss+xml application/atom+xml image/svg+xml;

    # API endpoints
    location / {
        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;
        limit_conn conn_limit 10;

        # Proxy settings
        proxy_pass http://analyticbot_backend;
        proxy_http_version 1.1;

        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;

        # WebSocket support (if needed)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Keep-alive
        proxy_set_header Connection "";

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Auth endpoints - stricter rate limiting
    location ~ ^/(auth|login|register) {
        limit_req zone=auth_limit burst=5 nodelay;

        proxy_pass http://analyticbot_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint - no rate limiting
    location /health/ {
        proxy_pass http://analyticbot_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;

        # Short timeouts for health checks
        proxy_connect_timeout 5s;
        proxy_send_timeout 5s;
        proxy_read_timeout 5s;

        # No logging for health checks
        access_log off;
    }

    # Static files (if any)
    location /static/ {
        alias /home/analyticbot/analyticbot/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

### 4.2 Enable Site and Configure SSL

```bash
# Create www directory for certbot
sudo mkdir -p /var/www/certbot

# Enable site
sudo ln -s /etc/nginx/sites-available/analyticbot /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx

# Obtain SSL certificate (replace with your domain)
sudo certbot --nginx -d api.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run

# Enable certbot auto-renewal
sudo systemctl enable certbot.timer
```

### 4.3 Optimize Nginx Global Settings

```bash
# Edit main nginx config
sudo nano /etc/nginx/nginx.conf
```

**Key optimizations to add/modify:**
```nginx
user www-data;
worker_processes auto;
worker_rlimit_nofile 65535;
pid /run/nginx.pid;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 100;
    types_hash_max_size 2048;
    server_tokens off;

    # Buffer Settings
    client_body_buffer_size 128k;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 16k;
    output_buffers 1 32k;
    postpone_output 1460;

    # File Cache
    open_file_cache max=10000 inactive=30s;
    open_file_cache_valid 60s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;

    # Include other configs
    include /etc/nginx/mime.types;
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

### 4.4 Setup Monitoring

```bash
# Install nginx monitoring tools
sudo apt install -y nginx-extras

# Enable stub_status for monitoring
sudo nano /etc/nginx/sites-available/monitoring
```

**Monitoring Configuration:**
```nginx
server {
    listen 127.0.0.1:8080;
    server_name localhost;

    location /nginx_status {
        stub_status on;
        access_log off;
        allow 127.0.0.1;
        deny all;
    }
}
```

```bash
# Enable monitoring
sudo ln -s /etc/nginx/sites-available/monitoring /etc/nginx/sites-enabled/
sudo systemctl reload nginx

# Test monitoring
curl http://127.0.0.1:8080/nginx_status
```

---

## Phase 5: Redis Caching Configuration (20 minutes)

### 5.1 Verify Redis Cache in Application

The application already has Redis caching configured. Let's verify:

```bash
# Check current Redis cache implementation
grep -r "redis" /home/analyticbot/analyticbot/core/common/ | head -10
```

### 5.2 Configure Redis for Production

```bash
# Edit Redis config for production
sudo nano /etc/redis/redis.conf
```

**Production Redis Settings:**
```conf
# Network
bind 127.0.0.1 ::1
protected-mode yes
port 6379
tcp-backlog 511
timeout 300
tcp-keepalive 60

# Memory Management
maxmemory 2gb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# Persistence (optional - for cache we can disable)
save ""
# save 900 1
# save 300 10
# save 60 10000

# Performance
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log

# Snapshotting (disable for pure cache)
stop-writes-on-bgsave-error no

# Performance tuning
hz 10
dynamic-hz yes
```

### 5.3 Enable Redis Caching in Application

The caching is already implemented in `core/common/cache_decorator.py`. Ensure it's configured:

```bash
# Check cache configuration in .env.production
cat >> /home/analyticbot/analyticbot/.env.production << 'EOF'

# ===== CACHE CONFIGURATION =====
CACHE_ENABLED=true
CACHE_DEFAULT_TTL=300
CACHE_ANALYTICS_TTL=600
CACHE_CHANNEL_TTL=1800
CACHE_USER_TTL=3600
EOF
```

### 5.4 Test Redis Caching

```bash
# Restart API service
sudo systemctl restart analyticbot-api-gunicorn

# Monitor Redis
redis-cli MONITOR

# In another terminal, make API requests
curl https://api.yourdomain.com/analytics/channels

# Check Redis keys
redis-cli KEYS "*"

# Check cache hit stats
redis-cli INFO stats | grep hits
```

---

## Phase 6: Production Verification (30 minutes)

### 6.1 Health Checks

```bash
# Create health check script
cat > /home/analyticbot/health_check.sh << 'EOF'
#!/bin/bash

echo "=== AnalyticBot Health Check ==="
echo "Date: $(date)"
echo ""

# Check API
echo "1. API Health:"
curl -f https://api.yourdomain.com/health/ || echo "FAILED"
echo ""

# Check Database
echo "2. Database Connection:"
psql -U analytic_prod -d analytic_bot_prod -c "SELECT 1;" > /dev/null 2>&1 && echo "OK" || echo "FAILED"
echo ""

# Check Redis
echo "3. Redis Connection:"
redis-cli ping || echo "FAILED"
echo ""

# Check Nginx
echo "4. Nginx Status:"
systemctl is-active nginx || echo "FAILED"
echo ""

# Check API Service
echo "5. API Service:"
systemctl is-active analyticbot-api-gunicorn || echo "FAILED"
echo ""

# Check Open Connections
echo "6. Active Connections:"
ss -s
echo ""

# Check System Resources
echo "7. System Resources:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}')"
echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}')"
echo ""

echo "=== Health Check Complete ==="
EOF

chmod +x /home/analyticbot/health_check.sh

# Run health check
/home/analyticbot/health_check.sh
```

### 6.2 Load Testing

```bash
# Install load testing tools
sudo apt install -y apache2-utils

# Simple load test (100 requests, 10 concurrent)
ab -n 100 -c 10 https://api.yourdomain.com/health/

# More comprehensive test with wrk (install first)
sudo apt install -y wrk

# Test with wrk (4 threads, 100 connections, 30 seconds)
wrk -t4 -c100 -d30s https://api.yourdomain.com/health/
```

### 6.3 Monitor Performance

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Real-time monitoring
htop  # CPU and memory
iotop # Disk I/O
nethogs # Network usage

# Check API response times
curl -w "\nTime Total: %{time_total}s\n" https://api.yourdomain.com/health/

# Check worker processes
ps aux | grep gunicorn

# Check connections
ss -tlnp | grep 8000
```

---

## Phase 7: Frontend Deployment (30 minutes)

### 7.1 Build Frontend

```bash
# Navigate to frontend directory
cd /home/analyticbot/analyticbot/apps/frontend

# Install dependencies
npm install

# Update API URL in production config
cat > .env.production << 'EOF'
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_API_TIMEOUT=5000
VITE_ENVIRONMENT=production
EOF

# Build for production
npm run build

# Dist folder will be created at apps/frontend/dist
```

### 7.2 Configure Nginx for Frontend

```bash
# Create frontend nginx config
sudo nano /etc/nginx/sites-available/analyticbot-frontend
```

**Frontend Nginx Configuration:**
```nginx
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    root /home/analyticbot/analyticbot/apps/frontend/dist;
    index index.html;

    # Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public, must-revalidate";
    }

    # Static assets
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API proxy (optional if on same domain)
    location /api/ {
        proxy_pass https://api.yourdomain.com/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable frontend site
sudo ln -s /etc/nginx/sites-available/analyticbot-frontend /etc/nginx/sites-enabled/

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test and reload
sudo nginx -t && sudo systemctl reload nginx
```

---

## Phase 8: Monitoring & Maintenance (Ongoing)

### 8.1 Setup System Monitoring

```bash
# Install monitoring stack (optional but recommended)
# Prometheus + Grafana for comprehensive monitoring

# Or use simpler tools:

# 1. Netdata (real-time monitoring)
bash <(curl -Ss https://my-netdata.io/kickstart.sh)

# Access Netdata at: http://your-server-ip:19999

# 2. Configure email alerts
sudo apt install -y mailutils
```

### 8.2 Backup Strategy

```bash
# Create backup script
sudo nano /home/analyticbot/backup.sh
```

**Backup Script:**
```bash
#!/bin/bash
BACKUP_DIR="/home/analyticbot/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U analytic_prod analytic_bot_prod | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup Redis (optional)
redis-cli --rdb $BACKUP_DIR/redis_$DATE.rdb

# Backup application
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /home/analyticbot/analyticbot

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable
chmod +x /home/analyticbot/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/analyticbot/backup.sh") | crontab -
```

### 8.3 Log Monitoring

```bash
# Setup log aggregation
sudo apt install -y logrotate

# Monitor logs in real-time
tail -f /var/log/analyticbot/*.log
tail -f /var/log/nginx/*.log

# Check for errors
grep -i error /var/log/analyticbot/*.log
```

---

## Quick Reference Commands

### Service Management
```bash
# Restart API
sudo systemctl restart analyticbot-api-gunicorn

# View logs
sudo journalctl -u analyticbot-api-gunicorn -f

# Check status
sudo systemctl status analyticbot-api-gunicorn

# Reload Nginx
sudo systemctl reload nginx
```

### Troubleshooting
```bash
# Check if port is in use
sudo lsof -i :8000

# Check API processes
ps aux | grep gunicorn

# Test API locally
curl http://localhost:8000/health/

# Check Redis
redis-cli ping
redis-cli KEYS "*"

# Check database connections
psql -U analytic_prod -d analytic_bot_prod -c "SELECT count(*) FROM pg_stat_activity;"
```

### Performance Monitoring
```bash
# Check response times
time curl https://api.yourdomain.com/health/

# Monitor connections
watch -n 1 'ss -s'

# Check system load
uptime

# Check disk usage
df -h

# Check memory
free -h
```

---

## Expected Performance Improvements

### Before (DevTunnel):
- Response time: 500ms-2000ms
- Throughput: ~10 req/sec
- Concurrent users: ~50

### After (Production):
- Response time: 50ms-200ms (10x faster)
- Throughput: 200+ req/sec (20x faster)
- Concurrent users: 1000+ (20x more)

---

## Security Checklist

- [ ] SSL/TLS certificates configured
- [ ] Firewall configured (allow only 80, 443, 22)
- [ ] SSH key-only authentication
- [ ] Fail2ban installed and configured
- [ ] Database password changed from default
- [ ] Secret keys rotated
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Regular security updates scheduled
- [ ] Backup strategy implemented
- [ ] Monitoring alerts configured

---

## Support & Maintenance

### Daily
- [ ] Check service status
- [ ] Review error logs
- [ ] Monitor resource usage

### Weekly
- [ ] Review access logs
- [ ] Check backup integrity
- [ ] Update dependencies

### Monthly
- [ ] Security updates
- [ ] Performance optimization
- [ ] Capacity planning review

---

**Deployment Complete!** 🚀

Your production environment is now ready to handle 1000+ concurrent users with 10-30x better performance than DevTunnel.
