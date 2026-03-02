#  Agri tech AI Platform

A **microservices-based precision agriculture platform** that helps farmers detect crop diseases, receive AI-powered treatment advice, get irrigation recommendations, and check market prices.

> **Disclaimer:** For educational use only. Contains intentional bugs for learning purposes.

##  Architecture

| Service | Port | Technology | Purpose |
|---------|------|-----------|---------|
| **Nginx** | 80 | nginx:alpine | Reverse proxy |
| **API Gateway** | 8000 | FastAPI + JWT + Redis | Auth, rate limiting, routing |
| **Disease Detection** | 8001 | FastAPI + MobileNetV2 + Kafka | Crop disease classification |
| **AI Advisory (RAG)** | 8002 | LangChain + Qdrant + Kafka | Treatment advice via RAG |
| **Irrigation** | 8003 | FastAPI + Redis | Rule-based irrigation scheduling |
| **Market Price** | 8004 | FastAPI + PostgreSQL + Redis | Mandi price data & trends |
| **Notification** | 8005 | FastAPI + Kafka | Multi-channel alerts |
| **PostgreSQL** | 5532 | postgres:16-alpine | Relational data |
| **Redis** | 6579 | redis:7-alpine | Caching & rate limiting |
| **Kafka** | 9092, 9094 | apache/kafka (KRaft) | Event streaming |
| **Qdrant** | 6433 | qdrant/qdrant | Vector embeddings |

##  Quick Start

### 1. Setup Environment
```bash
cp .env.example .env
# Edit .env with your settings (optional: add OPENAI_API_KEY for real LLM)
```

### 2. Start All Services
```bash
docker compose -f docker-compose_v2.yml up -d --build
```

### 3. Test the Platform
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Register a farmer
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Ravi Kumar", "email": "ravi@example.com", "password": "farmer123", "state": "Karnataka"}'

# Login (save the token)
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "ravi@example.com", "password": "farmer123"}' | jq -r .access_token)

# Upload crop image for disease detection
curl -X POST http://localhost:8000/api/v1/detect \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_leaf.jpg"

# Get irrigation recommendation
curl "http://localhost:8000/api/v1/irrigation?crop=rice&soil_moisture=35&temperature=32&growth_stage=vegetative" \
  -H "Authorization: Bearer $TOKEN"

# Check market prices
curl "http://localhost:8000/api/v1/market-prices?crop=rice&state=Karnataka" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. View API Documentation
- Gateway (via Nginx): http://localhost/docs — or directly http://localhost:8000/docs
- Disease Detection: http://localhost:8001/docs
- AI Advisory: http://localhost:8002/docs
- Irrigation: http://localhost:8003/docs
- Market Price: http://localhost:8004/docs
- Notification: http://localhost:8005/docs

##  Project Structure

```
AgentChiguruV2/
├── docker-compose_v2.yml       # Full stack orchestration (12 services)
├── .env.example                # Environment template
├── nginx/                      # Reverse proxy config
│   └── nginx.conf
├── shared/                     # Shared across all services
│   ├── config.py               # Pydantic settings
│   ├── database.py             # SQLAlchemy engine
│   ├── models/                 # SQLAlchemy models
│   └── schemas/events.py       # Kafka event schemas
├── migrations/                 # Alembic migrations
├── alembic.ini                 # Alembic config
├── gateway/                    # API Gateway (:8000)
├── disease_detection/          # Disease Detection (:8001)
├── ai_advisory/                # AI Advisory RAG (:8002)
├── irrigation/                 # Irrigation Engine (:8003)
├── market_price/               # Market Prices (:8004)
├── notification/               # Notifications (:8005)
└── ai_ml_models/               # MobileNetV2 disease model
```

##  Key Features

- **JWT Authentication** with bcrypt password hashing
- **Redis Rate Limiting** (sliding window, 100 req/min)
- **MobileNetV2 Disease Detection** (44 PlantVillage classes, mock fallback)
- **LangChain RAG Pipeline** (Qdrant + OpenAI/mock)
- **Rule-based Irrigation** (4 crops × 3 growth stages)
- **Kafka Event Streaming** (4 topics, async processing)
- **Redis Caching** (market prices, irrigation, sessions)

##  Configuration

Set `LLM_PROVIDER` in `.env` to control the AI Advisory:
- `mock` — Workshop mode, no API key needed 
- `openai` — Real OpenAI GPT-4o (requires `OPENAI_API_KEY`)
- `ollama` — Local Ollama models

##  8-Day Build Plan

| Day | Focus |
|-----|-------|
| 1 | System design, architecture |
| 2 | FastAPI, API Gateway |
| 3 | PostgreSQL, Farmer APIs |
| 4 | Disease Detection service |
| 5 | RAG pipeline, Vector DB |
| 6 | Irrigation, Market Price, Redis |
| 7 | Kafka, Docker Compose |
| 8 | Integration, testing, deployment |
