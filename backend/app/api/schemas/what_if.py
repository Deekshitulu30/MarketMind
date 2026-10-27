from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class WhatIfRequest(BaseModel):
    symbol: str = Field(...)
    model_id: Optional[str] = Field(None)
    market_return_delta: float = Field(0.0, ge=-0.15, le=0.15)
    volume_delta_pct: float = Field(0.0, ge=-0.80, le=0.80)
    volatility_delta_pct: float = Field(0.0, ge=-0.80, le=0.80)
    momentum_delta_pct: float = Field(0.0, ge=-0.80, le=0.80)

class ScenarioOutput(BaseModel):
    predicted_direction: str
    probability_up_pct: float
    expected_return_pct: float
    risk_level: str

class WhatIfComparison(BaseModel):
    probability_up_delta_pct: float
    expected_return_delta_pct: float
    direction_shifted: bool

class WhatIfResponse(BaseModel):
    symbol: str
    company_name: str
    data_cutoff: str
    model_metadata: Dict[str, Any]
    scenario_inputs: Dict[str, float]
    baseline: ScenarioOutput
    scenario: ScenarioOutput
    comparison: WhatIfComparison
    assumptions: List[str]
    disclaimer: str
