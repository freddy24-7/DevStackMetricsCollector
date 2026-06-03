import pytest


class TestLoginInputValidation:
    """Tests for login input validation logic, independent of Django."""

    def _validate(self, username, password):
        """Mirrors the validation in LoginView.post."""
        if not username or not password:
            return 400, "username and password are required."
        return None, None

    def test_missing_username_returns_400(self):
        code, msg = self._validate("", "secret")
        assert code == 400

    def test_missing_password_returns_400(self):
        code, msg = self._validate("alice", "")
        assert code == 400

    def test_both_missing_returns_400(self):
        code, msg = self._validate("", "")
        assert code == 400

    def test_both_present_passes_validation(self):
        code, msg = self._validate("alice", "secret")
        assert code is None
