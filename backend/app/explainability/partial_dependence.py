import numpy as np
import pandas as pd
from typing import Dict, Any, List
from app.models.base import BaseModel

def compute_partial_dependence(
    model_instance: BaseModel,
    X_sample: pd.DataFrame,
    feature_name: str,
    grid_points: int = 15
) -> Dict[str, Any]:
    """
    Computes partial dependence data for a specific feature by marginalizing over the sample dataset.
    """
    if feature_name not in X_sample.columns:
        return {"feature": feature_name, "points": []}

    f_values = X_sample[feature_name].dropna().values
    if len(f_values) == 0:
        return {"feature": feature_name, "points": []}

    f_min = float(np.percentile(f_values, 5))
    f_max = float(np.percentile(f_values, 95))
    grid = np.linspace(f_min, f_max, grid_points)

    points: List[Dict[str, float]] = []
    
    for val in grid:
        X_temp = X_sample.copy()
        X_temp[feature_name] = val
        
        probas = model_instance.predict_proba(X_temp)
        if probas is not None:
            avg_prob = float(np.mean(probas[:, 1]))
        else:
            preds = model_instance.predict(X_temp)
            avg_prob = float(np.mean(preds))

        points.append({
            "feature_value": round(float(val), 4),
            "predicted_probability": round(avg_prob, 4)
        })

    return {
        "feature": feature_name,
        "points": points
    }
