import pandas as pd
from typing import Dict, Any, List, Tuple
from app.core.exceptions import InvalidDataException

REQUIRED_COLUMNS = ["date", "open", "high", "low", "close", "volume"]

def validate_market_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validates market price dataframe for schema integrity, dates, duplicates,
    and OHLC economic consistency.
    """
    errors: List[str] = []

    if df.empty:
        errors.append("Dataset is completely empty.")
        return False, errors

    # Check required columns (case-insensitive conversion)
    df.columns = [c.lower().strip() for c in df.columns]
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
        return False, errors

    # Convert date
    try:
        df["date"] = pd.to_datetime(df["date"])
    except Exception as e:
        errors.append(f"Failed to parse 'date' column into valid timestamps: {str(e)}")
        return False, errors

    # Duplicate dates check
    duplicates = df[df.duplicated(subset=["date"], keep=False)]
    if not duplicates.empty:
        errors.append(f"Found {len(duplicates)} duplicate date records.")

    # Numeric check
    numeric_cols = ["open", "high", "low", "close", "volume"]
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            except Exception:
                errors.append(f"Column '{col}' must contain numeric values.")

        null_count = df[col].isnull().sum()
        if null_count > 0:
            errors.append(f"Column '{col}' contains {null_count} null/NaN values.")

    # OHLC Logic validation
    # High >= Low
    invalid_hl = df[df["high"] < df["low"]]
    if not invalid_hl.empty:
        errors.append(f"High price is strictly less than Low price on {len(invalid_hl)} records.")

    # High >= Open and High >= Close
    invalid_ho = df[df["high"] < df["open"]]
    if not invalid_ho.empty:
        errors.append(f"High price is less than Open price on {len(invalid_ho)} records.")

    invalid_hc = df[df["high"] < df["close"]]
    if not invalid_hc.empty:
        errors.append(f"High price is less than Close price on {len(invalid_hc)} records.")

    # Low <= Open and Low <= Close
    invalid_lo = df[df["low"] > df["open"]]
    if not invalid_lo.empty:
        errors.append(f"Low price is greater than Open price on {len(invalid_lo)} records.")

    invalid_lc = df[df["low"] > df["close"]]
    if not invalid_lc.empty:
        errors.append(f"Low price is greater than Close price on {len(invalid_lc)} records.")

    # Non-negative prices and volume
    for col in ["open", "high", "low", "close", "volume"]:
        neg_count = (df[col] < 0).sum()
        if neg_count > 0:
            errors.append(f"Column '{col}' contains {neg_count} negative values.")

    # Zero prices check
    for col in ["open", "high", "low", "close"]:
        zero_count = (df[col] <= 0).sum()
        if zero_count > 0:
            errors.append(f"Column '{col}' contains {zero_count} zero or non-positive price records.")

    is_valid = len(errors) == 0
    return is_valid, errors

def validate_or_raise(df: pd.DataFrame):
    is_valid, errors = validate_market_dataframe(df)
    if not is_valid:
        raise InvalidDataException(
            "Market data failed schema and domain validation checks.",
            details={"validation_errors": errors}
        )
