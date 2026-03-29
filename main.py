from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Ride, create_tables
from schemas import RideStartRequest, RideEndRequest, RideResponse, RideCostResponse
from services import start_ride, end_ride, get_ride_by_id, calculate_ride_cost

# Initialize FastAPI
app = FastAPI(
    title="LocoBike Ride Service API",
    description="Backend API for LocoBike ride service (start/end ride, cost calculation)",
    version="1.0.0"
)

# Initialize the SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./locobike.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}  # Exclusive configuration for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a database table (automatically created on the first run)
create_tables(engine)

# Dependencies: Obtain a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. POST /ride/start - Start cycling
@app.post("/ride/start", response_model=RideResponse, status_code=201)
def api_start_ride(db: Session = Depends(get_db)):
    try:
        ride = start_ride(db)
        return ride
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 2. POST /ride/end - End the cycling
@app.post("/ride/end", response_model=RideResponse)
def api_end_ride(request: RideEndRequest, db: Session = Depends(get_db)):
    try:
        ride = end_ride(db, request.ride_id)
        return ride
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 3. GET /ride/{id} - Get cycling details
@app.get("/ride/{id}", response_model=RideResponse)
def api_get_ride(id: int, db: Session = Depends(get_db)):
    try:
        ride = get_ride_by_id(db, id)
        return ride
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 4. GET /ride/{id}/cost - Get the cycling cost
@app.get("/ride/{id}/cost", response_model=RideCostResponse)
def api_get_ride_cost(id: int, db: Session = Depends(get_db)):
    try:
        ride = get_ride_by_id(db, id)
        cost_detail = calculate_ride_cost(ride)
        return cost_detail
    except ValueError as e:
        if "not completed" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Root path health check
@app.get("/")
def health_check():
    return {"status": "healthy", "service": "LocoBike Ride API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
