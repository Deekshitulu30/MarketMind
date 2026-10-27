import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

def calculate_true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """
    Computes standard True Range (TR) for each period:
    TR = max(High - Low, abs(High - Prior Close), abs(Low - Prior Close))
    """
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
    """
    Computes Average True Range (ATR) over a specified rolling window (default 14 periods).
    """
    if len(close) < 2:
        return 0.0
    
    tr = calculate_true_range(high, low, close)
    # 14-day simple rolling mean of TR (or available periods if fewer)
    window = min(period, len(tr))
    atr_series = tr.rolling(window=window, min_periods=1).mean()
    val = atr_series.iloc[-1]
    return float(val) if not np.isnan(val) else 0.0

def compute_model_reference_levels(
    last_close: float,
    expected_return: float,
    predicted_direction: str,
    atr_value: float,
    k_target_multiplier: float = 1.5,
    m_stoploss_multiplier: float = 1.0,
    model_version: str = "v1.0-ensemble",
    confidence_pct: float = 65.0
) -> Dict[str, Any]:
    """
    Calculates model-derived educational reference levels based on ATR volatility bounds.
    
    CRITICAL REGULATORY FRAMING COMPLIANCE:
    - Never frames values as financial advice or trade signals.
    - Uses exact labels: 'Model Reference Stop-Loss (educational)' and 'Model Reference Target (educational)'.
    - Visually and structurally binds model version, confidence %, multipliers, and mandatory disclaimer.
    """
    predicted_price = round(last_close * (1.0 + expected_return), 2)
    direction_upper = predicted_direction.upper()

    if direction_upper == "UP":
        ref_target = round(predicted_price + (k_target_multiplier * atr_value), 2)
        ref_stop_loss = round(predicted_price - (m_stoploss_multiplier * atr_value), 2)
    else:  # DOWN
        ref_target = round(predicted_price - (k_target_multiplier * atr_value), 2)
        ref_stop_loss = round(predicted_price + (m_stoploss_multiplier * atr_value), 2)

    risk_buffer = round(m_stoploss_multiplier * atr_value, 2)
    target_buffer = round(k_target_multiplier * atr_value, 2)
    risk_reward_ratio = round(k_target_multiplier / m_stoploss_multiplier, 2) if m_stoploss_multiplier > 0 else 1.5

    return {
        "is_educational_reference": True,
        "model_version": model_version,
        "confidence_pct": confidence_pct,
        "direction": direction_upper,
        "last_close": round(last_close, 2),
        "expected_return_pct": round(expected_return * 100, 2),
        "predicted_price": predicted_price,
        "atr_14": round(atr_value, 2),
        "multipliers": {
            "target_k": k_target_multiplier,
            "stop_loss_m": m_stoploss_multiplier
        },
        "reference_target": {
            "label": "Model Reference Target (educational)",
            "value": ref_target,
            "buffer": target_buffer,
            "formula": f"Predicted Price {'+' if direction_upper == 'UP' else '-'} ({k_target_multiplier} × ATR)"
        },
        "reference_stop_loss": {
            "label": "Model Reference Stop-Loss (educational)",
            "value": ref_stop_loss,
            "buffer": risk_buffer,
            "formula": f"Predicted Price {'-' if direction_upper == 'UP' else '+'} ({m_stoploss_multiplier} × ATR)"
        },
        "risk_reward_ratio": risk_reward_ratio,
        "mandatory_disclaimer": "Derived from historical volatility and model output. Not a recommendation to buy, sell, or hold.",
        "methodology": {
            "technique": "Average True Range (ATR) Statistical Volatility Banding",
            "atr_period": 14,
            "formula_description": (
                f"True Range captures maximum intraday and gap dispersion. "
                f"Reference Target uses +{k_target_multiplier}×ATR for UP (or -{k_target_multiplier}×ATR for DOWN) "
                f"and Reference Stop-Loss uses -{m_stoploss_multiplier}×ATR for UP (or +{m_stoploss_multiplier}×ATR for DOWN) "
                f"anchored at the predicted price."
            ),
            "purpose": "Educational illustration of volatility-adjusted statistical dispersion framing."
        }
    }
