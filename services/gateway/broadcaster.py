import asyncio
import os
from datetime import datetime, timezone
from typing import Any

import psycopg2

_db_url = os.environ["DATABASE_URL"]

# Connected WebSocket clients
_clients: set = set()


def register(ws):
    _clients.add(ws)


def unregister(ws):
    _clients.discard(ws)


async def broadcast(message: dict):
    dead = set()
    for ws in _clients:
        try:
            await ws.send_json(message)
        except Exception:
            dead.add(ws)
    _clients.difference_update(dead)


def _fetch_new_metrics(since: datetime) -> list[dict[str, Any]]:
    conn = psycopg2.connect(_db_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, node_id, cpu_pct, ram_pct, disk_pct, recorded_at
                FROM metrics
                WHERE recorded_at > %s
                ORDER BY recorded_at ASC
                """,
                (since,),
            )
            cols = ["id", "node_id", "cpu_pct", "ram_pct", "disk_pct", "recorded_at"]
            rows = cur.fetchall()
            return [dict(zip(cols, row)) for row in rows]
    finally:
        conn.close()


async def poll_loop(interval: float = 1.0):
    last_seen = datetime.now(timezone.utc)
    while True:
        await asyncio.sleep(interval)
        try:
            rows = _fetch_new_metrics(last_seen)
        except Exception:
            # DB not ready yet (e.g. migrations still running); retry next tick
            continue
        if rows:
            last_seen = rows[-1]["recorded_at"]
            for row in rows:
                await broadcast(
                    {
                        "node_id": str(row["node_id"]),
                        "cpu_pct": float(row["cpu_pct"]),
                        "ram_pct": float(row["ram_pct"]),
                        "disk_pct": float(row["disk_pct"]),
                        "recorded_at": row["recorded_at"].isoformat(),
                    }
                )
