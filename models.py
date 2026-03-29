from sqlalchemy import Column, Integer, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)  # 骑行开始时间（UTC）
    end_time = Column(DateTime, nullable=True)                              # 骑行结束时间（未结束为Null）
    unlock_fee = Column(Float, default=5.0, nullable=False)                 # 固定解锁费$5
    total_cost = Column(Float, nullable=True)                               # 骑行总费用（结束后计算）
    is_completed = Column(Boolean, default=False, nullable=False)           # 骑行完成状态
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 数据库初始化函数
def create_tables(engine):
    Base.metadata.create_all(bind=engine)
