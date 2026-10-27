import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

def clean_market_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans market data by sorting chronologically, removing duplicates,
    forward-filling small gaps, and computing adjusted close if absent.
    """
    clean_df = df.copy()
    report: Dict[str, Any] = {
        "initial_rows": len(clean_df),
        "duplicates_removed": 0,
        "missing_filled": 0
    }

    # Normalize column names
    clean_df.columns = [c.lower().strip() for c in clean_df.columns]

    # Convert dates with mixed format and drop unparseable rows
    clean_df["date"] = pd.to_datetime(clean_df["date"], format="mixed", errors="coerce")
    bad_rows = clean_df["date"].isna().sum()
    if bad_rows > 0:
        clean_df = clean_df.dropna(subset=["date"])
        report["unparseable_dates_dropped"] = int(bad_rows)

    clean_df = clean_df.sort_values("date").reset_index(drop=True)

    # Drop duplicate timestamps, keeping latest
    initial_len = len(clean_df)
    clean_df = clean_df.drop_duplicates(subset=["date"], keep="last").reset_index(drop=True)
    report["duplicates_removed"] = initial_len - len(clean_df)

    # Convert and coerce numeric columns
    numeric_cols = ["open", "high", "low", "close", "volume"]
    for col in numeric_cols:
        if col in clean_df.columns:
            clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce")
            nulls = clean_df[col].isnull().sum()
            if nulls > 0:
                clean_df[col] = clean_df[col].ffill().bfill()
                report["missing_filled"] += int(nulls)

    # Ensure adjusted_close exists
    if "adjusted_close" not in clean_df.columns:
        clean_df["adjusted_close"] = clean_df["close"]
    else:
        clean_df["adjusted_close"] = clean_df["adjusted_close"].fillna(clean_df["close"])

    report["final_rows"] = len(clean_df)
    return clean_df, report
