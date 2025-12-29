# W12D2 Advanced API Patterns — Reflection & Current State

## What this project is

This project is a production-style FastAPI backend for a “Watchlist” app (movies/shows I want to watch later).
The goal is to practice enterprise API patterns: auth, JWT, middleware, versioning, error handling, DB persistence, caching, etc.

The domain is intentionally simple so I can focus on architecture and correctness instead of business complexity.

---

## What is currently implemented

### 1. API Structure

- Versioned API at `/v1`
- Modular router structure:
  - `/v1/auth` → authentication routes
  - `/v1/watchlists` → watchlist resource routes
- Central `api_router` includes all versioned routers.

---

### 2. Authentication (working end-to-end)

Implemented in `app/api/v1/auth.py`:

- `POST /v1/auth/register`
  - Registers a user (persisted in SQLite DB)
  - Validates email + password strength
  - Hashes password with bcrypt
- `POST /v1/auth/login`
  - Verifies credentials
  - Returns a JWT access token
- `GET /v1/auth/me`
  - Protected endpoint
  - Reads JWT from `Authorization: Bearer <token>`
  - Returns the authenticated user's email
- JWT handling lives in `app/core/security.py` (create + decode)

✅ Users are persisted in DB (no longer in-memory), so restarts no longer wipe accounts.

---

### 3. Middleware, Logging & Error Handling

- Request ID middleware:
  - Every request gets an `X-Request-ID` header
- Custom error system + global exception handler:
  - Standardized error response format (`code`, `message`, `request_id`)
- Application logging:
  - Structured logging via `app/core/app_logger.py`
  - Logs key events like item creation and errors
- Audit logging:
  - Writes basic audit entries (add actions) to `audit.log` via background task

---

### 4. Database Persistence (SQLite)

- SQLite database at `sqlite:///./app.db`
- SQLAlchemy models:
  - `User` (email, password_hash, role, created_at)
  - `WatchlistItem` (user_id, title, media_type, created_at)
- DB session wiring:
  - `app/db/session.py` defines engine + SessionLocal + Base
  - `app/db/deps.py` provides `get_db()` dependency
- Tables confirmed:
  - `users`
  - `watchlist_items`

---

### 5. Watchlists (CRUD working + protected)

Implemented in `app/api/v1/watchlists.py`:

- `GET /v1/watchlists/`
  - Supports pagination, sorting, and filtering
  - Returns only items belonging to the authenticated user
  - Results are cached in Redis for 30 seconds
- `POST /v1/watchlists/items`
  - Adds a watchlist item
  - Saves to DB
  - Invalidates Redis cache
- `DELETE /v1/watchlists/items/{item_id}`
  - Deletes item owned by user
  - Invalidates Redis cache
- `PATCH /v1/watchlists/items/{item_id}`
  - Updates title and/or type
  - Invalidates Redis cache

---

### 6. Redis Caching

- Redis used for caching `GET /watchlists` responses
- Cache key includes:
  - user email
  - skip / limit
  - filters and sort
- Cache invalidated on add / delete / update

---

### 7. Streamlit Dashboard (working UI)

Built a Streamlit frontend (`streamlit_app.py`) to test and interact with the API:

- Register + login users
- Store JWT in session
- View watchlists
- Add, delete, and update items
- Auto-refresh after mutations

Verified working flows:

- Register → Login → Access protected routes works
- `/health` and `/health/detailed` work
- `/v1/auth/me` works with JWT
- Watchlist flows work end-to-end:
  - Add items (POST)
  - List items (GET)
  - Delete item (DELETE)
  - Update item (PATCH)
- Items persist across server restarts

---

### 8. Docker & Local Infrastructure

- `Dockerfile` for the FastAPI API service
- `docker-compose.yml` to run:
  - API service
  - Redis
- Allows running the stack with:

  ```bash
  docker compose up --build
  ```

### Current Git state

- Active branch: feature/db-persistence

- DB persistence, caching, and CRUD routes are implemented

- Streamlit UI exists locally and is ready to be committed

- Reflection and cleanup changes pending commit

Where I stopped today
I stopped after:
- Adding Redis caching to watchlist GET
- Implementing PATCH update for watchlist items
- Building a Streamlit dashboard to exercise the API
- Debugging DB persistence and confirming data integrity
- Cleaning up logging and audit behavior

What still needs to be done
- Add pagination controls to the Streamlit UI (skip/limit)
- Add role-based access control (admin vs user)
- Add tests for watchlist routes and auth flows
- Possibly switch SQLite → Postgres for realism
- Add observability (metrics or tracing)

Notes for future me
- Tokens expire — re-login if requests fail.
- Always check which user you’re logged in as when viewing watchlists.
- Redis cache keys include query params — remember to invalidate correctly.
- If Streamlit behaves oddly, check indentation and widget keys.
