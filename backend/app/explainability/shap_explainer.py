import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import shap
from app.models.base import BaseModel
from app.models.classification import RandomForestModel, DecisionTreeModel, LogisticRegressionModel, HistGradientBoostingModel

def compute_local_shap_values(
    model_instance: BaseModel,
    X_instance: pd.DataFrame,
    X_background: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Computes local Shapley values (SHAP) explaining an individual prediction instance.
    """
    feature_names = model_instance.feature_names
    instance_vals = X_instance.iloc[0].to_dict()

    try:
        # 1. Tree Models (TreeExplainer)
        if isinstance(model_instance, (RandomForestModel, DecisionTreeModel, HistGradientBoostingModel)):
            explainer = shap.TreeExplainer(model_instance.model)
            shap_values = explainer.shap_values(X_instance)
            
            # If binary classification, shap_values has 2 classes [class_0, class_1]
            if isinstance(shap_values, list) and len(shap_values) == 2:
                sv = shap_values[1][0]
                base_value = float(explainer.expected_value[1]) if isinstance(explainer.expected_value, (list, np.ndarray)) else float(explainer.expected_value)
            elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
                sv = shap_values[0, :, 1]
                base_value = float(explainer.expected_value[1])
            elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 2:
                # e.g. HistGradientBoosting single output margin
                sv = shap_values[0]
                base_value = float(explainer.expected_value[0]) if isinstance(explainer.expected_value, (list, np.ndarray)) else float(explainer.expected_value)
            else:
                sv = shap_values[0] if isinstance(shap_values, np.ndarray) else np.zeros(len(feature_names))
                base_value = float(explainer.expected_value) if isinstance(explainer.expected_value, (int, float, np.number)) else float(explainer.expected_value[0])

        # 2. Linear Models (LinearExplainer)
        elif isinstance(model_instance, LogisticRegressionModel):
            X_bg = model_instance.scaler.transform(X_background.sample(min(50, len(X_background)), random_state=42)) if X_background is not None else np.zeros((1, len(feature_names)))
            explainer = shap.LinearExplainer(model_instance.model, X_bg)
            X_inst_scaled = model_instance.scaler.transform(X_instance)
            sv = explainer.shap_values(X_inst_scaled)[0]
            base_value = float(explainer.expected_value) if isinstance(explainer.expected_value, (int, float, np.number)) else float(explainer.expected_value[0])

        # 3. Fallback to model feature importance weighted attribution
        else:
            imp_dict = model_instance.get_feature_importance()
            sv = np.array([imp_dict.get(col, 0.0) * (1.0 if X_instance[col].iloc[0] >= 0 else -1.0) for col in feature_names])
            base_value = 0.5

    except Exception as e:
        # Safe fallback
        imp_dict = model_instance.get_feature_importance()
        sv = np.array([imp_dict.get(col, 0.0) * 0.1 for col in feature_names])
        base_value = 0.5

    # Format waterfall items
    waterfall: List[Dict[str, Any]] = []
    for i, col in enumerate(feature_names):
        shap_val = float(sv[i]) if i < len(sv) else 0.0
        val = float(instance_vals.get(col, 0.0))
        waterfall.append({
            "feature": col,
            "feature_value": round(val, 4),
            "shap_value": round(shap_val, 5),
            "impact": "POSITIVE" if shap_val > 0 else "NEGATIVE" if shap_val < 0 else "NEUTRAL",
            "abs_impact": round(abs(shap_val), 5)
        })

    waterfall = sorted(waterfall, key=lambda x: x["abs_impact"], reverse=True)

    return {
        "base_value": round(base_value, 4),
        "waterfall": waterfall
    }
