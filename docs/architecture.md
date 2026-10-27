# Architecture — MarketMind

## 1. Architecture Style

MarketMind uses a modular layered architecture with clear boundaries between presentation, application services, domain logic and infrastructure.

## 2. Logical Architecture

```text
┌────────────────────────────────────────────────────────────┐
│                        Presentation                         │
│        Dashboard / Web UI / Interactive Visualizations    │
└───────────────────────────┬────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│                         API Layer                           │
│              Request validation / routing / auth           │
└───────────────────────────┬────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│                    Application Services                    │
│ Prediction | Statistics | Backtest | What-If | Explain    │
└──────────────┬──────────────┬──────────────┬───────────────┘
               │              │              │
       ┌───────▼──────┐ ┌─────▼─────┐ ┌────▼──────────┐
       │ Feature      │ │ ML Engine │ │ Statistical   │
       │ Engineering  │ │           │ │ Engine        │
       └───────┬──────┘ └─────┬─────┘ └────┬──────────┘
               │              │             │
               └──────────────┼─────────────┘
                              ▼
                    ┌──────────────────┐
                    │ Data/ML Storage  │
                    │ PostgreSQL/files │
                    └──────────────────┘
```

## 3. Major Components

### Data Ingestion

Responsibilities:

- Acquire/import historical data.
- Normalize schema.
- Validate records.
- Preserve source metadata.

### Feature Engineering

Responsibilities:

- Compute returns.
- Compute rolling statistics.
- Build model features.
- Enforce cutoff-time rules.

### Statistical Engine

Responsibilities:

- Descriptive statistics.
- Correlation.
- Distribution analysis.
- Hypothesis tests.
- Regression statistics.

### ML Engine

Responsibilities:

- Training.
- Validation.
- Model comparison.
- Model serialization.
- Prediction.

### Explainability Engine

Responsibilities:

- Feature importance.
- SHAP-compatible explanations.
- Partial dependence.
- Explanation metadata.

### Backtesting Engine

Responsibilities:

- Chronological evaluation.
- Rolling/walk-forward evaluation.
- Actual vs predicted comparisons.
- Performance reports.

### What-If Engine

Responsibilities:

- Accept controlled scenario changes.
- Recompute affected features.
- Run the selected model.
- Compare baseline and scenario outputs.

### Dashboard

Responsibilities:

- Market exploration.
- Statistics.
- Prediction.
- Explainability.
- Backtesting.
- Scenario analysis.

## 4. Data Architecture

```text
RAW
 ↓
VALIDATED
 ↓
CLEAN
 ↓
FEATURE STORE
 ↓
TRAIN/VALIDATION/TEST
 ↓
MODEL ARTIFACT
 ↓
PREDICTION
```

Raw data is immutable.

## 5. Model Lifecycle

```text
Dataset Version
      ↓
Feature Version
      ↓
Training Run
      ↓
Validation
      ↓
Evaluation
      ↓
Approved Model
      ↓
Prediction
      ↓
Monitoring
```

## 6. Deployment Architecture

```text
                    Internet / LAN
                         |
                 ┌───────▼───────┐
                 │ Reverse Proxy │
                 └───────┬───────┘
                         |
             ┌───────────┴───────────┐
             │                       │
       ┌─────▼─────┐           ┌────▼─────┐
       │ Dashboard │           │ FastAPI  │
       └───────────┘           └────┬─────┘
                                    |
                              ┌─────▼─────┐
                              │ PostgreSQL│
                              └───────────┘
                                    |
                              ┌─────▼─────┐
                              │ Artifacts │
                              └───────────┘
```

## 7. Design Decisions

- Python is used throughout the analytical and ML stack.
- FastAPI provides a clean service boundary.
- PostgreSQL stores structured metadata and application state.
- Plotly is preferred for interactive analytical charts.
- Streamlit may serve as the MVP dashboard.
- Model artifacts are versioned independently from source code.

## 8. Failure Boundaries

If the data source fails:

- Existing validated datasets remain available.

If a model fails:

- Dashboard shows model-unavailable state.
- Previously approved model can remain available.

If explanation fails:

- Prediction remains available with an explanation-unavailable notice.

If database is unavailable:

- API reports service degradation rather than returning fabricated data.

## 9. Observability

Track:

- API latency
- Training duration
- Data freshness
- Prediction count
- Model version
- Error rates
- Backtest run status

## 10. Architecture Quality Attributes

Priority order:

1. Correctness
2. Reproducibility
3. Maintainability
4. Security
5. Performance
6. Scalability

## 11. Architecture

                         ┌─────────────────────────┐
                         │       USER / ADMIN      │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │    WEB / DASHBOARD UI   │
                         │                         │
                         │  • Market Overview      │
                         │  • Stock Explorer       │
                         │  • Statistics           │
                         │  • Prediction           │
                         │  • Explainability       │
                         │  • Backtesting          │
                         │  • What-If Simulator    │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │       API GATEWAY       │
                         │        FastAPI          │
                         └────────────┬────────────┘
                                      │
             ┌────────────────────────┼────────────────────────┐
             │                        │                        │
             ▼                        ▼                        ▼

┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Market Service │ │ Prediction │ │ Analytics │
│ │ │ Service │ │ Service │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
│ │ │
└────────────────────────┼────────────────────────┘
│
▼
┌─────────────────────────┐
│ FEATURE ENGINE │
│ │
│ • Returns │
│ • Momentum │
│ • Volatility │
│ • Rolling statistics │
│ • Volume features │
│ • Market relationships │
└────────────┬────────────┘
│
┌─────────────────┼─────────────────┐
│ │ │
▼ ▼ ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ STATISTICS │ │ ML ENGINE │ │ RISK ENGINE │
│ │ │ │ │ │
│ • Probability │ │ • Regression │ │ • Volatility │
│ • Distribution │ │ • SVM │ │ • Variance │
│ • Correlation │ │ • Tree │ │ • Risk score │
│ • Hypothesis │ │ • Ensemble │ │ • Drawdown │
│ • Regression │ │ • Clustering │ │ │
└───────┬────────┘ └───────┬────────┘ └───────┬────────┘
│ │ │
└──────────────────┼──────────────────┘
│
▼
┌─────────────────────────┐
│ MODEL EVALUATION │
│ │
│ • MAE │
│ • RMSE │
│ • R² │
│ • Accuracy │
│ • Precision │
│ • Recall │
│ • Confusion Matrix │
└────────────┬────────────┘
│
┌──────────────┼──────────────┐
▼ ▼ ▼
┌────────────┐ ┌────────────┐ ┌──────────────┐
│EXPLAINABLE │ │ BACKTEST │ │ WHAT-IF │
│ AI │ │ ENGINE │ │ SIMULATOR │
│ │ │ │ │ │
│ SHAP │ │ Historical │ │ Scenario │
│ Feature │ │ Walk │ │ Simulation │
│ Importance │ │ Forward │ │ │
└─────┬──────┘ └─────┬──────┘ └──────┬───────┘
│ │ │
└──────────────┼───────────────┘
▼
┌─────────────────────────┐
│ RESULTS / ARTIFACTS │
│ │
│ PostgreSQL │
│ Model Registry │
│ Feature Metadata │
│ Backtest Results │
└─────────────────────────┘

## 12. 🧩 Major Modules

The system should have 10 major modules.

Module 1 — Data Ingestion

Responsible for obtaining historical market data.

Data Source
↓
Downloader
↓
Schema Validator
↓
Data Cleaner
↓
Raw Storage

Input:

Date
Open
High
Low
Close
Adjusted Close
Volume

Output:

Validated Market Dataset

## 13. 🧹 Data Processing Pipeline

Don't directly send raw stock prices to ML.

Use:

RAW DATA
↓
Validation
↓
Missing Value Handling
↓
Duplicate Detection
↓
Outlier Analysis
↓
Normalization / Scaling
↓
Feature Engineering
↓
ML Dataset
Important rule

For stock prediction:

Never allow future information into past features.

For example, when predicting Monday's movement, Sunday's information cannot accidentally appear in Monday's feature set.

This is one of the most important technical points in your project.

## 14. 📐 Mathematical & Statistical Engine

This is where you explicitly cover your Mathematics/Statistics subject.

Descriptive statistics

Calculate:

Mean
Median
Mode
Variance
Standard Deviation
Minimum
Maximum
Range
Returns

For example:

R
t
​

=
P
t−1
​

P
t
​

−P
t−1
​

    ​

or log return:

R
t
​

=ln(
P
t−1
​

P
t
​

    ​

)
Correlation

Analyze relationships:

Stock ↔ Market Index
Volume ↔ Return
Volatility ↔ Return
Probability

For example:

P(Return > 0)
P(Return < 0)
Hypothesis testing

You could investigate questions such as:

"Is the average return significantly different between two defined market periods?"

The project should report the hypothesis, test, assumptions and result rather than merely displaying a p-value.

## 15. ⚙️ Feature Engineering Engine

This is the bridge between statistics and ML.

Create features such as:

price_change
percentage_return
rolling_mean
rolling_std
volume_change
momentum
volatility
market_return
stock_market_correlation
lag_1_return
lag_5_return

Example:

Date Close Return Volatility Volume
────────────────────────────────────────────────────
Day 1 2450 — — 120K
Day 2 2470 0.81% — 145K
Day 3 2460 -0.40% 0.62% 132K

## 16. 🤖 ML Engine

Don't use only one algorithm.

Create a Model Laboratory.

                 DATA
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼

Regression Classification Clustering
│ │ │
▼ ▼ ▼
Linear Logistic K-Means
Regression Regression
Multiple SVM
Regression Decision Tree
Ensemble
Regression

Predict:

Next return

or:

Next price
Classification

Predict:

UP
DOWN

This is preferable as the main prediction target because it avoids presenting an exact price as if it were certain.

Clustering

Discover market regimes:

Cluster 1 → Low volatility
Cluster 2 → High volatility
Cluster 3 → High volume / momentum
PCA

Use PCA to investigate dimensionality reduction and visualize high-dimensional feature relationships.

## 17. 🧠 Prediction Engine

The user selects:

Stock: XYZ
Prediction Horizon: 1 day
Model: Random Forest

System returns:

╔══════════════════════════════╗
║ MARKET PREDICTION ║
╠══════════════════════════════╣
║ ║
║ Direction: 📈 UP ║
║ Probability: 71.4% ║
║ ║
║ Expected Return: +1.2% ║
║ Risk: MEDIUM ║
║ ║
║ Model: Random Forest ║
║ Version: v1.4 ║
╚══════════════════════════════╝

And importantly:

Data cutoff:
2026-08-17 15:30

Prediction generated:
2026-08-18 09:00

This makes the result reproducible.

## 18. 🔍 Explainable AI Engine

This should be one of your project's strongest features.

Instead of:

"UP — 71%"

show:

WHY?

Feature Impact
──────────────────────────────────
Momentum ██████████
Market Return ████████
Volume Change ██████
Volatility ████
Previous Return ███

Use:

Global explanation

"What features generally matter?"

Local explanation

"Why did this particular prediction happen?"

SHAP

For supported models.

Partial Dependence

Show how prediction changes as a feature changes.

This gives you a strong Data Visualization + ML connection.

## 19. 🔄 Backtesting Engine

This is mandatory if you want the project to be taken seriously.

Instead of training and testing randomly:

2021 ───── 2022 ───── 2023 ───── 2024 ───── 2025
| TRAIN | TEST |

Better:

TRAIN TEST
2021-2022 2023
↓
TRAIN TEST
2021-2023 2024
↓
TRAIN TEST
2021-2024 2025

This is essentially a walk-forward evaluation design.

Show:

Actual
vs
Predicted

and metrics.

## 20. 🔮 What-If Simulator

This is what makes your project different from a normal stock predictor.

User changes scenario parameters:

Market Return +2%
Trading Volume +15%
Volatility -10%
Momentum +5%

Then:

              BASELINE       SCENARIO

Prediction 58% UP 72% UP

Return +0.6% +1.8%

Risk HIGH MEDIUM

Visualize:

Scenario Impact

Baseline █████████
Scenario ███████████████

Important: label this as model-based scenario analysis, not a causal prediction.

## 21. 📊 Visualization Architecture

Create separate dashboard pages rather than putting everything on one screen.

Page 1 — Market Overview
Market Index
Top movers
Volume
Market trend
Market volatility
Page 2 — Stock Explorer
Search stock
Select date range
Price chart
Volume
Returns
Volatility
Page 3 — Statistical Lab
Distribution
Histogram
Boxplot
Correlation matrix
Scatter plots
Regression
Hypothesis tests
Page 4 — ML Prediction
Prediction
Probability
Expected return
Risk
Model
Metrics
Page 5 — Model Laboratory
Model Accuracy
────────────────────────────
Logistic 67.2%
SVM 69.8%
Decision Tree 64.5%
Random Forest 72.4%
Page 6 — Explainable AI
Feature importance
SHAP
Partial dependence
Prediction explanation
Page 7 — Backtesting
Actual vs predicted
Model performance
Confusion matrix
Error distribution
Walk-forward results
Page 8 — What-If Simulator
┌─────────────────────────┐
│ Market Return [+2%] │
│ Volume [+15%] │
│ Volatility [-10%] │
└─────────────────────────┘

          ↓ RUN SCENARIO

Baseline → 58%
Scenario → 72%

## 22. 🗄️ Database Architecture

Use PostgreSQL.

                    stocks
                       │
                       │
                       ▼
                 market_prices
                       │
                       ▼
                    features
                       │
              ┌────────┴────────┐
              ▼                 ▼
         model_runs        predictions
              │                 │
              ▼                 ▼
         backtests          explanations

Main tables

stocks

id
symbol
company_name
exchange
currency

market_prices

id
stock_id
timestamp
open
high
low
close
adjusted_close
volume

features

id
stock_id
timestamp
feature_name
feature_value
feature_version

model_runs

id
model_name
model_version
dataset_version
training_period
validation_method
hyperparameters
metrics
artifact_path
created_at

predictions

id
model_run_id
stock_id
data_cutoff
horizon
predicted_value
predicted_class
probability
created_at

backtests

id
model_run_id
test_period
metrics
artifact_path

## 23. 🔌 API Architecture

FastAPI endpoints:

GET /health

GET /stocks

GET /stocks/{symbol}/history

POST /statistics/analyze

POST /features/generate

POST /models/train

GET /models

GET /models/{model_id}

POST /predict

POST /explain

POST /backtest

POST /what-if

## 24. 📁 Complete Project Structure

I recommend this:

marketmind/
│
├── app/
│ │
│ ├── main.py
│ │
│ ├── api/
│ │ ├── routes/
│ │ │ ├── market.py
│ │ │ ├── statistics.py
│ │ │ ├── prediction.py
│ │ │ ├── explainability.py
│ │ │ ├── backtest.py
│ │ │ └── what_if.py
│ │ │
│ │ └── schemas/
│ │ ├── market.py
│ │ ├── prediction.py
│ │ └── backtest.py
│ │
│ ├── core/
│ │ ├── config.py
│ │ ├── logging.py
│ │ └── exceptions.py
│ │
│ ├── data/
│ │ ├── ingestion.py
│ │ ├── validation.py
│ │ ├── cleaning.py
│ │ └── repository.py
│ │
│ ├── features/
│ │ ├── returns.py
│ │ ├── volatility.py
│ │ ├── momentum.py
│ │ ├── volume.py
│ │ └── pipeline.py
│ │
│ ├── statistics/
│ │ ├── descriptive.py
│ │ ├── probability.py
│ │ ├── correlation.py
│ │ ├── distributions.py
│ │ ├── hypothesis.py
│ │ └── regression.py
│ │
│ ├── models/
│ │ ├── base.py
│ │ ├── regression.py
│ │ ├── classification.py
│ │ ├── svm.py
│ │ ├── decision_tree.py
│ │ ├── ensemble.py
│ │ ├── clustering.py
│ │ ├── pca.py
│ │ ├── trainer.py
│ │ └── registry.py
│ │
│ ├── explainability/
│ │ ├── feature_importance.py
│ │ ├── shap_explainer.py
│ │ └── partial_dependence.py
│ │
│ ├── backtesting/
│ │ ├── splitter.py
│ │ ├── walk_forward.py
│ │ ├── evaluator.py
│ │ └── metrics.py
│ │
│ ├── what_if/
│ │ ├── scenarios.py
│ │ ├── simulator.py
│ │ └── comparison.py
│ │
│ └── database/
│ ├── models.py
│ ├── session.py
│ └── migrations/
│
├── dashboard/
│ ├── app.py
│ ├── pages/
│ │ ├── overview.py
│ │ ├── explorer.py
│ │ ├── statistics.py
│ │ ├── prediction.py
│ │ ├── models.py
│ │ ├── explainability.py
│ │ ├── backtesting.py

## 25. 🛠️ Technology Stack

Frontend

For your first version:

Streamlit + Plotly

This is much faster to build.

For a more professional version:

React + TypeScript + Tailwind

Backend

Python + FastAPI

ML
Python
NumPy
Pandas
Scikit-learn
SHAP
SciPy
Visualization
Plotly
Matplotlib
Seaborn
Database

PostgreSQL

DevOps
Git
GitHub
Docker
Docker Compose

## 26. 🔐 Security Architecture

Even though this is an educational project, implement basic security.

User
↓
API
↓
Authentication
↓
Authorization
↓
Service

Don't store:

API keys
Database passwords
Broker credentials

inside Git.

Use:

.env

and environment variables.

## 27. 🧪 Testing Architecture

Your Software Engineering component should explicitly demonstrate testing.

                 TESTING
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
     UNIT       INTEGRATION    SYSTEM
       │            │            │
       ▼            ▼            ▼

Features API + ML Full App
Statistics DB + API Workflow
Metrics Pipeline
Example unit test
Input:
100 → 105

Expected return:
5%
ML test

Check:

Does the feature pipeline accidentally use future data?

System test
Select stock
↓
Generate statistics
↓
Train model
↓
Predict
↓
Explain
↓
Backtest
↓
Display dashboard

## 28. 🔄 Complete End-to-End Workflow

This is the most important diagram for your project presentation:

                         USER
                          │
                          ▼
                  Select Stock
                          │
                          ▼
                   Historical Data
                          │
                          ▼
                  Data Validation
                          │
                          ▼
                    Data Cleaning
                          │
                          ▼
                Statistical Analysis
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
      Exploratory Analysis       Feature Engineering
                                       │
                                       ▼
                              Train / Validation
                                       │
                         ┌─────────────┼─────────────┐
                         ▼             ▼             ▼
                    Regression       SVM       Decision Tree
                         │             │             │
                         └─────────────┼─────────────┘
                                       ▼
                                Model Comparison
                                       │
                                       ▼
                                Best Model
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
                Prediction        Explainability      Backtest
                    │                  │                  │
                    └──────────────────┼──────────────────┘
                                       ▼
                              What-If Simulation
                                       │
                                       ▼
                               Visualization
                                       │
                                       ▼
                              USER INTERPRETATION

## 29. How Your Four Subjects Fit

This is what I would show your faculty:

Subject MarketMind Component
Mathematics / Statistics Probability, distributions, variance, correlation, regression, hypothesis testing
Machine Learning Regression, SVM, Decision Trees, Ensemble Learning, K-Means, PCA
Data Visualization Time-series, heatmaps, distributions, dashboards, KPIs, model explanations
Software Engineering Requirements, UML, modular architecture, database, APIs, testing, Git, deployment

## 30. MarketMind-Scale: Whole-Exchange Architecture & Regulatory Reference Framing

### 30.1 Whole-Exchange Separation: Master Symbol Directory vs. Lazy On-Demand Pricing
To achieve instantaneous sub-millisecond search across thousands of equities without rate-limiting upstream providers:
1. **Symbol Master Layer (`data/symbol_master/`)**: Static, lightweight datasets (`EQUITY_L.csv` for NSE and US directories) loaded into memory for instant prefix typeahead filtering.
2. **On-Demand Price Fetching & Caching (`OnDemandDataFetcher`)**: Lazily fetches 5-year OHLCV via `yfinance` on ticker selection, storing normalized, cleaned data in `data/raw/{symbol}.csv` and SQLite with full cryptographic checksums.

### 30.2 Official TradingView Advanced Real-Time Chart Embed
- Embeds the official TradingView Advanced Real-Time widget within an isolated, sandboxed container.
- Translates internal symbols to exchange-qualified identifiers (`NSE:RELIANCE`, `NASDAQ:AAPL`, `NYSE:SPY`).
- Retains separation: custom predictive overlays are never drawn directly onto the sandboxed TradingView widget, but presented in sibling relationship alongside the chart.

### 30.3 ATR-Based Educational Model Reference Levels Methodology
In strict compliance with SEBI / regulatory non-advisory constraints:
- **Predicted Price**: $P = C_{latest} \times (1 + \text{expected\_return})$
- **14-Period Average True Range (ATR)**: $TR_t = \max(H_t - L_t, |H_t - C_{t-1}|, |L_t - C_{t-1}|)$, $ATR = \frac{1}{14}\sum_{i=0}^{13} TR_{t-i}$
- **Reference Target (educational)**: $P + (k \times ATR)$ for UP (or $P - (k \times ATR)$ for DOWN), default $k=1.5$.
- **Reference Stop-Loss (educational)**: $P - (m \times ATR)$ for UP (or $P + (m \times ATR)$ for DOWN), default $m=1.0$.
- **Regulatory Framing Rules**:
  1. Mandatory explicit labels: *"Model Reference Target (educational)"* and *"Model Reference Stop-Loss (educational)"*.
  2. Single-glance context: Model version, directional confidence %, and mandatory disclaimer (*"Derived from historical volatility and model output. Not a recommendation to buy, sell, or hold."*).
  3. Single-stock view only (no multi-stock hot picks feed).
  4. Interactive *"How is this calculated?"* methodology modal explaining the mathematical formula.
  5. Session opt-in toggle gating (default OFF on page load).
