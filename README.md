# W12D2 After-Class Assignment: Advanced API Patterns

## Production-Ready Watchlist API

This project implements a production-style REST API using FastAPI that demonstrates advanced API patterns covered in W12D2.

The domain is intentionally simple (a personal Watchlist app) so the focus can be on architecture, correctness, and production concerns rather than business complexity.

The API allows users to:
- Register and authenticate using JWT tokens
- Create and manage private watchlists
- Add, update, and remove titles from their watchlists

---

## Implemented Patterns

- Versioned REST API (`/v1`)
- JWT authentication with hashed passwords (bcrypt)
- Protected routes using dependency injection
- SQLAlchemy persistence with SQLite
- Centralized configuration using environment variables (`pydantic-settings`)
- Custom middleware for request ID tracing
- Global exception handling with standardized error responses
- Modular project structure (api, core, db)
- Health check endpoint for monitoring
- Async-ready FastAPI endpoints
- Basic automated testing with pytest + httpx

---

## Verified Flows

- Register → Login → Access protected routes
- Add / list / update / delete watchlist items
- Tokens expire and invalid tokens are rejected
- Restarting the server does not lose data
- Automated tests pass for health and authentication

---

## Tech Stack

- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- PyJWT + passlib[bcrypt]
- httpx
- pytest

---

## What I Learned

- How to structure a production-style API with clean separation of concerns
- How JWT authentication works end-to-end
- How to persist and manage relational data using SQLAlchemy
- How to centralize configuration safely with environment variables
- How to write automated tests for async APIs
- How to reason about production concerns beyond "just making it work"

---

## Future Improvements

- Rate limiting (e.g., Redis-based)
- Caching for frequently accessed endpoints
- Background tasks for cleanup or notifications
- Containerized deployment with Docker
- More extensive automated test coverage

---

## Assignment

W12D2 After-Class Assignment: Advanced API Patterns