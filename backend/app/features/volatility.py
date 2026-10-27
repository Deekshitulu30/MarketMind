import pandas as pd
import numpy as np

def calculate_volatility(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes rolling standard deviations and Parkinson high-low volatility.
    """
    res = pd.DataFrame(index=df.index)
    daily_ret = df["close"].pct_change()

    res["rolling_std_5"] = daily_ret.rolling(window=5).std()
    res["rolling_std_20"] = daily_ret.rolling(window=20).std()
    res["volatility"] = res["rolling_std_20"] * np.sqrt(252)

    # Stationary rolling standard deviations of log returns as defined in architecture specification
    log_ret = np.log(df["close"] / df["close"].shift(1))
    res["volatility_5d"] = log_ret.rolling(window=5).std()
    res["volatility_20d"] = log_ret.rolling(window=20).std()

    # Parkinson intraday volatility estimator
    hl_ratio = np.log(df["high"] / df["low"])**2
    res["parkinson_vol_20"] = np.sqrt((1.0 / (4.0 * np.log(2.0))) * hl_ratio.rolling(window=20).mean() * 252)

    return res
