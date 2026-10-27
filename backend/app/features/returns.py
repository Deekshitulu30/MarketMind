import pandas as pd
import numpy as np

def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes daily return, log return, and lagged returns.
    """
    res = pd.DataFrame(index=df.index)
    close = df["close"]

    res["daily_return"] = close.pct_change()
    res["log_return"] = np.log(close / close.shift(1))
    res["lag_1_return"] = res["daily_return"].shift(1)
    res["lag_2_return"] = res["daily_return"].shift(2)
    res["lag_5_return"] = res["daily_return"].shift(5)

    return res
