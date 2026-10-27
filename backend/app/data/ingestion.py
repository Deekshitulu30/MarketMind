import hashlib
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import InvalidDataException, InvalidSymbolException
from app.database.models import Stock, MarketPrice, DataVersion
from app.data.validation import validate_or_raise
from app.data.cleaning import clean_market_dataframe
from app.data.sample_data import generate_and_save_raw_datasets, DEFAULT_STOCKS

def compute_checksum(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

class DataIngestionService:
    @staticmethod
    def ingest_csv(
        db: Session,
        file_path: Path,
        symbol: str,
        company_name: Optional[str] = None,
        exchange: str = "NASDAQ",
        currency: str = "USD",
        sector: Optional[str] = None,
        source_name: str = "CSV_IMPORT"
    ) -> Dict[str, Any]:
        """
        Validates, cleans, versions, and loads a market CSV dataset into database.
        """
        if not file_path.exists():
            raise InvalidDataException(f"CSV file not found at {file_path}")

        raw_df = pd.read_csv(file_path)
        validate_or_raise(raw_df)

        clean_df, clean_report = clean_market_dataframe(raw_df)
        checksum = compute_checksum(file_path)

        # Save validated clean copy to processed folder
        processed_file = settings.PROCESSED_DATA_DIR / f"{symbol}_processed.parquet"
        clean_df.to_parquet(processed_file, index=False)

        # Register or get DataVersion
        version_name = f"data_{symbol}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        data_ver = db.query(DataVersion).filter_by(checksum=checksum).first()
        if not data_ver:
            data_ver = DataVersion(
                name=version_name,
                source=str(file_path.name),
                checksum=checksum,
                row_count=len(clean_df),
                start_date=clean_df["date"].min(),
                end_date=clean_df["date"].max()
            )
            db.add(data_ver)
            db.flush()

        # Register or get Stock
        stock = db.query(Stock).filter_by(symbol=symbol.upper()).first()
        if not stock:
            stock = Stock(
                symbol=symbol.upper(),
                company_name=company_name or f"{symbol.upper()} Inc.",
                exchange=exchange,
                currency=currency,
                sector=sector
            )
            db.add(stock)
            db.flush()

        # Insert / Update MarketPrices
        # To make it fast, delete existing prices for this stock or bulk upsert
        db.query(MarketPrice).filter_by(stock_id=stock.id).delete()

        price_records = []
        for _, row in clean_df.iterrows():
            price_records.append(
                MarketPrice(
                    stock_id=stock.id,
                    timestamp=pd.to_datetime(row["date"]).to_pydatetime(),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    adjusted_close=float(row.get("adjusted_close", row["close"])),
                    volume=float(row["volume"]),
                    source=source_name,
                    data_version_id=data_ver.id
                )
            )

        db.bulk_save_objects(price_records)
        db.commit()

        logger.info(f"Successfully ingested {len(price_records)} prices for symbol {symbol} (Version: {data_ver.name})")

        return {
            "symbol": stock.symbol,
            "company_name": stock.company_name,
            "rows_ingested": len(price_records),
            "start_date": clean_df["date"].min().strftime("%Y-%m-%d"),
            "end_date": clean_df["date"].max().strftime("%Y-%m-%d"),
            "data_version": data_ver.name,
            "cleaning_report": clean_report
        }

    @staticmethod
    def initialize_default_datasets(db: Session):
        """Generates sample historical datasets and seeds the database if empty."""
        stock_count = db.query(Stock).count()
        if stock_count > 0:
            logger.info("Stock database already contains records. Skipping default seeding.")
            return

        logger.info("Database empty. Generating baseline historical datasets...")
        generate_and_save_raw_datasets(settings.RAW_DATA_DIR)

        for stock_meta in DEFAULT_STOCKS:
            csv_path = settings.RAW_DATA_DIR / f"{stock_meta['symbol']}.csv"
            DataIngestionService.ingest_csv(
                db=db,
                file_path=csv_path,
                symbol=stock_meta["symbol"],
                company_name=stock_meta["company_name"],
                exchange=stock_meta["exchange"],
                sector=stock_meta["sector"],
                source_name="HISTORICAL_SIMULATION"
            )
        logger.info("Default market data seeding complete.")
