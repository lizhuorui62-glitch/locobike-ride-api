from sqlalchemy.orm import Session
from models import Ride
from schemas import RideCostResponse
from datetime import datetime
from math import ceil

# 定价规则常量（便于维护）
UNLOCK_FEE = 5.0
FREE_DURATION_MIN = 15
RATE_PER_5MIN = 1.0
DAILY_CAP = 25.0

def start_ride(db: Session) -> Ride:
    """创建新骑行会话，返回骑行对象"""
    new_ride = Ride()
    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)
    return new_ride

def end_ride(db: Session, ride_id: int) -> Ride:
    """结束骑行，计算总费用，更新骑行状态"""
    # 校验骑行是否存在
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise ValueError(f"Ride with ID {ride_id} does not exist")
    # 校验骑行是否已结束
    if ride.is_completed:
        raise ValueError(f"Ride with ID {ride_id} is already completed")
    # 更新结束时间和状态
    ride.end_time = datetime.utcnow()
    ride.is_completed = True
    # 计算总费用
    ride.total_cost = calculate_ride_cost(ride).total_cost
    db.commit()
    db.refresh(ride)
    return ride

def get_ride_by_id(db: Session, ride_id: int) -> Ride:
    """根据ID获取骑行详情"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise ValueError(f"Ride with ID {ride_id} does not exist")
    return ride

def calculate_ride_cost(ride: Ride) -> RideCostResponse:
    """计算骑行费用，严格遵循定价规则，返回费用详情"""
    # 未结束的骑行无法计算费用
    if not ride.end_time:
        raise ValueError(f"Ride with ID {ride.id} is not completed, cannot calculate cost")
    
    # 计算骑行时长（分钟）
    duration_seconds = (ride.end_time - ride.start_time).total_seconds()
    duration_min = duration_seconds / 60

    # 计算额外费用（前15分钟免费，之后每5分钟$1，向上取整）
    if duration_min <= FREE_DURATION_MIN:
        additional_fee = 0.0
    else:
        extra_min = duration_min - FREE_DURATION_MIN
        extra_5min_units = ceil(extra_min / 5)  # 不足5分钟按1个单位算
        additional_fee = extra_5min_units * RATE_PER_5MIN

    # 总费用（解锁费+额外费用），并判断是否触发每日上限
    pre_cap_total = UNLOCK_FEE + additional_fee
    total_cost = min(pre_cap_total, DAILY_CAP)
    daily_cap_applied = pre_cap_total >= DAILY_CAP

    # 返回费用详情
    return RideCostResponse(
        ride_id=ride.id,
        unlock_fee=UNLOCK_FEE,
        ride_duration_min=round(duration_min, 2),
        additional_fee=round(additional_fee, 2),
        total_cost=round(total_cost, 2),
        daily_cap_applied=daily_cap_applied
    )
