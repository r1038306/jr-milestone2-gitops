#!/bin/bash

set -e

echo "========================================="
echo "JR Milestone 2 - Kubernetes Deployment"
echo "========================================="
echo ""

echo "Checking prerequisites..."
if ! command -v kind &> /dev/null; then
    echo "❌ kind not found"
    exit 1
fi
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found"
    exit 1
fi
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found"
    exit 1
fi
echo "✓ All prerequisites met"
echo ""

echo "Building Docker images..."
cd ..
docker build -t jr-frontend:latest ./frontend
docker build -t jr-api:latest ./api
echo "✓ Images built"
echo ""

cd k8s
echo "Creating kind cluster..."
if kind get clusters | grep -q "jr-milestone2"; then
    echo "⚠️  Cluster exists. Deleting..."
    kind delete cluster --name jr-milestone2
fi

kind create cluster --config kind-config.yaml
echo "✓ Cluster created"
echo ""

echo "Loading images into kind cluster..."
kind load docker-image jr-frontend:latest --name jr-milestone2
kind load docker-image jr-api:latest --name jr-milestone2
echo "✓ Images loaded"
echo ""

echo "Deploying applications..."
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f database-init-configmap.yaml
kubectl apply -f database-pv-pvc.yaml
kubectl apply -f database-deployment.yaml

echo "  → Waiting for database..."
kubectl wait --namespace jr-namespace --for=condition=ready pod --selector=tier=database --timeout=120s

kubectl apply -f api-deployment.yaml
echo "  → Waiting for API..."
kubectl wait --namespace jr-namespace --for=condition=ready pod --selector=tier=api --timeout=120s

kubectl apply -f frontend-deployment.yaml
echo "  → Waiting for frontend..."
kubectl wait --namespace jr-namespace --for=condition=ready pod --selector=tier=frontend --timeout=120s

echo ""
echo "========================================="
echo "Deployment Complete! ✓"
echo "========================================="
echo ""
kubectl get all -n jr-namespace
echo ""
echo "Frontend: http://localhost:30080"
