from sqlalchemy import Column, Integer, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)  # Riding start time（UTC）
    end_time = Column(DateTime, nullable=True)                              # Cycling end time (Null if not ended)
    unlock_fee = Column(Float, default=5.0, nullable=False)                 # Fixed unlocking fee: $5
    total_cost = Column(Float, nullable=True)                               # Total cycling cost (calculated after the end)
    is_completed = Column(Boolean, default=False, nullable=False)           # Cycling completion status
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database initialization function
def create_tables(engine):
    Base.metadata.create_all(bind=engine)
