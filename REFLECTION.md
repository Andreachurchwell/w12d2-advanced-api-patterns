# W12D2 Advanced API Patterns — Reflection & Current State

## What this project is
This project is a production-style FastAPI backend for a “Watchlist” app (think: movies/shows I want to watch later).  
The goal is to practice enterprise API patterns: auth, JWT, middleware, versioning, error handling, rate limiting (later), etc.

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
  - Registers a user (in-memory for now)
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

⚠ Users are currently stored in-memory (`USERS` dict), so restarting the server clears users.

---

### 3. Middleware & Error Handling

- Request ID middleware:
  - Every request gets an `X-Request-ID` header
- Custom error system:
  - `AppError` base class
  - `UnauthorizedError`, `NotFoundError`, etc.
  - Global exception handler formats errors consistently

---

### 4. Watchlists (scaffolded + protected)

Implemented in `app/api/v1/watchlists.py`:

- `GET /v1/watchlists/`
  - Protected via JWT
  - Returns `{ user, watchlist: [] }`
  - Currently returns an empty list (no storage yet)

This confirms:
- Routing is correct
- Auth dependency injection is working
- Authorization is enforced

---

## Verified working flows

- Register → Login → Access protected route works
- `/health` works
- `/v1/auth/me` works with JWT
- `/v1/watchlists/` requires auth and returns user context

---

## Current Git state

- Active branch: `feature/watchlists`
- Branch is clean and pushed
- `dev` remains stable
- No uncommitted changes

---

## Where I stopped

I stopped after:
- Successfully wiring auth
- Protecting routes with JWT
- Scaffolding watchlists
- Verifying `/v1/watchlists/` returns correct user with auth

I **have not yet implemented**:
- Adding items to a watchlist
- Deleting items from a watchlist
- Pagination/filtering
- Persistence (database)
- Rate limiting
- Caching
- Async external API calls
- Testing beyond smoke tests

---

## Next intended step

Add watchlist item management:

- `POST /v1/watchlists/items` → add a title to the user's watchlist
- `DELETE /v1/watchlists/items/{id}` → remove a title
- Store watchlists per-user (in memory first, DB later)

---

## Notes for future me

- If auth suddenly says "Invalid credentials", it's because USERS is in memory and was wiped — re-register.
- If protected endpoints return 401, check the Authorization header formatting.
- Don’t rush — each production pattern should be added deliberately.

