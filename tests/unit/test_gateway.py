import os
import sys
import unittest.mock as mock

import pytest

# Point Python at the gateway source before importing anything from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../services/gateway"))

os.environ.setdefault("DATABASE_URL", "postgres://x:x@localhost/x")

# Stub out poll_loop before the app module triggers asyncio.create_task on it
import broadcaster
broadcaster.poll_loop = mock.AsyncMock()

from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_ok_body(self, client):
        response = client.get("/health")
        assert response.json() == {"status": "ok"}


class TestWebSocketEndpoint:
    def test_websocket_accepts_connection(self, client):
        with client.websocket_connect("/ws/metrics") as ws:
            ws.send_text("ping")
