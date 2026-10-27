import pytest
import json
from fastapi.testclient import TestClient
from app.main import app
from app.services.live_service import LivePriceService

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.mark.asyncio
async def test_live_price_service_snapshot():
    snapshot = await LivePriceService.get_initial_snapshot("AAPL")
    assert snapshot is not None
    assert snapshot["symbol"] == "AAPL"
    assert "predicted_direction" in snapshot
    assert "probability_up_pct" in snapshot
    assert "reference_levels" in snapshot
    assert snapshot["reference_levels"]["is_educational_reference"] is True

def test_websocket_live_connection(client):
    with client.websocket_connect("/api/v1/ws/live/AAPL?mode=fast_demo") as websocket:
        # Receive immediate snapshot on connect (0 latency)
        data = websocket.receive_text()
        payload = json.loads(data)

        assert payload["symbol"] == "AAPL"
        assert payload["predicted_direction"] in ["UP", "DOWN"]
        assert "reference_levels" in payload
        assert payload["reference_levels"]["reference_target"]["label"] == "Model Reference Target (educational)"
        assert payload["reference_levels"]["reference_stop_loss"]["label"] == "Model Reference Stop-Loss (educational)"

        # Send PING heartbeat
        websocket.send_text(json.dumps({"action": "PING"}))
        pong = websocket.receive_text()
        pong_payload = json.loads(pong)
        assert pong_payload.get("type") == "PONG"
