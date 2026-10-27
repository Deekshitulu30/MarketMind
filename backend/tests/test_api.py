import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["app_name"] == "MarketMind"

def test_get_stocks(client):
    response = client.get("/api/v1/stocks")
    assert response.status_code == 200
    stocks = response.json()
    assert len(stocks) > 0
    symbols = [s["symbol"] for s in stocks]
    assert "AAPL" in symbols

def test_get_stock_history(client):
    response = client.get("/api/v1/stocks/AAPL/history")
    assert response.status_code == 200
    history = response.json()
    assert history["symbol"] == "AAPL"
    assert len(history["prices"]) > 0

def test_statistics_analyze(client):
    response = client.post("/api/v1/statistics/analyze", json={"symbol": "AAPL"})
    assert response.status_code == 200
    stats = response.json()
    assert "price_summary" in stats
    assert "return_summary" in stats
    assert "distribution_analysis" in stats
    assert "hypothesis_test" in stats

def test_train_models(client):
    response = client.post("/api/v1/models/train", json={"symbol": "AAPL", "train_ratio": 0.70})
    assert response.status_code == 200
    result = response.json()
    assert "classification_models" in result
    assert "best_classification_model" in result

def test_search_stocks(client):
    # Test prefix search
    response = client.get("/api/v1/stocks/search?q=REL")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    symbols = [r["symbol"] for r in results]
    assert "RELIANCE" in symbols

    # Test US search
    response = client.get("/api/v1/stocks/search?q=NVDA")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert results[0]["symbol"] == "NVDA"
    assert results[0]["exchange"] == "NASDAQ"

def test_predict_market_direction(client):
    response = client.post("/api/v1/predict", json={"symbol": "AAPL", "horizon": 1})
    assert response.status_code == 200
    pred = response.json()
    assert pred["predicted_direction"] in ["UP", "DOWN"]
    assert 0 <= pred["probability_up_pct"] <= 100
    assert "risk_profile" in pred
    assert "reference_levels" in pred
    ref = pred["reference_levels"]
    assert ref is not None
    assert ref["reference_target"]["label"] == "Model Reference Target (educational)"
    assert ref["reference_stop_loss"]["label"] == "Model Reference Stop-Loss (educational)"
    assert "Derived from historical volatility and model output. Not a recommendation to buy, sell, or hold." in ref["mandatory_disclaimer"]

def test_explain_prediction(client):
    response = client.post("/api/v1/explain", json={"symbol": "AAPL"})
    assert response.status_code == 200
    explain = response.json()
    assert "global_feature_importance" in explain
    assert "shap_waterfall" in explain
    assert "natural_language_summary" in explain

def test_what_if_simulation(client):
    response = client.post("/api/v1/what-if", json={
        "symbol": "AAPL",
        "market_return_delta": 0.02,
        "volume_delta_pct": 0.15,
        "volatility_delta_pct": -0.10
    })
    assert response.status_code == 200
    sim = response.json()
    assert "baseline" in sim
    assert "scenario" in sim
    assert "comparison" in sim

def test_backtest(client):
    response = client.post("/api/v1/backtest", json={
        "symbol": "AAPL",
        "model_name": "Random Forest Classifier",
        "n_folds": 2
    })
    assert response.status_code == 200
    bt = response.json()
    assert "fold_results" in bt
    assert len(bt["fold_results"]) == 2
