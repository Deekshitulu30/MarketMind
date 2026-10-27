import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

def generate_stock_history(
    symbol: str,
    start_date: str = "2021-01-01",
    end_date: str = "2025-12-31",
    initial_price: float = 150.0,
    mu: float = 0.0004,  # daily drift (~10% annual)
    sigma: float = 0.015,  # daily volatility (~24% annual)
    seed: int = 42
) -> pd.DataFrame:
    """
    Generates realistic historical OHLCV data using Geometric Brownian Motion
    with intraday volatility and volume relationships.
    """
    np.random.seed(seed)
    date_range = pd.bdate_range(start=start_date, end=end_date)
    n_days = len(date_range)

    # Daily log returns with random shocks
    daily_shocks = np.random.normal(mu - 0.5 * sigma**2, sigma, n_days)
    
    # Add occasional market regime shifts / volatility spikes
    vol_spikes = np.random.binomial(1, 0.05, n_days) * np.random.normal(0, sigma * 2, n_days)
    total_returns = daily_shocks + vol_spikes

    # Generate close prices
    close_prices = initial_price * np.exp(np.cumsum(total_returns))

    opens = []
    highs = []
    lows = []
    volumes = []

    base_volume = {
        "AAPL": 55_000_000,
        "MSFT": 25_000_000,
        "GOOGL": 20_000_000,
        "NVDA": 45_000_000,
        "TSLA": 60_000_000,
        "SPY": 75_000_000
    }.get(symbol, 30_000_000)

    for i in range(n_days):
        prev_close = initial_price if i == 0 else close_prices[i-1]
        curr_close = close_prices[i]

        # Open is near previous close with overnight gap
        gap = np.random.normal(0, sigma * 0.3) * prev_close
        open_p = max(prev_close + gap, 1.0)

        # High is above max(open, close)
        intraday_up = abs(np.random.normal(0, sigma * 0.7)) * max(open_p, curr_close)
        high_p = max(open_p, curr_close) + intraday_up

        # Low is below min(open, close)
        intraday_down = abs(np.random.normal(0, sigma * 0.7)) * min(open_p, curr_close)
        low_p = max(min(open_p, curr_close) - intraday_down, 0.5)

        # Volume correlates with absolute price change + noise
        pct_change = abs(curr_close - prev_close) / prev_close
        vol_multiplier = 1.0 + (pct_change * 15.0) + np.random.normal(0, 0.2)
        vol = max(base_volume * vol_multiplier, 500_000)

        opens.append(round(open_p, 2))
        highs.append(round(high_p, 2))
        lows.append(round(low_p, 2))
        volumes.append(int(vol))

    df = pd.DataFrame({
        "date": date_range.strftime("%Y-%m-%d"),
        "open": opens,
        "high": highs,
        "low": lows,
        "close": [round(c, 2) for c in close_prices],
        "adjusted_close": [round(c, 2) for c in close_prices],
        "volume": volumes
    })
    return df

DEFAULT_STOCKS = [
    {"symbol": "AAPL", "company_name": "Apple Inc.", "exchange": "NASDAQ", "sector": "Technology", "initial_price": 130.0, "sigma": 0.016, "seed": 101},
    {"symbol": "MSFT", "company_name": "Microsoft Corporation", "exchange": "NASDAQ", "sector": "Technology", "initial_price": 220.0, "sigma": 0.015, "seed": 102},
    {"symbol": "GOOGL", "company_name": "Alphabet Inc.", "exchange": "NASDAQ", "sector": "Communication Services", "initial_price": 90.0, "sigma": 0.017, "seed": 103},
    {"symbol": "NVDA", "company_name": "NVIDIA Corporation", "exchange": "NASDAQ", "sector": "Technology", "initial_price": 135.0, "sigma": 0.026, "seed": 104},
    {"symbol": "TSLA", "company_name": "Tesla Inc.", "exchange": "NASDAQ", "sector": "Consumer Cyclical", "initial_price": 240.0, "sigma": 0.032, "seed": 105},
    {"symbol": "SPY", "company_name": "SPDR S&P 500 ETF Trust", "exchange": "NYSE", "sector": "Index ETF", "initial_price": 375.0, "sigma": 0.011, "seed": 106},
]

def generate_and_save_raw_datasets(target_dir: Path) -> List[Path]:
    target_dir.mkdir(parents=True, exist_ok=True)
    saved_files = []
    for stock in DEFAULT_STOCKS:
        df = generate_stock_history(
            symbol=stock["symbol"],
            initial_price=stock["initial_price"],
            sigma=stock["sigma"],
            seed=stock["seed"]
        )
        file_path = target_dir / f"{stock['symbol']}.csv"
        df.to_csv(file_path, index=False)
        saved_files.append(file_path)
    return saved_files
