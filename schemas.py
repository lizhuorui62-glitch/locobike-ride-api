from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# 骑行开始请求（无参数，仅创建会话）
class RideStartRequest(BaseModel):
    pass

# 骑行结束请求（必传ride_id）
class RideEndRequest(BaseModel):
    ride_id: int = Field(..., gt=0, description="骑行ID，必须为正整数")

# 骑行详情响应模型
class RideResponse(BaseModel):
    id: int
    start_time: datetime
    end_time: Optional[datetime]
    unlock_fee: float
    total_cost: Optional[float]
    is_completed: bool

    class Config:
        orm_mode = True  # 支持从SQLAlchemy ORM对象转换

# 骑行费用响应模型
class RideCostResponse(BaseModel):
    ride_id: int
    unlock_fee: float
    ride_duration_min: Optional[float]
    additional_fee: float
    total_cost: float
    daily_cap_applied: bool  # 是否触发每日上限$25
