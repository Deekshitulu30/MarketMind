from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.schemas.statistics import StatisticsAnalyzeRequest, StatisticsResponse
from app.statistics.engine import StatisticsEngine

router = APIRouter()

@router.post("/statistics/analyze", response_model=StatisticsResponse)
def analyze_statistics(req: StatisticsAnalyzeRequest, db: Session = Depends(get_db)):
    dt_start = datetime.strptime(req.start_date, "%Y-%m-%d") if req.start_date else None
    dt_end = datetime.strptime(req.end_date, "%Y-%m-%d") if req.end_date else None

    result = StatisticsEngine.analyze_stock(
        db=db,
        symbol=req.symbol.upper(),
        start_date=dt_start,
        end_date=dt_end
    )
    return result
