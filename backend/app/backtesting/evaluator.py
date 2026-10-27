import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def evaluate_backtest_predictions(
    dates: pd.Series,
    actual_direction: pd.Series,
    predicted_direction: np.ndarray,
    predicted_proba: Optional[np.ndarray],
    actual_return: pd.Series
) -> Dict[str, Any]:
    """
    Computes out-of-sample prediction metrics, fold confusion matrix,
    error distribution, and model directional strategy return vs buy-and-hold.
    """
    y_true = actual_direction.values
    y_pred = np.array(predicted_direction)
    rets = actual_return.values

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    cm = confusion_matrix(y_true, y_pred).tolist()

    # Strategy Simulation:
    # Go Long if predicted UP (1), Stay in cash (0 return) or Flat if predicted DOWN (0)
    strategy_returns = np.where(y_pred == 1, rets, 0.0)
    
    cum_strategy = np.cumprod(1 + strategy_returns) - 1
    cum_benchmark = np.cumprod(1 + rets) - 1

    series_data = []
    for i in range(len(dates)):
        series_data.append({
            "date": pd.to_datetime(dates.iloc[i]).strftime("%Y-%m-%d"),
            "actual_direction": "UP" if y_true[i] == 1 else "DOWN",
            "predicted_direction": "UP" if y_pred[i] == 1 else "DOWN",
            "probability_up": round(float(predicted_proba[i, 1]), 3) if predicted_proba is not None else 0.5,
            "actual_return_pct": round(float(rets[i] * 100), 2),
            "strategy_cumulative_return_pct": round(float(cum_strategy[i] * 100), 2),
            "benchmark_cumulative_return_pct": round(float(cum_benchmark[i] * 100), 2),
            "is_correct": bool(y_true[i] == y_pred[i])
        })

    total_strategy_return = float(cum_strategy[-1]) if len(cum_strategy) > 0 else 0.0
    total_benchmark_return = float(cum_benchmark[-1]) if len(cum_benchmark) > 0 else 0.0

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": cm,
        "total_strategy_return_pct": round(total_strategy_return * 100, 2),
        "total_benchmark_return_pct": round(total_benchmark_return * 100, 2),
        "series": series_data
    }
