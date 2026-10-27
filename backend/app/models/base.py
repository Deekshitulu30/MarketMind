from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import joblib

class BaseModel(ABC):
    """
    Abstract Base Class for all MarketMind Machine Learning models.
    Enforces unified interfaces for training, inference, evaluation, explainability, and persistence.
    """
    def __init__(self, name: str, task_type: str, hyperparameters: Optional[Dict[str, Any]] = None):
        self.name = name
        self.task_type = task_type  # 'classification' or 'regression' or 'unsupervised'
        self.hyperparameters = hyperparameters or {}
        self.model: Any = None
        self.scaler: Any = None
        self.feature_names: List[str] = []
        self.is_trained: bool = False

    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None) -> Dict[str, Any]:
        """Trains model and fits preprocessing scalers ONLY on training data."""
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generates predictions."""
        pass

    def predict_proba(self, X: pd.DataFrame) -> Optional[np.ndarray]:
        """Generates class probabilities if classification model."""
        return None

    @abstractmethod
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        """Evaluates model performance metrics on test set."""
        pass

    def get_feature_importance(self) -> Dict[str, float]:
        """Returns normalized feature importance dictionary if supported by model."""
        return {}

    def save(self, filepath: Path) -> str:
        """Serializes model, scaler, and metadata to disk."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "name": self.name,
            "task_type": self.task_type,
            "hyperparameters": self.hyperparameters,
            "model": self.model,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "is_trained": self.is_trained
        }
        joblib.dump(payload, filepath)
        return str(filepath)

    def load(self, filepath: Path):
        """Deserializes model artifact from disk."""
        payload = joblib.load(filepath)
        self.name = payload["name"]
        self.task_type = payload["task_type"]
        self.hyperparameters = payload["hyperparameters"]
        self.model = payload["model"]
        self.scaler = payload["scaler"]
        self.feature_names = payload["feature_names"]
        self.is_trained = payload["is_trained"]
