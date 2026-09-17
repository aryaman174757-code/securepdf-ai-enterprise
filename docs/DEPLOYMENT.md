# SecurePDF AI v3.0 — Enterprise Deployment Guide

## 1. Prerequisites

- Docker Engine 24.0+ & Docker Compose v2.20+
- (Optional for Bare Metal) Python 3.12, Node.js 20+, PostgreSQL 16, Redis 7, Qdrant 1.11, Tesseract OCR

---

## 2. Docker Compose Deployment (Recommended)

### Step 1: Environment Setup
Navigate to the `docker/` directory and copy the environment template:
```bash
cd docker
cp .env.example .env
```
Ensure `SECRET_KEY` is replaced with a 32+ character cryptographically secure secret.

### Step 2: Build & Start All Services
```bash
docker compose up -d --build
```

### Step 3: Verify Container Health
```bash
docker compose ps
```
The following services will be running:
- `securepdf_gateway` (Nginx Reverse Proxy on port 80)
- `securepdf_frontend` (Next.js 15 UI on port 3000)
- `securepdf_backend` (FastAPI Core on port 8000)
- `securepdf_worker` (Celery Distributed Worker)
- `securepdf_postgres` (PostgreSQL 16 on port 5432)
- `securepdf_redis` (Redis 7 Cache on port 6379)
- `securepdf_qdrant` (Qdrant Vector DB on port 6333)

---

## 3. Kubernetes Production Helm / Manifest Architecture

For Kubernetes deployments:
1. Deploy `PostgreSQL` and `Redis` StatefulSets with persistent volume claims.
2. Deploy `Qdrant` vector search cluster.
3. Deploy `Backend` Deployment with autoscaling (HPA) targeting CPU > 70%.
4. Deploy `Worker` Deployment with KEDA autoscaling based on Celery queue length.
5. Deploy `Frontend` Deployment behind an Ingress Controller with TLS termination.
