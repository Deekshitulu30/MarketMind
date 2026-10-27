# MarketMind Backend Schema

## Stack
FastAPI + Pydantic + SQLAlchemy + PostgreSQL.

## Tables

### stocks
`id UUID PK`, `symbol VARCHAR(32) UNIQUE`, `company_name`, `exchange`, `currency`, `sector`, `created_at`

### market_prices
`id BIGSERIAL PK`, `stock_id UUID FK`, `timestamp TIMESTAMPTZ`, `open`, `high`, `low`, `close`, `adjusted_close`, `volume`, `source`, `data_version_id UUID FK`.

Unique: `(stock_id, timestamp)`.

### data_versions
`id UUID PK`, `name`, `source`, `checksum`, `row_count`, `start_date`, `end_date`, `created_at`.

### feature_versions
`id UUID PK`, `name`, `version`, `definition_hash`, `created_at`.

### features
`id BIGSERIAL PK`, `stock_id UUID FK`, `timestamp`, `feature_version_id UUID FK`,
`daily_return`, `log_return`, `rolling_mean`, `rolling_std`, `volatility`, `momentum`,
`volume_change`, `market_return`, `market_correlation`, `lag_1_return`, `lag_5_return`.

Unique: `(stock_id, timestamp, feature_version_id)`.

### model_runs
`id UUID PK`, `model_name`, `model_version`, `task_type`, `data_version_id UUID FK`,
`feature_version_id UUID FK`, training/validation/test dates, `hyperparameters JSONB`,
`metrics JSONB`, `random_seed`, `artifact_uri`, `status`, `created_at`.

### predictions
`id UUID PK`, `model_run_id UUID FK`, `stock_id UUID FK`, `data_cutoff`,
`horizon`, `predicted_class`, `probability_up`, `predicted_return`,
`predicted_price`, `risk_level`, `created_at`.

### explanations
`id UUID PK`, `prediction_id UUID FK`, `method`, `payload JSONB`, `created_at`.

### backtests
`id UUID PK`, `model_run_id UUID FK`, `stock_id UUID FK`, `strategy`,
`start_date`, `end_date`, `metrics JSONB`, `fold_results JSONB`,
`artifact_uri`, `created_at`.

### scenarios
`id UUID PK`, `stock_id UUID FK`, `model_run_id UUID FK`,
`baseline_prediction_id UUID FK`, `inputs JSONB`, `baseline_output JSONB`,
`scenario_output JSONB`, `created_at`.

### experiments
`id UUID PK`, `name`, `objective`, `model_run_id UUID FK`, `notes`, `created_at`.

## Relationships
stocks 1:N market_prices
stocks 1:N features
data_versions 1:N market_prices
feature_versions 1:N features
model_runs N:1 data_versions
model_runs N:1 feature_versions
model_runs 1:N predictions
predictions 1:N explanations
model_runs 1:N backtests
model_runs 1:N scenarios

## API
GET `/api/v1/health`
GET `/api/v1/stocks`
GET `/api/v1/stocks/{symbol}/history`
POST `/api/v1/statistics/analyze`
POST `/api/v1/features/generate`
POST `/api/v1/models/train`
GET `/api/v1/models`
GET `/api/v1/models/{model_id}`
POST `/api/v1/predict`
POST `/api/v1/explain`
POST `/api/v1/backtest`
POST `/api/v1/what-if`

## Rules
- Business logic stays in services, not routes.
- Pydantic validates all API payloads.
- Chronological evaluation for time-series.
- No future-data leakage.
- Scalers/imputers fit only on training data.
- Every prediction records data, feature and model versions plus data cutoff.
