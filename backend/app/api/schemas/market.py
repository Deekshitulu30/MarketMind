from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class StockSummary(BaseModel):
    id: str
    symbol: str
    company_name: str
    exchange: str
    currency: str
    sector: Optional[str] = None

class PricePoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float
    volume: float

class StockHistoryResponse(BaseModel):
    symbol: str
    company_name: str
    total_records: int
    start_date: str
    end_date: str
    prices: List[PricePoint]

class IngestCsvRequest(BaseModel):
    symbol: str = Field(...)
    company_name: Optional[str] = Field(None)
    exchange: str = Field("NASDAQ")
    currency: str = Field("USD")
    sector: Optional[str] = Field(None)

class StockSearchResult(BaseModel):
    symbol: str
    company_name: str
    exchange: str
    currency: str
    sector: Optional[str] = None
    isin: Optional[str] = None
    tradingview_symbol: str
    yfinance_ticker: str
