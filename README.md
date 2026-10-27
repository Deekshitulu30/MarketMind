# MarketMind

## 1. Executive Summary and Project Vision

MarketMind is a research-oriented stock-market intelligence platform that unifies financial mathematics, machine learning engineering, and full-stack product delivery. The system intentionally avoids exact price regression and instead frames forecasting as binary next-period direction classification (**UP**/**DOWN**) with calibrated confidence.

This architecture is designed to:
- convert noisy market data into stationary features,
- serve low-latency ticker-specific inference,
- provide transparent model reasoning through SHAP,
- and present interactive financial visualizations in the browser.

---

## 2. Problem Statement

Traditional workflows are fragmented across notebooks, spreadsheets, and disconnected apps, causing:
- **Notebook bottlenecks** (no production latency/concurrency constraints),
- **Global model overreach** (memory pressure + cross-ticker contamination),
- **Black-box predictions** (no user trust),
- **Data leakage** from incorrect temporal splitting.

MarketMind addresses these with ticker-wise model isolation, strict chronological feature/target construction, and first-class explainability.

---

## 3. Core Methodology: Ticker-Wise Modeling

Each ticker is modeled independently (e.g., `model_AAPL.pkl`), not as part of one global model.

### Benefits
- **O(1) model loading per request**: load only one artifact for one ticker.
- **Behavioral isolation**: no cross-asset profile contamination.
- **Horizontal scaling**: add new tickers by adding new artifacts.

---

## 4. Mathematical Feature Engineering

Raw OHLCV data is transformed into stationary and structure-aware features.

### 4.1 Log Returns
\[
R_t = \ln\left(\frac{P_t}{P_{t-1}}\right)
\]

### 4.2 Rolling Volatility
\[
\sigma_{t,N} = \sqrt{\frac{1}{N-1} \sum_{i=0}^{N-1}(R_{t-i} - \bar{R}_N)^2}
\]

### 4.3 Structural Momentum
- short/long moving averages,
- close-to-high ratio:
\[
\text{C2H Ratio} = \frac{\text{Close}_t - \text{Low}_t}{\text{High}_t - \text{Low}_t}
\]

### 4.4 Leakage-Free Target Construction
\[
Y_t =
\begin{cases}
1 & \text{if } P_{t+1} > P_t \\
0 & \text{if } P_{t+1} \le P_t
\end{cases}
\]

Implemented via `shift(-1)` so day-\(t\) features map only to day-\(t+1\) outcomes.

---

## 5. Machine Learning and Explainability

### 5.1 Predictive Model
**Histogram Gradient Boosting Classifier** is used for tabular financial data.

Why this model:
- robust under noisy signals,
- native missing-value handling,
- efficient histogram-based split search for fast inference.

### 5.2 Explainable AI
**TreeSHAP** decomposes probability outputs into per-feature contributions, enabling users to see why the model leaned UP or DOWN.

---

## 6. Backend Architecture (FastAPI)

FastAPI provides asynchronous, stateless APIs (for example, `GET /api/predict/{ticker}`) with Pydantic validation.

Backend responsibilities:
- input/output schema enforcement,
- dynamic ticker artifact loading (`joblib`),
- async data retrieval + feature generation,
- graceful handling of unknown/untrained tickers (`404`),
- low-latency request flow targeting sub-3-second end-to-end responses.

---

## 7. Data and Storage Architecture (PostgreSQL + Artifact Store)

### 7.1 `StockPrice` (raw OHLCV)
- composite PK: `(ticker, date_utc)`
- `open_price`, `high_price`, `low_price`, `close_price`, `volume`

### 7.2 `FeatureSet` (engineered indicators)
- `feature_set_id` (UUID PK), `ticker` (FK)
- `log_return`, `volatility_5d`, `volatility_20d`, `momentum_ratio`

### 7.3 `ModelRun` (MLOps metadata)
- `model_run_id` (UUID PK), `ticker` (FK)
- `model_type`, `baseline_accuracy`, `final_accuracy`
- `artifact_filepath`, `training_timestamp`

### 7.4 `PredictionLog` (audit trail)
- `log_id` (UUID PK), `requested_ticker` (FK)
- `predicted_direction`, `confidence_score`, `latency_ms`, `timestamp`

Model binaries (`.pkl`) are stored outside PostgreSQL (e.g., local `./models/` or S3), with URI references in `ModelRun`.

---

## 8. Frontend Architecture (React + Plotly)

The React client handles query flow, state caching, and interactive charting.

- Cache recent ticker queries (Context API or Redux) to reduce redundant API calls.
- Render OHLCV and overlays with Plotly.
- Render SHAP contribution visualizations (bar/force style views) for interpretability.

---

## 9. End-to-End Request Lifecycle

1. User submits ticker (e.g., `MSFT`).
2. Frontend calls `GET /api/predict/MSFT`.
3. Backend fetches latest historical rows.
4. ETL computes current feature vector.
5. Backend loads `model_MSFT.pkl`.
6. Inference + SHAP explanations execute.
7. Structured JSON returns prediction, confidence, and explanations.
8. Frontend updates state and renders charts.

---

## 10. Future Scope

- Integrate fundamental/financial statement features (e.g., valuation/leverage ratios).
- Automate retraining via CI/CD orchestration (e.g., weekly pipelines).
- Add WebSocket streaming for live intraday updates and probability shifts.
