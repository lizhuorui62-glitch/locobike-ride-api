# LocoBike Ride Service API
Backend API for LocoBike ride service, built with FastAPI + SQLite + SQLAlchemy. Implements core functions: start ride, end ride, retrieve ride details, calculate ride cost, following all pricing rules and technical requirements.

## Project Overview
- **Tech Stack**: Python 3.10+, FastAPI, SQLite, SQLAlchemy, Pydantic
- **Core Endpoints**: 4 API endpoints as required (start/end ride, get details, calculate cost)
- **Pricing Rules**: Unlock fee $5 + 15mins free + $1 per 5mins after + $25 daily cap
- **Features**: Data validation, error handling, ORM database, unit tests, AI usage reflection

## Environment Requirements
- Python 3.10 or higher
- pip (Python package manager)

## Local Setup & Run
### 1. Clone the repository
```bash
git clone <your-github-repo-link>
cd locobike-ride-api
