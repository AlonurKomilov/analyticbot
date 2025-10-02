# 🚀 AnalyticBot Deployment Guide

**Complete production deployment instructions for AnalyticBot.** This guide covers everything from server setup to monitoring and maintenance.

---

## 📖 **Table of Contents**

1. [Quick Deploy (15 minutes)](#-quick-deploy-15-minutes)
2. [Prerequisites](#-prerequisites)
3. [Server Setup](#-server-setup)
4. [Environment Configuration](#-environment-configuration)
5. [Docker Deployment](#-docker-deployment)
6. [Kubernetes Deployment](#-kubernetes-deployment)
7. [Security Configuration](#-security-configuration)
8. [Monitoring & Logging](#-monitoring--logging)
9. [Backup & Recovery](#-backup--recovery)
10. [Maintenance](#-maintenance)
11. [Troubleshooting](#-troubleshooting)
12. [Scaling](#-scaling)

---

## ⚡ **Quick Deploy (15 minutes)**

Get AnalyticBot running in production quickly:

```bash
# 1. Clone repository
git clone https://github.com/AlonurKomilov/analyticbot.git
cd analyticbot

# 2. Copy production environment
cp .env.production.example .env
# Edit .env with your configuration

# 3. Deploy with Docker
./infra/scripts/deploy.sh

# 4. Verify deployment
curl http://your-server:10300/health/
```

**Your AnalyticBot is now live!** 🎉

**Services running:**
- 🌐 **API**: `http://your-server:10300` 
- 📊 **Web Interface**: `http://your-server:10400`
- 🤖 **Telegram Bot**: Active and responding
- 📈 **Monitoring**: `http://your-server:9090` (Prometheus)

---

## 📋 **Prerequisites**

### **Server Requirements**

#### **Minimum Requirements**
| Resource | Specification | Purpose |
|----------|---------------|---------|
| **CPU** | 2 cores (2 GHz) | API + Bot processing |
| **RAM** | 4GB | Service containers |
| **Storage** | 50GB SSD | Database + logs |
| **Network** | 100 Mbps | API responses |
| **OS** | Ubuntu 20.04+ | Docker support |

#### **Recommended Production**
| Resource | Specification | Purpose |
|----------|---------------|---------|
| **CPU** | 4+ cores (3 GHz) | High-load processing |
| **RAM** | 8GB+ | Optimal performance |
| **Storage** | 200GB+ SSD | Growth capacity |
| **Network** | 1 Gbps | Fast responses |
| **OS** | Ubuntu 22.04 LTS | Latest features |

### **Software Requirements**

```bash
# Required packages
sudo apt update
sudo apt install -y \
    docker.io \
    docker-compose \
    git \
    curl \
    wget \
    ufw \
    fail2ban \
    nginx \
    certbot \
    python3-certbot-nginx
```

### **Domain & DNS Setup**

```bash
# Set up DNS records (A records):
api.yourdomain.com      → YOUR_SERVER_IP
web.yourdomain.com      → YOUR_SERVER_IP
bot.yourdomain.com      → YOUR_SERVER_IP
analytics.yourdomain.com → YOUR_SERVER_IP
```

### **SSL Certificate Setup**

```bash
# Install SSL certificates
sudo certbot --nginx -d api.yourdomain.com
sudo certbot --nginx -d web.yourdomain.com
sudo certbot --nginx -d analytics.yourdomain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

---

## 🖥️ **Server Setup**

### **Step 1: Initial Server Configuration**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Create deployment user
sudo useradd -m -s /bin/bash analyticbot
sudo usermod -aG sudo,docker analyticbot
sudo su - analyticbot

# Set up SSH key (recommended)
mkdir -p ~/.ssh
chmod 700 ~/.ssh
# Add your public key to ~/.ssh/authorized_keys
```

### **Step 2: Security Hardening**

```bash
# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 10300/tcp  # API port
sudo ufw allow 10400/tcp  # Web port
sudo ufw --force enable

# Configure fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### **Step 3: Docker Configuration**

```bash
# Start Docker service
sudo systemctl enable docker
sudo systemctl start docker

# Verify Docker installation
docker --version
docker-compose --version

# Test Docker (optional)
docker run hello-world
```

### **Step 4: Application Directory Setup**

```bash
# Create application directory
sudo mkdir -p /opt/analyticbot
sudo chown analyticbot:analyticbot /opt/analyticbot
cd /opt/analyticbot

# Clone repository
git clone https://github.com/AlonurKomilov/analyticbot.git .

# Set up directory structure
mkdir -p {logs,data,backups,ssl}
chmod 755 logs data backups
```

---

## ⚙️ **Environment Configuration**

### **Production Environment Variables**

Create and configure your production environment file:

```bash
# Copy template
cp .env.production.example .env

# Edit configuration
nano .env
```

#### **Critical Configuration**

```bash
# ============ ENVIRONMENT ============
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# ============ APPLICATION ============
APP_NAME=AnalyticBot
APP_VERSION=2.0.0
SECRET_KEY=your-super-secret-key-change-me

# ============ TELEGRAM BOT ============
BOT_TOKEN=1234567890:AABBCCDDEEFFGGHHIIJJKKLLMMNNOOPPQQRr
BOT_USERNAME=@your_bot_username
WEBHOOK_URL=https://api.yourdomain.com/webhook/telegram
STORAGE_CHANNEL_ID=-1001234567890

# ============ DATABASE ============
# PostgreSQL Production Configuration
DATABASE_URL=postgresql://analyticuser:secure_password_123@db:5432/analyticbot_prod
POSTGRES_DB=analyticbot_prod
POSTGRES_USER=analyticuser
POSTGRES_PASSWORD=secure_password_123
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Database Connection Pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# ============ REDIS ============
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=redis_secure_password_456

# ============ API CONFIGURATION ============
API_HOST=0.0.0.0
API_PORT=10300
API_WORKERS=4
CORS_ORIGINS=https://web.yourdomain.com,https://analytics.yourdomain.com

# ============ SECURITY ============
ALLOWED_HOSTS=api.yourdomain.com,localhost,127.0.0.1
JWT_SECRET_KEY=jwt-super-secret-key-change-me-too
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=200

# ============ MTPROTO ============
API_ID=1234567
API_HASH=abcdef1234567890abcdef1234567890
SESSION_STRING=your_session_string_here

# MTProto Rate Limiting (Production Values)
MTPROTO_REQUEST_DELAY=2
MTPROTO_BATCH_SIZE=50
MTPROTO_MAX_RETRIES=3

# ============ CELERY ============
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
CELERY_TASK_SERIALIZER=json
CELERY_ACCEPT_CONTENT=json
CELERY_RESULT_SERIALIZER=json
CELERY_TIMEZONE=UTC

# ============ MONITORING ============
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# ============ EMAIL ============
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=true

# ============ FILE STORAGE ============
UPLOAD_PATH=/app/data/uploads
MAX_FILE_SIZE=50MB
ALLOWED_FILE_TYPES=jpg,jpeg,png,gif,pdf,txt,csv

# ============ BACKUP ============
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
BACKUP_RETENTION_DAYS=30
S3_BACKUP_BUCKET=analyticbot-backups
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
```

### **Environment Validation**

```bash
# Validate configuration
python3 scripts/validate_env.py

# Test critical connections
python3 scripts/test_connections.py
```

---

## 🐳 **Docker Deployment**

### **Option A: Docker Compose (Recommended)**

#### **Production Deployment**

```bash
# Start production deployment
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d

# Monitor startup
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml logs -f
```

#### **Service Architecture**

```yaml
# Production services overview:
services:
  # Core Services
  - db          # PostgreSQL database
  - redis       # Redis cache
  - api         # FastAPI REST API
  - bot         # Telegram bot
  - frontend    # React web app
  
  # Background Processing
  - worker      # Celery workers
  - beat        # Celery scheduler
  - mtproto     # MTProto client
  
  # Monitoring
  - prometheus  # Metrics collection
  - grafana     # Monitoring dashboard
  
  # Infrastructure
  - nginx       # Reverse proxy
```

#### **Deployment Commands**

```bash
# Full deployment
./infra/scripts/deploy.sh

# Manual deployment steps
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml pull
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml build
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d

# Health checks
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml ps
curl http://localhost:10300/health/
```

### **Option B: Docker Swarm**

```bash
# Initialize Docker Swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker/docker-compose.swarm.yml analyticbot

# Monitor services
docker service ls
docker service logs analyticbot_api
```

---

## ☸️ **Kubernetes Deployment**

### **Prerequisites**

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://get.helm.sh/helm-v3.12.0-linux-amd64.tar.gz | tar xz
sudo mv linux-amd64/helm /usr/local/bin/
```

### **Kubernetes Deployment**

```bash
# Apply Kubernetes manifests
kubectl apply -f infra/k8s/

# Monitor deployment
kubectl get pods -n analyticbot
kubectl get services -n analyticbot
```

### **Helm Deployment (Recommended)**

```bash
# Install with Helm
helm install analyticbot infra/helm/ \
  --namespace analyticbot \
  --create-namespace \
  --values infra/helm/values-production.yaml

# Upgrade deployment
helm upgrade analyticbot infra/helm/ \
  --namespace analyticbot \
  --values infra/helm/values-production.yaml

# Monitor deployment
helm status analyticbot -n analyticbot
kubectl get all -n analyticbot
```

### **Ingress Configuration**

```yaml
# infra/k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: analyticbot-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    - web.yourdomain.com
    secretName: analyticbot-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: analyticbot-api
            port:
              number: 10300
  - host: web.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: analyticbot-frontend
            port:
              number: 10400
```

---

## 🔒 **Security Configuration**

### **Nginx Reverse Proxy**

```nginx
# /etc/nginx/sites-available/analyticbot
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    # Proxy to application
    location / {
        proxy_pass http://localhost:10300;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://localhost:10300/health;
    }
}
```

### **Database Security**

```bash
# PostgreSQL security configuration
sudo nano /etc/postgresql/14/main/postgresql.conf

# Key settings:
# listen_addresses = 'localhost'
# ssl = on
# shared_preload_libraries = 'pg_stat_statements'
# log_statement = 'mod'
# log_min_duration_statement = 1000

# User permissions
sudo -u postgres psql
CREATE USER analyticuser WITH ENCRYPTED PASSWORD 'secure_password_123';
CREATE DATABASE analyticbot_prod OWNER analyticuser;
GRANT ALL PRIVILEGES ON DATABASE analyticbot_prod TO analyticuser;
```

### **Redis Security**

```bash
# Redis security configuration
sudo nano /etc/redis/redis.conf

# Key settings:
# bind 127.0.0.1
# requirepass redis_secure_password_456
# rename-command FLUSHDB ""
# rename-command FLUSHALL ""
# rename-command DEBUG ""
```

---

## 📊 **Monitoring & Logging**

### **Prometheus Configuration**

```yaml
# infra/monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  
scrape_configs:
  - job_name: 'analyticbot-api'
    static_configs:
      - targets: ['localhost:10300']
    metrics_path: '/metrics'
    scrape_interval: 30s
    
  - job_name: 'analyticbot-bot'
    static_configs:
      - targets: ['localhost:10301']
    metrics_path: '/metrics'
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
    
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

### **Grafana Dashboards**

```bash
# Start monitoring stack
docker-compose -f docker/docker-compose.monitoring.yml up -d

# Access Grafana
# URL: http://your-server:3000
# Default: admin/admin123

# Import dashboards:
# - AnalyticBot API Metrics (ID: 12345)
# - PostgreSQL Dashboard (ID: 9628)
# - Redis Dashboard (ID: 763)
# - System Overview (ID: 1860)
```

### **Log Configuration**

```yaml
# docker/docker-compose.prod.yml logging configuration
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
    labels: "service,environment"
```

### **Centralized Logging**

```bash
# ELK Stack deployment
docker-compose -f docker/docker-compose.logging.yml up -d

# Log aggregation
# Elasticsearch: http://localhost:9200
# Kibana: http://localhost:5601
# Filebeat: Configured for log shipping
```

---

## 💾 **Backup & Recovery**

### **Automated Backup Script**

```bash
#!/bin/bash
# infra/scripts/backup.sh

BACKUP_DIR="/opt/analyticbot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Database backup
docker exec analyticbot-db pg_dump -U analyticuser analyticbot_prod > \
  "$BACKUP_DIR/db_backup_$DATE.sql"

# Redis backup
docker exec analyticbot-redis redis-cli --rdb /tmp/dump.rdb
docker cp analyticbot-redis:/tmp/dump.rdb "$BACKUP_DIR/redis_backup_$DATE.rdb"

# Application data backup
tar -czf "$BACKUP_DIR/data_backup_$DATE.tar.gz" \
  /opt/analyticbot/data \
  /opt/analyticbot/.env \
  /opt/analyticbot/logs

# Upload to S3 (optional)
if command -v aws &> /dev/null; then
    aws s3 sync "$BACKUP_DIR" s3://analyticbot-backups/
fi

# Cleanup old backups
find "$BACKUP_DIR" -name "*backup*" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $DATE"
```

### **Backup Automation**

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/analyticbot/infra/scripts/backup.sh

# Weekly full backup at Sunday 1 AM
0 1 * * 0 /opt/analyticbot/infra/scripts/full_backup.sh
```

### **Recovery Procedures**

```bash
# Database recovery
docker exec -i analyticbot-db psql -U analyticuser analyticbot_prod < backup.sql

# Redis recovery
docker cp redis_backup.rdb analyticbot-redis:/data/dump.rdb
docker restart analyticbot-redis

# Full system recovery
./infra/scripts/restore.sh backup_20240101_120000
```

---

## 🔧 **Maintenance**

### **Regular Maintenance Tasks**

#### **Daily Tasks**
```bash
# Health check script
./infra/scripts/health_check.sh

# Log rotation
sudo logrotate /etc/logrotate.d/analyticbot

# Disk usage check
df -h
du -sh /opt/analyticbot/logs/*
```

#### **Weekly Tasks**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean Docker images
docker system prune -f

# Optimize database
docker exec analyticbot-db psql -U analyticuser -d analyticbot_prod -c "VACUUM ANALYZE;"
```

#### **Monthly Tasks**
```bash
# Full backup verification
./infra/scripts/verify_backups.sh

# Security updates
sudo unattended-upgrades

# Certificate renewal check
sudo certbot renew
```

### **Update Procedures**

```bash
# Standard update procedure
cd /opt/analyticbot

# 1. Backup current state
./infra/scripts/backup.sh

# 2. Pull latest changes
git fetch origin
git checkout main
git pull origin main

# 3. Update dependencies
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml pull

# 4. Run database migrations
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml run --rm api alembic upgrade head

# 5. Restart services
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d

# 6. Verify deployment
curl http://localhost:10300/health/
```

### **Zero-Downtime Deployment**

```bash
# Blue-green deployment script
./infra/scripts/blue_green_deploy.sh

# Rolling update (Kubernetes)
kubectl rollout restart deployment/analyticbot-api -n analyticbot
kubectl rollout status deployment/analyticbot-api -n analyticbot
```

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Service Startup Issues**

**Problem**: Services fail to start
```bash
# Check service status
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml ps

# Check logs
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml logs api
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml logs bot

# Common solutions:
# 1. Check environment variables
# 2. Verify database connectivity
# 3. Check port conflicts
# 4. Verify file permissions
```

#### **Database Connection Issues**

**Problem**: Cannot connect to database
```bash
# Test database connection
docker exec analyticbot-db pg_isready -U analyticuser

# Check database logs
docker logs analyticbot-db

# Verify environment variables
grep DATABASE /opt/analyticbot/.env
```

#### **High Memory Usage**

**Problem**: Memory consumption too high
```bash
# Monitor container memory
docker stats

# Check for memory leaks
docker exec analyticbot-api ps aux --sort=-%mem | head -10

# Restart services if needed
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml restart api
```

#### **Performance Issues**

**Problem**: Slow API responses
```bash
# Check API logs
docker logs analyticbot-api --tail 100

# Monitor database performance
docker exec analyticbot-db psql -U analyticuser -d analyticbot_prod -c "
  SELECT query, calls, total_time, mean_time 
  FROM pg_stat_statements 
  ORDER BY total_time DESC 
  LIMIT 10;"

# Check Redis performance
docker exec analyticbot-redis redis-cli info stats
```

### **Monitoring Alerts**

```yaml
# Prometheus alerts configuration
groups:
- name: analyticbot
  rules:
  - alert: AnalyticBotAPIDown
    expr: up{job="analyticbot-api"} == 0
    for: 5m
    annotations:
      summary: "AnalyticBot API is down"
      
  - alert: HighMemoryUsage
    expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90
    for: 10m
    annotations:
      summary: "High memory usage detected"
      
  - alert: DatabaseConnectionsHigh
    expr: pg_stat_database_numbackends / pg_settings_max_connections * 100 > 80
    for: 5m
    annotations:
      summary: "Database connections are high"
```

---

## 📈 **Scaling**

### **Horizontal Scaling**

#### **Docker Swarm Scaling**
```bash
# Scale API service
docker service scale analyticbot_api=3

# Scale worker service
docker service scale analyticbot_worker=5
```

#### **Kubernetes Scaling**
```bash
# Scale deployments
kubectl scale deployment analyticbot-api --replicas=3 -n analyticbot
kubectl scale deployment analyticbot-worker --replicas=5 -n analyticbot

# Horizontal Pod Autoscaler
kubectl autoscale deployment analyticbot-api --cpu-percent=70 --min=2 --max=10 -n analyticbot
```

### **Vertical Scaling**

```yaml
# docker-compose.yml resource limits
services:
  api:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '1.0'
```

### **Database Scaling**

```yaml
# PostgreSQL read replicas
services:
  db-primary:
    image: postgres:16
    environment:
      POSTGRES_REPLICATION_MODE: master
      
  db-replica:
    image: postgres:16
    environment:
      POSTGRES_REPLICATION_MODE: slave
      POSTGRES_MASTER_SERVICE: db-primary
```

### **Load Balancing**

```nginx
# Nginx load balancer configuration
upstream analyticbot_api {
    server localhost:10300;
    server localhost:10301;
    server localhost:10302;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://analyticbot_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📋 **Production Checklist**

### **Pre-Deployment Checklist** ✅

- [ ] **Environment Configuration**
  - [ ] All environment variables set
  - [ ] Secrets properly configured
  - [ ] Database credentials secure
  - [ ] API keys validated

- [ ] **Security Setup**
  - [ ] SSL certificates installed
  - [ ] Firewall configured
  - [ ] Fail2ban active
  - [ ] Security headers set

- [ ] **Infrastructure**
  - [ ] Docker installed and running
  - [ ] Database server ready
  - [ ] Redis server ready
  - [ ] Reverse proxy configured

- [ ] **Monitoring**
  - [ ] Prometheus configured
  - [ ] Grafana dashboards imported
  - [ ] Alerts configured
  - [ ] Log aggregation setup

### **Post-Deployment Checklist** ✅

- [ ] **Health Checks**
  - [ ] API endpoints responding
  - [ ] Database connectivity verified
  - [ ] Bot responding to commands
  - [ ] All services running

- [ ] **Monitoring Verification**
  - [ ] Metrics being collected
  - [ ] Dashboards showing data
  - [ ] Alerts functioning
  - [ ] Logs being captured

- [ ] **Backup System**
  - [ ] Automated backups configured
  - [ ] Backup verification working
  - [ ] Recovery procedures tested
  - [ ] S3 upload functioning (if configured)

- [ ] **Performance**
  - [ ] Load testing completed
  - [ ] Response times acceptable
  - [ ] Resource usage optimal
  - [ ] Scaling configuration tested

---

## 🎯 **Support & Resources**

### **Documentation Links**

| Resource | Purpose | Location |
|----------|---------|----------|
| **Architecture Guide** | System design | [ARCHITECTURE.md](ARCHITECTURE.md) |
| **API Documentation** | Endpoint reference | [API_DOCUMENTATION.md](API_DOCUMENTATION.md) |
| **Developer Guide** | Development setup | [DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md) |
| **Monitoring Setup** | Observability | `infra/monitoring/` |

### **Quick Commands Reference**

```bash
# Deployment
./infra/scripts/deploy.sh                    # Full deployment
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d  # Start services

# Monitoring
curl http://localhost:10300/health/          # Health check
docker-compose logs -f api                   # View API logs
docker stats                                 # Container resource usage

# Maintenance
./infra/scripts/backup.sh                    # Manual backup
docker system prune -f                       # Clean up Docker
./infra/scripts/health_check.sh              # Full health check

# Scaling
docker service scale analyticbot_api=3       # Scale API (Swarm)
kubectl scale deployment api --replicas=3    # Scale API (K8s)
```

### **Emergency Contacts**

- **Technical Issues**: Create GitHub issue
- **Security Incidents**: security@yourdomain.com
- **Infrastructure**: DevOps team Slack
- **On-call Support**: PagerDuty rotation

---

## 🎉 **Deployment Complete!**

Your AnalyticBot is now running in production! 🚀

### **Next Steps**

1. **Monitor Performance**: Check dashboards regularly
2. **Set Up Alerts**: Configure notification channels
3. **Test Backup System**: Verify recovery procedures
4. **Plan Scaling**: Monitor resource usage trends
5. **Security Review**: Regular security audits

### **Success Metrics**

- **Uptime**: > 99.9%
- **Response Time**: < 200ms (95th percentile)
- **Error Rate**: < 0.1%
- **Resource Usage**: < 80% capacity

**Congratulations on your successful deployment!** 🎊

---

**Guide Version**: 1.0  
**Last Updated**: October 2, 2025  
**Maintained by**: DevOps Team  
**Questions?** Check documentation or create an issue