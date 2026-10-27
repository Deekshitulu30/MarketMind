import pandas as pd
import numpy as np

def calculate_momentum(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes momentum, moving averages, and technical indicators.
    """
    res = pd.DataFrame(index=df.index)
    close = df["close"]

    res["rolling_mean_5"] = close.rolling(window=5).mean()
    res["rolling_mean_20"] = close.rolling(window=20).mean()

    # Rate of change momentum
    res["momentum_5"] = (close - close.shift(5)) / close.shift(5)
    res["momentum_14"] = (close - close.shift(14)) / close.shift(14)

    # Relative position to 20-day MA
    res["price_to_sma20"] = (close - res["rolling_mean_20"]) / res["rolling_mean_20"]

    # Close-to-High (C2H) structural momentum ratio as defined in architecture specification: (Close - Low) / (High - Low)
    hl_range = df["high"] - df["low"]
    res["c2h_ratio"] = np.where(hl_range > 0, (close - df["low"]) / (hl_range + 1e-9), 0.5)

    # RSI (14-period approximation)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    res["rsi_14"] = 100.0 - (100.0 / (1.0 + rs))

    return res
