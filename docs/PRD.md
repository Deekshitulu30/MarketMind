# PRD — MarketMind

## 1. Product Overview
**Product name:** MarketMind  
**Product type:** Explainable Stock Market Intelligence & What-If Prediction System  
**Purpose:** An educational/research-oriented platform that analyzes historical market data, applies statistical and machine-learning methods, visualizes market behavior, explains model predictions, and allows users to test hypothetical market scenarios.

> This system is not intended to guarantee profits or provide personalized financial advice.

## 2. Problem Statement
Stock-market datasets contain price, volume, volatility, market-index and derived technical information. Raw data is difficult to interpret, while a simple price-prediction model does not explain uncertainty, risk, feature influence, or model reliability.

MarketMind addresses this by combining:
- Statistical analysis
- Machine learning
- Model comparison
- Explainable AI
- Risk analysis
- Backtesting
- Interactive visualization
- What-if simulation

## 3. Goals
1. Analyze historical stock-market data.
2. Predict short-term price direction and/or numerical return/price.
3. Estimate prediction probability/confidence and market risk indicators.
4. Compare multiple ML models.
5. Explain predictions using feature importance/SHAP where appropriate.
6. Provide historical backtesting.
7. Provide an interactive analytical dashboard.
8. Demonstrate concepts from Mathematics/Probability & Statistics, Machine Learning, Data Visualization, and Software Engineering.

## 4. Non-Goals
- Guaranteed profitable trading.
- Autonomous real-money trading.
- Personalized investment advice.
- High-frequency trading.
- Broker/order execution in the first release.

## 5. Target Users
### Primary
- College students
- Faculty evaluators
- ML/data-visualization learners

### Secondary
- Researchers and data enthusiasts

## 6. Core User Stories
### Market Analysis
- As a user, I want to select a stock and date range so I can analyze historical behavior.
- As a user, I want to view price, volume, return and volatility statistics.
- As a user, I want to compare multiple stocks.

### Prediction
- As a user, I want to generate a prediction for a selected horizon.
- As a user, I want to see upward/downward probability.
- As a user, I want to see model performance metrics.

### Explainability
- As a user, I want to know which features influenced a prediction.
- As a user, I want to compare explanations across models when supported.

### What-If
- As a user, I want to change selected input conditions and observe the model's estimated output.
- As a user, I want to compare baseline and scenario results.

### Backtesting
- As a user, I want to evaluate a model on historical unseen periods.
- As a user, I want to compare predicted and actual outcomes.

## 7. Functional Requirements
### FR-01 Data Ingestion
- Import historical market datasets through a controlled ingestion layer.
- Validate schema, dates, missing values and duplicate records.
- Preserve source metadata.

### FR-02 Data Preprocessing
- Handle missing values according to configured rules.
- Remove/flag duplicates.
- Encode categorical variables where required.
- Scale features where required.
- Prevent future-data leakage.

### FR-03 Statistical Analysis
Calculate and visualize:
- Mean, median and mode where applicable
- Range and dispersion
- Variance and standard deviation
- Returns
- Correlation
- Distributions
- Outliers
- Regression relationships
- Hypothesis tests where appropriate

### FR-04 Feature Engineering
Potential features:
- Lagged returns
- Rolling mean
- Rolling standard deviation
- Momentum
- Volume changes
- Market-index relationship
- Volatility
- Other documented technical/statistical features

### FR-05 ML Engine
Initial supported models:
- Linear Regression
- Multiple Linear Regression
- Logistic Regression
- Decision Tree
- SVM
- Naive Bayes where classification formulation is suitable
- K-Means for unsupervised market-state analysis
- Ensemble model(s)

PCA may be used for dimensionality reduction.

### FR-06 Model Evaluation
For regression:
- MAE
- RMSE
- R²

For classification:
- Accuracy
- Precision
- Recall
- Confusion Matrix

Also report validation methodology and train/test periods.

### FR-07 Prediction
Provide:
- Direction prediction
- Probability for classification
- Regression estimate where implemented
- Model name/version
- Prediction timestamp
- Data cutoff timestamp
- Confidence/uncertainty information when supported

### FR-08 Explainability
Provide:
- Global feature importance
- Local prediction explanation
- SHAP where compatible
- Partial-dependence analysis where useful

### FR-09 Backtesting
- Chronological train/test split.
- Rolling or walk-forward evaluation in advanced mode.
- Actual vs predicted comparison.
- Performance summary.

### FR-10 Visualization
Interactive views:
- Candlestick/price chart
- Volume chart
- Returns chart
- Volatility chart
- Correlation heatmap
- Actual vs predicted
- Model comparison
- Confusion matrix
- Feature importance
- Time-series forecast
- What-if comparison

### FR-11 Dashboard
Dashboard sections:
1. Market Overview
2. Stock Explorer
3. Statistical Analysis
4. Prediction
5. Model Comparison
6. Explainability
7. Backtesting
8. What-If Simulator

## 8. Mathematical/Academic Coverage
The project should demonstrate:
- Probability and distributions
- Expected value and dispersion
- Correlation
- Regression
- Statistical inference
- Hypothesis testing where a valid question exists
- Bias/variance considerations
- Cross-validation where applicable
- Model performance evaluation

## 9. Data Visualization Coverage
The system should demonstrate:
- Appropriate chart selection
- Histograms
- Scatter plots
- Boxplots
- Heatmaps
- Time-series charts
- Interactive plots
- Dashboard storytelling
- KPI cards
- Filters
- ML interpretability visualizations

## 10. Software Engineering Deliverables
- SRS
- Use-case model
- UML diagrams
- Architecture documentation
- Database design
- Modular implementation
- Version control
- Test plan
- Unit/integration/system tests
- Deployment documentation
- Maintenance plan

## 11. Non-Functional Requirements
### Performance
Interactive dashboard operations should normally respond within a few seconds for supported datasets.

### Reliability
Invalid or incomplete data must produce clear validation errors.

### Security
No brokerage credentials or real-money transaction capability in MVP.

### Maintainability
Data, ML, API and visualization layers must be separated.

### Reproducibility
Every trained model must record:
- Dataset version
- Feature configuration
- Training period
- Algorithm
- Hyperparameters
- Evaluation results

## 12. Success Criteria
The project is successful when:
- A dataset can be ingested and validated.
- Statistical analysis can be reproduced.
- At least three ML models can be compared.
- Leakage-free evaluation is demonstrated.
- Predictions and explanations are visible in the dashboard.
- Backtesting produces reproducible results.
- All four academic subject areas are demonstrably covered.

## 13. MVP
MVP includes:
- Historical dataset ingestion
- Preprocessing
- Statistical analysis
- Regression + classification model
- Model evaluation
- Basic explainability
- Backtesting
- Interactive dashboard

## 14. Future Scope
- News/sentiment analysis
- NLP-based market signals
- CNN-based chart/image experiments
- More advanced time-series models
- Paper-trading simulation
- Multi-asset portfolio analysis
- Scheduled data refresh
