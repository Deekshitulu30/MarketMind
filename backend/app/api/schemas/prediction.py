from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    symbol: str = Field(...)
    model_id: Optional[str] = Field(None)
    horizon: int = Field(1, ge=1, le=30)

class RiskProfile(BaseModel):
    risk_level: str
    description: str
    daily_volatility: float
    annualized_volatility: float
    annualized_downside_volatility: float
    max_drawdown_pct: float
    var_95_daily_pct: float
    var_99_daily_pct: float
    disclaimer: str

class PredictResponse(BaseModel):
    prediction_id: str
    symbol: str
    ticker: Optional[str] = None
    company_name: str
    current_price: float
    data_cutoff: str
    prediction_generated_at: str
    horizon_days: int
    predicted_direction: str
    probability_up_pct: float
    probability_up: Optional[float] = None
    confidence_pct: float
    confidence_score: Optional[float] = None
    expected_return_pct: float
    predicted_price: float
    latency_ms: Optional[float] = None
    features: Optional[Dict[str, Any]] = None
    shap_values: Optional[Dict[str, Any]] = None
    risk_profile: RiskProfile
    reference_levels: Optional[Dict[str, Any]] = None
    model_metadata: Dict[str, Any]
    disclaimer: str

    model_config = {"extra": "allow"}

