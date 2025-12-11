# Delete old cluster
kind delete cluster --name jr-milestone2

# Create new cluster with monitoring ports
kind create cluster --config kind-config.yaml

# Load images
kind load docker-image jr-frontend:latest --name jr-milestone2
kind load docker-image jr-api:latest --name jr-milestone2

# Deploy monitoring stack
kubectl apply -f prometheus-stack.yaml

# Wait for monitoring to be ready
kubectl wait --namespace monitoring --for=condition=ready pod --all --timeout=120s

# Deploy application
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f database-init-configmap.yaml
kubectl apply -f database-pv-pvc.yaml
kubectl apply -f database-deployment.yaml
kubectl wait --namespace jr-namespace --for=condition=ready pod --selector=tier=database --timeout=120s

kubectl apply -f api-deployment.yaml
kubectl apply -f api-service-nodeport.yaml
kubectl wait --namespace jr-namespace --for=condition=ready pod --selector=tier=api --timeout=120s

kubectl apply -f frontend-deployment.yaml
kubectl wait --namespace jr-namespace --for=condition=ready pod --selector=tier=frontend --timeout=120s

# Deploy certificates and ingress
kubectl apply -f certificate-issuer.yaml
kubectl apply -f ingress-https.yaml

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host "Prometheus: http://localhost:30090" -ForegroundColor Yellow
Write-Host "Grafana: http://localhost:30030 (admin/admin)" -ForegroundColor Yellow