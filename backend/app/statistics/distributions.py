import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, List

def compute_return_series(prices: pd.Series) -> Dict[str, pd.Series]:
    """
    Computes simple percentage returns and log returns.
    """
    clean_p = prices.dropna()
    pct_returns = clean_p.pct_change().dropna()
    log_returns = np.log(clean_p / clean_p.shift(1)).dropna()
    cumulative_returns = (1 + pct_returns).cumprod() - 1

    return {
        "pct_returns": pct_returns,
        "log_returns": log_returns,
        "cumulative_returns": cumulative_returns
    }

def analyze_return_distribution(pct_returns: pd.Series, bins_count: int = 40) -> Dict[str, Any]:
    """
    Analyzes return distribution, histogram bins, empirical probabilities,
    fitted Gaussian curve, and Value at Risk.
    """
    returns = pct_returns.dropna().values
    if len(returns) == 0:
        return {}

    mean_ret = float(np.mean(returns))
    std_ret = float(np.std(returns, ddof=1)) if len(returns) > 1 else 0.0

    # Empirical Probabilities
    prob_positive = float(np.mean(returns > 0)) * 100.0
    prob_negative = float(np.mean(returns < 0)) * 100.0
    prob_zero = float(np.mean(returns == 0)) * 100.0

    # Value at Risk (Historical & Parametric)
    var_95_hist = float(-np.percentile(returns, 5))
    var_99_hist = float(-np.percentile(returns, 1))
    var_95_param = float(-(mean_ret - 1.645 * std_ret))
    var_99_param = float(-(mean_ret - 2.326 * std_ret))

    # Annualized Metrics
    annualized_return = float((1 + mean_ret)**252 - 1) if mean_ret > -1 else -1.0
    annualized_volatility = float(std_ret * np.sqrt(252))
    sharpe_ratio = (annualized_return - 0.04) / annualized_volatility if annualized_volatility > 0 else 0.0

    # Histogram Bins
    hist, bin_edges = np.histogram(returns, bins=bins_count, density=True)
    bins_data: List[Dict[str, float]] = []
    
    # Fitted normal PDF points
    x_pdf = np.linspace(float(np.min(returns)), float(np.max(returns)), 100)
    pdf_curve = stats.norm.pdf(x_pdf, loc=mean_ret, scale=std_ret) if std_ret > 0 else np.zeros_like(x_pdf)

    for i in range(len(hist)):
        bin_center = (bin_edges[i] + bin_edges[i+1]) / 2.0
        bins_data.append({
            "bin_start": round(float(bin_edges[i]), 5),
            "bin_end": round(float(bin_edges[i+1]), 5),
            "bin_center": round(float(bin_center), 5),
            "density": round(float(hist[i]), 5),
            "count": int(np.sum((returns >= bin_edges[i]) & (returns < bin_edges[i+1])))
        })

    pdf_points = [
        {"x": round(float(x), 5), "y": round(float(y), 5)}
        for x, y in zip(x_pdf, pdf_curve)
    ]

    return {
        "sample_size": len(returns),
        "mean_return": round(mean_ret, 6),
        "std_return": round(std_ret, 6),
        "mean_daily_return": round(mean_ret, 6),
        "std_daily_return": round(std_ret, 6),
        "mean_log_return": round(float(np.mean(np.log(np.maximum(1 + returns, 1e-6)))), 6),
        "annualized_return": round(annualized_return, 4),
        "annualized_volatility": round(annualized_volatility, 4),
        "sharpe_ratio": round(sharpe_ratio, 4),
        "prob_positive_pct": round(prob_positive, 2),
        "prob_negative_pct": round(prob_negative, 2),
        "prob_zero_pct": round(prob_zero, 2),
        "var_95": round(var_95_hist, 4),
        "var_99": round(var_99_hist, 4),
        "var_95_historical": round(var_95_hist, 4),
        "var_99_historical": round(var_99_hist, 4),
        "var_95_parametric": round(var_95_param, 4),
        "var_99_parametric": round(var_99_param, 4),
        "histogram_bins": bins_data,
        "fitted_normal_curve": pdf_points
    }
