import pytest
import numpy as np
import pandas as pd
from app.statistics.descriptive import compute_descriptive_stats
from app.statistics.distributions import compute_return_series, analyze_return_distribution
from app.statistics.hypothesis import run_hypothesis_test

def test_descriptive_statistics():
    series = pd.Series([100.0, 102.0, 101.0, 105.0, 103.0, 107.0, 106.0])
    stats = compute_descriptive_stats(series)

    assert stats["count"] == 7
    assert np.isclose(stats["mean"], 103.428571, atol=1e-4)
    assert stats["min"] == 100.0
    assert stats["max"] == 107.0
    assert stats["range"] == 7.0
    assert stats["std_dev"] > 0

def test_return_calculations():
    prices = pd.Series([100.0, 105.0, 102.0])
    res = compute_return_series(prices)

    pct_ret = res["pct_returns"]
    log_ret = res["log_returns"]

    assert len(pct_ret) == 2
    assert np.isclose(pct_ret.iloc[0], 0.05)  # (105-100)/100 = 5%
    assert np.isclose(pct_ret.iloc[1], -0.028571, atol=1e-4)  # (102-105)/105 = -2.857%
    assert np.isclose(log_ret.iloc[0], np.log(1.05))

def test_distribution_analysis():
    returns = pd.Series(np.random.normal(0.001, 0.02, 500))
    dist = analyze_return_distribution(returns, bins_count=20)

    assert "mean_daily_return" in dist
    assert "annualized_volatility" in dist
    assert "prob_positive_pct" in dist
    assert "prob_negative_pct" in dist
    assert len(dist["histogram_bins"]) == 20
    assert len(dist["fitted_normal_curve"]) > 0

def test_hypothesis_test_two_sample():
    np.random.seed(42)
    sample_a = pd.Series(np.random.normal(0.02, 0.01, 100))
    sample_b = pd.Series(np.random.normal(-0.01, 0.01, 100))

    result = run_hypothesis_test(sample_a, sample_b, label_a="Regime A", label_b="Regime B", alpha=0.05)

    assert result["reject_null"] is True
    assert result["p_value"] < 0.001
    assert "Reject H0" in result["decision"]
