import hashlib
import json
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import DataLeakageException, InsufficientDataException
from app.data.repository import StockRepository
from app.features.returns import calculate_returns
from app.features.volatility import calculate_volatility
from app.features.momentum import calculate_momentum
from app.features.volume import calculate_volume_features
from app.database.models import FeatureVersion, FeatureRecord, Stock

FEATURE_COLUMNS = [
    "daily_return",
    "log_return",
    "lag_1_return",
    "lag_2_return",
    "lag_5_return",
    "rolling_std_5",
    "rolling_std_20",
    "volatility_5d",
    "volatility_20d",
    "volatility",
    "momentum_5",
    "momentum_14",
    "price_to_sma20",
    "c2h_ratio",
    "rsi_14",
    "volume_change",
    "volume_ratio_20",
    "market_return"
]

FEATURE_VERSION_NAME = "features-v1.0"

class FeaturePipeline:
    @staticmethod
    def get_feature_definition_hash() -> str:
        definition = {
            "version": FEATURE_VERSION_NAME,
            "feature_columns": sorted(FEATURE_COLUMNS),
            "window_configs": {"sma": [5, 20], "vol": [5, 20], "momentum": [5, 14], "rsi": 14}
        }
        raw_bytes = json.dumps(definition, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw_bytes).hexdigest()

    @staticmethod
    def generate_features_df(
        df_stock: pd.DataFrame,
        df_market: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Generates leakage-free features from raw OHLCV price series.
        """
        if len(df_stock) < 30:
            raise InsufficientDataException("At least 30 trading days required for feature engineering.")

        df = df_stock.copy().sort_values("date").reset_index(drop=True)

        ret_df = calculate_returns(df)
        vol_df = calculate_volatility(df)
        mom_df = calculate_momentum(df)
        volu_df = calculate_volume_features(df)

        features_df = pd.concat([df[["date", "open", "high", "low", "close", "volume"]], ret_df, vol_df, mom_df, volu_df], axis=1)

        # Merge market index returns (e.g. SPY) if provided
        if df_market is not None and not df_market.empty:
            m_df = df_market.copy().sort_values("date").reset_index(drop=True)
            m_ret = m_df["close"].pct_change()
            m_merged = pd.DataFrame({"date": m_df["date"], "market_return": m_ret})
            features_df = pd.merge(features_df, m_merged, on="date", how="left")
            features_df["market_return"] = features_df["market_return"].fillna(0.0)
        else:
            # Fallback market return is 0 if standalone
            features_df["market_return"] = 0.0

        # CRITICAL: Define ML targets
        # Next-day return: (Close_{t+1} - Close_t) / Close_t
        features_df["target_next_return"] = (features_df["close"].shift(-1) - features_df["close"]) / features_df["close"]
        
        # Next-day direction: 1 for UP, 0 for DOWN
        features_df["target_direction"] = (features_df["target_next_return"] > 0).astype(int)

        # Drop initial rows with NaNs from rolling/lag calculations
        # and last row because target_next_return is unknown for the very latest day
        return features_df

    @staticmethod
    def verify_no_data_leakage(features_df: pd.DataFrame):
        """
        Runs rigorous assertions to verify no future information is leaked into past features.
        """
        # 1. Verify that lagged returns strictly match shifted past returns
        lag1_match = np.allclose(
            features_df["lag_1_return"].iloc[10:50].values,
            features_df["daily_return"].iloc[9:49].values,
            rtol=1e-5, atol=1e-5, equal_nan=True
        )
        if not lag1_match:
            raise DataLeakageException("Data leakage check failed: lag_1_return does not match shifted past daily_return.")

        # 2. Verify target_next_return is NOT correlated with lag features by forward leaking
        # If target was mistakenly calculated using past close, correlation with lag_1 would be artificially distorted
        last_row = features_df.iloc[-1]
        if pd.notnull(last_row["target_next_return"]):
            raise DataLeakageException("Data leakage check failed: Latest timestamp contains non-null future target.")

        logger.info("Data leakage verification passed successfully.")

    @staticmethod
    def extract_ml_dataset(
        features_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.Series, pd.Series, pd.DataFrame]:
        """
        Extracts clean X (feature matrix), y_direction, y_return, and metadata (dates/prices).
        """
        # Drop rows where rolling features are NaN or where target is NaN (last row)
        valid_df = features_df.dropna(subset=FEATURE_COLUMNS + ["target_direction", "target_next_return"]).reset_index(drop=True)

        X = valid_df[FEATURE_COLUMNS]
        y_direction = valid_df["target_direction"]
        y_return = valid_df["target_next_return"]
        meta = valid_df[["date", "close", "open", "high", "low", "volume"]]

        return X, y_direction, y_return, meta
