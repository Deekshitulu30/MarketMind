import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
from app.models.base import BaseModel

class MajorityClassBaseline(BaseModel):
    def __init__(self):
        super().__init__(name="Majority Class Baseline", task_type="classification")
        self.majority_class: int = 1
        self.majority_proba: float = 0.5

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None) -> Dict[str, Any]:
        self.feature_names = list(X_train.columns)
        counts = y_train.value_counts(normalize=True)
        self.majority_class = int(counts.idxmax())
        self.majority_proba = float(counts.max())
        self.is_trained = True
        return {"majority_class": self.majority_class, "majority_probability": self.majority_proba}

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return np.full(len(X), self.majority_class)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        prob_down = 1.0 - self.majority_proba if self.majority_class == 1 else self.majority_proba
        prob_up = self.majority_proba if self.majority_class == 1 else 1.0 - self.majority_proba
        return np.tile([prob_down, prob_up], (len(X), 1))

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        preds = self.predict(X_test)
        acc = float(accuracy_score(y_test, preds))
        cm = confusion_matrix(y_test, preds).tolist()
        return {
            "accuracy": round(acc, 4),
            "precision": round(float(precision_score(y_test, preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, preds, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, preds, zero_division=0)), 4),
            "confusion_matrix": cm,
            "is_baseline": True
        }

class HistoricalMeanRegressorBaseline(BaseModel):
    def __init__(self):
        super().__init__(name="Historical Mean Baseline", task_type="regression")
        self.mean_return: float = 0.0

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None) -> Dict[str, Any]:
        self.feature_names = list(X_train.columns)
        self.mean_return = float(y_train.mean())
        self.is_trained = True
        return {"mean_return": self.mean_return}

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return np.full(len(X), self.mean_return)

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        preds = self.predict(X_test)
        mae = float(mean_absolute_error(y_test, preds))
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        r2 = float(r2_score(y_test, preds))
        return {
            "mae": round(mae, 6),
            "rmse": round(rmse, 6),
            "r2_score": round(r2, 4),
            "is_baseline": True
        }
