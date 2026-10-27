import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from app.models.base import BaseModel

class LinearRegressionModel(BaseModel):
    def __init__(self, fit_intercept: bool = True):
        super().__init__(
            name="Linear Regression",
            task_type="regression",
            hyperparameters={"fit_intercept": fit_intercept}
        )
        self.scaler = StandardScaler()
        self.model = LinearRegression(fit_intercept=fit_intercept)

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None) -> Dict[str, Any]:
        self.feature_names = list(X_train.columns)
        X_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_scaled, y_train)
        self.is_trained = True
        return {"features_count": len(self.feature_names), "train_samples": len(X_train)}

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        preds = self.predict(X_test)
        mae = float(mean_absolute_error(y_test, preds))
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        r2 = float(r2_score(y_test, preds))
        return {
            "mae": round(mae, 6),
            "rmse": round(rmse, 6),
            "r2_score": round(r2, 4)
        }

    def get_feature_importance(self) -> Dict[str, float]:
        if not self.is_trained:
            return {}
        coefs = np.abs(self.model.coef_)
        total = np.sum(coefs) if np.sum(coefs) > 0 else 1.0
        normalized = (coefs / total).round(4)
        return dict(zip(self.feature_names, normalized.tolist()))

class RandomForestRegressorModel(BaseModel):
    def __init__(self, n_estimators: int = 100, max_depth: int = 6, random_state: int = 42):
        super().__init__(
            name="Random Forest Regressor",
            task_type="regression",
            hyperparameters={"n_estimators": n_estimators, "max_depth": max_depth, "random_state": random_state}
        )
        self.scaler = None
        self.model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=random_state)

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None) -> Dict[str, Any]:
        self.feature_names = list(X_train.columns)
        self.model.fit(X_train, y_train)
        self.is_trained = True
        return {"features_count": len(self.feature_names), "train_samples": len(X_train)}

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict(X)

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        preds = self.predict(X_test)
        mae = float(mean_absolute_error(y_test, preds))
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        r2 = float(r2_score(y_test, preds))
        return {
            "mae": round(mae, 6),
            "rmse": round(rmse, 6),
            "r2_score": round(r2, 4)
        }

    def get_feature_importance(self) -> Dict[str, float]:
        if not self.is_trained:
            return {}
        importances = self.model.feature_importances_.round(4)
        return dict(zip(self.feature_names, importances.tolist()))
