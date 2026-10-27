from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.schemas.backtest import BacktestRequest, BacktestResponse
from app.backtesting.engine import BacktestingEngine

router = APIRouter()

@router.post("/backtest", response_model=BacktestResponse)
def run_backtest(req: BacktestRequest, db: Session = Depends(get_db)):
    result = BacktestingEngine.run_walk_forward_backtest(
        db=db,
        symbol=req.symbol.upper(),
        model_name=req.model_name,
        n_folds=req.n_folds
    )
    return result
