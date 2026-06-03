"""
Seam 1: API key lifecycle
  - Active key → Flask returns 201
  - No key → Flask returns 401
  - Wrong key → Flask returns 401
  - Revoked key → Flask returns 401
"""
import uuid

import httpx
import pytest

BASE_URL = "http://localhost"


def _post_metrics(raw_key, node_id):
    return httpx.post(
        f"{BASE_URL}/api/v1/metrics",
        json={
            "node_id": str(node_id),
            "cpu_pct": 10.0,
            "ram_pct": 20.0,
            "disk_pct": 30.0,
        },
        headers={"Authorization": f"Bearer {raw_key}"},
    )


class TestApiKeySeam:
    def test_valid_key_returns_201(self, active_api_key, test_node):
        response = _post_metrics(active_api_key["raw_key"], test_node["id"])
        assert response.status_code == 201

    def test_missing_auth_header_returns_401(self, test_node):
        response = httpx.post(
            f"{BASE_URL}/api/v1/metrics",
            json={"node_id": str(test_node["id"]), "cpu_pct": 1.0, "ram_pct": 1.0, "disk_pct": 1.0},
        )
        assert response.status_code == 401

    def test_wrong_key_returns_401(self, test_node):
        response = _post_metrics("wrong_key_" + "x" * 54, test_node["id"])
        assert response.status_code == 401

    def test_revoked_key_returns_401(self, db, active_api_key, test_node):
        # Revoke the key directly in the DB
        with db.cursor() as cur:
            cur.execute(
                "UPDATE api_keys SET revoked_at = now() WHERE id = %s",
                (active_api_key["id"],),
            )
        response = _post_metrics(active_api_key["raw_key"], test_node["id"])
        assert response.status_code == 401

    def test_invalid_payload_returns_422(self, active_api_key):
        response = httpx.post(
            f"{BASE_URL}/api/v1/metrics",
            json={"node_id": "not-a-uuid", "cpu_pct": 999},
            headers={"Authorization": f"Bearer {active_api_key['raw_key']}"},
        )
        assert response.status_code == 422
