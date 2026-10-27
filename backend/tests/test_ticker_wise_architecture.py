import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.database.models import PredictionLog, ModelRun
from app.models.classification import HistGradientBoostingModel

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_api_predict_ticker_endpoint(client):
    """
    Validates the primary GET /api/predict/{ticker} endpoint defined in Section 6 & 9.
    Tests dynamic loading, sub-3 second latency, probabilistic output, and SHAP explainability.
    """
    response = client.get("/api/predict/AAPL")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    # Core Directional Output (UP or DOWN)
    assert data["predicted_direction"] in ["UP", "DOWN"]
    assert 50.0 <= data["confidence_score"] <= 100.0
    assert 0.0 <= data["probability_up"] <= 1.0

    # Latency constraint (<3000 ms)
    assert "latency_ms" in data
    assert data["latency_ms"] < 3000.0

    # Stationary Feature Signals (Section 4)
    features = data["features"]
    assert "log_return" in features
    assert "volatility_5d" in features
    assert "volatility_20d" in features
    assert "c2h_ratio" in features
    assert 0.0 <= features["c2h_ratio"] <= 1.0

    # TreeSHAP Explainability (Section 5)
    assert "shap_values" in data
    shap_data = data["shap_values"]
    assert "base_value" in shap_data
    assert "waterfall" in shap_data
    assert len(shap_data["waterfall"]) > 0
    top_feature = shap_data["waterfall"][0]
    assert "feature" in top_feature
    assert "shap_value" in top_feature
    assert top_feature["impact"] in ["POSITIVE", "NEGATIVE", "NEUTRAL"]

    # Model Metadata
    assert data["model_metadata"]["architecture"] == "Ticker-Wise Isolated Classifier"

def test_api_predict_on_demand_ticker(client):
    """
    Validates on-demand ingestion and training for a stock present in stocks/ (e.g., MSFT).
    Ensures decentralized ticker-wise isolation where MSFT is modeled independently.
    """
    response = client.get("/api/predict/MSFT")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "MSFT"
    assert data["predicted_direction"] in ["UP", "DOWN"]
    assert data["features"]["c2h_ratio"] is not None

def test_nonexistent_ticker_graceful_404(client):
    """
    Validates Section 6 requirement:
    Graceful Fallbacks: requests for untrained or invalid ticker symbols return clean HTTP 404.
    """
    response = client.get("/api/predict/NONEXISTENT_XYZ_12345")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert "message" in data["error"]

def test_prediction_audit_trail_logging(client):
    """
    Validates Section 7 persistence requirement:
    PredictionLog records every query, latency_ms, and confidence_score.
    """
    # Fire prediction
    response = client.get("/api/predict/AAPL")
    assert response.status_code == 200

    db = SessionLocal()
    try:
        logs = db.query(PredictionLog).filter(PredictionLog.requested_ticker == "AAPL").all()
        assert len(logs) > 0
        latest_log = logs[-1]
        assert latest_log.requested_ticker == "AAPL"
        assert latest_log.predicted_direction in ["UP", "DOWN"]
        assert latest_log.latency_ms > 0
        assert latest_log.confidence_score >= 50.0
    finally:
        db.close()

def test_hist_gradient_boosting_model_direct():
    """
    Validates HistGradientBoostingModel unit implementation with 256 bins and sub-50ms inference.
    """
    import pandas as pd
    import numpy as np

    np.random.seed(42)
    X = pd.DataFrame(np.random.randn(200, 5), columns=["f1", "f2", "f3", "f4", "f5"])
    y = pd.Series((X["f1"] + X["f2"] * 0.5 > 0).astype(int))

    model = HistGradientBoostingModel(max_iter=20, random_state=42)
    model.train(X.iloc[:150], y.iloc[:150])
    assert model.is_trained is True

    # Fast inference (<50ms)
    import time
    t0 = time.time()
    preds = model.predict(X.iloc[150:])
    latency = (time.time() - t0) * 1000
    assert latency < 50.0
    assert len(preds) == 50

    metrics = model.evaluate(X.iloc[150:], y.iloc[150:])
    assert "accuracy" in metrics
    assert "roc_auc" in metrics
    assert metrics["accuracy"] > 0.5
