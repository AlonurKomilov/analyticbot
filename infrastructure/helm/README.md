# AnalyticBot Helm Chart Installation Guide

## Prerequisites

1. **Kubernetes Cluster**: Version 1.20 or higher
2. **Helm**: Version 3.x installed
3. **kubectl**: Configured to access your cluster
4. **Storage Class**: Available for persistent storage
5. **Ingress Controller**: nginx-ingress or similar (optional)

## Quick Start

### 1. Add Required Helm Repositories

```bash
# Add Bitnami repo for PostgreSQL and Redis
helm repo add bitnami https://charts.bitnami.com/bitnami

# Update repo index
helm repo update
```

### 2. Create Namespace

```bash
kubectl create namespace analyticbot
```

### 3. Create Secrets

Create a `secrets.yaml` file with your sensitive configuration:

```yaml
# secrets.yaml
secrets:
  BOT_TOKEN: "your-telegram-bot-token"
  WEBHOOK_SECRET: "your-webhook-secret"
  POSTGRES_PASSWORD: "secure-postgres-password"
  REDIS_PASSWORD: "secure-redis-password"
  OPENAI_API_KEY: "your-openai-api-key"
  JWT_SECRET_KEY: "your-jwt-secret-key"
  ENCRYPTION_KEY: "your-encryption-key"
  SENTRY_DSN: "your-sentry-dsn"
```

### 4. Install the Chart

#### Development/Local Installation
```bash
helm install analyticbot ./infrastructure/helm \
  --namespace analyticbot \
  --values ./infrastructure/helm/values.yaml \
  --values secrets.yaml
```

#### Staging Installation
```bash
helm install analyticbot ./infrastructure/helm \
  --namespace analyticbot \
  --values ./infrastructure/helm/values-staging.yaml \
  --values secrets.yaml
```

#### Production Installation
```bash
helm install analyticbot ./infrastructure/helm \
  --namespace analyticbot \
  --values ./infrastructure/helm/values-production.yaml \
  --values secrets.yaml
```

## Configuration

### Environment-Specific Values

The chart includes three value files for different environments:

- `values.yaml`: Default/Development configuration
- `values-staging.yaml`: Staging environment optimized
- `values-production.yaml`: Production environment optimized

### Key Configuration Options

#### API Service
```yaml
api:
  replicaCount: 2
  workers: 2
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 250m
      memory: 256Mi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
```

#### Database Configuration
```yaml
postgresql:
  enabled: true  # Set to false to use external database
  auth:
    username: analyticbot
    database: analyticbot
  primary:
    persistence:
      enabled: true
      size: 10Gi
```

#### Ingress Configuration
```yaml
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: api.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: analyticbot-tls
      hosts:
        - api.yourdomain.com
```

## Monitoring Setup

### Prometheus Integration

The chart includes ServiceMonitor and PrometheusRule resources for monitoring:

```yaml
serviceMonitor:
  enabled: true
  namespace: monitoring
  interval: 30s

prometheusRule:
  enabled: true
```

### Available Metrics

- HTTP request metrics
- Database connection pool metrics
- Bot message processing metrics
- System resource metrics

## Security

### Network Policies

Network policies are included to secure pod-to-pod communication:

```yaml
networkPolicies:
  enabled: true  # Enable in production
```

### Security Context

Pods run with restricted security contexts:

```yaml
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 65534
  fsGroup: 65534

securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  capabilities:
    drop:
      - ALL
```

## Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n analyticbot
kubectl logs -n analyticbot deployment/analyticbot-api
kubectl logs -n analyticbot deployment/analyticbot-bot
```

### Check Services
```bash
kubectl get svc -n analyticbot
kubectl describe svc -n analyticbot analyticbot-api
```

### Check Ingress
```bash
kubectl get ingress -n analyticbot
kubectl describe ingress -n analyticbot analyticbot
```

### Common Issues

1. **Pod CrashLoopBackOff**
   - Check logs: `kubectl logs -n analyticbot <pod-name>`
   - Verify secrets are correctly set
   - Check database connectivity

2. **Service Not Accessible**
   - Verify ingress configuration
   - Check service selectors match pod labels
   - Ensure ingress controller is running

3. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check connection parameters in ConfigMap
   - Verify network policies allow communication

## Upgrading

### Upgrade the Chart
```bash
helm upgrade analyticbot ./infrastructure/helm \
  --namespace analyticbot \
  --values ./infrastructure/helm/values-production.yaml \
  --values secrets.yaml
```

### Rollback if Needed
```bash
helm rollback analyticbot -n analyticbot
```

## Uninstalling

```bash
helm uninstall analyticbot -n analyticbot
kubectl delete namespace analyticbot
```

## Advanced Configuration

### External Dependencies

To use external PostgreSQL and Redis:

```yaml
postgresql:
  enabled: false

redis:
  enabled: false

env:
  POSTGRES_HOST: "external-postgres.example.com"
  POSTGRES_PORT: "5432"
  POSTGRES_USER: "analyticbot"
  POSTGRES_DB: "analyticbot"
  REDIS_HOST: "external-redis.example.com"
  REDIS_PORT: "6379"

secrets:
  POSTGRES_PASSWORD: "external-postgres-password"
  REDIS_PASSWORD: "external-redis-password"
```

### Custom Images

To use custom Docker images:

```yaml
api:
  image:
    repository: your-registry.com/analyticbot/api
    tag: "v2.0.0"

bot:
  image:
    repository: your-registry.com/analyticbot/bot
    tag: "v2.0.0"
```

### Horizontal Pod Autoscaler

Configure HPA for automatic scaling:

```yaml
api:
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 20
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
```

This completes the Helm chart setup for AnalyticBot with production-ready configurations.
