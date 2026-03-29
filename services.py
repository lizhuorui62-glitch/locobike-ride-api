from sqlalchemy.orm import Session
from models import Ride
from schemas import RideCostResponse
from datetime import datetime
from math import ceil

# Pricing rule constants (for easy maintenance)
UNLOCK_FEE = 5.0
FREE_DURATION_MIN = 15
RATE_PER_5MIN = 1.0
DAILY_CAP = 25.0

def start_ride(db: Session) -> Ride:
    """Create a new cycling session and return the cycling object"""
    new_ride = Ride()
    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)
    return new_ride

def end_ride(db: Session, ride_id: int) -> Ride:
    """End the bike ride, calculate the total cost, and update the ride status"""
    # Check if there is a bike ride
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise ValueError(f"Ride with ID {ride_id} does not exist")
    # Verify whether the cycling has ended
    if ride.is_completed:
        raise ValueError(f"Ride with ID {ride_id} is already completed")
    # Update the end time and status
    ride.end_time = datetime.utcnow()
    ride.is_completed = True
    # Calculate the total cost
    ride.total_cost = calculate_ride_cost(ride).total_cost
    db.commit()
    db.refresh(ride)
    return ride

def get_ride_by_id(db: Session, ride_id: int) -> Ride:
    """Get cycling details by ID"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise ValueError(f"Ride with ID {ride_id} does not exist")
    return ride

def calculate_ride_cost(ride: Ride) -> RideCostResponse:
    """Calculate the cycling cost, strictly follow the pricing rules, and return the cost details"""
    # The cost cannot be calculated for an unfinished bike ride
    if not ride.end_time:
        raise ValueError(f"Ride with ID {ride.id} is not completed, cannot calculate cost")
    
    # Calculate the cycling duration (minutes)
    duration_seconds = (ride.end_time - ride.start_time).total_seconds()
    duration_min = duration_seconds / 60

    # Calculate the additional fee (the first 15 minutes are free, and then it's $1 for every 5 minutes, rounded up)
    if duration_min <= FREE_DURATION_MIN:
        additional_fee = 0.0
    else:
        extra_min = duration_min - FREE_DURATION_MIN
        extra_5min_units = ceil(extra_min / 5)  # If it is less than 5 minutes, it will be counted as one unit
        additional_fee = extra_5min_units * RATE_PER_5MIN

    # Total cost (unlocking fee + additional fee), and determine whether the daily limit is triggered
    pre_cap_total = UNLOCK_FEE + additional_fee
    total_cost = min(pre_cap_total, DAILY_CAP)
    daily_cap_applied = pre_cap_total >= DAILY_CAP

    # Return to the cost details
    return RideCostResponse(
        ride_id=ride.id,
        unlock_fee=UNLOCK_FEE,
        ride_duration_min=round(duration_min, 2),
        additional_fee=round(additional_fee, 2),
        total_cost=round(total_cost, 2),
        daily_cap_applied=daily_cap_applied
    )
