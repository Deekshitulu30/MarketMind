import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, List

def compute_correlation_matrix(df_features: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes Pearson and Spearman correlation matrices across numeric features.
    """
    numeric_df = df_features.select_dtypes(include=[np.number]).dropna()
    if numeric_df.empty:
        return {"columns": [], "pearson": [], "spearman": []}

    columns = list(numeric_df.columns)
    pearson_corr = numeric_df.corr(method="pearson").round(4).to_dict(orient="split")
    spearman_corr = numeric_df.corr(method="spearman").round(4).to_dict(orient="split")

    return {
        "columns": columns,
        "pearson_matrix": pearson_corr["data"],
        "spearman_matrix": spearman_corr["data"]
    }

def compute_scatter_regression(
    x_series: pd.Series,
    y_series: pd.Series,
    x_label: str = "X",
    y_label: str = "Y",
    sample_limit: int = 300
) -> Dict[str, Any]:
    """
    Computes bivariate scatter points, OLS regression slope, intercept, p-value, and R-squared.
    """
    combined = pd.DataFrame({x_label: x_series, y_label: y_series}).dropna()
    if len(combined) < 2:
        return {}

    # Sample if too large for smooth plotting
    if len(combined) > sample_limit:
        sample_df = combined.sample(sample_limit, random_state=42).sort_values(x_label)
    else:
        sample_df = combined.sort_values(x_label)

    x_vals = combined[x_label].values
    y_vals = combined[y_label].values

    slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
    r_squared = float(r_value**2)

    # Generate regression line endpoints
    x_min, x_max = float(np.min(x_vals)), float(np.max(x_vals))
    line_points = [
        {"x": round(x_min, 5), "y": round(float(slope * x_min + intercept), 5)},
        {"x": round(x_max, 5), "y": round(float(slope * x_max + intercept), 5)}
    ]

    points = [
        {"x": round(float(r[x_label]), 5), "y": round(float(r[y_label]), 5)}
        for _, r in sample_df.iterrows()
    ]

    return {
        "x_label": x_label,
        "y_label": y_label,
        "slope": round(float(slope), 6),
        "intercept": round(float(intercept), 6),
        "r_value": round(float(r_value), 4),
        "r_squared": round(float(r_squared), 4),
        "p_value": round(float(p_value), 6),
        "std_err": round(float(std_err), 6),
        "scatter_points": points,
        "regression_line": line_points
    }
