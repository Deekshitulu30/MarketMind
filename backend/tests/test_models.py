import pytest
import numpy as np
import pandas as pd
from app.models.classification import LogisticRegressionModel, SVMModel, DecisionTreeModel, RandomForestModel
from app.models.regression import LinearRegressionModel, RandomForestRegressorModel
from app.models.baseline import MajorityClassBaseline, HistoricalMeanRegressorBaseline
from app.models.clustering import KMeansRegimeModel

@pytest.fixture
def sample_train_test_data():
    np.random.seed(42)
    n = 200
    X = pd.DataFrame({
        "feat1": np.random.randn(n),
        "feat2": np.random.randn(n),
        "feat3": np.random.randn(n)
    })
    y_cls = pd.Series((X["feat1"] + X["feat2"] > 0).astype(int))
    y_reg = pd.Series(X["feat1"] * 0.5 + X["feat2"] * 0.3 + np.random.normal(0, 0.1, n))

    X_train, X_test = X.iloc[:150], X.iloc[150:]
    y_cls_train, y_cls_test = y_cls.iloc[:150], y_cls.iloc[150:]
    y_reg_train, y_reg_test = y_reg.iloc[:150], y_reg.iloc[150:]

    return X_train, X_test, y_cls_train, y_cls_test, y_reg_train, y_reg_test

def test_majority_class_baseline(sample_train_test_data):
    X_train, X_test, y_cls_train, y_cls_test, _, _ = sample_train_test_data
    baseline = MajorityClassBaseline()
    baseline.train(X_train, y_cls_train)
    metrics = baseline.evaluate(X_test, y_cls_test)

    assert "accuracy" in metrics
    assert metrics["is_baseline"] is True

def test_classification_models(sample_train_test_data):
    X_train, X_test, y_cls_train, y_cls_test, _, _ = sample_train_test_data
    models = [
        LogisticRegressionModel(),
        SVMModel(),
        DecisionTreeModel(),
        RandomForestModel()
    ]

    for model in models:
        model.train(X_train, y_cls_train)
        metrics = model.evaluate(X_test, y_cls_test)
        assert metrics["accuracy"] >= 0.0
        assert metrics["f1_score"] >= 0.0
        assert "confusion_matrix" in metrics

def test_regression_models(sample_train_test_data):
    X_train, X_test, _, _, y_reg_train, y_reg_test = sample_train_test_data
    models = [
        LinearRegressionModel(),
        RandomForestRegressorModel()
    ]

    for model in models:
        model.train(X_train, y_reg_train)
        metrics = model.evaluate(X_test, y_reg_test)
        assert metrics["mae"] >= 0.0
        assert metrics["rmse"] >= 0.0

def test_kmeans_clustering(sample_train_test_data):
    X_train, X_test, _, _, _, _ = sample_train_test_data
    kmeans = KMeansRegimeModel(n_clusters=3)
    train_res = kmeans.train(X_train)
    eval_res = kmeans.evaluate(X_test)

    assert train_res["n_clusters"] == 3
    assert "regime_labels" in eval_res
