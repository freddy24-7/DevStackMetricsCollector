import hashlib
import os
import uuid
from datetime import datetime, timezone

import psycopg2
from flask import Flask, jsonify, request
from pydantic import BaseModel, Field, ValidationError

app = Flask(__name__)

_db_url = os.environ["DATABASE_URL"]


def get_db():
    return psycopg2.connect(_db_url)


class MetricsPayload(BaseModel):
    node_id: uuid.UUID
    cpu_pct: float = Field(ge=0, le=100)
    ram_pct: float = Field(ge=0, le=100)
    disk_pct: float = Field(ge=0, le=100)


def _resolve_api_key(raw_key: str):
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM api_keys WHERE key_hash = %s AND revoked_at IS NULL",
                (key_hash,),
            )
            return cur.fetchone() is not None
    finally:
        conn.close()


@app.route("/api/v1/metrics", methods=["POST"])
def ingest():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"detail": "Missing or invalid Authorization header."}), 401

    raw_key = auth.removeprefix("Bearer ").strip()
    if not _resolve_api_key(raw_key):
        return jsonify({"detail": "Invalid or revoked API key."}), 401

    try:
        payload = MetricsPayload.model_validate(request.get_json(force=True) or {})
    except ValidationError as exc:
        return jsonify({"detail": exc.errors()}), 422

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO metrics (id, node_id, cpu_pct, ram_pct, disk_pct, recorded_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    str(payload.node_id),
                    payload.cpu_pct,
                    payload.ram_pct,
                    payload.disk_pct,
                    datetime.now(timezone.utc),
                ),
            )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"status": "ok"}), 201


@app.route("/health")
def health():
    return jsonify({"status": "ok"})
