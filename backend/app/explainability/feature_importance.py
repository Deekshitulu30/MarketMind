from typing import Dict, List, Any
import numpy as np
import pandas as pd
from app.models.base import BaseModel

def get_global_feature_importance(model_instance: BaseModel) -> List[Dict[str, Any]]:
    """
    Returns global feature importance ranked in descending order.
    """
    importances = model_instance.get_feature_importance()
    if not importances:
        return []

    ranked = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    return [
        {
            "feature": k,
            "importance": round(float(v), 4),
            "percentage": round(float(v * 100), 2)
        }
        for k, v in ranked
    ]
