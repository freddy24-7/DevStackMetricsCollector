# DevStack Metrics Collector

A real-time server monitoring dashboard built as a technical demonstration of three Python web frameworks operating in concert over a shared data layer.

**Live demo:** https://metrics-nginx-freddy.fly.dev

---

## What it does

DevStack Metrics lets you monitor CPU, RAM, and disk usage from any server in real time. You run a lightweight Python agent on your server — it sends metrics every 5 seconds. A live dashboard updates instantly via WebSockets as data arrives.

**User flow:**
1. Sign up at the dashboard URL
2. Generate an API key and register a node in the Manage tab
3. Run the monitoring agent on your server (one command)
4. Watch your metrics update live in the dashboard

---

## Architecture

The project is a three-service Python monorepo. Each service uses a different framework, chosen deliberately to demonstrate distinct Python paradigms working together:

| Service | Framework | Paradigm | Responsibility |
|---|---|---|---|
| Gateway | FastAPI | Async ASGI | WebSocket connections, real-time broadcasting, dashboard UI |
| Admin | Django | Sync MVC | User auth, API key management, node registration |
| Collector | Flask | Sync WSGI | Metrics ingestion, Pydantic validation, DB writes |
| Database | PostgreSQL | — | Shared data layer for all three services |
| Proxy | Nginx | — | Path-based routing to each service |

### Why three frameworks?

- **FastAPI** handles the WebSocket gateway because it is built on ASGI and manages high-concurrency connections natively without blocking.
- **Django** manages auth and administration because its built-in User model, session handling, and admin interface eliminate boilerplate for CRUD-heavy management tasks.
- **Flask** handles ingestion because it demonstrates that a synchronous WSGI service integrates cleanly alongside async services, and its minimal footprint suits a single-purpose endpoint.

### Critical integration seams

Two integration points connect the services through the shared database — no inter-service HTTP calls:

- **API key lifecycle:** Keys are generated in Django, validated in Flask by querying the shared DB directly.
- **Broadcast pipeline:** Flask writes a metrics record → FastAPI polls for new records every second → broadcasts to all connected WebSocket clients.

---

## Technology stack

| Concern | Choice |
|---|---|
| Language | Python 3.12 |
| Frameworks | FastAPI 0.111, Django 5.0, Flask 3.0 |
| Database | PostgreSQL 16 |
| Validation | Pydantic v2 (used directly in Flask) |
| Frontend | Vanilla JS, Chart.js 4 |
| Deployment | Fly.io (each service as a separate app) |
| Proxy | Nginx (path-based routing, WebSocket upgrade) |
| Containerisation | Docker + Docker Compose |

---

## Try it out

### As a user

1. Visit **https://metrics-nginx-freddy.fly.dev**
2. Click **Sign up** and create an account
3. Go to the **Manage** tab — create an API key and add a node. Note down both the API key and the Node ID
4. Go to the **Setup Guide** tab and follow the instructions for your OS to download and run the agent
5. Switch to **Live Metrics** and watch your charts update in real time

### As a developer (run locally)

**Prerequisites:** Docker Desktop, Python 3.12

```bash
git clone <repo-url>
cd MetricsCollector

# Copy environment file and start the stack
cp .env.example .env
docker compose up --build
```

The dashboard will be available at http://localhost.

Create a superuser for the Django admin panel:

```bash
docker compose exec admin python manage.py createsuperuser
```

**Run the tests:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-test.txt

# Unit tests (no stack required)
pytest tests/unit/

# Integration tests (stack must be running)
pytest tests/integration/ -v

# E2E tests (stack must be running)
BASE_URL=http://localhost pytest tests/e2e/ -v
```

---

## Project structure

```
MetricsCollector/
├── services/
│   ├── admin/          # Django — auth, API keys, nodes
│   ├── collector/      # Flask — metrics ingestion
│   └── gateway/        # FastAPI — WebSocket, dashboard UI
│       └── static/
│           ├── index.html   # Dashboard frontend
│           └── agent.py     # Monitoring agent (download and run on your server)
├── db/                 # Shared schema reference
├── nginx/              # Nginx config (local + Fly.io)
├── fly/                # Fly.io deployment scripts
├── tests/
│   ├── unit/           # Pure logic tests (no DB)
│   ├── integration/    # Seam tests against live stack
│   └── e2e/            # Playwright browser tests
├── docker-compose.yml
└── requirements-test.txt
```

---

## Test coverage

| Suite | Count | What it covers |
|---|---|---|
| Unit | 22 | API key hashing, Pydantic validation, FastAPI endpoints |
| Integration | 6 | API key lifecycle seam, broadcast pipeline seam |
| E2E (Playwright) | 8 | Login, registration, WebSocket connection, live chart update |
