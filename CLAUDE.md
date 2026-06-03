# CLAUDE.md — DevStack Metrics Collector

---

## Project Context

This is a three-service Python monorepo. Each service is isolated but shares a single PostgreSQL database. Always consult this context before making changes that touch more than one service.

| Service | Framework | Root path | Responsibility |
|---|---|---|---|
| Gateway | FastAPI | `services/gateway/` | WebSocket, public API |
| Admin | Django | `services/admin/` | Auth, API keys, node CRUD |
| Collector | Flask | `services/collector/` | Metrics ingestion |
| Shared schema | — | `db/` | Migrations, models shared across services |

**Critical integration seams — treat with extra care:**
- **API key lifecycle:** Generated in `services/admin/`, validated in `services/collector/` via shared DB. No inter-service HTTP calls.
- **Broadcast pipeline:** Flask writes to `metrics` table → FastAPI reads and broadcasts over WebSocket. The mechanism (polling vs pg_notify) is defined in `services/gateway/broadcaster.py`.

**Test directories:**
```
tests/unit/
tests/integration/
tests/e2e/
```
All new tests go into the appropriate directory. Never co-locate tests with source files.

---

## Behavioral Protocol

### 1. Think Before Coding

- **No Assumptions:** If a requirement is unclear, state your assumptions explicitly or ask for clarification. For ambiguous *requirements*, ask first. For ambiguous *implementation details* (e.g. variable naming, minor structural choices), resolve them yourself and state what you chose.
- **Surface Tradeoffs:** If there are multiple valid approaches, briefly present the options and your rationale before writing code.
- **Push Back:** If a request is over-engineered or could be simpler, suggest the simpler approach first.
- **Stop When Confused:** Do not guess. If you do not understand the request or the context, pause and ask. In a multi-step task, complete what you can confidently, then flag the ambiguity at the end before stopping — do not silently skip or guess at the unclear part.

### 2. Simplicity First

- **Minimalism:** Write only the code required to solve the current problem.
- **No Overengineering:** Do not add flexibility or configurability unless explicitly requested.
- **The New Abstraction Test:** If your solution requires introducing more than one new abstraction (class, module, interface) that does not already exist in the codebase, explain why each is necessary before adding it.

### 3. Surgical Changes

- **Localize Changes:** Touch only what is necessary to fulfil the request.
- **Preserve Existing Style:** Do not refactor formatting, comments, or adjacent code that isn't broken.
- **Orphans:** If your changes render variables or imports unused, remove them. Do not remove pre-existing dead code unless explicitly asked — mention it instead.
- **Traceability:** Every line changed must map directly back to a specific part of the request.

### 4. Goal-Driven Execution

- **Verifiable Success:** Transform vague requests into concrete, testable goals before writing code.
  - *Example:* "Fix the ingestion bug" → "Write a test that POSTs an invalid payload and asserts HTTP 422, then make it pass."
- **Structured Planning:** For multi-step tasks, always provide a brief plan before starting:
  ```
  1. [Step] → verify: [check]
  2. [Step] → verify: [check]
  ```

### 5. Testing Behaviour

- **Match test type to what's being built.** Unit tests for pure logic; integration tests for anything crossing a service or database boundary; E2E (Playwright) only for frontend flows.
- **Seam tests are mandatory.** Any change touching the API key lifecycle or the broadcast pipeline requires an integration test that covers the full seam, not just the local change.
- **New tests go in the right directory.** `tests/unit/`, `tests/integration/`, or `tests/e2e/`. Never co-locate with source.
- **Do not delete existing tests** unless explicitly asked. If a test becomes irrelevant due to your change, flag it.

---

## Workflow & Git Constraints

- **Manual Git Control:** Never execute git commands, manage branches, or handle commits. All git operations are strictly the developer's responsibility.
- **Code Delivery:** Provide changes as diffs or full file blocks. Do not attempt to automate version control.
- **Issue Generation:** When asked to generate GitHub issues, decompose to task level with explicit verify conditions matching the planning format above. Always make the shared schema a dependency of any issue that touches the database.

---

## Cross-Service Rules

- **Schema changes require explicit approval.** If a task requires adding or modifying a table or column, propose the migration first and wait for confirmation before writing service code that depends on it.
- **No direct inter-service HTTP calls at MVP.** Services communicate only through the shared database. If you believe an inter-service call is necessary, raise it before implementing.
- **Pydantic is available in Flask.** Import directly — do not proxy validation through FastAPI.
