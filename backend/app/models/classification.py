import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, brier_score_loss

from app.models.base import BaseModel

class LogisticRegressionModel(BaseModel):
    def __init__(self, C: float = 1.0, max_iter: int = 1000, random_state: int = 42):
        super().__init__(
            name="Logistic Regression",
            task_type="classification",
            hyperparameters={"C": C, "max_iter": max_iter, "random_state": random_state}
        )
        self.scaler = StandardScaler()
        self.model = LogisticRegression(C=C, max_iter=max_iter, random_state=random_state)

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None) -> Dict[str, Any]:
        self.feature_names = list(X_train.columns)
        # Scaler fitted ONLY on training set
        X_train_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        return {"features_count": len(self.feature_names), "train_samples": len(X_train)}

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        preds = self.predict(X_test)
        probas = self.predict_proba(X_test)[:, 1]
        cm = confusion_matrix(y_test, preds).tolist()
        try:
            auc = float(roc_auc_score(y_test, probas))
        except Exception:
            auc = 0.5
        brier = float(brier_score_loss(y_test, probas))
        return {
            "accuracy": round(float(accuracy_score(y_test, preds)), 4),
            "precision": round(float(precision_score(y_test, preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, preds, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, preds, zero_division=0)), 4),
            "roc_auc": round(auc, 4),
            "brier_score": round(brier, 4),
            "confusion_matrix": cm
        }

    def get_feature_importance(self) -> Dict[str, float]:
        if not self.is_trained:
            return {}
        coefs = np.abs(self.model.coef_[0])
        total = np.sum(coefs) if np.sum(coefs) > 0 else 1.0
        normalized = (coefs / total).round(4)
        return dict(zip(self.feature_names, normalized.tolist()))

class SVMModel(BaseModel):
    def __init__(self, C: float = 1.0, kernel: str = "rbf", random_state: int = 42):
        super().__init__(
            name="Support Vector Machine",
            task_type="classification",
            hyperparameters={"C": C, "kernel": kernel, "random_state": random_state}
        )
        self.scaler = StandardScaler()
        self.model = SVC(C=C, kernel=kernel, probability=True, random_state=random_state)

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None) -> Dict[str, Any]:
        self.feature_names = list(X_train.columns)
        X_train_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        return {"features_count": len(self.feature_names), "train_samples": len(X_train)}

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        preds = self.predict(X_test)
        probas = self.predict_proba(X_test)[:, 1]
        cm = confusion_matrix(y_test, preds).tolist()
        try:
            auc = float(roc_auc_score(y_test, probas))
        except Exception:
            auc = 0.5
        brier = float(brier_score_loss(y_test, probas))
        return {
            "accuracy": round(float(accuracy_score(y_test, preds)), 4),
            "precision": round(float(precision_score(y_test, preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, preds, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, preds, zero_division=0)), 4),
            "roc_auc": round(auc, 4),
            "brier_score": round(brier, 4),
            "confusion_matrix": cm
        }

class DecisionTreeModel(BaseModel):
    def __init__(self, max_depth: int = 5, min_samples_split: int = 10, random_state: int = 42):
        super().__init__(
            name="Decision Tree",
            task_type="classification",
            hyperparameters={"max_depth": max_depth, "min_samples_split": min_samples_split, "random_state": random_state}
        )
        self.scaler = None
        self.model = DecisionTreeClassifier(max_depth=max_depth, min_samples_split=min_samples_split, random_state=random_state)

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None) -> Dict[str, Any]:
        self.feature_names = list(X_train.columns)
        self.model.fit(X_train, y_train)
        self.is_trained = True
        return {"features_count": len(self.feature_names), "train_samples": len(X_train)}

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict_proba(X)

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        preds = self.predict(X_test)
        probas = self.predict_proba(X_test)[:, 1]
        cm = confusion_matrix(y_test, preds).tolist()
        try:
            auc = float(roc_auc_score(y_test, probas))
        except Exception:
            auc = 0.5
        brier = float(brier_score_loss(y_test, probas))
        return {
            "accuracy": round(float(accuracy_score(y_test, preds)), 4),
            "precision": round(float(precision_score(y_test, preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, preds, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, preds, zero_division=0)), 4),
            "roc_auc": round(auc, 4),
            "brier_score": round(brier, 4),
            "confusion_matrix": cm
        }

    def get_feature_importance(self) -> Dict[str, float]:
        if not self.is_trained:
            return {}
        importances = self.model.feature_importances_.round(4)
        return dict(zip(self.feature_names, importances.tolist()))

class RandomForestModel(BaseModel):
    def __init__(self, n_estimators: int = 100, max_depth: int = 6, random_state: int = 42):
        super().__init__(
            name="Random Forest Classifier",
            task_type="classification",
            hyperparameters={"n_estimators": n_estimators, "max_depth": max_depth, "random_state": random_state}
        )
        self.scaler = None
        self.model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=random_state)

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None) -> Dict[str, Any]:
        self.feature_names = list(X_train.columns)
        self.model.fit(X_train, y_train)
        self.is_trained = True
        return {"features_count": len(self.feature_names), "train_samples": len(X_train)}

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict_proba(X)

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        preds = self.predict(X_test)
        probas = self.predict_proba(X_test)[:, 1]
        cm = confusion_matrix(y_test, preds).tolist()
        try:
            auc = float(roc_auc_score(y_test, probas))
        except Exception:
            auc = 0.5
        brier = float(brier_score_loss(y_test, probas))
        return {
            "accuracy": round(float(accuracy_score(y_test, preds)), 4),
            "precision": round(float(precision_score(y_test, preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, preds, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, preds, zero_division=0)), 4),
            "roc_auc": round(auc, 4),
            "brier_score": round(brier, 4),
            "confusion_matrix": cm
        }

    def get_feature_importance(self) -> Dict[str, float]:
        if not self.is_trained:
            return {}
        importances = self.model.feature_importances_.round(4)
        return dict(zip(self.feature_names, importances.tolist()))


class HistGradientBoostingModel(BaseModel):
    """
    MarketMind Core Predictive Engine: Histogram Gradient Boosting Classifier.
    Discretizes continuous tabular features into 256 integer-based bins for fast (<50ms)
    inference, robust noise filtration, and native missing-value tolerance.
    """
    def __init__(
        self,
        max_iter: int = 100,
        max_leaf_nodes: int = 31,
        min_samples_leaf: int = 20,
        learning_rate: float = 0.1,
        random_state: int = 42
    ):
        super().__init__(
            name="Histogram Gradient Boosting",
            task_type="classification",
            hyperparameters={
                "max_iter": max_iter,
                "max_leaf_nodes": max_leaf_nodes,
                "min_samples_leaf": min_samples_leaf,
                "learning_rate": learning_rate,
                "random_state": random_state
            }
        )
        self.scaler = None
        self.model = HistGradientBoostingClassifier(
            max_iter=max_iter,
            max_leaf_nodes=max_leaf_nodes,
            min_samples_leaf=min_samples_leaf,
            learning_rate=learning_rate,
            random_state=random_state
        )
        self._feature_importances: Dict[str, float] = {}

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        self.feature_names = list(X_train.columns)
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Compute normalized permutation feature importances
        try:
            eval_X = X_val if X_val is not None and len(X_val) > 0 else X_train
            eval_y = y_val if y_val is not None and len(y_val) > 0 else y_train
            perm = permutation_importance(self.model, eval_X, eval_y, n_repeats=5, random_state=42)
            raw_imp = np.maximum(0, perm.importances_mean)
            total = np.sum(raw_imp) if np.sum(raw_imp) > 0 else 1.0
            norm_imp = (raw_imp / total).round(4)
            self._feature_importances = dict(zip(self.feature_names, norm_imp.tolist()))
        except Exception:
            self._feature_importances = {col: round(1.0 / len(self.feature_names), 4) for col in self.feature_names}

        return {"features_count": len(self.feature_names), "train_samples": len(X_train)}

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict(X[self.feature_names] if self.feature_names else X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict_proba(X[self.feature_names] if self.feature_names else X)

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        preds = self.predict(X_test)
        probas = self.predict_proba(X_test)[:, 1]
        cm = confusion_matrix(y_test, preds).tolist()
        try:
            auc = float(roc_auc_score(y_test, probas))
        except Exception:
            auc = 0.5
        brier = float(brier_score_loss(y_test, probas))
        return {
            "accuracy": round(float(accuracy_score(y_test, preds)), 4),
            "precision": round(float(precision_score(y_test, preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, preds, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, preds, zero_division=0)), 4),
            "roc_auc": round(auc, 4),
            "brier_score": round(brier, 4),
            "confusion_matrix": cm
        }

    def get_feature_importance(self) -> Dict[str, float]:
        if not self.is_trained:
            return {}
        return self._feature_importances

