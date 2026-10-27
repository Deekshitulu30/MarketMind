# TRD — MarketMind

## 1. Technical Overview
MarketMind is designed as a modular data/ML web application.

### Proposed stack
- **Frontend/Dashboard:** Streamlit or a React frontend
- **Backend API:** Python + FastAPI
- **ML:** scikit-learn
- **Data processing:** Python, NumPy, Pandas
- **Visualization:** Plotly, Matplotlib/Seaborn where appropriate
- **Database:** PostgreSQL
- **Experiment/model metadata:** PostgreSQL + filesystem/object storage for model artifacts
- **Testing:** pytest
- **Version control:** Git
- **Containerization:** Docker

For a college MVP, Streamlit can be used as the primary UI while FastAPI remains the service boundary if the team wants a stronger software-engineering architecture.

## 2. High-Level Components
1. Data Ingestion Service
2. Data Validation Service
3. Data Processing/Feature Engineering Service
4. Statistical Analysis Engine
5. ML Training Engine
6. Prediction Service
7. Explainability Service
8. Backtesting Engine
9. What-If Simulation Engine
10. Dashboard/UI
11. Metadata/Model Registry
12. Logging and Monitoring

## 3. Data Flow
```text
Market Source / CSV
        |
        v
Data Ingestion
        |
        v
Validation
        |
        v
Clean Dataset
        |
        +--> Statistical Engine
        |
        +--> Feature Engineering
                    |
                    v
                ML Training
                    |
             +------+------+
             |             |
             v             v
        Model Registry   Evaluation
             |
             v
        Prediction API
             |
      +------+------+
      |      |      |
      v      v      v
 Explain  What-if  Backtest
      \      |      /
       \     |     /
        v    v    v
          Dashboard
```

## 4. Data Model
### stocks
- id
- symbol
- exchange
- company_name
- currency

### market_prices
- id
- stock_id
- timestamp/date
- open
- high
- low
- close
- adjusted_close
- volume

### features
- id
- stock_id
- timestamp/date
- feature_name
- feature_value
- feature_version

### model_runs
- id
- model_name
- model_version
- dataset_version
- training_start
- training_end
- validation_method
- hyperparameters
- metrics
- artifact_path
- created_at

### predictions
- id
- model_run_id
- stock_id
- cutoff_time
- horizon
- predicted_value
- predicted_class
- probability
- created_at

### backtests
- id
- model_run_id
- test_start
- test_end
- metrics
- result_artifact_path

## 5. ML Pipeline
### Step 1 — Data split
Use chronological splitting rather than random shuffling for time-dependent prediction.

### Step 2 — Preprocessing
- Missing-value strategy
- Duplicate detection
- Scaling where required
- Feature validation

### Step 3 — Feature creation
All features must be computed using information available at or before the prediction cutoff.

### Step 4 — Training
Train baseline and candidate models.

### Step 5 — Validation
Use time-aware validation.

### Step 6 — Evaluation
Store all metrics and configuration.

### Step 7 — Model selection
Select based on the predefined evaluation objective, not the test set.

## 6. Leakage Prevention
Critical rules:
- Never use future prices to calculate historical features.
- Fit scalers only on training data.
- Fit imputers only on training data.
- Do not randomly split time-series data for the final evaluation.
- Keep the final test period untouched until model selection is complete.
- Record the exact data cutoff for every prediction.

## 7. Statistical Engine
Implement reusable functions for:
- Descriptive statistics
- Return calculation
- Volatility
- Correlation matrix
- Distribution analysis
- Outlier detection
- Regression statistics
- Hypothesis tests when applicable

## 8. API Design
### GET /health
Returns service health.

### GET /stocks
Returns supported instruments.

### GET /stocks/{symbol}/history
Returns historical market data.

### POST /analysis/statistics
Runs statistical analysis.

### POST /models/train
Starts model training.

### GET /models
Lists model versions.

### POST /predict
Generates a prediction using a selected model.

### POST /explain
Generates model explanation.

### POST /backtest
Runs a historical evaluation.

### POST /what-if
Runs a scenario analysis.

## 9. Error Handling
Standard error categories:
- INVALID_DATA
- INVALID_SYMBOL
- INVALID_DATE_RANGE
- INSUFFICIENT_DATA
- FEATURE_ERROR
- MODEL_NOT_FOUND
- TRAINING_ERROR
- PREDICTION_ERROR
- BACKTEST_ERROR

Return structured error responses.

## 10. Configuration
Use environment variables/configuration for:
- Database URL
- Data source
- API port
- Model artifact location
- Logging level
- Allowed symbols
- Default prediction horizon

Never hard-code credentials.

## 11. Testing
### Unit tests
- Feature calculations
- Statistical functions
- Validation
- API schemas
- Prediction formatting

### Integration tests
- Ingestion → preprocessing
- Training → model registry
- Prediction → explanation

### System tests
- End-to-end dashboard workflow

### ML tests
- No leakage
- Deterministic preprocessing
- Metric calculation
- Baseline comparison

## 12. Deployment
Recommended:
```text
Docker Compose
├── api
├── dashboard
├── postgres
└── model/data volume
```

For a lightweight college deployment, API + dashboard can initially run together, while PostgreSQL remains separate.

## 13. Logging
Log:
- Request ID
- Model version
- Dataset version
- Data cutoff
- Training run
- Error category
- Execution duration

Do not log secrets.

## 14. Repository Structure
```text
marketmind/
├── app/
│   ├── api/
│   ├── core/
│   ├── data/
│   ├── features/
│   ├── statistics/
│   ├── models/
│   ├── explainability/
│   ├── backtesting/
│   └── what_if/
├── dashboard/
├── tests/
├── notebooks/
├── configs/
├── docs/
├── models/
├── data/
├── scripts/
├── Dockerfile
├── docker-compose.yml
└── README.md
```
