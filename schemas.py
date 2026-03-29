from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Ride start request (no parameters, only create a session)
class RideStartRequest(BaseModel):
    pass

# Ride end request (ride_id must be passed)
class RideEndRequest(BaseModel):
    ride_id: int = Field(..., gt=0, description="Cycling ID must be a positive integer")

# Riding details response model
class RideResponse(BaseModel):
    id: int
    start_time: datetime
    end_time: Optional[datetime]
    unlock_fee: float
    total_cost: Optional[float]
    is_completed: bool

    class Config:
        orm_mode = True  # Support conversion from SQLAlchemy ORM objects

# Ride cost response model
class RideCostResponse(BaseModel):
    ride_id: int
    unlock_fee: float
    ride_duration_min: Optional[float]
    additional_fee: float
    total_cost: float
    daily_cap_applied: bool  # Whether the daily limit of $25 is triggered
