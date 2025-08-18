# Phase 0: Infrastructure Modernization Implementation Guide

## 🎯 Overview
Phase 0 is the foundation for enterprise-grade scalability. We'll migrate from basic Docker Compose to a professional Kubernetes-based infrastructure with Infrastructure as Code (IaC).

## 📋 Implementation Plan

### Module 0.1: Container Orchestration (Week 1-2)
**Priority: CRITICAL**

#### Step 1: Kubernetes Migration Strategy

##### Current State Analysis:
```bash
# Current docker-compose.yml structure
services:
  - bot (Python/aiogram)
  - api (FastAPI)
  - celery (Background tasks)
  - celery-beat (Scheduler)
  - postgres (Database)
  - redis (Cache/Queue)
```

##### Target Kubernetes Architecture:
```yaml
# Kubernetes Resources to Create:
- Namespace: analyticbot
- Deployments: bot, api, celery-worker, celery-beat
- Services: api-service, postgres-service, redis-service
- ConfigMaps: app-config, celery-config
- Secrets: database-secret, bot-token-secret
- PersistentVolumes: postgres-data, redis-data
- Ingress: Load balancer + SSL termination
- HorizontalPodAutoscaler: Auto-scaling based on CPU/memory
```

#### Implementation Tasks:

##### Task 1.1: Create Kubernetes Manifests
**Timeline: 2-3 days**

1. **Namespace Configuration**
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: analyticbot
  labels:
    environment: production
    app: analyticbot
```

2. **ConfigMaps for Application Settings**
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: analyticbot
data:
  LOG_LEVEL: "INFO"
  DEBUG_MODE: "false"
  ANALYTICS_UPDATE_INTERVAL: "300"
  TELEGRAM_API_DELAY: "0.5"
```

3. **Secrets Management**
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: analyticbot
type: Opaque
stringData:
  BOT_TOKEN: "${BOT_TOKEN}"
  DATABASE_URL: "${DATABASE_URL}"
  REDIS_URL: "${REDIS_URL}"
  POSTGRES_PASSWORD: "${POSTGRES_PASSWORD}"
```

##### Task 1.2: Database Deployment
**Timeline: 1-2 days**

```yaml
# k8s/postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: analyticbot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: "analyticbot"
        - name: POSTGRES_USER
          value: "analyticbot_user"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: POSTGRES_PASSWORD
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: postgres-data
        persistentVolumeClaim:
          claimName: postgres-pvc
```

##### Task 1.3: Application Deployments
**Timeline: 2-3 days**

```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: analyticbot
spec:
  replicas: 2  # Start with 2 replicas for HA
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: analyticbot/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DATABASE_URL
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

##### Task 1.4: Horizontal Pod Autoscaler
**Timeline: 1 day**

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
  namespace: analyticbot
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Module 0.2: Infrastructure as Code (Week 2-3)
**Priority: HIGH**

#### Step 2: Terraform Infrastructure

##### Task 2.1: VPS Provisioning with Terraform
**Timeline: 2-3 days**

```hcl
# terraform/main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    contabo = {
      source  = "contabo/contabo"
      version = "~> 0.1"
    }
  }
}

# VPS Instance
resource "contabo_instance" "analyticbot" {
  display_name = "analyticbot-k8s-master"
  product_id   = "V45"  # Adjust based on your needs
  region       = "EU"
  period       = 1

  user_data = base64encode(templatefile("${path.module}/scripts/install-k8s.sh", {
    cluster_name = "analyticbot"
  }))

  tags = {
    Environment = "production"
    Project     = "analyticbot"
    ManagedBy   = "terraform"
  }
}

# Output the IP for SSH access
output "server_ip" {
  value = contabo_instance.analyticbot.ip_address
}
```

##### Task 2.2: Ansible Configuration Management
**Timeline: 2-3 days**

```yaml
# ansible/playbooks/setup-k8s.yml
---
- name: Setup Kubernetes on Contabo VPS
  hosts: all
  become: yes
  vars:
    k8s_version: "1.28"
    docker_version: "24.0"
  
  tasks:
    - name: Update system packages
      apt:
        update_cache: yes
        upgrade: dist

    - name: Install Docker
      block:
        - name: Install Docker dependencies
          apt:
            name:
              - apt-transport-https
              - ca-certificates
              - curl
              - gnupg
              - lsb-release
            state: present

        - name: Add Docker GPG key
          apt_key:
            url: https://download.docker.com/linux/ubuntu/gpg
            state: present

        - name: Add Docker repository
          apt_repository:
            repo: "deb [arch=amd64] https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable"
            state: present

        - name: Install Docker
          apt:
            name: docker-ce
            state: present

    - name: Install Kubernetes
      block:
        - name: Add Kubernetes GPG key
          apt_key:
            url: https://packages.cloud.google.com/apt/doc/apt-key.gpg
            state: present

        - name: Add Kubernetes repository
          apt_repository:
            repo: "deb https://apt.kubernetes.io/ kubernetes-xenial main"
            state: present

        - name: Install Kubernetes components
          apt:
            name:
              - kubelet={{ k8s_version }}*
              - kubeadm={{ k8s_version }}*
              - kubectl={{ k8s_version }}*
            state: present

    - name: Initialize Kubernetes cluster
      command: kubeadm init --pod-network-cidr=10.244.0.0/16
      creates: /etc/kubernetes/admin.conf

    - name: Setup kubectl for root user
      block:
        - name: Create .kube directory
          file:
            path: /root/.kube
            state: directory

        - name: Copy admin.conf
          copy:
            src: /etc/kubernetes/admin.conf
            dest: /root/.kube/config
            remote_src: yes

    - name: Install Flannel network plugin
      command: kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml
```

#### Step 3: Helm Charts for Application Management

##### Task 3.1: Create Helm Chart Structure
**Timeline: 2 days**

```bash
# Create Helm chart
helm create analyticbot

# Chart structure:
analyticbot/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── hpa.yaml
│   └── _helpers.tpl
└── charts/
```

```yaml
# helm/analyticbot/values.yaml
# Default values for analyticbot
replicaCount: 2

image:
  repository: analyticbot
  pullPolicy: IfNotPresent
  tag: "latest"

nameOverride: ""
fullnameOverride: ""

service:
  type: ClusterIP
  port: 80
  targetPort: 8000

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: api.analyticbot.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: analyticbot-tls
      hosts:
        - api.analyticbot.com

resources:
  limits:
    cpu: 500m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

# Database configuration
postgresql:
  enabled: true
  auth:
    postgresPassword: "secure_password"
    database: "analyticbot"
  primary:
    persistence:
      enabled: true
      size: 10Gi

# Redis configuration
redis:
  enabled: true
  auth:
    enabled: false
  master:
    persistence:
      enabled: true
      size: 2Gi
```

### Module 0.3: Advanced Monitoring Stack (Week 3-4)
**Priority: HIGH**

#### Step 4: ELK Stack for Logging

##### Task 4.1: Elasticsearch Deployment
**Timeline: 2 days**

```yaml
# k8s/elasticsearch.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: elasticsearch
  namespace: monitoring
spec:
  serviceName: elasticsearch
  replicas: 1
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: elasticsearch:8.8.0
        ports:
        - containerPort: 9200
        - containerPort: 9300
        env:
        - name: discovery.type
          value: single-node
        - name: ES_JAVA_OPTS
          value: "-Xms1g -Xmx1g"
        - name: xpack.security.enabled
          value: "false"
        volumeMounts:
        - name: elasticsearch-data
          mountPath: /usr/share/elasticsearch/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "1000m"
  volumeClaimTemplates:
  - metadata:
      name: elasticsearch-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi
```

##### Task 4.2: Jaeger for Distributed Tracing
**Timeline: 1-2 days**

```yaml
# k8s/jaeger.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
      - name: jaeger
        image: jaegertracing/all-in-one:1.47
        ports:
        - containerPort: 16686  # UI
        - containerPort: 14268  # HTTP collector
        - containerPort: 6831   # UDP collector
        env:
        - name: COLLECTOR_OTLP_ENABLED
          value: "true"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
```

#### Step 5: Enhanced Prometheus Configuration

##### Task 5.1: Prometheus with Custom Metrics
**Timeline: 2 days**

```yaml
# k8s/prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    rule_files:
      - "/etc/prometheus/rules/*.yml"
    
    scrape_configs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
      
      - job_name: 'analyticbot-api'
        static_configs:
          - targets: ['api-service:8000']
        metrics_path: '/metrics'
        scrape_interval: 30s
      
      - job_name: 'analyticbot-celery'
        static_configs:
          - targets: ['celery-worker:9540']
        metrics_path: '/metrics'
        scrape_interval: 30s

    alerting:
      alertmanagers:
        - static_configs:
            - targets:
              - alertmanager:9093
```

### Implementation Scripts

#### Script 1: Deployment Script
**Timeline: 1 day**

```bash
#!/bin/bash
# scripts/deploy-k8s.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Phase 0: Infrastructure Modernization${NC}"

# Step 1: Create namespace
echo -e "${YELLOW}📦 Creating namespace...${NC}"
kubectl apply -f k8s/namespace.yaml

# Step 2: Apply ConfigMaps and Secrets
echo -e "${YELLOW}🔧 Applying configurations...${NC}"
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# Step 3: Deploy databases
echo -e "${YELLOW}💾 Deploying databases...${NC}"
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml

# Wait for databases to be ready
echo -e "${YELLOW}⏳ Waiting for databases...${NC}"
kubectl wait --for=condition=ready pod -l app=postgres -n analyticbot --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n analyticbot --timeout=300s

# Step 4: Deploy applications
echo -e "${YELLOW}🚀 Deploying applications...${NC}"
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/bot-deployment.yaml
kubectl apply -f k8s/celery-deployment.yaml

# Step 5: Apply services and ingress
echo -e "${YELLOW}🌐 Setting up networking...${NC}"
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/ingress.yaml

# Step 6: Apply HPA
echo -e "${YELLOW}📈 Setting up auto-scaling...${NC}"
kubectl apply -f k8s/hpa.yaml

# Step 7: Deploy monitoring stack
echo -e "${YELLOW}📊 Setting up monitoring...${NC}"
kubectl apply -f k8s/monitoring/

echo -e "${GREEN}✅ Phase 0 deployment completed!${NC}"
echo -e "${GREEN}🎯 Your AnalyticBot is now running on Kubernetes!${NC}"

# Show status
echo -e "${YELLOW}📊 Current status:${NC}"
kubectl get pods -n analyticbot
kubectl get services -n analyticbot
kubectl get ingress -n analyticbot
```

#### Script 2: Health Check Script
**Timeline: 1 day**

```bash
#!/bin/bash
# scripts/health-check.sh

echo "🔍 Performing health checks..."

# Check namespace
if kubectl get namespace analyticbot &> /dev/null; then
    echo "✅ Namespace: analyticbot exists"
else
    echo "❌ Namespace: analyticbot missing"
    exit 1
fi

# Check pods
PODS_READY=$(kubectl get pods -n analyticbot --no-headers | awk '{print $2}' | grep -c "1/1\|2/2\|3/3")
TOTAL_PODS=$(kubectl get pods -n analyticbot --no-headers | wc -l)

if [ "$PODS_READY" -eq "$TOTAL_PODS" ]; then
    echo "✅ All pods are ready ($PODS_READY/$TOTAL_PODS)"
else
    echo "❌ Some pods are not ready ($PODS_READY/$TOTAL_PODS)"
    kubectl get pods -n analyticbot
fi

# Check services
SERVICES=$(kubectl get services -n analyticbot --no-headers | wc -l)
echo "✅ Services running: $SERVICES"

# Check ingress
if kubectl get ingress -n analyticbot &> /dev/null; then
    echo "✅ Ingress configured"
else
    echo "❌ Ingress not configured"
fi

# API health check
API_URL="http://$(kubectl get ingress -n analyticbot -o jsonpath='{.items[0].spec.rules[0].host}')/health"
if curl -f -s "$API_URL" &> /dev/null; then
    echo "✅ API health check passed"
else
    echo "❌ API health check failed"
fi

echo "🎉 Health check completed!"
```

## 🎯 Expected Outcomes

### Week 1-2: Container Orchestration
- ✅ Kubernetes cluster running on Contabo VPS
- ✅ All services deployed with HA (High Availability)
- ✅ Auto-scaling configured
- ✅ Health checks and monitoring

### Week 2-3: Infrastructure as Code
- ✅ Terraform managing VPS infrastructure
- ✅ Ansible automating server configuration
- ✅ Helm charts for easy application management
- ✅ GitOps workflow established

### Week 3-4: Advanced Monitoring
- ✅ ELK stack for centralized logging
- ✅ Jaeger for distributed tracing
- ✅ Enhanced Prometheus monitoring
- ✅ Grafana dashboards with alerts

## 📊 Success Metrics

- **Uptime**: 99.9% availability target
- **Scalability**: Auto-scale from 2 to 10 replicas
- **Performance**: <200ms API response time
- **Monitoring**: <5 second alert response time

## 💰 Cost Estimation

- **Contabo VPS**: ~$30-50/month
- **Additional monitoring**: ~$20/month
- **SSL certificates**: Free (Let's Encrypt)
- **Total**: ~$50-70/month

Bu Phase 0 ni implement qilgandan so'ng, sizning infrastructure'ingiz enterprise-ready bo'ladi va keyingi fazalar uchun mustahkam asos yaratadi! 🚀
