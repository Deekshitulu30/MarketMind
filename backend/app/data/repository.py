import pandas as pd
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.database.models import Stock, MarketPrice
from app.core.exceptions import InvalidSymbolException, InsufficientDataException

class StockRepository:
    @staticmethod
    def get_all_stocks(db: Session) -> List[Stock]:
        return db.query(Stock).order_by(Stock.symbol).all()

    @staticmethod
    def get_by_symbol(db: Session, symbol: str) -> Stock:
        from app.data.fetcher import OnDemandDataFetcher
        clean_sym = symbol.strip().upper()
        if clean_sym.endswith(".NS"):
            clean_sym = clean_sym.replace(".NS", "")

        stock = db.query(Stock).filter_by(symbol=clean_sym).first()
        if not stock:
            # Trigger on-demand whole-exchange fetch
            stock = OnDemandDataFetcher.ensure_stock_data_available(db, clean_sym)
        return stock

    @staticmethod
    def get_price_history_df(
        db: Session,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        stock = StockRepository.get_by_symbol(db, symbol)

        query = db.query(MarketPrice).filter(MarketPrice.stock_id == stock.id)
        if start_date:
            query = query.filter(MarketPrice.timestamp >= start_date)
        if end_date:
            query = query.filter(MarketPrice.timestamp <= end_date)

        prices = query.order_by(MarketPrice.timestamp.asc()).all()
        if not prices:
            # Try refreshing via on-demand fetcher
            from app.data.fetcher import OnDemandDataFetcher
            stock = OnDemandDataFetcher.ensure_stock_data_available(db, symbol, force_refresh=True)
            query = db.query(MarketPrice).filter(MarketPrice.stock_id == stock.id)
            if start_date:
                query = query.filter(MarketPrice.timestamp >= start_date)
            if end_date:
                query = query.filter(MarketPrice.timestamp <= end_date)
            prices = query.order_by(MarketPrice.timestamp.asc()).all()

        if not prices:
            raise InsufficientDataException(f"No price records found for symbol '{symbol}' in requested period.")

        data = [{
            "date": p.timestamp,
            "open": p.open,
            "high": p.high,
            "low": p.low,
            "close": p.close,
            "adjusted_close": p.adjusted_close,
            "volume": p.volume
        } for p in prices]

        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        return df
