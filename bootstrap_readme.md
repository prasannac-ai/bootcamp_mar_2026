# Bootstrap Guide — Agent Chiguru AI Platform

## Prerequisites
- Docker + Docker Compose installed
- `.env` file present at project root

---

## Step 1 — Start Infrastructure

```bash
docker compose -f docker-compose_v2.yml up -d
```

Wait for all containers to be healthy:
```bash
docker compose -f docker-compose_v2.yml ps
```

Generate initial schema:
```bash
docker exec -it sf-gateway alembic revision --autogenerate -m "initial schema"
```


---

## Step 2 — Run Database Migrations

Run from inside the gateway container (no local Python needed):

```bash
docker exec -it sf-gateway alembic upgrade head
```

---

## Step 3 — Verify

```bash
# Check all services are up
docker compose -f docker-compose_v2.yml ps

# Check gateway health (all services)
curl http://localhost:8000/api/v1/health
```

---

## Alembic Commands Reference

### Apply all pending migrations
```bash
docker exec -it sf-gateway alembic upgrade head
```

### Roll back last migration
```bash
docker exec -it sf-gateway alembic downgrade -1
```

### Check current migration version
```bash
docker exec -it sf-gateway alembic current
```

### View migration history
```bash
docker exec -it sf-gateway alembic history
```

### Generate a new migration after model changes
```bash
# 1. Edit shared/models/<model>.py
# 2. Generate migration
docker exec -it sf-gateway alembic revision --autogenerate -m "describe your change"

# 3. Apply it
docker exec -it sf-gateway alembic upgrade head
```

# 4 seed data.
```bash
docker compose -f docker-compose_v2.yml exec sf-gateway python -m app.cli seed
```



---

## Teardown

```bash
# Stop all containers (keeps data volumes)
docker compose -f docker-compose_v2.yml down

# Stop and wipe all data (fresh start)
docker compose -f docker-compose_v2.yml down -v
```

> After `down -v`, run Step 2 again to re-apply migrations on the fresh database.

---

## Service Ports

| Service          | URL                          |
|------------------|------------------------------|
| Gateway (API)    | http://localhost:8000        |
| API Docs         | http://localhost:8000/docs   |
| Disease Detection| http://localhost:8001        |
| AI Advisory      | http://localhost:8002        |
| Irrigation       | http://localhost:8003        |
| Market Price     | http://localhost:8004        |
| Notification     | http://localhost:8005        |
| PostgreSQL       | localhost:5532               |
| Redis            | localhost:6579               |
| Qdrant           | http://localhost:6433        |
| Kafka            | localhost:9094 (external)    |
