from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.schemas.prediction import PredictRequest, PredictResponse
from app.services.prediction_service import PredictionService

router = APIRouter()

@router.get("/predict/{ticker}", response_model=PredictResponse)
def get_prediction_by_ticker(ticker: str, db: Session = Depends(get_db)):
    """
    Stateless high-performance prediction endpoint as specified in MarketMind architecture:
    GET /api/predict/{ticker}
    Dynamically deserializes model_{ticker}.joblib (.pkl), computes stationary features and TreeSHAP,
    returns probabilistic direction and confidence in <3s, and clears memory.
    """
    result = PredictionService.generate_prediction(
        db=db,
        symbol=ticker.strip().upper(),
        horizon=1
    )
    return result

@router.post("/predict/{ticker}", response_model=PredictResponse)
def post_prediction_by_ticker(ticker: str, db: Session = Depends(get_db)):
    result = PredictionService.generate_prediction(
        db=db,
        symbol=ticker.strip().upper(),
        horizon=1
    )
    return result

@router.post("/predict", response_model=PredictResponse)
def predict_market_direction(req: PredictRequest, db: Session = Depends(get_db)):
    result = PredictionService.generate_prediction(
        db=db,
        symbol=req.symbol.upper(),
        model_id=req.model_id,
        horizon=req.horizon
    )
    return result

