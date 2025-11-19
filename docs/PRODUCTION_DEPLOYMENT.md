# Production Deployment Guide

## Prerequisites

- Ubuntu/Debian server (20.04 LTS or newer)
- Python 3.10+
- PostgreSQL 14+
- Redis 6+
- Nginx (for reverse proxy)
- 2+ CPU cores, 4GB+ RAM

## Installation Steps

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    git \
    build-essential \
    libpq-dev

# Create application user
sudo useradd -m -s /bin/bash analyticbot
sudo usermod -aG sudo analyticbot
```

### 2. Application Deployment

```bash
# Switch to app user
sudo su - analyticbot

# Clone repository
cd /opt
sudo mkdir analyticbot
sudo chown analyticbot:analyticbot analyticbot
git clone https://github.com/yourusername/analyticbot.git analyticbot
cd analyticbot

# Create virtual environment
python3.10 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.prod.txt

# Create necessary directories
mkdir -p logs data
chmod 755 logs data
```

### 3. Configuration

```bash
# Copy production environment file
cp .env.production.example .env.production

# Edit configuration
nano .env.production
```

**Required settings in `.env.production`:**
```bash
# Database
DATABASE_URL=postgresql://analyticbot:STRONG_PASSWORD@localhost:5432/analyticbot

# Redis
REDIS_URL=redis://localhost:6379/0

# Bot
BOT_TOKEN=your_telegram_bot_token_here

# Security
SECRET_KEY=generate_with_openssl_rand_hex_32
ENCRYPTION_KEY=generate_with_fernet_key

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# MTProto
MTPROTO_ENABLED=true
MTPROTO_API_ID=your_api_id
MTPROTO_API_HASH=your_api_hash
```

### 4. Database Setup

```bash
# Create database user
sudo -u postgres psql -c "CREATE USER analyticbot WITH PASSWORD 'STRONG_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE analyticbot OWNER analyticbot;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE analyticbot TO analyticbot;"

# Run migrations
cd /opt/analyticbot
source .venv/bin/activate
alembic upgrade head
```

### 5. Systemd Service Installation

```bash
# Copy service files
sudo cp infra/systemd/*.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable analyticbot-api
sudo systemctl enable analyticbot-bot
sudo systemctl enable analyticbot-mtproto-worker

# Start services
sudo systemctl start analyticbot-api
sudo systemctl start analyticbot-bot
sudo systemctl start analyticbot-mtproto-worker

# Check status
sudo systemctl status analyticbot-*
```

### 6. Nginx Configuration

```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/analyticbot
```

**Nginx configuration:**
```nginx
upstream analyticbot_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 10M;

    # API
    location /api/ {
        proxy_pass http://analyticbot_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health checks
    location /health {
        proxy_pass http://analyticbot_api/health;
        access_log off;
    }

    # Frontend (if serving from same server)
    location / {
        root /opt/analyticbot/apps/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/analyticbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL/TLS Setup (Certbot)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
sudo systemctl status certbot.timer
```

## Monitoring Setup

### 1. Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/analyticbot
```

```
/opt/analyticbot/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0644 analyticbot analyticbot
    sharedscripts
    postrotate
        systemctl reload analyticbot-* > /dev/null 2>&1 || true
    endscript
}
```

### 2. Prometheus Node Exporter

```bash
# Install node exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
sudo mv node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
sudo useradd -rs /bin/false node_exporter

# Create systemd service
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
```

### 3. Health Check Monitoring

```bash
# Create health check script
sudo tee /usr/local/bin/check_analyticbot_health.sh > /dev/null <<'EOF'
#!/bin/bash
set -e

# Check API
curl -f http://localhost:8000/health || exit 1

# Check MTProto worker health
curl -f http://localhost:9091/health || exit 1

echo "All services healthy"
EOF

sudo chmod +x /usr/local/bin/check_analyticbot_health.sh

# Add to crontab for monitoring
sudo crontab -e
# Add: */5 * * * * /usr/local/bin/check_analyticbot_health.sh || mail -s "AnalyticBot Health Check Failed" admin@example.com
```

## Maintenance

### Daily Operations

```bash
# Check service status
sudo systemctl status analyticbot-*

# View logs
sudo journalctl -u analyticbot-mtproto-worker -f
sudo journalctl -u analyticbot-api --since "1 hour ago"

# Check resource usage
htop
free -h
df -h
```

### Updates

```bash
# Pull latest code
cd /opt/analyticbot
git pull origin main

# Activate venv
source .venv/bin/activate

# Update dependencies
pip install -r requirements.prod.txt

# Run migrations
alembic upgrade head

# Restart services
sudo systemctl restart analyticbot-*

# Verify
sudo systemctl status analyticbot-*
curl http://localhost:8000/health
```

### Backups

```bash
# Database backup
sudo -u postgres pg_dump analyticbot > /backup/analyticbot_$(date +%Y%m%d_%H%M%S).sql

# Automated backups (crontab)
0 2 * * * /usr/local/bin/backup_analyticbot.sh
```

**Backup script** (`/usr/local/bin/backup_analyticbot.sh`):
```bash
#!/bin/bash
BACKUP_DIR="/backup/analyticbot"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database
sudo -u postgres pg_dump analyticbot | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Configuration
cp /opt/analyticbot/.env.production $BACKUP_DIR/env_$DATE

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "env_*" -mtime +7 -delete
```

### Disaster Recovery

```bash
# Restore database
gunzip < /backup/analyticbot/db_20251119_020000.sql.gz | sudo -u postgres psql analyticbot

# Restore configuration
cp /backup/analyticbot/env_20251119_020000 /opt/analyticbot/.env.production

# Restart services
sudo systemctl restart analyticbot-*
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u analyticbot-mtproto-worker -n 50
sudo journalctl -u analyticbot-api -n 50

# Check configuration
cd /opt/analyticbot
source .venv/bin/activate
python -m apps.mtproto.worker --status

# Check permissions
ls -la /opt/analyticbot
sudo chown -R analyticbot:analyticbot /opt/analyticbot
```

### High Memory Usage

```bash
# Check process stats
ps aux | grep python | head -10

# Check worker health
curl http://localhost:9091/metrics | jq '.metrics'

# Restart workers
sudo systemctl restart analyticbot-mtproto-worker
```

### Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname='analyticbot';"

# Reset connections
sudo systemctl restart analyticbot-*
```

## Security Hardening

### 1. Firewall Setup

```bash
# Install ufw
sudo apt install -y ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Block direct access to API
# (only allow through nginx)

# Enable firewall
sudo ufw enable
sudo ufw status
```

### 2. Fail2Ban

```bash
# Install fail2ban
sudo apt install -y fail2ban

# Create custom jail
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-limit-req]
enabled = true
```

```bash
sudo systemctl restart fail2ban
```

### 3. PostgreSQL Security

```bash
# Edit pg_hba.conf
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

Only allow local connections:
```
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
```

### 4. Redis Security

```bash
# Edit redis config
sudo nano /etc/redis/redis.conf
```

```
# Bind to localhost only
bind 127.0.0.1

# Require password
requirepass STRONG_REDIS_PASSWORD

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

```bash
sudo systemctl restart redis
```

## Performance Optimization

### 1. Database Tuning

```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/14/main/postgresql.conf
```

For 4GB RAM server:
```
shared_buffers = 1GB
effective_cache_size = 3GB
maintenance_work_mem = 256MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10485kB
min_wal_size = 1GB
max_wal_size = 4GB
```

### 2. Connection Pooling

Already configured in application settings. Verify:
```python
# config/settings.py
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10
```

### 3. Caching

Ensure Redis is properly configured for caching. Application uses Redis for:
- Session management
- Rate limiting
- Celery task queue

## Monitoring Checklist

Daily:
- [ ] Check service status
- [ ] Review error logs
- [ ] Monitor disk space
- [ ] Check backup completion

Weekly:
- [ ] Review performance metrics
- [ ] Check for security updates
- [ ] Analyze slow queries
- [ ] Review user activity

Monthly:
- [ ] Update dependencies
- [ ] Review resource utilization
- [ ] Plan capacity upgrades
- [ ] Audit security settings

## Support

For issues:
1. Check logs: `sudo journalctl -u analyticbot-*`
2. Review documentation: `/opt/analyticbot/docs/`
3. Check health endpoints
4. Contact support team
