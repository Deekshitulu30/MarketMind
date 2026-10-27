# Architecture Essentials — MarketMind

## 1. Core Rule
MarketMind must never allow future information to influence a historical prediction.

## 2. Mandatory Boundaries
```text
UI
 ↓
API
 ↓
Application Services
 ↓
Domain/ML/Statistics
 ↓
Infrastructure
```

UI code must not directly access the database.

## 3. Data Rules
- Raw data is immutable.
- Every dataset has a version.
- Every feature pipeline has a version.
- Every prediction records a data cutoff.
- Date/time handling must be explicit.

## 4. ML Rules
- Chronological split for time-series prediction.
- Training-only preprocessing.
- No test-set tuning.
- Baseline model required.
- Model version required for every prediction.
- Metrics must be stored with the training run.

## 5. Prediction Contract
Every prediction should contain:
```text
symbol
data_cutoff
horizon
model_name
model_version
prediction
probability (if classification)
generated_at
```

## 6. What-If Contract
A what-if scenario must contain:
```text
baseline inputs
changed inputs
model version
baseline prediction
scenario prediction
difference
assumptions
```

## 7. Explainability Contract
Explanation output should identify:
- Model version
- Prediction
- Important features
- Direction/magnitude of influence where supported
- Explanation method

## 8. Visualization Rules
- Never imply certainty when the model is uncertain.
- Distinguish actual and predicted values.
- Always show date/time ranges.
- Label units.
- Avoid deceptive axis truncation.
- Use interactive filters without hiding the current selection.

## 9. Security Essentials
- No secrets in source code.
- No real brokerage credentials.
- No real-money execution in MVP.
- Validate all external inputs.
- Limit administrative/model-training endpoints.

## 10. Reliability Essentials
- Graceful errors.
- Structured logging.
- Reproducible model runs.
- Automated tests for critical calculations.
- Health endpoint.

## 11. MVP Architecture
For the first version:
```text
Streamlit
   |
Python service modules
   |
PostgreSQL
   |
Local model artifacts
```

For the stronger production-style version:
```text
React/Streamlit
      |
   FastAPI
      |
Application Services
      |
PostgreSQL + Model Store
```

## 12. Academic Integrity
The project must clearly distinguish:
- Historical observations
- Statistical estimates
- ML predictions
- Simulated what-if outputs

No simulated result may be presented as an observed market fact.
