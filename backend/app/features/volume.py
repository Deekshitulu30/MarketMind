import pandas as pd
import numpy as np

def calculate_volume_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes volume changes and volume moving average ratios.
    """
    res = pd.DataFrame(index=df.index)
    volume = df["volume"]

    res["volume_change"] = volume.pct_change()
    res["rolling_volume_20"] = volume.rolling(window=20).mean()
    res["volume_ratio_20"] = volume / (res["rolling_volume_20"] + 1e-9)

    return res
