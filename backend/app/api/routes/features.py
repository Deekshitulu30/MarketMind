from typing import Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.data.repository import StockRepository
from app.features.pipeline import FeaturePipeline, FEATURE_COLUMNS, FEATURE_VERSION_NAME

router = APIRouter()

@router.post("/features/generate")
def generate_features(
    symbol: str = Query("AAPL", description="Stock symbol"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    df_stock = StockRepository.get_price_history_df(db, symbol)
    
    df_market = None
    try:
        if symbol.upper() != "SPY":
            df_market = StockRepository.get_price_history_df(db, "SPY")
    except Exception:
        pass

    features_df = FeaturePipeline.generate_features_df(df_stock, df_market)
    FeaturePipeline.verify_no_data_leakage(features_df)

    def_hash = FeaturePipeline.get_feature_definition_hash()

    sample_records = [
        {
            "date": row["date"].strftime("%Y-%m-%d"),
            "daily_return": round(float(row["daily_return"]), 4) if pd_notnull(row["daily_return"]) else None,
            "volatility": round(float(row["volatility"]), 4) if pd_notnull(row["volatility"]) else None,
            "momentum_5": round(float(row["momentum_5"]), 4) if pd_notnull(row["momentum_5"]) else None,
            "rsi_14": round(float(row["rsi_14"]), 2) if pd_notnull(row["rsi_14"]) else None,
            "volume_change": round(float(row["volume_change"]), 4) if pd_notnull(row["volume_change"]) else None,
            "market_return": round(float(row["market_return"]), 4) if pd_notnull(row["market_return"]) else None,
            "target_direction": int(row["target_direction"]) if pd_notnull(row.get("target_direction")) else None
        }
        for _, row in features_df.tail(20).iterrows()
    ]

    return {
        "symbol": symbol.upper(),
        "feature_version": FEATURE_VERSION_NAME,
        "definition_hash": def_hash,
        "total_feature_rows": len(features_df),
        "feature_columns": FEATURE_COLUMNS,
        "sample_tail": sample_records
    }

def pd_notnull(val):
    import pandas as pd
    return pd.notnull(val)
