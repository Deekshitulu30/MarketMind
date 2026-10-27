# MarketMind App Flow

## Main Journey
Overview → Stock Explorer → Statistics → Prediction → Explainability → Backtesting → What-If.

## Startup
Browser → Frontend → API health check → fetch stocks/market summary → render Overview.
Never substitute fake market data when the API fails.

## Stock Explorer
Search symbol → validate → load historical prices → render price/volume/return charts → open Statistics.

## Statistics
Load history → returns → descriptive statistics → volatility → distributions → correlation → optional hypothesis test → render charts + interpretation.

## Prediction
Select stock + horizon + approved model → resolve point-in-time features → inference → probability/return → risk calculation → persist prediction → optional explanation.

## Explainability
Prediction → verify explanation support → load exact model/input → SHAP or supported method → persist → render contribution chart.

## Backtesting
Select model/stock/period → create chronological folds → train on past only → predict next period → calculate metrics → aggregate → persist → visualize.

## What-If
Freeze baseline → user changes allowed inputs → validate bounds → run scenario → compare baseline/scenario → show changed inputs and assumptions.

## Error Handling
Service error → structured error code + request ID → friendly frontend message → technical details only in logs.
