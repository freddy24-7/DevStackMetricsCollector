"""
Seam 2: Broadcast pipeline
  POST to Flask → metrics table written → FastAPI poll loop picks it up
  → WebSocket client receives the message within 2 seconds.
"""
import asyncio
import json

import httpx
import pytest
import websockets

WS_URL = "ws://localhost/ws/metrics"
BASE_URL = "http://localhost"


@pytest.mark.asyncio
async def test_post_metrics_broadcasts_to_websocket(active_api_key, test_node):
    received = []

    async with websockets.connect(WS_URL) as ws:
        # POST metrics after the WebSocket is connected
        response = httpx.post(
            f"{BASE_URL}/api/v1/metrics",
            json={
                "node_id": str(test_node["id"]),
                "cpu_pct": 11.1,
                "ram_pct": 22.2,
                "disk_pct": 33.3,
            },
            headers={"Authorization": f"Bearer {active_api_key['raw_key']}"},
        )
        assert response.status_code == 201

        # Wait up to 2s for the broadcast to arrive
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
            received.append(json.loads(raw))
        except asyncio.TimeoutError:
            pass

    assert len(received) == 1, "WebSocket did not receive a message within 2 seconds"
    msg = received[0]
    assert msg["node_id"] == str(test_node["id"])
    assert abs(msg["cpu_pct"] - 11.1) < 0.01
    assert abs(msg["ram_pct"] - 22.2) < 0.01
    assert abs(msg["disk_pct"] - 33.3) < 0.01
