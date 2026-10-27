from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ExplainRequest(BaseModel):
    symbol: str = Field(...)
    model_id: Optional[str] = Field(None)

class ShapWaterfallItem(BaseModel):
    feature: str
    feature_value: float
    shap_value: float
    impact: str
    abs_impact: float

class GlobalImportanceItem(BaseModel):
    feature: str
    importance: float
    percentage: float

class ExplainResponse(BaseModel):
    symbol: str
    company_name: str
    model_metadata: Dict[str, Any]
    data_cutoff: str
    global_feature_importance: List[GlobalImportanceItem]
    shap_waterfall: List[ShapWaterfallItem]
    base_value: float
    partial_dependence: Dict[str, List[Dict[str, float]]]
    natural_language_summary: str
