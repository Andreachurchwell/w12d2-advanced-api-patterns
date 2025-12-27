# W12D2 Advanced API Patterns — Reflection & Current State

## What this project is
This project is a production-style FastAPI backend for a “Watchlist” app (movies/shows I want to track).
The goal is to practice enterprise API patterns: routing/versioning, auth + JWT, middleware, standardized errors,
database persistence, protected CRUD, and later rate limiting + caching + async patterns.

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
Implemented in `app/api/v1/auth.py` + `app/core/security.py`:

- `POST /v1/auth/register`
  - Registers a user
  - Validates email + password strength
  - Hashes password with bcrypt

- `POST /v1/auth/login`
  - Verifies credentials
  - Returns a JWT access token

- `GET /v1/auth/me`
  - Protected endpoint
  - Reads JWT from `Authorization: Bearer <token>`
  - Returns the authenticated user's email

- JWT handling:
  - Token creation + decoding in `app/core/security.py`
  - Token subject = user email

✅ **Update:** Users are now stored in the database (not in-memory), so credentials persist across restarts.

---

### 3. Middleware & Error Handling
- Request ID middleware:
  - Every request gets an `X-Request-ID` header
- Custom error system:
  - `AppError` base class
  - `UnauthorizedError`, `NotFoundError`, etc.
  - Global exception handler formats errors consistently

---

### 4. Database Persistence (SQLite)
Database is now wired up and working:

- SQLAlchemy setup:
  - `app/db/session.py` → engine + SessionLocal + Base
  - `app/db/deps.py` → `get_db()` dependency
  - `app/db/models.py` → SQLAlchemy models
  - `app/db/init_db.py` → creates tables

- SQLite file:
  - `app.db`
- Verified tables exist:
  - `users`
  - `watchlist_items`

---

### 5. Watchlists (Protected CRUD — partially complete)
Implemented in `app/api/v1/watchlists.py`.

✅ Working endpoints:

- `GET /v1/watchlists/`
  - Protected via JWT
  - Returns `{ user, watchlist: [...] }`
  - Pulls from the DB (not memory)

- `POST /v1/watchlists/items`
  - Protected via JWT
  - Adds a watchlist item for the logged-in user
  - Stores in DB

- `DELETE /v1/watchlists/items/{id}`
  - Protected via JWT
  - Deletes the specified item (and confirms with a response)

✅ Verified with curl:
- Register → Login → Token → Add items → List → Delete → List again works.

---

### 6. Streamlit Dashboard (UI helper for testing)
A Streamlit dashboard was created to test the API without Swagger.
Work was stashed (WIP) so backend work could continue cleanly.

- Stashes created:
  - `stash@{0}: WIP Streamlit app file`
  - `stash@{1}: WIP Streamlit dashboard UI`

This can be restored later with:
- `git stash pop` (or `git stash apply`)

---

## Verified working flows
- `/health` works
- Register → Login → Access protected route works
- `/v1/auth/me` works with JWT
- `/v1/watchlists/` requires auth and returns user context
- Database tables are created and persist across restart
- Watchlist items can be created + deleted + listed

---

## Current Git state
- Watchlists work branch existed earlier: `feature/watchlists`
- Database persistence work is now on: `feature/db-persistence`
- DB persistence branch has been committed and pushed:
  - commit message: “Add database persistence for users and watchlists”

---

## Where I stopped (latest stopping point)
I stopped after successfully:
- Moving users from in-memory to SQLite persistence
- Creating SQLAlchemy models (`User`, `WatchlistItem`)
- Creating tables and confirming they exist
- Wiring watchlist CRUD (GET + POST + DELETE) to the database
- Testing the full workflow with curl + JWT

---

## What is NOT done yet (still needed for full assignment)
### CRUD completeness
- PATCH or PUT endpoint for updating a watchlist item (not done yet)

### Production Patterns / Requirements still missing
- Pagination + filtering + sorting on list endpoints
- Rate limiting with Redis (headers + 429 behavior)
- Caching strategy
- At least one async endpoint using httpx
- BackgroundTasks example
- Tests (pytest + coverage target)
- Dockerfile + docker-compose (API + Redis + DB)
- Deployment + Postman collection + demo video

---

## Notes for future me
- If login says "Invalid credentials", make sure the user was registered in the DB.
- Always include: `Authorization: Bearer <token>` for protected endpoints.
- Easiest workflow for tokens in terminal:
  - export TOKEN="..." once and reuse it in curl commands.
- If Streamlit work disappears: it’s in git stash (WIP).
