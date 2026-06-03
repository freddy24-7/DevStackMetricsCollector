# Product Requirements Document: DevStack Metrics Collector

## 1. Executive Summary

The DevStack Metrics Collector is a centralized monitoring dashboard that allows users to view real-time system metrics (CPU, RAM, Disk usage) from remote machines. The project serves as a technical demonstration of a microservices-based architecture using FastAPI for high-concurrency async communication, Django for administrative management, and Flask for synchronous WSGI-based data ingestion.

The three-framework design is intentional and instructive: each framework was chosen to demonstrate a distinct Python paradigm — asynchronous ASGI (FastAPI), batteries-included MVC (Django), and lightweight synchronous WSGI (Flask) — operating in concert over a shared data layer.

---

## 2. Target Audience

- **Primary:** Hiring managers and technical recruiters assessing full-stack engineering competency.
- **Secondary:** Developers looking for a lightweight, self-hosted monitoring solution for home labs or small server environments.

---

## 3. Product Goals & Success Metrics

**Goal:** Demonstrate interoperability between three distinct Python frameworks within a containerised, production-style deployment.

**Success Metrics:**

- Fully functional containerised deployment accessible via a public URL.
- WebSocket dashboard updates within 2 seconds of a metrics POST arriving at the ingestion endpoint.
- Flask ingestion endpoint handles at least 50 concurrent POST requests without error.
- All three services connect to the shared database and pass migrations cleanly in CI.

---

## 4. System Architecture

The application follows a service-oriented architecture with a shared PostgreSQL database. All inter-service traffic is routed through an Nginx reverse proxy.

| Service | Framework | Paradigm | Responsibility |
|---|---|---|---|
| Gateway | FastAPI | Async ASGI | WebSocket connections, real-time broadcasting, public API |
| Admin | Django | Sync MVC | User auth, API key management, node CRUD |
| Collector | Flask | Sync WSGI | Metrics ingestion, Pydantic validation, DB writes |
| Database | PostgreSQL | — | Shared data layer for all services |
| Proxy | Nginx | — | Path-based routing to each service |

### 4.1 Framework Justification

- **FastAPI** handles the WebSocket gateway because it is built on ASGI and handles high-concurrency connections natively without blocking.
- **Django** manages auth and administration because its built-in User model, session handling, and admin interface eliminate boilerplate for CRUD-heavy management tasks.
- **Flask** handles ingestion because it demonstrates that a synchronous WSGI service can be integrated cleanly alongside async services, and its minimal footprint is appropriate for a single-purpose endpoint.

### 4.2 Critical Integration Seams

Two integration points carry architectural risk and are treated as first-class requirements:

**Seam 1 — API Key Lifecycle:**
- Keys are generated and stored by Django (owner: Django Admin service).
- Keys are validated on every inbound POST by Flask (owner: Collector service).
- Flask validates by querying the shared database directly — no inter-service HTTP call.

**Seam 2 — Metrics Broadcast Pipeline:**
- Flask writes a validated metrics record to PostgreSQL.
- FastAPI polls or listens for new records and broadcasts them over the WebSocket connection to connected dashboard clients.
- The broadcast mechanism (polling interval or pg_notify) must be specified before Phase 3 begins.

---

## 5. Functional Requirements

### 5.1 Real-Time Dashboard (WebSockets)

- The UI shall display live system metrics using Chart.js line charts.
- A WebSocket connection to `wss://domain/ws/metrics` pushes updates without manual page refresh.
- The dashboard shall display a "disconnected" state if the WebSocket drops, and attempt automatic reconnection.

### 5.2 User Management (Django Admin)

- Users shall have a secure account to view their unique dashboard.
- Authentication uses Django's built-in User model with session-based login.
- Users can perform CRUD operations on registered infrastructure nodes via the Django admin interface.

### 5.3 API Key Management

- Authenticated users shall be able to generate, view, and revoke API keys from the dashboard.
- Each API key is scoped to a single user account.
- The Collector service validates the API key on every inbound POST request. Invalid or revoked keys return HTTP 401.

### 5.4 Data Ingestion

- The Collector shall accept incoming metrics via POST to `/api/v1/metrics`.
- Payloads are validated using Pydantic before any database write.
- Invalid payloads return HTTP 422 with a structured error response.
- Validated records are written to the shared PostgreSQL database.

---

## 6. Technical Requirements

| Concern | Decision |
|---|---|
| Language | Python 3.12+ |
| Frameworks | FastAPI, Django 5.x, Flask 3.x |
| Database | PostgreSQL 16 (shared, single instance for MVP) |
| Validation | Pydantic v2 (used in Flask via direct import) |
| Deployment | Docker Compose locally; Railway for public deployment |
| Proxy | Nginx with path-based routing |
| WebSocket | `wss://` (TLS enforced on Railway) |
| Frontend | Chart.js; vanilla JS for WebSocket client |

---

## 7. Database Schema (Foundation — Defined Before Any Service Code)

The schema is the single source of truth shared across all three services. It must be finalised and migrated before Phase 2 begins.

**Core tables:**

- `users` — managed by Django (via Django's built-in User model)
- `api_keys` — `id`, `user_id` (FK), `key_hash`, `created_at`, `revoked_at`
- `nodes` — `id`, `user_id` (FK), `hostname`, `label`, `created_at`
- `metrics` — `id`, `node_id` (FK), `cpu_pct`, `ram_pct`, `disk_pct`, `recorded_at`

Schema changes after Phase 1 require explicit review before implementation.

---

## 8. User Flow

1. **Registration:** User creates an account on the Django portal.
2. **Configuration:** User generates an API key in the dashboard and registers a node.
3. **Provisioning:** User runs a local monitoring script on their server that POSTs metrics to `/api/v1/metrics` using the API key.
4. **Monitoring:** User navigates to the dashboard and sees their server appear in real-time, with charts updating live via WebSockets.

---

## 9. Testing Strategy

Testing is applied per phase, matched to what is actually being built. All tests live under a consistent directory structure from the start:

```
tests/
  unit/
  integration/
  e2e/
```

| Phase | Unit | Integration | E2E |
|---|---|---|---|
| 1 — Schema + Docker | — | DB connectivity + migrations for all 3 services | — |
| 2 — Django Auth + FastAPI | Auth logic, API key generation, FastAPI endpoints | — | — |
| 3 — Flask Collector | Pydantic validation logic | POST → DB write; API key validation across seam | — |
| 4 — Containerisation + Nginx | — | Full routing through Nginx per service | — |
| 5 — Frontend | — | — | Register → key → dashboard; WebSocket connect; live update on POST |

**Integration seam tests** (written at the moment each seam is built, not deferred):
- API key: generate in Django → validate in Flask → confirm 401 on revoked key.
- Broadcast pipeline: POST to Flask → confirm WebSocket client receives update within 2s.

---

## 10. Implementation Roadmap

| Phase | Deliverable | Gate before next phase |
|---|---|---|
| 1 | Monorepo structure, shared DB schema, Docker Compose skeleton, Nginx config | All 3 services connect to DB; migrations pass |
| 2 | Django auth + API key management; FastAPI WebSocket gateway + public endpoints | Unit tests pass; WebSocket accepts connections |
| 3 | Flask ingestion endpoint; Pydantic validation; API key validation | Integration tests pass for both seams |
| 4 | Full containerisation; Railway deployment; Nginx routing | Integration tests pass through Nginx layer |
| 5 | Frontend dashboard; Chart.js visualisation; WebSocket client | E2E Playwright tests pass for 3 core flows |

---

## 11. Future Considerations (Out of Scope for MVP)

- **Alerting:** Discord/Slack webhook integration for CPU/RAM threshold breaches. (Good candidate for a single-purpose agent post-MVP.)
- **Historical Data:** Long-term trend analysis and time-range queries (currently optimised for live state only).
- **Multi-tenancy:** Team and organisation structures beyond individual user accounts.
- **Agent-based issue generation:** GitHub issue generation via Claude Code for Phase 2+ once Phase 1 schema is locked.
