from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.data.repository import StockRepository
from app.data.ingestion import DataIngestionService
from app.core.config import settings
from app.data.symbol_master import SymbolMasterService
from app.api.schemas.market import StockSummary, StockHistoryResponse, PricePoint, StockSearchResult

router = APIRouter()

@router.get("/stocks/search", response_model=List[StockSearchResult])
def search_stocks(
    q: str = Query("", description="Symbol or company name prefix/search term"),
    exchange: Optional[str] = Query(None, description="Filter by exchange (NSE, NASDAQ, NYSE)"),
    limit: int = Query(20, ge=1, le=100)
):
    results = SymbolMasterService.search_symbols(query=q, exchange=exchange, limit=limit)
    return [
        StockSearchResult(
            symbol=r["symbol"],
            company_name=r["company_name"],
            exchange=r["exchange"],
            currency=r["currency"],
            sector=r.get("sector"),
            isin=r.get("isin"),
            tradingview_symbol=r.get("tradingview_symbol", f"{r['exchange']}:{r['symbol']}"),
            yfinance_ticker=r.get("yfinance_ticker", r["symbol"])
        )
        for r in results
    ]

@router.get("/stocks", response_model=List[StockSummary])
def list_stocks(db: Session = Depends(get_db)):
    stocks = StockRepository.get_all_stocks(db)
    return [
        StockSummary(
            id=s.id,
            symbol=s.symbol,
            company_name=s.company_name,
            exchange=s.exchange,
            currency=s.currency,
            sector=s.sector
        )
        for s in stocks
    ]

@router.get("/stocks/{symbol}", response_model=StockSummary)
def get_stock(symbol: str, db: Session = Depends(get_db)):
    s = StockRepository.get_by_symbol(db, symbol)
    return StockSummary(
        id=s.id,
        symbol=s.symbol,
        company_name=s.company_name,
        exchange=s.exchange,
        currency=s.currency,
        sector=s.sector
    )

@router.get("/stocks/{symbol}/history", response_model=StockHistoryResponse)
def get_stock_history(
    symbol: str,
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    dt_start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    dt_end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

    stock = StockRepository.get_by_symbol(db, symbol)
    df = StockRepository.get_price_history_df(db, symbol, dt_start, dt_end)

    def _fmt(d):
        return d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)[:10]

    price_points = [
        PricePoint(
            date=_fmt(row["date"]),
            open=round(float(row["open"]), 2),
            high=round(float(row["high"]), 2),
            low=round(float(row["low"]), 2),
            close=round(float(row["close"]), 2),
            adjusted_close=round(float(row["adjusted_close"]), 2),
            volume=float(row["volume"])
        )
        for _, row in df.iterrows()
    ]

    return StockHistoryResponse(
        symbol=stock.symbol,
        company_name=stock.company_name,
        total_records=len(price_points),
        start_date=_fmt(df["date"].min()),
        end_date=_fmt(df["date"].max()),
        prices=price_points
    )

@router.post("/stocks/ingest")
def ingest_csv_data(
    symbol: str = Form(...),
    company_name: Optional[str] = Form(None),
    exchange: str = Form("NASDAQ"),
    currency: str = Form("USD"),
    sector: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    temp_path = settings.RAW_DATA_DIR / f"{symbol.upper()}_upload.csv"
    with open(temp_path, "wb") as buffer:
        buffer.write(file.file.read())

    result = DataIngestionService.ingest_csv(
        db=db,
        file_path=temp_path,
        symbol=symbol.upper(),
        company_name=company_name,
        exchange=exchange,
        currency=currency,
        sector=sector,
        source_name="USER_CSV_UPLOAD"
    )
    return {"status": "success", "result": result}
