# W12D2 Advanced API Patterns — Reflection & Current State

## What this project is
This project is a production-style FastAPI backend for a “Watchlist” app (movies/shows I want to watch later).
The goal is to practice enterprise API patterns: auth, JWT, middleware, versioning, error handling, DB persistence, etc.

The domain is intentionally simple so I can focus on architecture and correctness instead of business complexity.

---

## What is currently implemented

### 1. API Structure
- Versioned API at `/v1`
- Modular router structure:
  - `/v1/auth` → authentication routes
  - `/v1/watchlists` → watchlist resource routes
- Central `api_router` includes all versioned routers.

### 2. Authentication (working end-to-end)
Implemented in `app/api/v1/auth.py`:
- `POST /v1/auth/register`
  - Registers a user (now persisted in SQLite DB)
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

✅ Important improvement: users are no longer in-memory, so restarting the server does NOT wipe them.

### 3. Middleware & Error Handling
- Request ID middleware:
  - Every request gets an `X-Request-ID` header
- Custom error system + global exception handler:
  - Standardized error response format (code/message/request_id)

### 4. Database Persistence (SQLite)
- SQLite database at `sqlite:///./app.db`
- SQLAlchemy models:
  - `User` (email, password_hash, role, created_at)
  - `WatchlistItem` (user_id, title, media_type, created_at)
- DB session wiring:
  - `app/db/session.py` defines engine + SessionLocal + Base
  - `app/db/deps.py` provides `get_db()` dependency
- Tables are created successfully: `users`, `watchlist_items`

### 5. Watchlists (CRUD working + protected)
Implemented in `app/api/v1/watchlists.py` (all routes require JWT):
- `GET /v1/watchlists/`
  - Returns the authenticated user + their items
- `POST /v1/watchlists/items`
  - Adds a watchlist item (title + type)
  - Saves to DB
- `DELETE /v1/watchlists/items/{item_id}`
  - Deletes an item by id (owned by the logged-in user)
- `PATCH /v1/watchlists/items/{item_id}`
  - Partially updates an item (title and/or type)

---

## Verified working flows
- Register → Login → Access protected routes works
- `/health` works
- `/v1/auth/me` works with JWT
- Watchlist flows work end-to-end:
  - Add items (POST)
  - List items (GET)
  - Delete item (DELETE)
  - Update item (PATCH)

---

## Current Git state
- Active branch: `feature/db-persistence`
- DB persistence code has been committed + pushed
- Working tree currently has local edits (REFLECTION.md, watchlists.py, .gitignore)

---

## Where I stopped today
I stopped after:
- Switching from in-memory storage to SQLite persistence
- Implementing full watchlist CRUD routes (GET/POST/DELETE) + PATCH update
- Testing endpoints using curl with exported `$TOKEN`

---

## Notes for future me
- Tokens expire. If you get `Invalid or expired token`, re-login and re-export TOKEN.
- If login ever says invalid credentials, confirm the user exists in DB (register once).
- Keep DB session usage consistent: use `db: Session = Depends(get_db)` in every route (avoid `next(get_db())`).
