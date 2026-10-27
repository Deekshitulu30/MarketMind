from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.schemas.what_if import WhatIfRequest, WhatIfResponse
from app.what_if.simulator import WhatIfSimulator

router = APIRouter()

@router.post("/what-if", response_model=WhatIfResponse)
def run_what_if_scenario(req: WhatIfRequest, db: Session = Depends(get_db)):
    result = WhatIfSimulator.simulate_scenario(
        db=db,
        symbol=req.symbol.upper(),
        model_id=req.model_id,
        market_return_delta=req.market_return_delta,
        volume_delta_pct=req.volume_delta_pct,
        volatility_delta_pct=req.volatility_delta_pct,
        momentum_delta_pct=req.momentum_delta_pct
    )
    return result
