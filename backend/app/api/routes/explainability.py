from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.schemas.explainability import ExplainRequest, ExplainResponse
from app.explainability.engine import ExplainabilityEngine

router = APIRouter()

@router.post("/explain", response_model=ExplainResponse)
def explain_prediction(req: ExplainRequest, db: Session = Depends(get_db)):
    result = ExplainabilityEngine.explain_prediction(
        db=db,
        symbol=req.symbol.upper(),
        model_id=req.model_id
    )
    return result
