# Task Manager Cloud Application

## 1. Software Description

Task Manager is a small multi-user web application designed to demonstrate how a cloud-native microservice architecture can be built, deployed, and managed with Kubernetes. The system allows a user to register, log in, and create, view, update, and delete their own tasks.

The application is implemented as a web frontend and two backend microservices:

- `frontend`: a React application served through Nginx, used by the browser to interact with the system.
- `user-service`: exposes user authentication and account-related APIs; it handles registration, login, JWT issuance, and ownership checks.
- `task-service`: exposes task-related APIs; it provides task CRUD operations and enforces that each user can only access their own tasks.
- `postgres`: a PostgreSQL database running as a separate service, storing relational data for both backend services.

The application is intentionally small and simple because it is built as a teaching project. The small size is acknowledged explicitly: it does not naturally require production-scale load, but it demonstrates the patterns and structure needed to scale a cloud application in a realistic way.

The assignment requires the app to behave like a real distributed system, even though the workload is intentionally modest. To make the architecture meaningful, the project is designed to pretend the system is larger than it is by separating concerns, isolating state, and applying autoscaling and deployment patterns that would be used in a real cloud system.

## 2. Architecture Design

### High-level architecture

```text
Browser
  |
  v
Ingress / port-forward -> frontend Service -> frontend Pods (React + Nginx)
                             |
                             +--> user-service API via frontend requests
                             |
                             +--> task-service API via frontend requests
                                         |
                                         v
                                postgres Service -> PostgreSQL
                                         |
                                         v
                               PersistentVolumeClaim (data storage)
```

### Component responsibilities

| Component | Responsibility | Implementation |
|---|---|---|
| Frontend | Provides the user interface and calls backend APIs | React app in `frontend/` |
| User service | Register/login, password hashing, JWT generation, user lookup | `user-service` Flask app |
| Task service | Create/read/update/delete tasks, user ownership enforcement | `task-service` Flask app |
| PostgreSQL | Stores application data persistently | `k8s/postgres/` |
| Ingress | Provides external access point into the cluster | `k8s/ingress.yaml` |
| Kubernetes Services | Stable internal network routing to Pods | `k8s/*/service.yaml` |
| HPA | Scales stateless services independently | `k8s/*/hpa.yaml` |
| Secret and ConfigMap | Externalises configuration and sensitive data | `k8s/secrets.yaml`, `k8s/configmap.yaml` |

### Mapping between software components and microservices

| Software component | Microservice / service |
|---|---|
| User account logic | `user-service` |
| Task logic | `task-service` |
| User interface | `frontend` |
| Persistent data store | `postgres` |
| Connection and routing | Kubernetes Service + Ingress |

### Architecture principles used

This system uses several standard cloud architecture patterns:

- Service decomposition: each domain is separate (`user-service`, `task-service`, `frontend`, `database`).
- Independent deployment: each microservice has its own Deployment and Service resource.
- Horizontal scaling: each stateless service has its own HorizontalPodAutoscaler.
- Service discovery: backend services communicate via Kubernetes DNS names and Service endpoints.
- External access: Ingress provides a single external entry point for browser traffic.
- Persistence: PostgreSQL data is kept in a PVC so it survives Pod and deployment restarts.
- Health checks: readiness and liveness probes are configured so Kubernetes can handle unhealthy Pods.
- Configuration externalisation: environment variables come from ConfigMap and Secret objects.

## 3. Benefits and Challenges of the Architecture

### Benefits

- Independent development and deployment for each service.
- Horizontal scaling can be applied to each microservice separately.
- A failure in one service does not necessarily require the whole application to stop.
- Services can be replaced or updated with minimal impact on the rest of the system.
- Persistent database storage preserves state across restarts.
- Kubernetes Service discovery simplifies inter-service communication.
- The architecture demonstrates how cloud deployment patterns work in practice.

### Challenges and mitigations

- **Database bottleneck:** PostgreSQL is intentionally a single instance for this assignment. This is acceptable because the application is small, but in production it would be replaced with a managed database or replicated database solution. Backups, read replicas, and failover would be added in a larger deployment.
- **Shared database ownership:** The two backend services use the same PostgreSQL database for simplicity. In a production-ready system, separate schemas or separate databases would help enforce ownership boundaries and reduce coupling.
- **Security of secrets:** Demo values are stored in `k8s/secrets.yaml` for demonstration. In production, they should be replaced with cloud secret management solutions, such as Kubernetes Secrets managed via a secure external secret manager.
- **Credential security:** Passwords are hashed with Werkzeug before being stored. This avoids plaintext storage.
- **Ingress and CORS security:** The frontend is intended to interact with the backend through the frontend proxy. In production, TLS, HTTPS, restricted CORS rules, and network policies should be added.
- **Schema management:** The project uses database creation at startup (`db.create_all()`). In a production system, this should be migrated to versioned database migrations, such as Alembic.
- **Small workload:** The app is intentionally small enough to be manageable for a course assignment. To make the system look realistic for a business case, you would need to pretend the workload is larger and that future load demands autoscaling and more robust infrastructure.

### Security discussion

Security is an important concern in this design. The application uses JWT tokens for authentication and authorization, and the JWT secret is supplied through a Kubernetes Secret instead of being hardcoded in source code. Passwords are hashed with Werkzeug before they are stored in the database, so plaintext passwords are not kept in persistent storage.

However, several security improvements are still needed for production deployment:

- TLS/HTTPS at the Ingress layer
- rotation of secrets and stronger secret storage
- tighter CORS rules and network policies
- rate limiting and account lockout logic
- secure handling of database credentials
- production-grade monitoring and logging

## 4. Configuration Management and Source Code Repository

The application source code and the Kubernetes deployment configuration are stored in this repository. The repository includes:

- application code for the backend services and frontend
- Docker build configuration files
- Kubernetes YAML files in `k8s/`
- documentation in this README

Repository link:

- Add your GitHub/GitLab repository URL here before submission.

This repository is the configuration management repository for both the application and its Kubernetes deployment specification.

## 5. Run Locally with Docker Compose

Requirements: Docker and Docker Compose.

```bash
docker compose up --build
```

Then open:

```text
http://localhost:8080
```

The PostgreSQL data is stored in a named Docker volume for local development.

## 6. Build and Push Docker Images

Before deploying to Kubernetes, the required images must be built and pushed to Docker Hub.

```bash
docker login
docker build -t YOUR_DOCKERHUB_USERNAME/task-manager-user-service:1.0.0 ./user-service
docker build -t YOUR_DOCKERHUB_USERNAME/task-manager-task-service:1.0.0 ./task-service
docker build -t YOUR_DOCKERHUB_USERNAME/task-manager-frontend:1.0.0 ./frontend
docker push YOUR_DOCKERHUB_USERNAME/task-manager-user-service:1.0.0
docker push YOUR_DOCKERHUB_USERNAME/task-manager-task-service:1.0.0
docker push YOUR_DOCKERHUB_USERNAME/task-manager-frontend:1.0.0
```

Then update the image names in the Kubernetes Deployment files if your Docker Hub username differs.

## 7. Deploy to Kubernetes

A Kubernetes cluster is required. This project has been tested with a local `kind` cluster.

### Local kind example

```bash
kind create cluster --name task-manager
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml -f k8s/secrets.yaml
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/user-service/ -f k8s/task-service/ -f k8s/frontend/
kubectl apply -f k8s/ingress.yaml
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl -n kube-system patch deployment metrics-server --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
```

Check the deployment:

```bash
kubectl -n task-manager get pods,svc,ingress,hpa
```

Access the application through the frontend service or by port-forwarding:

```bash
kubectl -n task-manager port-forward service/frontend 8081:80
```

Then open:

```text
http://localhost:8081
```

## 8. Kubernetes Deployment Notes

The project satisfies the required requirements for a Kubernetes-deployed microservice application:

- deployable with Kubernetes
- at least two microservices plus a database
- REST APIs on each microservice
- external access via browser
- independent horizontal scaling per stateless service
- persistent database storage across restarts
- Docker Hub image references for deployment

The database is intentionally not horizontally scaled, because the assignment explicitly allows the database to remain single-instance.

## 9. Video Walkthrough

Thia assignment requried a short 5-10 minute demonstration video should be recorded and submitted. The video should show:

1. A short introduction to the app and architecture.
2. The separate microservices and what each one does.
3. The project running in Kubernetes.
4. Frontend access via browser.
5. Example API interaction and log output.
6. A brief walk-through of the Kubernetes YAML files.

Video link:

- Add your video upload link or YouTube link here before submission.

## 10. Business and Course Relevance

This project demonstrates the business value of cloud deployment patterns:

- faster scaling of user-facing services
- decoupling of components to reduce operational risk
- persistent storage for critical business data
- improved reliability through health checks and service discovery
- ability to deploy the same application in a way that is portable between environments

This is relevant to both the course themes of Cloud Provisioning and Deployment and the Business Case for Cloud Computing, because it shows how small, modular services can be deployed, scaled, and managed more efficiently than a monolithic application.

## 11. Summary

This project is a simple but realistic example of a cloud-native microservice application. Although it is intentionally small, it demonstrates the key design patterns needed for a larger business application and it is structured so that questions about architecture, deployment, scale, and security can be answered confidently.
