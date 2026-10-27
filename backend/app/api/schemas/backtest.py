from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class BacktestRequest(BaseModel):
    symbol: str = Field("AAPL")
    model_name: str = Field("Random Forest Classifier")
    n_folds: int = Field(3, ge=2, le=5)

class FoldResult(BaseModel):
    fold_id: int
    train_period: str
    test_period: str
    train_samples: int
    test_samples: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: List[List[int]]
    strategy_return_pct: float
    benchmark_return_pct: float

class BacktestResponse(BaseModel):
    backtest_id: Optional[str] = None
    symbol: str
    company_name: str
    model_name: str
    strategy: str
    total_folds: int
    summary_metrics: Dict[str, float]
    fold_results: List[FoldResult]
    time_series_evaluation: List[Dict[str, Any]]
