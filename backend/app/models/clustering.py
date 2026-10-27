import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from app.models.base import BaseModel

REGIME_LABELS = {
    0: "Low Volatility / Steady Trend",
    1: "High Volatility / Expansion",
    2: "High Momentum / Breakout",
    3: "Heavy Volume / Distribution"
}

class KMeansRegimeModel(BaseModel):
    def __init__(self, n_clusters: int = 4, random_state: int = 42):
        super().__init__(
            name="K-Means Regime Clustering",
            task_type="unsupervised",
            hyperparameters={"n_clusters": n_clusters, "random_state": random_state}
        )
        self.scaler = StandardScaler()
        self.model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)

    def train(self, X_train: pd.DataFrame, y_train: Optional[pd.Series] = None, X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None) -> Dict[str, Any]:
        self.feature_names = list(X_train.columns)
        X_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_scaled)
        self.is_trained = True

        cluster_counts = pd.Series(self.model.labels_).value_counts().to_dict()
        inertia = float(self.model.inertia_)

        return {
            "n_clusters": self.hyperparameters["n_clusters"],
            "inertia": round(inertia, 2),
            "cluster_distribution": cluster_counts
        }

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def evaluate(self, X_test: pd.DataFrame, y_test: Optional[pd.Series] = None) -> Dict[str, Any]:
        preds = self.predict(X_test)
        counts = pd.Series(preds).value_counts().to_dict()
        return {
            "inertia": round(float(self.model.inertia_), 2),
            "cluster_counts": counts,
            "regime_labels": REGIME_LABELS
        }
