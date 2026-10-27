import pytest
import pandas as pd
import numpy as np
from app.risk.reference_levels import (
    calculate_true_range,
    calculate_atr,
    compute_model_reference_levels
)

def test_true_range_calculation():
    # Hand-crafted test dataset
    highs = pd.Series([105.0, 110.0, 115.0])
    lows = pd.Series([95.0, 98.0, 106.0])
    closes = pd.Series([100.0, 108.0, 112.0])

    tr = calculate_true_range(highs, lows, closes)

    # Day 0 (no prev close): TR = High - Low = 105 - 95 = 10
    assert tr.iloc[0] == 10.0

    # Day 1: prev_close = 100.0. TR = max(110-98, |110-100|, |98-100|) = max(12, 10, 2) = 12.0
    assert tr.iloc[1] == 12.0

    # Day 2: prev_close = 108.0. TR = max(115-106, |115-108|, |106-108|) = max(9, 7, 2) = 9.0
    assert tr.iloc[2] == 9.0

def test_atr_calculation():
    highs = pd.Series([105.0, 110.0, 115.0])
    lows = pd.Series([95.0, 98.0, 106.0])
    closes = pd.Series([100.0, 108.0, 112.0])

    # 2-period ATR at index 2 = mean(12.0, 9.0) = 10.5
    atr_2 = calculate_atr(highs, lows, closes, period=2)
    assert atr_2 == 10.5

def test_hand_calculated_up_reference_levels():
    """
    Hand-calculated UP Scenario:
    Last Close = 100.0
    Expected Return = +0.05 (+5%)
    Predicted Price = 105.00
    ATR = 4.00
    k (Target Multiplier) = 1.5
    m (Stop-Loss Multiplier) = 1.0

    Expected:
    Reference Target = 105.0 + (1.5 * 4.0) = 111.00
    Reference Stop-Loss = 105.0 - (1.0 * 4.0) = 101.00
    """
    result = compute_model_reference_levels(
        last_close=100.0,
        expected_return=0.05,
        predicted_direction="UP",
        atr_value=4.0,
        k_target_multiplier=1.5,
        m_stoploss_multiplier=1.0,
        model_version="v2.1-rf-classifier",
        confidence_pct=72.5
    )

    assert result["predicted_price"] == 105.00
    assert result["direction"] == "UP"
    assert result["confidence_pct"] == 72.5
    assert result["model_version"] == "v2.1-rf-classifier"

    # Mandatory Framing Assertions
    assert result["reference_target"]["label"] == "Model Reference Target (educational)"
    assert result["reference_target"]["value"] == 111.00

    assert result["reference_stop_loss"]["label"] == "Model Reference Stop-Loss (educational)"
    assert result["reference_stop_loss"]["value"] == 101.00

    assert "Derived from historical volatility and model output. Not a recommendation to buy, sell, or hold." in result["mandatory_disclaimer"]
    assert result["multipliers"]["target_k"] == 1.5
    assert result["multipliers"]["stop_loss_m"] == 1.0

def test_hand_calculated_down_reference_levels():
    """
    Hand-calculated DOWN Scenario:
    Last Close = 200.0
    Expected Return = -0.04 (-4%)
    Predicted Price = 192.00
    ATR = 6.00
    k (Target Multiplier) = 1.5
    m (Stop-Loss Multiplier) = 1.0

    Expected:
    Reference Target = 192.0 - (1.5 * 6.0) = 183.00
    Reference Stop-Loss = 192.0 + (1.0 * 6.0) = 198.00
    """
    result = compute_model_reference_levels(
        last_close=200.0,
        expected_return=-0.04,
        predicted_direction="DOWN",
        atr_value=6.0,
        k_target_multiplier=1.5,
        m_stoploss_multiplier=1.0
    )

    assert result["predicted_price"] == 192.00
    assert result["direction"] == "DOWN"
    assert result["reference_target"]["value"] == 183.00
    assert result["reference_stop_loss"]["value"] == 198.00
    assert result["reference_target"]["label"] == "Model Reference Target (educational)"
    assert result["reference_stop_loss"]["label"] == "Model Reference Stop-Loss (educational)"
