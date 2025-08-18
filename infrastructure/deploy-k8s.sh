#!/bin/bash

# Phase 0: Infrastructure Modernization Deployment Script
# This script deploys AnalyticBot to Kubernetes cluster

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="analyticbot"
K8S_DIR="infrastructure/k8s"

echo -e "${GREEN}🚀 Phase 0: Infrastructure Modernization Deployment${NC}"
echo -e "${BLUE}=================================================${NC}"

# Function to check if kubectl is installed
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl is not installed. Please install kubectl first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ kubectl is available${NC}"
}

# Function to check if cluster is accessible
check_cluster() {
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}❌ Kubernetes cluster is not accessible. Please check your kubeconfig.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Kubernetes cluster is accessible${NC}"
}

# Function to create namespace
create_namespace() {
    echo -e "${YELLOW}📦 Creating namespace: ${NAMESPACE}${NC}"
    if kubectl get namespace $NAMESPACE &> /dev/null; then
        echo -e "${YELLOW}⚠️  Namespace $NAMESPACE already exists${NC}"
    else
        kubectl apply -f $K8S_DIR/namespace.yaml
        echo -e "${GREEN}✅ Namespace created${NC}"
    fi
}

# Function to apply configurations
apply_configurations() {
    echo -e "${YELLOW}🔧 Applying configurations and secrets...${NC}"
    
    # Apply ConfigMap
    kubectl apply -f $K8S_DIR/configmap.yaml
    echo -e "${GREEN}✅ ConfigMap applied${NC}"
    
    # Apply Secrets (user should update secrets.yaml first)
    echo -e "${YELLOW}⚠️  Please ensure you've updated secrets.yaml with actual values${NC}"
    read -p "Have you updated secrets.yaml? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl apply -f $K8S_DIR/secrets.yaml
        echo -e "${GREEN}✅ Secrets applied${NC}"
    else
        echo -e "${RED}❌ Please update secrets.yaml first, then run the script again${NC}"
        exit 1
    fi
}

# Function to deploy databases
deploy_databases() {
    echo -e "${YELLOW}💾 Deploying databases...${NC}"
    
    # Deploy PostgreSQL
    kubectl apply -f $K8S_DIR/postgres-deployment.yaml
    echo -e "${GREEN}✅ PostgreSQL deployment created${NC}"
    
    # Deploy Redis
    kubectl apply -f $K8S_DIR/redis-deployment.yaml
    echo -e "${GREEN}✅ Redis deployment created${NC}"
    
    # Wait for databases to be ready
    echo -e "${YELLOW}⏳ Waiting for databases to be ready...${NC}"
    kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s
    echo -e "${GREEN}✅ Databases are ready${NC}"
}

# Function to build and push Docker images
build_images() {
    echo -e "${YELLOW}🐳 Building Docker images...${NC}"
    
    # Build API image
    docker build -t analyticbot/api:latest -f Dockerfile .
    echo -e "${GREEN}✅ API image built${NC}"
    
    # Build Bot image (same Dockerfile, different command)
    docker build -t analyticbot/bot:latest -f Dockerfile .
    echo -e "${GREEN}✅ Bot image built${NC}"
    
    # Build Celery image (same Dockerfile, different command)
    docker build -t analyticbot/celery:latest -f Dockerfile .
    echo -e "${GREEN}✅ Celery image built${NC}"
    
    # Note: In production, you would push these to a registry
    echo -e "${YELLOW}ℹ️  Images built locally. In production, push to Docker registry.${NC}"
}

# Function to deploy applications
deploy_applications() {
    echo -e "${YELLOW}🚀 Deploying applications...${NC}"
    
    # Deploy API
    kubectl apply -f $K8S_DIR/api-deployment.yaml
    echo -e "${GREEN}✅ API deployment created${NC}"
    
    # Deploy Bot
    kubectl apply -f $K8S_DIR/bot-deployment.yaml
    echo -e "${GREEN}✅ Bot deployment created${NC}"
    
    # Deploy Celery
    kubectl apply -f $K8S_DIR/celery-deployment.yaml
    echo -e "${GREEN}✅ Celery deployments created${NC}"
    
    # Wait for applications to be ready
    echo -e "${YELLOW}⏳ Waiting for applications to be ready...${NC}"
    kubectl wait --for=condition=ready pod -l app=api -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app=bot -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app=celery-worker -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app=celery-beat -n $NAMESPACE --timeout=300s
    echo -e "${GREEN}✅ Applications are ready${NC}"
}

# Function to setup networking
setup_networking() {
    echo -e "${YELLOW}🌐 Setting up networking...${NC}"
    
    # Apply Ingress
    if kubectl get ingressclass nginx &> /dev/null; then
        kubectl apply -f $K8S_DIR/ingress.yaml
        echo -e "${GREEN}✅ Ingress applied${NC}"
    else
        echo -e "${YELLOW}⚠️  NGINX Ingress Controller not found. Install it first or use different ingress class${NC}"
    fi
}

# Function to setup autoscaling
setup_autoscaling() {
    echo -e "${YELLOW}📈 Setting up auto-scaling...${NC}"
    
    # Check if metrics server is available
    if kubectl get apiservice v1beta1.metrics.k8s.io &> /dev/null; then
        kubectl apply -f $K8S_DIR/hpa.yaml
        echo -e "${GREEN}✅ Horizontal Pod Autoscalers created${NC}"
    else
        echo -e "${YELLOW}⚠️  Metrics server not found. HPA won't work without it${NC}"
    fi
}

# Function to show deployment status
show_status() {
    echo -e "${BLUE}📊 Deployment Status${NC}"
    echo -e "${BLUE}==================${NC}"
    
    echo -e "${YELLOW}Pods:${NC}"
    kubectl get pods -n $NAMESPACE
    
    echo -e "\n${YELLOW}Services:${NC}"
    kubectl get services -n $NAMESPACE
    
    echo -e "\n${YELLOW}Ingress:${NC}"
    kubectl get ingress -n $NAMESPACE
    
    echo -e "\n${YELLOW}HPA:${NC}"
    kubectl get hpa -n $NAMESPACE
    
    echo -e "\n${YELLOW}PVC:${NC}"
    kubectl get pvc -n $NAMESPACE
}

# Function to perform health checks
health_check() {
    echo -e "${YELLOW}🔍 Performing health checks...${NC}"
    
    # Check if API is responding
    API_POD=$(kubectl get pods -n $NAMESPACE -l app=api -o jsonpath="{.items[0].metadata.name}")
    if [ ! -z "$API_POD" ]; then
        echo -e "${YELLOW}Testing API health endpoint...${NC}"
        if kubectl exec -n $NAMESPACE $API_POD -- curl -f http://localhost:8000/health &> /dev/null; then
            echo -e "${GREEN}✅ API health check passed${NC}"
        else
            echo -e "${RED}❌ API health check failed${NC}"
        fi
    fi
}

# Main execution
main() {
    echo -e "${GREEN}Starting Phase 0 deployment...${NC}"
    
    # Pre-flight checks
    check_kubectl
    check_cluster
    
    # Deploy infrastructure
    create_namespace
    apply_configurations
    deploy_databases
    
    # Build and deploy applications
    build_images
    deploy_applications
    
    # Setup additional features
    setup_networking
    setup_autoscaling
    
    # Show results
    show_status
    health_check
    
    echo -e "${GREEN}🎉 Phase 0 deployment completed!${NC}"
    echo -e "${GREEN}🎯 Your AnalyticBot is now running on Kubernetes!${NC}"
    echo -e "${BLUE}=================================================${NC}"
    
    # Next steps
    echo -e "${YELLOW}📋 Next Steps:${NC}"
    echo -e "1. Configure DNS to point to your ingress IP"
    echo -e "2. Install cert-manager for SSL certificates"
    echo -e "3. Setup monitoring (Prometheus/Grafana)"
    echo -e "4. Configure backups"
    echo -e ""
    echo -e "${YELLOW}📚 Documentation:${NC}"
    echo -e "- View logs: kubectl logs -f deployment/api -n $NAMESPACE"
    echo -e "- Scale deployment: kubectl scale deployment api --replicas=3 -n $NAMESPACE"
    echo -e "- Port forward for testing: kubectl port-forward svc/api-service 8000:80 -n $NAMESPACE"
}

# Run main function
main
