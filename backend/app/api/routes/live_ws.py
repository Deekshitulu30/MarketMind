import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.core.logging import logger
from app.services.live_service import LivePriceService

router = APIRouter()

@router.websocket("/ws/live/{symbol}")
async def websocket_live_prediction(
    websocket: WebSocket,
    symbol: str,
    mode: str = Query("fast_demo", description="Streaming mode: 'fast_demo' (3-5s) or 'live_market' (15-30s)")
):
    """
    WebSocket endpoint streaming real-time prices and continuously updated model predictions
    and educational reference levels for an actively viewed stock.
    """
    clean_sym = symbol.strip().upper()
    await websocket.accept()
    logger.info(f"WebSocket client connected for symbol: {clean_sym} (mode={mode})")

    try:
        await LivePriceService.register_client(clean_sym, websocket, mode=mode)
        while True:
            # Receive client control messages or heartbeats
            data_text = await websocket.receive_text()
            try:
                msg = json.loads(data_text)
                action = msg.get("action")
                if action == "SET_MODE":
                    new_mode = msg.get("mode", "fast_demo")
                    await LivePriceService.set_mode(clean_sym, new_mode)
                elif action == "PING":
                    await websocket.send_text(json.dumps({"type": "PONG"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for symbol: {clean_sym}")
    except Exception as e:
        logger.warning(f"WebSocket error for symbol {clean_sym}: {e}")
    finally:
        await LivePriceService.unregister_client(clean_sym, websocket)
