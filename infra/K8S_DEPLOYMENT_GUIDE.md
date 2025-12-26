# K8s/Helm Deployment Readiness Report

## 📊 Current Status

### ✅ What You Have:
- **K8s Manifests**: 13 YAML files ready
  - `api-deployment.yaml` (API service)
  - `bot-deployment.yaml` (Telegram bot)
  - `celery-deployment.yaml` (Workers)
  - `postgres-deployment.yaml` (Database)
  - `redis-deployment.yaml` (Cache)
  - `ingress.yaml` (Load balancer)
  - `secrets.yaml`, `configmap.yaml`
  - HPA (auto-scaling), monitoring

- **Helm Chart**: Complete structure
  - `Chart.yaml` (v2.1.0)
  - `values.yaml` (default config)
  - `values-production.yaml` (prod config)
  - `values-staging.yaml` (staging config)
  - Templates: 9 files
  - Dependencies: PostgreSQL, Redis

- **Dockerfile**: Multi-stage Alpine (production-ready)

### ❌ What's Missing:

#### 1. **Docker Images** (CRITICAL)
```bash
# Current: No images built
# Need: Build and push to registry

docker build -t analyticbot/api:2.1.0 .
docker build -t analyticbot/bot:2.1.0 .
```

#### 2. **Kubernetes Cluster** (CRITICAL)
Your VPS needs K8s installed. Options:
- **k3s** (recommended for single VPS) - Lightweight K8s
- **microk8s** - Canonical's K8s
- **kubeadm** - Full K8s cluster

#### 3. **Container Registry**
Need place to store Docker images:
- **Docker Hub** (free, public/private)
- **GitHub Container Registry** (GHCR)
- **Private registry** on VPS

#### 4. **kubectl & helm** (CLI Tools)
Need to install on your machine and VPS

#### 5. **Configuration Updates**
- Secrets (passwords, tokens)
- Domain names
- Resource limits (CPU/RAM)

---

## 🎯 Deployment Plan for Your VPS

### Prerequisites:
- VPS with **2+ GB RAM, 2+ CPU cores**
- Ubuntu/Debian Linux
- Root access
- Domain name (optional but recommended)

---

### Step 1: Install K3s on VPS (Easiest)

```bash
# SSH to your VPS
ssh user@your-vps-ip

# Install k3s (lightweight K8s)
curl -sfL https://get.k3s.io | sh -

# Verify installation
sudo k3s kubectl get nodes

# Get kubeconfig for remote access
sudo cat /etc/rancher/k3s/k3s.yaml
```

---

### Step 2: Install Tools on Your Machine

```bash
# Install kubectl (K8s CLI)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install helm (K8s package manager)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify
kubectl version --client
helm version
```

---

### Step 3: Setup kubeconfig (Access VPS K8s)

```bash
# Copy k3s.yaml from VPS to your machine
scp user@your-vps-ip:/etc/rancher/k3s/k3s.yaml ~/.kube/config

# Edit config: Replace 127.0.0.1 with your VPS IP
sed -i 's/127.0.0.1/YOUR_VPS_IP/g' ~/.kube/config

# Test connection
kubectl get nodes
```

---

### Step 4: Build Docker Images

```bash
cd /home/abcdev/projects/analyticbot

# Build API image
docker build -f docker/Dockerfile --target api -t analyticbot/api:2.1.0 .

# Build Bot image
docker build -f docker/Dockerfile --target bot -t analyticbot/bot:2.1.0 .

# Build Worker image
docker build -f docker/Dockerfile --target worker -t analyticbot/bot:2.1.0 .
```

---

### Step 5: Push Images to Registry

**Option A: Docker Hub (Recommended)**
```bash
# Login to Docker Hub
docker login

# Tag images with your username
docker tag analyticbot/api:2.1.0 YOUR_USERNAME/analyticbot-api:2.1.0
docker tag analyticbot/bot:2.1.0 YOUR_USERNAME/analyticbot-bot:2.1.0

# Push to Docker Hub
docker push YOUR_USERNAME/analyticbot-api:2.1.0
docker push YOUR_USERNAME/analyticbot-bot:2.1.0
```

**Option B: VPS Private Registry**
```bash
# On VPS: Run private registry
docker run -d -p 5000:5000 --restart=always --name registry registry:2

# Tag for private registry
docker tag analyticbot/api:2.1.0 your-vps-ip:5000/analyticbot-api:2.1.0

# Push to private registry
docker push your-vps-ip:5000/analyticbot-api:2.1.0
```

---

### Step 6: Update K8s Configs

**Update image references:**
```bash
# Edit infra/k8s/api-deployment.yaml
# Change:
#   image: analyticbot/api:2.1.0
# To:
#   image: YOUR_USERNAME/analyticbot-api:2.1.0

# OR for Helm values.yaml:
image:
  repository: YOUR_USERNAME/analyticbot-api
  tag: "2.1.0"
```

**Update secrets:**
```bash
# Create secrets file (NEVER commit to git!)
cat > infra/k8s/secrets-prod.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: analyticbot-secrets
  namespace: analyticbot
type: Opaque
stringData:
  POSTGRES_PASSWORD: "YOUR_SECURE_PASSWORD"
  REDIS_PASSWORD: "YOUR_REDIS_PASSWORD"
  BOT_TOKEN: "YOUR_TELEGRAM_BOT_TOKEN"
  SECRET_KEY: "YOUR_DJANGO_SECRET_KEY"
EOF
```

---

### Step 7: Deploy Using Helm (Recommended)

```bash
cd /home/abcdev/projects/analyticbot

# Create namespace
kubectl create namespace analyticbot

# Install/Update Helm dependencies (PostgreSQL, Redis)
cd infra/helm
helm dependency update

# Deploy with Helm
helm install analyticbot . \
  --namespace analyticbot \
  --values values-production.yaml \
  --set image.repository=YOUR_USERNAME/analyticbot \
  --set api.image.repository=YOUR_USERNAME/analyticbot-api \
  --set bot.image.repository=YOUR_USERNAME/analyticbot-bot

# Check deployment status
kubectl get pods -n analyticbot
kubectl get services -n analyticbot
```

---

### Step 7 Alternative: Deploy Raw K8s Manifests

```bash
# Apply all manifests
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/secrets-prod.yaml
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/postgres-deployment.yaml
kubectl apply -f infra/k8s/redis-deployment.yaml
kubectl apply -f infra/k8s/api-deployment.yaml
kubectl apply -f infra/k8s/bot-deployment.yaml
kubectl apply -f infra/k8s/ingress.yaml

# Check status
kubectl get all -n analyticbot
```

---

### Step 8: Expose Service (Access from Internet)

**Option A: NodePort (Simple)**
```yaml
# In api-deployment.yaml service section:
apiVersion: v1
kind: Service
metadata:
  name: analyticbot-api
spec:
  type: NodePort
  ports:
    - port: 8000
      targetPort: 8000
      nodePort: 30080  # Access via http://VPS_IP:30080
```

**Option B: Ingress + Domain (Production)**
```bash
# Install ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Update ingress.yaml with your domain
# Then access via http://your-domain.com
```

---

### Step 9: Verify Deployment

```bash
# Check pods running
kubectl get pods -n analyticbot

# Check logs
kubectl logs -f deployment/analyticbot-api -n analyticbot

# Test API
curl http://VPS_IP:30080/health

# Port forward for testing (local)
kubectl port-forward svc/analyticbot-api 8000:8000 -n analyticbot
curl http://localhost:8000/health
```

---

## 📋 Configuration Files That Need Updates

### 1. infra/helm/values-production.yaml
```yaml
# Update these:
image:
  repository: YOUR_DOCKERHUB_USERNAME/analyticbot
  tag: "2.1.0"

api:
  replicaCount: 2  # Adjust based on VPS resources
  resources:
    limits:
      memory: "1Gi"  # Adjust for your VPS
      cpu: "500m"
    requests:
      memory: "512Mi"
      cpu: "250m"

postgresql:
  enabled: true
  auth:
    password: "CHANGE_THIS"  # Strong password

redis:
  enabled: true
  auth:
    password: "CHANGE_THIS"
```

### 2. infra/k8s/secrets.yaml
```yaml
# Base64 encode your secrets:
echo -n 'your-password' | base64

# Update with real values
```

### 3. infra/k8s/configmap.yaml
```yaml
# Update environment-specific configs
data:
  DATABASE_URL: "postgresql://user:pass@postgres:5432/db"
  REDIS_URL: "redis://redis:6379"
```

---

## 🚀 Quick Start Script

Save this as `deploy-to-vps.sh`:

```bash
#!/bin/bash
set -e

VPS_IP="YOUR_VPS_IP"
DOCKER_USERNAME="YOUR_DOCKERHUB_USERNAME"

echo "🚀 Deploying AnalyticBot to K8s..."

# 1. Build images
echo "📦 Building Docker images..."
docker build -f docker/Dockerfile --target api -t $DOCKER_USERNAME/analyticbot-api:2.1.0 .
docker build -f docker/Dockerfile --target bot -t $DOCKER_USERNAME/analyticbot-bot:2.1.0 .

# 2. Push to registry
echo "📤 Pushing to Docker Hub..."
docker push $DOCKER_USERNAME/analyticbot-api:2.1.0
docker push $DOCKER_USERNAME/analyticbot-bot:2.1.0

# 3. Deploy with Helm
echo "☸️ Deploying to K8s..."
helm upgrade --install analyticbot infra/helm \
  --namespace analyticbot \
  --create-namespace \
  --values infra/helm/values-production.yaml \
  --set image.repository=$DOCKER_USERNAME/analyticbot \
  --set api.image.repository=$DOCKER_USERNAME/analyticbot-api \
  --set bot.image.repository=$DOCKER_USERNAME/analyticbot-bot

echo "✅ Deployment complete!"
echo "Check status: kubectl get pods -n analyticbot"
```

---

## ⚠️ Current Issues to Fix

### 1. Dockerfile Targets
Your Dockerfile has multi-stage but needs target names:
```dockerfile
# Add these stages:
FROM python-deps AS api
# ... API specific code

FROM python-deps AS bot
# ... Bot specific code

FROM python-deps AS worker
# ... Worker specific code
```

### 2. Image Names Mismatch
K8s configs reference `analyticbot/api` but you need your registry:
- Update all `image:` fields to your Docker Hub username

### 3. Secrets Management
Currently secrets.yaml has placeholders - need real values

### 4. Resource Limits
Default configs assume lots of RAM - adjust for your VPS size

---

## 📝 Checklist Before Deploy

- [ ] VPS has 2+ GB RAM, 2+ CPU
- [ ] K3s installed on VPS
- [ ] kubectl installed locally
- [ ] helm installed locally
- [ ] Docker Hub account created
- [ ] Images built and pushed
- [ ] K8s configs updated with your registry
- [ ] Secrets updated with real passwords
- [ ] Resource limits adjusted for VPS
- [ ] Domain name configured (optional)
- [ ] Ingress controller installed (if using domain)

---

## 🎯 Recommended Approach

**EASIEST:** Use Helm + k3s + Docker Hub

1. Install k3s on VPS (5 minutes)
2. Build & push images to Docker Hub (15 minutes)
3. Update Helm values (5 minutes)
4. Deploy with `helm install` (2 minutes)
5. Total: ~30 minutes to production!

**Want me to help you through the actual deployment?** Let me know:
1. Your VPS specs (RAM, CPU)
2. Do you have Docker Hub account?
3. Do you have a domain name?
