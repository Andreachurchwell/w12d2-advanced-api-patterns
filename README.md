# W12D2 After-Class Assignment: Advanced API Patterns

## Production-Ready Watchlist API

This project implements a production-ready REST API using FastAPI that demonstrates advanced API patterns covered in W12D2.

The API allows users to:
- Register and authenticate using JWT tokens
- Search for movies and TV shows from an external API
- Create and manage private watchlists
- Add and remove titles from their watchlists

The system includes:
- Role-based access control (user, admin)
- Rate limiting using Redis
- Async external API calls with httpx
- Background task processing
- Response caching
- Structured logging and request ID tracking
- Health check endpoints for deployment monitoring
- API versioning (/v1)
- Comprehensive testing and containerized deployment

## Tech Stack
- FastAPI
- Uvicorn
- Redis
- PyJWT + passlib[bcrypt]
- httpx
- pytest + pytest-cov
- Docker & docker-compose

## Assignment
W12D2 After-Class Assignment: Advanced API Patterns