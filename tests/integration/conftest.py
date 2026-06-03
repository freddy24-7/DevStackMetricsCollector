import hashlib
import secrets
import uuid

import psycopg2
import pytest

# Stack must be running via `docker compose up`
DB_DSN = "postgres://metrics_user:metrics_pass@localhost:5432/metrics"
BASE_URL = "http://localhost"


@pytest.fixture(scope="session")
def db():
    conn = psycopg2.connect(DB_DSN)
    conn.autocommit = True
    yield conn
    conn.close()


@pytest.fixture
def test_user(db):
    """Create a Django auth_user row directly and clean up after the test."""
    import hashlib as hl

    user_id = None
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    # Django's unusable password marker — we won't test login through Django here
    password = "!"

    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO auth_user
                (username, password, email, first_name, last_name,
                 is_staff, is_active, is_superuser, date_joined)
            VALUES (%s, %s, %s, %s, %s, false, true, false, now())
            RETURNING id
            """,
            (username, password, f"{username}@example.com", "", ""),
        )
        user_id = cur.fetchone()[0]

    yield {"id": user_id, "username": username}

    with db.cursor() as cur:
        cur.execute("DELETE FROM api_keys WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM auth_user WHERE id = %s", (user_id,))


@pytest.fixture
def test_node(db, test_user):
    """Create a node belonging to test_user and clean up after the test."""
    node_id = str(uuid.uuid4())
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO nodes (id, user_id, hostname, label, created_at)
            VALUES (%s, %s, %s, %s, now())
            """,
            (node_id, test_user["id"], "test-host", "Test Node"),
        )
    yield {"id": node_id, "user_id": test_user["id"]}
    with db.cursor() as cur:
        cur.execute("DELETE FROM metrics WHERE node_id = %s", (node_id,))
        cur.execute("DELETE FROM nodes WHERE id = %s", (node_id,))


@pytest.fixture
def active_api_key(db, test_user):
    """Insert an active API key and return the raw key + its DB id."""
    raw_key = secrets.token_hex(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_id = str(uuid.uuid4())

    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO api_keys (id, user_id, key_hash, created_at)
            VALUES (%s, %s, %s, now())
            """,
            (key_id, test_user["id"], key_hash),
        )
    yield {"id": key_id, "raw_key": raw_key}
    with db.cursor() as cur:
        cur.execute("DELETE FROM api_keys WHERE id = %s", (key_id,))
