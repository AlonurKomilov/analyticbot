# 🚀 Infrastructure Deployment Guide - Phase 0.0

**Project:** AnalyticBot Enterprise Infrastructure  
**Version:** Phase 0.0 Complete  
**Last Updated:** August 22, 2025  
**Status:** Production Ready ✅

## 📋 Overview

This guide provides comprehensive instructions for deploying AnalyticBot's enterprise-grade infrastructure using the Phase 0.0 modernization stack. The infrastructure includes Kubernetes orchestration, monitoring, CI/CD pipelines, and disaster recovery capabilities.

## 🎯 Deployment Options

### 1. **Quick Start (Docker Compose)**
Best for: Development, testing, small-scale production

### 2. **Enterprise Kubernetes (Phase 0.0)**  
Best for: Production, high-availability, enterprise environments

### 3. **Cloud-Native Deployment**
Best for: Scalable cloud deployments with managed services

---

## 🚢 Option 1: Quick Start Deployment

### Prerequisites
- Docker 20.0+ and Docker Compose 2.0+
- 4GB+ RAM available
- 10GB+ disk space

### Deployment Steps

```bash
# 1. Clone and setup
git clone https://github.com/AlonurKomilov/analyticbot.git
cd analyticbot

# 2. Environment configuration
cp .env.example .env
# Edit .env with your configurations

# 3. Deploy services
docker-compose up -d

# 4. Verify deployment
docker-compose ps
docker-compose logs -f analytics-bot
```

### Services Included
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ AnalyticBot API
- ✅ Celery workers
- ✅ Basic monitoring

---

## 🏢 Option 2: Enterprise Kubernetes Deployment (Phase 0.0)

### Prerequisites

#### Software Requirements
- Kubernetes 1.24+ cluster
- Helm 3.13+ package manager
- kubectl configured for your cluster
- 8GB+ RAM per node
- 50GB+ disk space

#### Phase 0.0 Components
- ✅ Module 1: Enterprise Helm Charts
- ✅ Module 2: Testing & Deployment automation  
- ✅ Module 3: Advanced DevOps & Observability

### Step 1: Cluster Preparation

```bash
# Verify cluster access
kubectl cluster-info
kubectl get nodes

# Create namespace
kubectl create namespace analyticbot-production

# Verify Helm installation
helm version
```

### Step 2: Deploy Infrastructure Components

#### 2.1 Deploy Core Application

```bash
# Navigate to Helm charts
cd infrastructure/helm

# Install production deployment
helm install analyticbot-production . \
  -f values-production.yaml \
  -n analyticbot-production \
  --create-namespace

# Verify deployment
kubectl get pods -n analyticbot-production
kubectl get services -n analyticbot-production
```

#### 2.2 Deploy Monitoring Stack (Module 3)

```bash
# Deploy Prometheus monitoring
kubectl apply -f infrastructure/monitoring/prometheus/ -n analyticbot-production

# Deploy Grafana dashboards
kubectl apply -f infrastructure/monitoring/grafana/ -n analyticbot-production

# Verify monitoring stack
kubectl get pods -l app=prometheus -n analyticbot-production
kubectl get pods -l app=grafana -n analyticbot-production
```

#### 2.3 Configure CI/CD Pipeline

```bash
# Setup GitHub Actions secrets (in GitHub UI):
# - KUBECONFIG_DATA: Base64 encoded kubeconfig
# - DOCKER_USERNAME: Container registry username
# - DOCKER_PASSWORD: Container registry password

# Trigger deployment via Git tag
git tag -a v1.0.0 -m "Production Release v1.0.0"
git push origin v1.0.0
```

### Step 3: Initialize Backup System

```bash
# Configure backup system
chmod +x scripts/backup/backup-system.sh

# Test backup system
./scripts/backup/backup-system.sh health

# Run initial backup
./scripts/backup/backup-system.sh full
```

### Step 4: Verification & Access

```bash
# Check deployment status
kubectl get deployments -n analyticbot-production
kubectl get services -n analyticbot-production
kubectl get ingress -n analyticbot-production

# Access monitoring dashboards
kubectl port-forward svc/grafana 3000:3000 -n analyticbot-production
# Visit: http://localhost:3000

# Access application
kubectl port-forward svc/analyticbot-api 8000:8000 -n analyticbot-production
# Visit: http://localhost:8000
```

### Production Configuration

#### Environment Variables (values-production.yaml)
```yaml
env:
  ENVIRONMENT: "production"
  LOG_LEVEL: "info"
  
  # Database Configuration
  DATABASE_URL: "postgresql://user:pass@postgres-service:5432/analyticbot"
  
  # Redis Configuration  
  REDIS_URL: "redis://redis-service:6379/0"
  
  # Monitoring
  PROMETHEUS_PORT: "9090"
  GRAFANA_PORT: "3000"
  
  # Security
  JWT_SECRET: "your-production-jwt-secret"
  ENCRYPTION_KEY: "your-32-char-encryption-key"
```

#### Resource Requirements
```yaml
resources:
  api:
    requests:
      memory: "512Mi"
      cpu: "200m"
    limits:
      memory: "1Gi"
      cpu: "500m"
      
  worker:
    requests:
      memory: "256Mi" 
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "300m"
```

---

## ☁️ Option 3: Cloud-Native Deployment

### AWS EKS Deployment

```bash
# 1. Create EKS cluster
eksctl create cluster --name analyticbot-prod --region us-west-2 --nodegroup-name standard-workers --node-type m5.large --nodes 3

# 2. Configure kubectl
aws eks update-kubeconfig --region us-west-2 --name analyticbot-prod

# 3. Deploy using Helm
cd infrastructure/helm
helm install analyticbot-production . -f values-aws.yaml
```

### Google GKE Deployment

```bash
# 1. Create GKE cluster
gcloud container clusters create analyticbot-prod --zone us-central1-a --num-nodes 3 --machine-type n1-standard-2

# 2. Configure kubectl
gcloud container clusters get-credentials analyticbot-prod --zone us-central1-a

# 3. Deploy using Helm
cd infrastructure/helm
helm install analyticbot-production . -f values-gcp.yaml
```

### Azure AKS Deployment

```bash
# 1. Create AKS cluster
az aks create --resource-group analyticbot-rg --name analyticbot-prod --node-count 3 --node-vm-size Standard_D2s_v3

# 2. Configure kubectl
az aks get-credentials --resource-group analyticbot-rg --name analyticbot-prod

# 3. Deploy using Helm
cd infrastructure/helm
helm install analyticbot-production . -f values-azure.yaml
```

---

## 📊 Monitoring & Observability

### Grafana Dashboards (Module 3)

#### 1. Business Metrics Dashboard
**Access:** http://grafana-url/d/business-metrics
```
Panels Include:
- Active Users (last 24h)
- API Request Rate
- Bot Interaction Success Rate  
- Revenue Metrics
- User Engagement Trends
- Error Rate Monitoring
- Response Time Tracking
```

#### 2. Infrastructure Dashboard  
**Access:** http://grafana-url/d/infrastructure
```
Panels Include:
- CPU Usage (per service)
- Memory Utilization
- Network I/O
- Database Performance
- Redis Cache Metrics
- Container Health Status
- Storage Utilization
- Service Availability
```

#### 3. SLA/SLO Dashboard
**Access:** http://grafana-url/d/sla-slo
```
Panels Include:
- 99.9% SLA Compliance Tracking
- Service Uptime Monitoring
- P95/P99 Response Time Metrics
- Error Budget Consumption
- Availability Over Time
- SLO Violations
- Alert Status Overview
- Performance Degradation Alerts
```

### Prometheus Alerts (23 Rules)

#### Alert Categories:
1. **SLA/SLO Monitoring** - 4 rules
   - High Error Rate (>0.5% for 2min)
   - High Response Time (P95 >200ms for 3min)  
   - SLA Violation (<99.9% uptime)
   - Service Availability Issues

2. **Infrastructure Health** - 6 rules
   - High CPU Usage (>80% for 5min)
   - High Memory Usage (>85% for 5min)
   - Container Restart Alerts
   - Disk Space Issues (>85%)
   - Network Connectivity Problems
   - Pod Crash Looping

3. **Database Performance** - 4 rules
   - Connection Pool Exhaustion (>80%)
   - Slow Query Detection (P95 >100ms)
   - Database Unavailability
   - Replication Lag Issues

4. **Business Metrics** - 4 rules
   - Low User Activity Detection
   - High Bot Error Rates (>5%)
   - Subscription Churn Alerts
   - Revenue Drop Notifications

5. **Security Monitoring** - 3 rules
   - Suspicious Activity Detection
   - Rate Limiting Violations
   - Authentication Failures

6. **Performance Alerts** - 2 rules
   - Service Performance Degradation
   - Resource Optimization Alerts

---

## 🔒 Security Configuration

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: analyticbot-network-policy
spec:
  podSelector:
    matchLabels:
      app: analyticbot
  policyTypes:
  - Ingress
  - Egress
```

### TLS/SSL Configuration
```yaml
spec:
  tls:
    - hosts:
      - analyticbot.yourdomain.com
      secretName: analyticbot-tls
```

### RBAC Configuration
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: analyticbot-role
rules:
- apiGroups: [""]
  resources: ["pods", "configmaps", "secrets"]
  verbs: ["get", "list", "create", "update"]
```

---

## 💾 Backup & Disaster Recovery

### Automated Backup System (Module 3)

#### Configuration
```bash
# Configure backup credentials
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export BACKUP_S3_BUCKET="analyticbot-backups"
export GPG_PASSPHRASE="your-encryption-passphrase"
```

#### Backup Operations
```bash
# Full backup (database + configurations)
./scripts/backup/backup-system.sh full

# Database backup only
./scripts/backup/backup-system.sh database

# Configuration backup only
./scripts/backup/backup-system.sh config

# Health check
./scripts/backup/backup-system.sh health

# Restore from backup
./scripts/backup/backup-system.sh restore backup-20250822-143052.tar.gz.gpg
```

#### Backup Features
- ✅ PostgreSQL database backup with point-in-time recovery
- ✅ Kubernetes configuration backup
- ✅ Helm charts and values backup
- ✅ Encrypted backup with GPG (AES256)
- ✅ Cross-region S3 replication
- ✅ Automated retention policies (90 days)
- ✅ Integrity verification
- ✅ Health monitoring and alerting

---

## 🔄 CI/CD Pipeline (Module 2)

### GitHub Actions Workflow

The deployment pipeline includes:

#### Workflow Stages
1. **Validation Stage**
   - Helm chart linting
   - Template validation
   - Security scanning (kubesec)
   - Documentation validation

2. **Testing Stage**
   - Kind cluster creation
   - Resource validation
   - Pod readiness verification
   - Service accessibility testing

3. **Deployment Stages**
   - **Staging:** Auto-deploy on main branch
   - **Production:** Release-based deployment with approval
   - **Rollback:** Automated rollback on failure

#### Trigger Deployment
```bash
# Automated deployment on push to main (staging)
git push origin main

# Production deployment via release tag
git tag -a v1.0.1 -m "Production Release v1.0.1"
git push origin v1.0.1

# Manual workflow trigger
gh workflow run helm-deploy.yml -f environment=production
```

---

## 📈 Performance Optimization

### Resource Scaling

#### Horizontal Pod Autoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: analyticbot-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: analyticbot-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

#### Vertical Pod Autoscaler
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: analyticbot-api-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: analyticbot-api
  updatePolicy:
    updateMode: "Auto"
```

### Performance Benchmarks
- **API Response Time:** <200ms P95
- **Database Query Time:** <50ms for complex analytics
- **Memory Usage:** <512MB per pod under normal load
- **CPU Usage:** <300m per pod under normal load
- **Concurrent Users:** 1000+ supported
- **Throughput:** 10,000+ requests/minute

---

## 🔧 Troubleshooting Guide

### Common Issues

#### 1. Pod CrashLoopBackOff
```bash
# Check pod logs
kubectl logs -f deployment/analyticbot-api -n analyticbot-production

# Check pod events
kubectl describe pod <pod-name> -n analyticbot-production

# Check resource limits
kubectl top pod -n analyticbot-production
```

#### 2. Database Connection Issues
```bash
# Test database connectivity
kubectl exec -it deployment/analyticbot-api -n analyticbot-production -- psql $DATABASE_URL

# Check database pod
kubectl logs -f deployment/postgres -n analyticbot-production

# Verify service endpoints
kubectl get endpoints -n analyticbot-production
```

#### 3. Monitoring Stack Issues
```bash
# Check Prometheus targets
kubectl port-forward svc/prometheus 9090:9090 -n analyticbot-production
# Visit: http://localhost:9090/targets

# Check Grafana data sources
kubectl port-forward svc/grafana 3000:3000 -n analyticbot-production
# Visit: http://localhost:3000/datasources

# Verify alert rules
kubectl get prometheusrule -n analyticbot-production
```

#### 4. Backup System Issues
```bash
# Test backup health
./scripts/backup/backup-system.sh health

# Check backup logs
tail -f /var/log/analyticbot-backup.log

# Verify S3 connectivity
aws s3 ls s3://analyticbot-backups --region us-west-2
```

### Performance Tuning

#### Database Optimization
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM posts WHERE created_at > NOW() - INTERVAL '24 hours';
```

#### Redis Optimization
```bash
# Monitor Redis performance
kubectl exec -it deployment/redis -n analyticbot-production -- redis-cli info memory

# Check Redis slow queries
kubectl exec -it deployment/redis -n analyticbot-production -- redis-cli slowlog get 10
```

---

## ✅ Post-Deployment Checklist

### Immediate Verification (First 30 minutes)
- [ ] All pods are running and ready
- [ ] Services are accessible internally
- [ ] Database connectivity verified
- [ ] Redis cache operational
- [ ] Basic API health check passes
- [ ] Logs are being generated normally

### Day 1 Verification
- [ ] Monitoring dashboards showing data
- [ ] Alerts are configured and testable
- [ ] Backup system completes successfully
- [ ] External services (if any) are integrated
- [ ] Load testing completed
- [ ] SSL/TLS certificates valid

### Week 1 Validation
- [ ] Performance meets benchmarks
- [ ] No memory leaks observed
- [ ] Scaling policies working correctly
- [ ] Monitoring alerts are meaningful
- [ ] Backup restoration tested
- [ ] Disaster recovery procedures documented
- [ ] Security scanning completed
- [ ] User acceptance testing passed

### Production Readiness
- [ ] SLA compliance monitoring active (99.9%)
- [ ] Incident response procedures in place
- [ ] On-call rotation established
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Change management process defined

---

## 📞 Support & Resources

### Documentation
- **Helm Charts:** [infrastructure/helm/README.md](../infrastructure/helm/README.md)
- **Monitoring Setup:** [infrastructure/monitoring/README.md](../infrastructure/monitoring/README.md)
- **API Documentation:** [docs/API.md](./API.md)
- **Security Guide:** [docs/SECURITY.md](./SECURITY.md)

### Emergency Contacts
- **Infrastructure Team:** infrastructure@company.com
- **DevOps On-call:** +1-XXX-XXX-XXXX
- **Security Team:** security@company.com

### Community Resources
- **GitHub Discussions:** [Project Discussions](https://github.com/AlonurKomilov/analyticbot/discussions)
- **Issue Tracking:** [GitHub Issues](https://github.com/AlonurKomilov/analyticbot/issues)
- **Release Notes:** [Releases](https://github.com/AlonurKomilov/analyticbot/releases)

---

## 🎯 Next Steps

After successful deployment, consider:

1. **Phase 1.0+:** Advanced feature development with solid infrastructure foundation
2. **Multi-Region Setup:** Deploy across multiple geographic regions
3. **Advanced Security:** Implement additional security measures
4. **Performance Optimization:** Fine-tune based on production metrics  
5. **Disaster Recovery Testing:** Regular DR drills and procedures
6. **Cost Optimization:** Monitor and optimize cloud costs

---

*Deployment Guide - Phase 0.0 Complete*  
*Enterprise Infrastructure Ready for Production*  
*Built with ❤️ for scalable, reliable operations*
