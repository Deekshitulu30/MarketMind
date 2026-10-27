import asyncio
import json
import random
from datetime import datetime
from typing import Dict, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.database.session import SessionLocal
from app.data.repository import StockRepository
from app.services.prediction_service import PredictionService
from app.data.symbol_master import SymbolMasterService

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

class LivePriceService:
    """
    Manages live WebSocket streaming, subscription lifecycles, and asynchronous
    prediction re-evaluation upon real-time price updates or candle ticks.
    """
    _subscribers: Dict[str, Set[WebSocket]] = {}
    _tasks: Dict[str, asyncio.Task] = {}
    _cached_snapshots: Dict[str, Dict[str, Any]] = {}
    _latest_prices: Dict[str, float] = {}
    _polling_modes: Dict[str, str] = {}  # 'fast_demo' (3-5s) vs 'live_market' (15-30s)
    _lock = asyncio.Lock()

    @classmethod
    async def get_initial_snapshot(cls, symbol: str) -> Dict[str, Any]:
        clean_sym = symbol.strip().upper()
        if clean_sym in cls._cached_snapshots:
            snapshot = dict(cls._cached_snapshots[clean_sym])
            snapshot["is_cached"] = True
            snapshot["timestamp"] = datetime.utcnow().isoformat()
            return snapshot

        db: Session = SessionLocal()
        try:
            pred = PredictionService.generate_prediction(db=db, symbol=clean_sym)
            pred["type"] = "INITIAL_SNAPSHOT"
            pred["is_live"] = True
            pred["timestamp"] = datetime.utcnow().isoformat()
            cls._cached_snapshots[clean_sym] = pred
            cls._latest_prices[clean_sym] = float(pred.get("current_price", 150.0))
            return pred
        except Exception as e:
            logger.error(f"Error generating initial snapshot for {clean_sym}: {e}")
            return {
                "type": "ERROR",
                "symbol": clean_sym,
                "message": f"Failed to compute initial prediction: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            db.close()

    @classmethod
    async def register_client(cls, symbol: str, websocket: WebSocket, mode: str = "fast_demo"):
        clean_sym = symbol.strip().upper()
        async with cls._lock:
            if clean_sym not in cls._subscribers:
                cls._subscribers[clean_sym] = set()
            cls._subscribers[clean_sym].add(websocket)
            cls._polling_modes[clean_sym] = mode

            # Start background polling task for this symbol if not already active
            if clean_sym not in cls._tasks or cls._tasks[clean_sym].done():
                logger.info(f"Starting LivePriceService streaming task for {clean_sym} (mode={mode})")
                cls._tasks[clean_sym] = asyncio.create_task(cls._stream_loop(clean_sym))

        # Send initial snapshot immediately to the connected client
        initial_payload = await cls.get_initial_snapshot(clean_sym)
        try:
            await websocket.send_text(json.dumps(initial_payload))
        except Exception as e:
            logger.warning(f"Failed to send initial snapshot to client for {clean_sym}: {e}")

    @classmethod
    async def unregister_client(cls, symbol: str, websocket: WebSocket):
        clean_sym = symbol.strip().upper()
        async with cls._lock:
            if clean_sym in cls._subscribers:
                cls._subscribers[clean_sym].discard(websocket)
                if len(cls._subscribers[clean_sym]) == 0:
                    logger.info(f"0 active subscribers for {clean_sym}. Scheduling task wind-down.")
                    # Let the loop terminate cleanly on its next iteration

    @classmethod
    async def set_mode(cls, symbol: str, mode: str):
        clean_sym = symbol.strip().upper()
        async with cls._lock:
            cls._polling_modes[clean_sym] = mode

    @classmethod
    async def broadcast_to_symbol(cls, symbol: str, message: Dict[str, Any]):
        clean_sym = symbol.strip().upper()
        clients = list(cls._subscribers.get(clean_sym, []))
        if not clients:
            return

        dead_clients = []
        msg_text = json.dumps(message)
        for client in clients:
            try:
                await client.send_text(msg_text)
            except Exception:
                dead_clients.append(client)

        if dead_clients:
            async with cls._lock:
                for dc in dead_clients:
                    cls._subscribers.get(clean_sym, set()).discard(dc)

    @classmethod
    async def _fetch_live_quote(cls, symbol: str) -> Optional[float]:
        """Fetches the latest live quote via yfinance if available."""
        if not YFINANCE_AVAILABLE:
            return None
        try:
            meta = SymbolMasterService.get_symbol_metadata(symbol)
            yf_ticker = meta.get("yfinance_ticker", symbol)
            ticker_obj = yf.Ticker(yf_ticker)
            fast_info = getattr(ticker_obj, 'fast_info', None)
            if fast_info and 'last_price' in fast_info and fast_info['last_price'] is not None:
                return float(fast_info['last_price'])
            
            hist = ticker_obj.history(period="1d", interval="1m")
            if hist is not None and len(hist) > 0 and 'Close' in hist:
                return float(hist['Close'].iloc[-1])
        except Exception as e:
            logger.debug(f"Live quote fetch error for {symbol}: {e}")
        return None

    @classmethod
    async def _stream_loop(cls, symbol: str):
        """
        Continuously produces live price ticks, updates the feature cutoff state,
        re-evaluates model predictions and educational reference levels, and broadcasts updates.
        """
        clean_sym = symbol.strip().upper()
        idle_counter = 0

        # Base price tracking
        base_price = cls._latest_prices.get(clean_sym, 150.0)

        while True:
            # Check subscriber count
            sub_count = len(cls._subscribers.get(clean_sym, set()))
            if sub_count == 0:
                idle_counter += 1
                if idle_counter > 12:  # ~60 seconds grace period
                    logger.info(f"Stopping live stream task for {clean_sym} due to lack of subscribers.")
                    break
            else:
                idle_counter = 0

            mode = cls._polling_modes.get(clean_sym, "fast_demo")
            interval = 3.5 if mode == "fast_demo" else 15.0
            await asyncio.sleep(interval)

            if len(cls._subscribers.get(clean_sym, set())) == 0:
                continue

            try:
                # 1. Determine new price
                new_price = None
                if mode == "live_market":
                    new_price = await cls._fetch_live_quote(clean_sym)

                if new_price is None or new_price <= 0:
                    # Realistic Brownian motion tick: slight drift + volatility shock
                    curr_p = cls._latest_prices.get(clean_sym, base_price)
                    # Gaussian shock with 0.15% standard deviation
                    shock = random.gauss(0.0002, 0.0018)
                    new_price = round(curr_p * (1.0 + shock), 2)

                prev_price = cls._latest_prices.get(clean_sym, new_price)
                price_delta = round(new_price - prev_price, 2)
                price_delta_pct = round((price_delta / prev_price) * 100, 3) if prev_price > 0 else 0.0
                cls._latest_prices[clean_sym] = new_price

                # 2. Re-run prediction service with live price
                db: Session = SessionLocal()
                try:
                    updated_pred = PredictionService.generate_prediction(
                        db=db,
                        symbol=clean_sym,
                        live_price=new_price
                    )
                    updated_pred["type"] = "PREDICTION_UPDATE"
                    updated_pred["is_live"] = True
                    updated_pred["stream_mode"] = mode
                    updated_pred["price_change"] = price_delta
                    updated_pred["price_change_pct"] = price_delta_pct
                    updated_pred["timestamp"] = datetime.utcnow().isoformat()

                    cls._cached_snapshots[clean_sym] = updated_pred

                    # 3. Broadcast to all active viewers
                    await cls.broadcast_to_symbol(clean_sym, updated_pred)
                finally:
                    db.close()

            except Exception as e:
                logger.error(f"Error in LivePriceService stream loop for {clean_sym}: {e}")
                await asyncio.sleep(2.0)
