# Task Manager Cloud Application

## 1. Software Description

Task Manager is a small multi-user web application. A user registers or logs in, receives a JWT, and can create, list, update, and delete private tasks. The React frontend is served by Nginx. Authentication and user accounts are owned by `user-service`; task ownership and CRUD operations are owned by `task-service`; PostgreSQL persists both services' data.

The application is intentionally small for a course demonstration. The cloud value is demonstrated through independent deployment, health checks, horizontal scaling, service discovery, external access, and persistent storage. A realistic production version could add team sharing, notifications, audit history, and a larger workload that justifies autoscaling.

## 2. Architecture

```text
Browser
	|
	v
Nginx Ingress -> frontend Service -> frontend Pods (React + Nginx, 2+ replicas)
												  |
												  +-- /api/users -> user-service Service -> user-service Pods (2+)
												  |
												  +-- /api/tasks -> task-service Service -> task-service Pods (2+)
																										|
																										v
																	  postgres Service -> PostgreSQL (1 replica)
																										|
																										v
																							  PersistentVolumeClaim
```

### Component mapping

| Component | Responsibility | Kubernetes resource |
|---|---|---|
| React/Nginx frontend | Browser UI and API reverse proxy | `frontend` Deployment and Service |
| User service | Registration, password hashing, login, JWT creation | `user-service` Deployment and Service |
| Task service | Authenticated task CRUD and ownership checks | `task-service` Deployment and Service |
| PostgreSQL | Durable relational storage | `postgres` Deployment, Service, and PVC |
| Ingress | External HTTP entry point | `k8s/ingress.yaml` |

Both APIs are REST APIs. The frontend uses Axios to call them programmatically. Services communicate through Kubernetes DNS names, and the browser only needs access to the frontend/Ingress.

## 3. Architecture Discussion

### Benefits

- User and task functionality can be deployed and scaled independently.
- Kubernetes Services provide stable discovery while Pods are replaced or scaled.
- Stateless API replicas can be load-balanced horizontally.
- PostgreSQL uses a persistent volume, so data survives Pod and deployment restarts.
- Health probes allow Kubernetes to remove unhealthy API replicas from service traffic.
- An Ingress provides one external browser entry point instead of exposing every internal service.

### Challenges and mitigations

- **Database bottleneck:** PostgreSQL is intentionally single-instance for this assignment. Production could use a managed PostgreSQL service, replicas, backups, and failover.
- **Shared database ownership:** Both small services use one database for simplicity. A larger system should use separate schemas/databases or a dedicated data ownership strategy.
- **JWT secret management:** The example Secret is for demonstration only. Replace it before deployment and use a cloud secret manager or sealed/external secrets in production.
- **Credential security:** Passwords are hashed with Werkzeug, never stored as plaintext. Production should also add rate limiting, TLS, refresh-token rotation, and account lockout controls.
- **CORS and ingress security:** The APIs are intended to be reached through the frontend proxy. Production should restrict CORS, enable HTTPS, add network policies, and avoid exposing internal Services as LoadBalancers.
- **Schema management:** The current prototype uses idempotent `create_all()` during container startup. A production system should replace this with versioned Alembic/Flask-Migrate migrations.
- **Small workload:** The sample app does not naturally need five replicas. HPA configuration demonstrates the cloud pattern; load testing can be used to simulate enough traffic to trigger it.

## 4. Run Locally with Docker Compose

Requirements: Docker and Docker Compose.

```bash
docker compose up --build
```

Open <http://localhost:8080>. The local PostgreSQL data is stored in the `postgres-data` named volume.

## 5. Build and Push Images

Replace `YOUR_DOCKERHUB_USERNAME` with the Docker Hub account used for the submission.

```bash
docker login
docker build -t YOUR_DOCKERHUB_USERNAME/task-manager-user-service:1.0.0 ./user-service
docker build -t YOUR_DOCKERHUB_USERNAME/task-manager-task-service:1.0.0 ./task-service
docker build -t YOUR_DOCKERHUB_USERNAME/task-manager-frontend:1.0.0 ./frontend
docker push YOUR_DOCKERHUB_USERNAME/task-manager-user-service:1.0.0
docker push YOUR_DOCKERHUB_USERNAME/task-manager-task-service:1.0.0
docker push YOUR_DOCKERHUB_USERNAME/task-manager-frontend:1.0.0
```

Update the three image names in the Kubernetes Deployment manifests if necessary.

## 6. Deploy to Kubernetes

The cluster needs an Ingress controller and Metrics Server for the Ingress and HPA resources.

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml -f k8s/secrets.yaml
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/user-service/ -f k8s/task-service/ -f k8s/frontend/
kubectl apply -f k8s/ingress.yaml
kubectl -n task-manager get pods,svc,ingress,hpa
```

Replace the demonstration values in `k8s/secrets.yaml` before using a shared or public cluster. Access the application through the address reported by the Ingress controller, or use a local port-forward:

```bash
kubectl -n task-manager port-forward service/frontend 8080:80
```

## 7. Suggested Video Walkthrough

1. Introduce the task manager and show the architecture diagram.
2. Show the repository structure and the three Docker images.
3. Apply the Kubernetes YAML and show `kubectl get pods,svc,ingress,hpa`.
4. Open the frontend in a browser, register a user, log in, and create/delete tasks.
5. Explain that the browser sends a JWT and the task service derives ownership from it.
6. Show `kubectl logs` for the user and task services and briefly explain the Deployment, Service, HPA, Ingress, Secret, and PVC files.
7. Optionally scale the task service with `kubectl scale deployment/task-service --replicas=3` and show the new Pods.
