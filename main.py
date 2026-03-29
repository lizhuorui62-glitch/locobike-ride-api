from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Ride, create_tables
from schemas import RideStartRequest, RideEndRequest, RideResponse, RideCostResponse
from services import start_ride, end_ride, get_ride_by_id, calculate_ride_cost

# 初始化FastAPI
app = FastAPI(
    title="LocoBike Ride Service API",
    description="Backend API for LocoBike ride service (start/end ride, cost calculation)",
    version="1.0.0"
)

# 初始化SQLite数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./locobike.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}  # SQLite专属配置
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库表（首次运行自动创建）
create_tables(engine)

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. POST /ride/start - 开始骑行
@app.post("/ride/start", response_model=RideResponse, status_code=201)
def api_start_ride(db: Session = Depends(get_db)):
    try:
        ride = start_ride(db)
        return ride
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 2. POST /ride/end - 结束骑行
@app.post("/ride/end", response_model=RideResponse)
def api_end_ride(request: RideEndRequest, db: Session = Depends(get_db)):
    try:
        ride = end_ride(db, request.ride_id)
        return ride
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 3. GET /ride/{id} - 获取骑行详情
@app.get("/ride/{id}", response_model=RideResponse)
def api_get_ride(id: int, db: Session = Depends(get_db)):
    try:
        ride = get_ride_by_id(db, id)
        return ride
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 4. GET /ride/{id}/cost - 获取骑行费用
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

# 根路径健康检查
@app.get("/")
def health_check():
    return {"status": "healthy", "service": "LocoBike Ride API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
