import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, List

def compute_descriptive_stats(series: pd.Series) -> Dict[str, Any]:
    """
    Computes rigorous descriptive metrics and dispersion statistics for a given numerical series.
    """
    clean_s = series.dropna()
    if clean_s.empty:
        return {}

    values = clean_s.values
    mean_val = float(np.mean(values))
    median_val = float(np.median(values))
    var_val = float(np.var(values, ddof=1)) if len(values) > 1 else 0.0
    std_val = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
    min_val = float(np.min(values))
    max_val = float(np.max(values))
    range_val = max_val - min_val

    # Mode calculation
    mode_res = stats.mode(values, keepdims=False)
    mode_val = float(mode_res.mode) if isinstance(mode_res.mode, (int, float, np.number)) else float(mode_res.mode[0]) if len(mode_res.mode) > 0 else mean_val

    # Quartiles & IQR
    q25 = float(np.percentile(values, 25))
    q75 = float(np.percentile(values, 75))
    iqr = q75 - q25

    # Skewness & Kurtosis
    skew_val = float(stats.skew(values)) if len(values) > 2 else 0.0
    kurt_val = float(stats.kurtosis(values)) if len(values) > 3 else 0.0

    # Outliers via IQR
    lower_bound = q25 - 1.5 * iqr
    upper_bound = q75 + 1.5 * iqr
    outliers_count = int(np.sum((values < lower_bound) | (values > upper_bound)))

    return {
        "count": int(len(values)),
        "mean": round(mean_val, 6),
        "median": round(median_val, 6),
        "mode": round(mode_val, 6),
        "variance": round(var_val, 8),
        "std_dev": round(std_val, 6),
        "min": round(min_val, 6),
        "max": round(max_val, 6),
        "range": round(range_val, 6),
        "q25": round(q25, 6),
        "q75": round(q75, 6),
        "iqr": round(iqr, 6),
        "skewness": round(skew_val, 4),
        "kurtosis": round(kurt_val, 4),
        "outliers_count": outliers_count,
        "outliers_pct": round((outliers_count / len(values)) * 100, 2)
    }
