# LocoBike Ride Service API
Backend API for LocoBike ride service, built with FastAPI + SQLite + SQLAlchemy. Implements core functions: start ride, end ride, retrieve ride details, calculate ride cost, following all official pricing rules and technical requirements.

## Project Overview
- **Tech Stack**: Python 3.10+, FastAPI, SQLite, SQLAlchemy, Pydantic
- **Core API Endpoints**: 4 required endpoints (start/end ride, get ride details, calculate ride cost)
- **Pricing Rules**: $5 unlock fee → 15 minutes free → $1 per 5 minutes (after free period) → $25 daily spending cap
- **Key Features**: Request/response validation, comprehensive error handling, ORM-based database, UTC time standardization, interactive API docs

## Environment Requirements
- Python 3.10 or higher (recommended 3.10/3.11/3.12)
- pip (Python package manager, included with Python 3.4+)

## Local Setup & Run
### 1. Clone the repository
```bash
git clone <your-github-repository-link>
cd locobike-ride-api
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the API server
```bash
# Direct run
python main.py

# Or run with uvicorn (hot reload for development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the API
- API Service Address: http://localhost:8000
- **Interactive Swagger UI** (for testing/debugging): http://localhost:8000/docs
- **Formal ReDoc Documentation**: http://localhost:8000/redoc
- Health Check: Visit http://localhost:8000 → returns `{"status": "healthy", "service": "LocoBike Ride API"}`

## API Test Examples (curl)
Run these commands in your terminal (replace `{ride_id}` with the actual ID returned from `/ride/start`)
### Start a new ride
```bash
curl -X POST http://localhost:8000/ride/start
```

### End an existing ride
```bash
curl -X POST -H "Content-Type: application/json" -d '{"ride_id": {ride_id}}' http://localhost:8000/ride/end
```

### Get ride details by ID
```bash
curl -X GET http://localhost:8000/ride/{ride_id}
```

### Calculate ride cost by ID (only for completed rides)
```bash
curl -X GET http://localhost:8000/ride/{ride_id}/cost
```

## Run Unit Tests
```bash
# Run all tests with verbose output
pytest tests/test_api.py -v

# Run tests and generate coverage report (optional)
pytest tests/test_api.py --cov=.
```

## Project Structure
All files are organized by responsibility for readability, maintainability and easy review:
```
locobike-ride-api/
├── main.py          # Project entry | FastAPI instance | Route registration
├── models.py        # SQLAlchemy ORM models | SQLite database schema
├── schemas.py       # Pydantic models | Request/response data validation
├── services.py      # Core business logic | Ride operations | Pricing calculation
├── requirements.txt # Project dependencies | Fixed versions for environment consistency
├── README.md        # Project setup | Run | Test instructions (this file)
├── AI_REFLECTION.md # AI tool usage reflection (required submission)
├── SYSTEM_DESIGN.md # Scalable backend architecture (bonus question)
└── tests/           # Unit test suite | Core logic & API endpoint testing
    └── test_api.py
```

## Other Key Documents
- **AI_REFLECTION.md**: Detailed reflection on AI tool usage (required) – includes AI tools used, prompts, AI-generated weaknesses and manual optimizations.
- **SYSTEM_DESIGN.md**: Scalable backend architecture design for 50k bikes & 500k users (bonus) – includes component boundaries, data flow and failure scenario handling.

## Notes
- SQLite database file (`locobike.db`) is created **automatically** on first run (no manual initialization needed).
- All time fields use **UTC time** for global service consistency.
- All API endpoints include detailed error handling with specific HTTP status codes and error messages.
- The project follows Python PEP8 coding standards for readability.

