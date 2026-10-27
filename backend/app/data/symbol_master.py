import os
import csv
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.database.models import Stock

SYMBOL_MASTER_DIR = settings.DATA_DIR / "symbol_master"
NSE_MASTER_FILE = SYMBOL_MASTER_DIR / "EQUITY_L.csv"
US_MASTER_FILE = SYMBOL_MASTER_DIR / "us_equities.csv"

# Comprehensive Initial Universe of Top & Midcap Indian Equities (NSE)
NSE_EQUITIES_DATA = [
    {"symbol": "RELIANCE", "name": "Reliance Industries Limited", "sector": "Energy & Petrochemicals", "isin": "INE002A01018", "series": "EQ"},
    {"symbol": "TCS", "name": "Tata Consultancy Services Limited", "sector": "IT Services & Consulting", "isin": "INE467B01029", "series": "EQ"},
    {"symbol": "HDFCBANK", "name": "HDFC Bank Limited", "sector": "Banking & Financial Services", "isin": "INE040A01034", "series": "EQ"},
    {"symbol": "INFY", "name": "Infosys Limited", "sector": "IT Services & Consulting", "isin": "INE009A01021", "series": "EQ"},
    {"symbol": "ICICIBANK", "name": "ICICI Bank Limited", "sector": "Banking & Financial Services", "isin": "INE090A01021", "series": "EQ"},
    {"symbol": "HINDUNILVR", "name": "Hindustan Unilever Limited", "sector": "Consumer Goods (FMCG)", "isin": "INE030A01027", "series": "EQ"},
    {"symbol": "ITC", "name": "ITC Limited", "sector": "Consumer Goods (FMCG)", "isin": "INE154A01025", "series": "EQ"},
    {"symbol": "SBIN", "name": "State Bank of India", "sector": "Public Sector Banking", "isin": "INE062A01020", "series": "EQ"},
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel Limited", "sector": "Telecommunications", "isin": "INE397D01024", "series": "EQ"},
    {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank Limited", "sector": "Banking & Financial Services", "isin": "INE237A01028", "series": "EQ"},
    {"symbol": "LT", "name": "Larsen & Toubro Limited", "sector": "Engineering & Infrastructure", "isin": "INE018A01030", "series": "EQ"},
    {"symbol": "AXISBANK", "name": "Axis Bank Limited", "sector": "Banking & Financial Services", "isin": "INE238A01034", "series": "EQ"},
    {"symbol": "BAJFINANCE", "name": "Bajaj Finance Limited", "sector": "Non-Banking Financial (NBFC)", "isin": "INE296A01024", "series": "EQ"},
    {"symbol": "MARUTI", "name": "Maruti Suzuki India Limited", "sector": "Automobiles", "isin": "INE585B01010", "series": "EQ"},
    {"symbol": "TATAMOTORS", "name": "Tata Motors Limited", "sector": "Automobiles", "isin": "INE155A01022", "series": "EQ"},
    {"symbol": "SUNPHARMA", "name": "Sun Pharmaceutical Industries Limited", "sector": "Pharmaceuticals & Healthcare", "isin": "INE044A01036", "series": "EQ"},
    {"symbol": "TITAN", "name": "Titan Company Limited", "sector": "Consumer Durables & Retail", "isin": "INE280A01028", "series": "EQ"},
    {"symbol": "ULTRACEMCO", "name": "UltraTech Cement Limited", "sector": "Materials & Cement", "isin": "INE481G01011", "series": "EQ"},
    {"symbol": "WIPRO", "name": "Wipro Limited", "sector": "IT Services & Consulting", "isin": "INE075A01022", "series": "EQ"},
    {"symbol": "NTPC", "name": "NTPC Limited", "sector": "Power Generation & Utilities", "isin": "INE733E01010", "series": "EQ"},
    {"symbol": "ONGC", "name": "Oil & Natural Gas Corporation Limited", "sector": "Oil & Gas Exploration", "isin": "INE213A01029", "series": "EQ"},
    {"symbol": "POWERGRID", "name": "Power Grid Corporation of India Limited", "sector": "Power Transmission", "isin": "INE752E01010", "series": "EQ"},
    {"symbol": "JSWSTEEL", "name": "JSW Steel Limited", "sector": "Metals & Mining", "isin": "INE019A01038", "series": "EQ"},
    {"symbol": "TATASTEEL", "name": "Tata Steel Limited", "sector": "Metals & Mining", "isin": "INE081A01020", "series": "EQ"},
    {"symbol": "COALINDIA", "name": "Coal India Limited", "sector": "Mining & Energy", "isin": "INE522F01014", "series": "EQ"},
    {"symbol": "ADANIENT", "name": "Adani Enterprises Limited", "sector": "Diversified Conglomerate", "isin": "INE423A01024", "series": "EQ"},
    {"symbol": "ADANIPORTS", "name": "Adani Ports and Special Economic Zone Limited", "sector": "Infrastructure & Ports", "isin": "INE742F01042", "series": "EQ"},
    {"symbol": "ASIANPAINT", "name": "Asian Paints Limited", "sector": "Paints & Chemicals", "isin": "INE021A01026", "series": "EQ"},
    {"symbol": "BAJAJFINSV", "name": "Bajaj Finserv Limited", "sector": "Financial Services", "isin": "INE918I01026", "series": "EQ"},
    {"symbol": "BPCL", "name": "Bharat Petroleum Corporation Limited", "sector": "Oil Refining & Marketing", "isin": "INE029A01011", "series": "EQ"},
    {"symbol": "BRITANNIA", "name": "Britannia Industries Limited", "sector": "Consumer Goods (FMCG)", "isin": "INE216A01030", "series": "EQ"},
    {"symbol": "CIPLA", "name": "Cipla Limited", "sector": "Pharmaceuticals", "isin": "INE059A01026", "series": "EQ"},
    {"symbol": "DIVISLAB", "name": "Divi's Laboratories Limited", "sector": "Pharmaceuticals & APIs", "isin": "INE361B01024", "series": "EQ"},
    {"symbol": "DRREDDY", "name": "Dr. Reddy's Laboratories Limited", "sector": "Pharmaceuticals", "isin": "INE089A01023", "series": "EQ"},
    {"symbol": "EICHERMOT", "name": "Eicher Motors Limited", "sector": "Automobiles", "isin": "INE066A01021", "series": "EQ"},
    {"symbol": "GRASIM", "name": "Grasim Industries Limited", "sector": "Diversified Materials", "isin": "INE047A01021", "series": "EQ"},
    {"symbol": "HCLTECH", "name": "HCL Technologies Limited", "sector": "IT Services & Consulting", "isin": "INE860A01027", "series": "EQ"},
    {"symbol": "HEROMOTOCO", "name": "Hero MotoCorp Limited", "sector": "Automobiles", "isin": "INE158A01026", "series": "EQ"},
    {"symbol": "HINDALCO", "name": "Hindalco Industries Limited", "sector": "Metals & Mining", "isin": "INE038A01020", "series": "EQ"},
    {"symbol": "INDUSINDBK", "name": "IndusInd Bank Limited", "sector": "Banking & Financial Services", "isin": "INE095A01012", "series": "EQ"},
    {"symbol": "IOC", "name": "Indian Oil Corporation Limited", "sector": "Oil Refining & Marketing", "isin": "INE242A01010", "series": "EQ"},
    {"symbol": "NESTLEIND", "name": "Nestle India Limited", "sector": "Consumer Goods (FMCG)", "isin": "INE239A01024", "series": "EQ"},
    {"symbol": "SBILIFE", "name": "SBI Life Insurance Company Limited", "sector": "Insurance", "isin": "INE123W01016", "series": "EQ"},
    {"symbol": "SHREECEM", "name": "Shree Cement Limited", "sector": "Materials & Cement", "isin": "INE070A01015", "series": "EQ"},
    {"symbol": "TECHM", "name": "Tech Mahindra Limited", "sector": "IT Services & Consulting", "isin": "INE669C01036", "series": "EQ"},
    {"symbol": "TATACONSUM", "name": "Tata Consumer Products Limited", "sector": "Consumer Goods (FMCG)", "isin": "INE192A01025", "series": "EQ"},
    {"symbol": "TRENT", "name": "Trent Limited", "sector": "Retail & Fashion", "isin": "INE849A01020", "series": "EQ"},
    {"symbol": "BEL", "name": "Bharat Electronics Limited", "sector": "Aerospace & Defence", "isin": "INE263A01024", "series": "EQ"},
    {"symbol": "HAL", "name": "Hindustan Aeronautics Limited", "sector": "Aerospace & Defence", "isin": "INE066F01012", "series": "EQ"},
    {"symbol": "IRCTC", "name": "Indian Railway Catering and Tourism Corporation Limited", "sector": "Travel & Hospitality", "isin": "INE335Y01020", "series": "EQ"},
    {"symbol": "ZOMATO", "name": "Zomato Limited", "sector": "Consumer Internet & Delivery", "isin": "INE758T01015", "series": "EQ"},
    {"symbol": "JIOFIN", "name": "Jio Financial Services Limited", "sector": "Financial Services", "isin": "INE758E01017", "series": "EQ"},
    {"symbol": "PAYTM", "name": "One97 Communications Limited (Paytm)", "sector": "Fintech & Payments", "isin": "INE982J01020", "series": "EQ"},
    {"symbol": "NYKAA", "name": "FSN E-Commerce Ventures Limited (Nykaa)", "sector": "E-Commerce & Retail", "isin": "INE388Y01029", "series": "EQ"},
    {"symbol": "POLYCAB", "name": "Polycab India Limited", "sector": "Electrical Cables & Equipment", "isin": "INE455K01017", "series": "EQ"},
    {"symbol": "TATAPOWER", "name": "Tata Power Company Limited", "sector": "Power Generation & Utilities", "isin": "INE245A01021", "series": "EQ"},
    {"symbol": "VEDL", "name": "Vedanta Limited", "sector": "Metals & Natural Resources", "isin": "INE205A01025", "series": "EQ"},
    {"symbol": "DLF", "name": "DLF Limited", "sector": "Real Estate Development", "isin": "INE271C01023", "series": "EQ"},
    {"symbol": "GAIL", "name": "GAIL (India) Limited", "sector": "Natural Gas Transmission", "isin": "INE129A01019", "series": "EQ"},
    {"symbol": "VBL", "name": "Varun Beverages Limited", "sector": "Beverages & FMCG", "isin": "INE200M01021", "series": "EQ"},
    {"symbol": "INDIGO", "name": "InterGlobe Aviation Limited (IndiGo)", "sector": "Aviation & Airlines", "isin": "INE646L01027", "series": "EQ"},
    {"symbol": "PIDILITIND", "name": "Pidilite Industries Limited", "sector": "Specialty Chemicals & Adhesives", "isin": "INE318A01026", "series": "EQ"},
    {"symbol": "SIEMENS", "name": "Siemens Limited", "sector": "Industrial Engineering", "isin": "INE003A01024", "series": "EQ"},
    {"symbol": "BHEL", "name": "Bharat Heavy Electricals Limited", "sector": "Heavy Electrical Equipment", "isin": "INE257A01026", "series": "EQ"},
    {"symbol": "PFC", "name": "Power Finance Corporation Limited", "sector": "Financial Institutions", "isin": "INE134E01011", "series": "EQ"},
    {"symbol": "RECLTD", "name": "REC Limited", "sector": "Financial Institutions", "isin": "INE020B01018", "series": "EQ"},
    {"symbol": "RVNL", "name": "Rail Vikas Nigam Limited", "sector": "Railway Infrastructure", "isin": "INE415G01027", "series": "EQ"},
]

US_EQUITIES_DATA = [
    {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "sector": "Technology", "currency": "USD"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ", "sector": "Technology", "currency": "USD"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "sector": "Semiconductors & Technology", "currency": "USD"},
    {"symbol": "GOOGL", "name": "Alphabet Inc. (Class A)", "exchange": "NASDAQ", "sector": "Communication Services", "currency": "USD"},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ", "sector": "Consumer Cyclical & Cloud", "currency": "USD"},
    {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ", "sector": "Communication Services", "currency": "USD"},
    {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ", "sector": "Automotive & Clean Energy", "currency": "USD"},
    {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "exchange": "NYSE", "sector": "Index ETF", "currency": "USD"},
    {"symbol": "QQQ", "name": "Invesco QQQ Trust", "exchange": "NASDAQ", "sector": "Index ETF", "currency": "USD"},
    {"symbol": "BRK-B", "name": "Berkshire Hathaway Inc.", "exchange": "NYSE", "sector": "Financial Conglomerate", "currency": "USD"},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE", "sector": "Financial Services", "currency": "USD"},
    {"symbol": "V", "name": "Visa Inc.", "exchange": "NYSE", "sector": "Payment Processing", "currency": "USD"},
    {"symbol": "WMT", "name": "Walmart Inc.", "exchange": "NYSE", "sector": "Consumer Defensive & Retail", "currency": "USD"},
    {"symbol": "MA", "name": "Mastercard Incorporated", "exchange": "NYSE", "sector": "Payment Processing", "currency": "USD"},
    {"symbol": "PG", "name": "The Procter & Gamble Company", "exchange": "NYSE", "sector": "Consumer Goods", "currency": "USD"},
    {"symbol": "JNJ", "name": "Johnson & Johnson", "exchange": "NYSE", "sector": "Healthcare & Pharmaceuticals", "currency": "USD"},
    {"symbol": "UNH", "name": "UnitedHealth Group Incorporated", "exchange": "NYSE", "sector": "Managed Healthcare", "currency": "USD"},
    {"symbol": "HD", "name": "The Home Depot Inc.", "exchange": "NYSE", "sector": "Home Improvement Retail", "currency": "USD"},
    {"symbol": "DIS", "name": "The Walt Disney Company", "exchange": "NYSE", "sector": "Entertainment & Media", "currency": "USD"},
    {"symbol": "NFLX", "name": "Netflix Inc.", "exchange": "NASDAQ", "sector": "Streaming & Media", "currency": "USD"},
    {"symbol": "AMD", "name": "Advanced Micro Devices Inc.", "exchange": "NASDAQ", "sector": "Semiconductors", "currency": "USD"},
    {"symbol": "INTC", "name": "Intel Corporation", "exchange": "NASDAQ", "sector": "Semiconductors", "currency": "USD"},
    {"symbol": "CRM", "name": "Salesforce Inc.", "exchange": "NYSE", "sector": "Enterprise Software & Cloud", "currency": "USD"},
    {"symbol": "ADBE", "name": "Adobe Inc.", "exchange": "NASDAQ", "sector": "Software & Creative Cloud", "currency": "USD"},
    {"symbol": "PYPL", "name": "PayPal Holdings Inc.", "exchange": "NASDAQ", "sector": "Digital Payments", "currency": "USD"},
    {"symbol": "COST", "name": "Costco Wholesale Corporation", "exchange": "NASDAQ", "sector": "Consumer Defensive", "currency": "USD"},
    {"symbol": "PEP", "name": "PepsiCo Inc.", "exchange": "NASDAQ", "sector": "Consumer Staples", "currency": "USD"},
    {"symbol": "KO", "name": "The Coca-Cola Company", "exchange": "NYSE", "sector": "Consumer Staples", "currency": "USD"},
    {"symbol": "XOM", "name": "Exxon Mobil Corporation", "exchange": "NYSE", "sector": "Energy & Oil", "currency": "USD"},
    {"symbol": "CVX", "name": "Chevron Corporation", "exchange": "NYSE", "sector": "Energy & Oil", "currency": "USD"},
    {"symbol": "NKE", "name": "NIKE Inc.", "exchange": "NYSE", "sector": "Apparel & Footwear", "currency": "USD"},
    {"symbol": "LLY", "name": "Eli Lilly and Company", "exchange": "NYSE", "sector": "Pharmaceuticals", "currency": "USD"},
    {"symbol": "AVGO", "name": "Broadcom Inc.", "exchange": "NASDAQ", "sector": "Semiconductors", "currency": "USD"},
    {"symbol": "ORCL", "name": "Oracle Corporation", "exchange": "NYSE", "sector": "Database & Cloud Software", "currency": "USD"},
    {"symbol": "BAC", "name": "Bank of America Corporation", "exchange": "NYSE", "sector": "Banking & Financial Services", "currency": "USD"},
    {"symbol": "CSCO", "name": "Cisco Systems Inc.", "exchange": "NASDAQ", "sector": "Networking Hardware", "currency": "USD"},
    {"symbol": "ACN", "name": "Accenture plc", "exchange": "NYSE", "sector": "IT Consulting & Services", "currency": "USD"},
    {"symbol": "MRK", "name": "Merck & Co. Inc.", "exchange": "NYSE", "sector": "Pharmaceuticals", "currency": "USD"},
    {"symbol": "TMO", "name": "Thermo Fisher Scientific Inc.", "exchange": "NYSE", "sector": "Life Sciences Tools", "currency": "USD"},
    {"symbol": "ABT", "name": "Abbott Laboratories", "exchange": "NYSE", "sector": "Medical Devices & Healthcare", "currency": "USD"},
    {"symbol": "QCOM", "name": "Qualcomm Incorporated", "exchange": "NASDAQ", "sector": "Wireless Telecom & Chips", "currency": "USD"},
    {"symbol": "TXN", "name": "Texas Instruments Incorporated", "exchange": "NASDAQ", "sector": "Semiconductors", "currency": "USD"},
]

class SymbolMasterService:
    _master_symbols_cache: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def ensure_master_files_exist(cls):
        SYMBOL_MASTER_DIR.mkdir(parents=True, exist_ok=True)
        if not NSE_MASTER_FILE.exists():
            df_nse = pd.DataFrame([
                {
                    "SYMBOL": item["symbol"],
                    "NAME OF COMPANY": item["name"],
                    "SERIES": item["series"],
                    "DATE OF LISTING": "01-JAN-2000",
                    "PAID UP VALUE": 10,
                    "MARKET LOT": 1,
                    "ISIN NUMBER": item["isin"],
                    "FACE VALUE": 10,
                    "SECTOR": item["sector"]
                }
                for item in NSE_EQUITIES_DATA
            ])
            df_nse.to_csv(NSE_MASTER_FILE, index=False)
            logger.info(f"Created NSE equity master directory at {NSE_MASTER_FILE}")

        if not US_MASTER_FILE.exists():
            df_us = pd.DataFrame([
                {
                    "SYMBOL": item["symbol"],
                    "NAME OF COMPANY": item["name"],
                    "EXCHANGE": item["exchange"],
                    "SECTOR": item["sector"],
                    "CURRENCY": item["currency"]
                }
                for item in US_EQUITIES_DATA
            ])
            df_us.to_csv(US_MASTER_FILE, index=False)
            logger.info(f"Created US equity master directory at {US_MASTER_FILE}")

    @classmethod
    def get_all_master_symbols(cls) -> List[Dict[str, Any]]:
        if cls._master_symbols_cache is not None:
            return cls._master_symbols_cache

        cls.ensure_master_files_exist()
        symbols = []

        # Load NSE
        if NSE_MASTER_FILE.exists():
            try:
                df_nse = pd.read_csv(NSE_MASTER_FILE)
                for _, row in df_nse.iterrows():
                    sym = str(row["SYMBOL"]).strip().upper()
                    symbols.append({
                        "symbol": sym,
                        "company_name": str(row.get("NAME OF COMPANY", sym)),
                        "exchange": "NSE",
                        "currency": "INR",
                        "sector": str(row.get("SECTOR", "Equities")),
                        "isin": str(row.get("ISIN NUMBER", "")),
                        "tradingview_symbol": f"NSE:{sym}",
                        "yfinance_ticker": f"{sym}.NS"
                    })
            except Exception as e:
                logger.error(f"Failed to read NSE master CSV: {e}")

        # Load US
        if US_MASTER_FILE.exists():
            try:
                df_us = pd.read_csv(US_MASTER_FILE)
                for _, row in df_us.iterrows():
                    sym = str(row["SYMBOL"]).strip().upper()
                    exchange = str(row.get("EXCHANGE", "NASDAQ")).strip().upper()
                    symbols.append({
                        "symbol": sym,
                        "company_name": str(row.get("NAME OF COMPANY", sym)),
                        "exchange": exchange,
                        "currency": str(row.get("CURRENCY", "USD")),
                        "sector": str(row.get("SECTOR", "Equities")),
                        "isin": "",
                        "tradingview_symbol": f"{exchange}:{sym}",
                        "yfinance_ticker": sym
                    })
            except Exception as e:
                logger.error(f"Failed to read US master CSV: {e}")

        cls._master_symbols_cache = symbols
        return symbols

    @classmethod
    def search_symbols(
        cls,
        query: str,
        exchange: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        all_syms = cls.get_all_master_symbols()
        q = query.strip().upper() if query else ""
        
        results = []
        for s in all_syms:
            if exchange and exchange.upper() != "ALL" and s["exchange"] != exchange.upper():
                continue
            
            if not q:
                results.append(s)
            else:
                # Prefix symbol match gets highest priority
                if s["symbol"].startswith(q):
                    score = 100 - len(s["symbol"])
                    results.append((score, s))
                elif q in s["symbol"]:
                    score = 50 - len(s["symbol"])
                    results.append((score, s))
                elif q.lower() in s["company_name"].lower():
                    score = 30
                    results.append((score, s))
                elif q.lower() in s["sector"].lower():
                    score = 10
                    results.append((score, s))

        if q:
            # Sort by score desc, then symbol
            results.sort(key=lambda x: (-x[0], x[1]["symbol"]))
            filtered = [r[1] for r in results]
        else:
            filtered = results

        return filtered[:limit]

    @classmethod
    def get_symbol_metadata(cls, symbol: str) -> Optional[Dict[str, Any]]:
        clean_sym = symbol.strip().upper()
        # Handle suffix like .NS
        if clean_sym.endswith(".NS"):
            clean_sym = clean_sym.replace(".NS", "")

        for s in cls.get_all_master_symbols():
            if s["symbol"] == clean_sym:
                return s

        # Default fallback metadata
        is_nse = not any(c in clean_sym for c in ["^", "="]) and len(clean_sym) > 4
        return {
            "symbol": clean_sym,
            "company_name": f"{clean_sym} Corporation",
            "exchange": "NSE" if is_nse else "NASDAQ",
            "currency": "INR" if is_nse else "USD",
            "sector": "Equities",
            "isin": "",
            "tradingview_symbol": f"NSE:{clean_sym}" if is_nse else f"NASDAQ:{clean_sym}",
            "yfinance_ticker": f"{clean_sym}.NS" if is_nse else clean_sym
        }

    @classmethod
    def is_known_symbol(cls, symbol: str) -> bool:
        """Checks if a symbol is recognized in the master universe or local stock datasets."""
        clean_sym = symbol.strip().upper()
        if clean_sym.endswith(".NS"):
            clean_sym = clean_sym.replace(".NS", "")

        for s in cls.get_all_master_symbols():
            if s["symbol"] == clean_sym:
                return True

        candidates = [
            settings.STOCKS_DIR / f"{clean_sym}.csv",
            settings.STOCKS_DIR / f"{clean_sym.lower()}.csv",
            settings.ETFS_DIR / f"{clean_sym}.csv",
            settings.ETFS_DIR / f"{clean_sym.lower()}.csv",
            settings.RAW_DATA_DIR / f"{clean_sym}.csv"
        ]
        return any(c.exists() for c in candidates)

