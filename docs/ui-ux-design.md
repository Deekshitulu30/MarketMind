# MarketMind UI/UX Design

## Direction
A human-designed financial research interface. It should not resemble a generic AI-generated dashboard.

Avoid: neon gradients, excessive glassmorphism, robot/brain artwork, giant “AI-powered” headings, endless identical cards, decorative animation.

Use: restrained typography, whitespace, strong chart hierarchy, subtle borders, compact controls, realistic labels, useful microcopy, and one restrained accent.

## Visual System
- Base: deep charcoal / off-white.
- Positive: muted green.
- Negative: muted red.
- Warning: amber.
- Accent: restrained blue/indigo.
- Radius: 8–12px.
- Shadows: subtle.
- Font: Inter, Geist or IBM Plex Sans.
- Financial figures use tabular numerals.

## Layout
Desktop: ~240px sidebar + flexible analytical canvas + 24px gutters.
Mobile: collapsed navigation, stacked panels, horizontally scrollable dense tables.

## Pages

### Overview
Top: global stock search, date range, data freshness, system status.
Main: large market chart + movers/watchlist.
Lower: model runs, prediction reliability and backtest snapshot.

### Stock Explorer
Symbol/company header → large candlestick/line chart → volume → returns → volatility → compact statistics.

### Statistics Lab
Distribution, boxplot, correlation heatmap, scatter/regression, descriptive statistics and hypothesis testing. Add “What this means” captions.

### Prediction
Do not use a giant BUY/SELL card. Show:
UP
71.4% probability
Expected return +1.2%
Risk Medium
Model/version
Data cutoff
Then show model evidence and historical reliability.

### Explainability
Horizontal feature-contribution chart. Clearly separate positive/negative effects. Only show actual model-derived explanations.

### Backtesting
Actual vs predicted, confusion matrix, metrics by fold and performance over time. Do not hide weak results.

### What-If
Controls on left; baseline vs scenario on right. Freeze baseline and show exactly which inputs changed.

## Human-Made Rules
1. Fewer components, better.
2. Charts get meaningful space.
3. Avoid card overload.
4. Use realistic copy.
5. Animations only for state changes, ~200–250ms.
6. Useful empty states.
7. Never use fake prices, predictions or metrics.
8. Keep filters persistent across navigation.
9. Make uncertainty and data freshness visible.

## Accessibility
Keyboard navigation, visible focus, semantic headings, color plus text/icons, readable legends, accessible tables.
