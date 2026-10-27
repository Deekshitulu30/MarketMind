import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

class PCAModel:
    """
    Principal Component Analysis for feature space dimensionality reduction and 2D/3D visualization.
    """
    def __init__(self, n_components: int = 2):
        self.n_components = n_components
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=n_components)
        self.feature_names: List[str] = []
        self.is_fitted: bool = False

    def fit_transform(self, X: pd.DataFrame) -> Dict[str, Any]:
        self.feature_names = list(X.columns)
        X_scaled = self.scaler.fit_transform(X)
        coords = self.pca.fit_transform(X_scaled)
        self.is_fitted = True

        explained_variance = [round(float(v), 4) for v in self.pca.explained_variance_ratio_]
        total_explained = round(float(np.sum(explained_variance)), 4)

        points = [
            {
                "pc1": round(float(coords[i, 0]), 4),
                "pc2": round(float(coords[i, 1]), 4),
                "pc3": round(float(coords[i, 2]), 4) if self.n_components >= 3 else 0.0
            }
            for i in range(len(coords))
        ]

        # Top feature loadings on PC1 and PC2
        loadings = []
        for i, feat in enumerate(self.feature_names):
            loadings.append({
                "feature": feat,
                "pc1_loading": round(float(self.pca.components_[0, i]), 4),
                "pc2_loading": round(float(self.pca.components_[1, i]), 4) if self.n_components >= 2 else 0.0
            })

        return {
            "n_components": self.n_components,
            "explained_variance_ratio": explained_variance,
            "total_explained_variance": total_explained,
            "points": points,
            "feature_loadings": loadings
        }
