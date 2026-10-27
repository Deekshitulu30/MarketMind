import pytest
import numpy as np
import pandas as pd
from app.features.pipeline import FeaturePipeline
from app.data.sample_data import generate_stock_history

def test_no_future_data_in_lag_features():
    """
    Asserts that lag_1_return at index i strictly equals daily_return at index i-1.
    """
    df = generate_stock_history("AAPL", seed=42)
    features_df = FeaturePipeline.generate_features_df(df)

    for i in range(10, len(features_df) - 5):
        lag1 = features_df["lag_1_return"].iloc[i]
        prev_daily = features_df["daily_return"].iloc[i-1]
        assert np.isclose(lag1, prev_daily, rtol=1e-5, atol=1e-5)

def test_rolling_statistics_use_past_data_only():
    """
    Asserts that 5-day rolling mean at index i only depends on rows i-4 to i,
    and has zero dependence on future row i+1.
    """
    df = generate_stock_history("AAPL", seed=42)
    features_df = FeaturePipeline.generate_features_df(df)

    for i in range(15, 25):
        expected_sma5 = features_df["close"].iloc[i-4:i+1].mean()
        actual_sma5 = features_df["rolling_mean_5"].iloc[i]
        assert np.isclose(actual_sma5, expected_sma5, rtol=1e-5, atol=1e-5)

def test_target_direction_does_not_leak_into_current_row_features():
    """
    Asserts that target_direction is computed from close[t+1] vs close[t],
    and that close[t] does not contain future price changes.
    """
    df = generate_stock_history("AAPL", seed=42)
    features_df = FeaturePipeline.generate_features_df(df)

    for i in range(len(features_df) - 2):
        curr_close = features_df["close"].iloc[i]
        next_close = features_df["close"].iloc[i+1]
        expected_target_dir = 1 if next_close > curr_close else 0
        actual_target_dir = features_df["target_direction"].iloc[i]
        assert actual_target_dir == expected_target_dir

def test_latest_row_target_is_nan_before_future_occurs():
    """
    Ensures that the latest timestamp has NaN/unassigned target because future is unknown.
    """
    df = generate_stock_history("AAPL", seed=42)
    features_df = FeaturePipeline.generate_features_df(df)

    last_row = features_df.iloc[-1]
    assert pd.isnull(last_row["target_next_return"])
