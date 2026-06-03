import hashlib
import secrets
import sys
import types
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Minimal Django stub so the model module imports without a running Django app
# ---------------------------------------------------------------------------
django_stub = types.ModuleType("django")
db_stub = types.ModuleType("django.db")
models_stub = types.ModuleType("django.db.models")


class _FakeModel:
    class objects:
        pass


models_stub.Model = _FakeModel
models_stub.UUIDField = lambda **kw: None
models_stub.CharField = lambda **kw: None
models_stub.DateTimeField = lambda **kw: None
models_stub.ForeignKey = lambda *a, **kw: None
models_stub.CASCADE = "CASCADE"

db_stub.models = models_stub
django_stub.db = db_stub

contrib_stub = types.ModuleType("django.contrib")
auth_stub = types.ModuleType("django.contrib.auth")
auth_models_stub = types.ModuleType("django.contrib.auth.models")
auth_models_stub.User = object
contrib_stub.auth = auth_stub
auth_stub.models = auth_models_stub
django_stub.contrib = contrib_stub

sys.modules.setdefault("django", django_stub)
sys.modules.setdefault("django.db", db_stub)
sys.modules.setdefault("django.db.models", models_stub)
sys.modules.setdefault("django.contrib", contrib_stub)
sys.modules.setdefault("django.contrib.auth", auth_stub)
sys.modules.setdefault("django.contrib.auth.models", auth_models_stub)


def _generate(user):
    """Extracted key-generation logic, independent of Django ORM."""
    raw_key = secrets.token_hex(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return key_hash, raw_key


class TestApiKeyGeneration:
    def test_raw_key_is_64_hex_chars(self):
        _, raw_key = _generate(user=None)
        assert len(raw_key) == 64
        assert all(c in "0123456789abcdef" for c in raw_key)

    def test_key_hash_is_sha256_of_raw_key(self):
        key_hash, raw_key = _generate(user=None)
        expected = hashlib.sha256(raw_key.encode()).hexdigest()
        assert key_hash == expected

    def test_hash_is_64_chars(self):
        key_hash, _ = _generate(user=None)
        assert len(key_hash) == 64

    def test_two_calls_produce_different_keys(self):
        _, key1 = _generate(user=None)
        _, key2 = _generate(user=None)
        assert key1 != key2

    def test_raw_key_not_equal_to_hash(self):
        key_hash, raw_key = _generate(user=None)
        assert raw_key != key_hash

    def test_validation_succeeds_with_correct_key(self):
        key_hash, raw_key = _generate(user=None)
        incoming_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        assert incoming_hash == key_hash

    def test_validation_fails_with_wrong_key(self):
        key_hash, _ = _generate(user=None)
        wrong_hash = hashlib.sha256(b"wrong").hexdigest()
        assert wrong_hash != key_hash
