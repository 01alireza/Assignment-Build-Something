.PHONY: help build up down k8s-apply k8s-status k8s-forward k8s-stop k8s-down kind-create metrics-install docker-push k8s-logs

help:
	@echo "Available targets:"
	@echo "  make build"
	@echo "  make up"
	@echo "  make down"
	@echo "  make kind-create"
	@echo "  make metrics-install"
	@echo "  make k8s-apply"
	@echo "  make k8s-status"
	@echo "  make k8s-forward"
	@echo "  make k8s-logs"
	@echo "  make k8s-stop"
	@echo "  make k8s-down"

build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

kind-create:
	kind create cluster --name task-manager || true

metrics-install:
	kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
	kubectl -n kube-system patch deployment metrics-server --type=json -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

k8s-apply:
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/configmap.yaml -f k8s/secrets.yaml
	kubectl apply -f k8s/postgres/
	kubectl apply -f k8s/user-service/ -f k8s/task-service/ -f k8s/frontend/
	kubectl apply -f k8s/ingress.yaml

k8s-status:
	kubectl -n task-manager get pods,svc,hpa,ingress

k8s-forward:
	kubectl -n task-manager port-forward service/frontend 8081:80

k8s-logs:
	kubectl -n task-manager logs -l app=user-service --tail=50
	kubectl -n task-manager logs -l app=task-service --tail=50

k8s-stop:
	kubectl -n task-manager scale deployment --all --replicas=0

k8s-down:
	kubectl delete namespace task-manager --ignore-not-found

docker-push:
	docker login
	docker push 01alireza/task-manager-user-service:1.0.0
	docker push 01alireza/task-manager-task-service:1.0.0
	docker push 01alireza/task-manager-frontend:1.0.0
