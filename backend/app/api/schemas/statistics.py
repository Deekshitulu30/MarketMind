from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class StatisticsAnalyzeRequest(BaseModel):
    symbol: str = Field(...)
    start_date: Optional[str] = Field(None)
    end_date: Optional[str] = Field(None)

class DescriptiveStats(BaseModel):
    count: int
    mean: float
    median: float
    mode: float
    variance: float
    std_dev: float
    min: float
    max: float
    range: float
    q25: float
    q75: float
    iqr: float
    skewness: float
    kurtosis: float
    outliers_count: int
    outliers_pct: float

class HypothesisTestResult(BaseModel):
    test_name: str
    null_hypothesis: str
    alternative_hypothesis: str
    significance_level: float
    sample_a_label: str
    sample_a_size: int
    sample_a_mean: float
    sample_a_std: float
    sample_b_label: str
    sample_b_size: int
    sample_b_mean: float
    sample_b_std: float
    t_statistic: float
    p_value: float
    reject_null: bool
    decision: str
    interpretation: str

class StatisticsResponse(BaseModel):
    symbol: str
    company_name: str
    period: Dict[str, Any]
    price_summary: DescriptiveStats
    return_summary: DescriptiveStats
    volume_summary: DescriptiveStats
    volatility_summary: DescriptiveStats
    distribution_analysis: Dict[str, Any]
    bivariate_regressions: Dict[str, Any]
    correlation_matrix: Dict[str, Any]
    hypothesis_test: HypothesisTestResult
    time_series: List[Dict[str, Any]]
    descriptive: Optional[Dict[str, Any]] = None
    distribution: Optional[Dict[str, Any]] = None
    correlation: Optional[Dict[str, Any]] = None
