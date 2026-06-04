"""
E2E tests against the live stack (local or Fly).
Set BASE_URL env var to target a specific deployment.
Default: http://localhost (local docker compose).
"""
import json
import os
import uuid

import pytest
from playwright.sync_api import Page, expect

BASE_URL = os.environ.get("BASE_URL", "http://localhost")
USERNAME = os.environ.get("E2E_USERNAME", "admin")
PASSWORD = os.environ.get("E2E_PASSWORD", "adminpass123")


@pytest.fixture
def page_with_login(page: Page):
    page.goto(BASE_URL)
    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)
    page.click("#login-btn")
    expect(page.locator("#dashboard")).to_be_visible(timeout=8000)
    return page


class TestLoginFlow:
    def test_login_page_loads(self, page: Page):
        page.goto(BASE_URL)
        expect(page.locator("#login-screen")).to_be_visible()
        expect(page.locator("#login-btn")).to_be_visible()

    def test_invalid_credentials_shows_error(self, page: Page):
        page.goto(BASE_URL)
        page.fill("#username", "wrong")
        page.fill("#password", "wrong")
        page.click("#login-btn")
        expect(page.locator("#login-error")).to_be_visible(timeout=5000)

    def test_valid_login_shows_dashboard(self, page: Page):
        page.goto(BASE_URL)
        page.fill("#username", USERNAME)
        page.fill("#password", PASSWORD)
        page.click("#login-btn")
        expect(page.locator("#dashboard")).to_be_visible(timeout=8000)
        expect(page.locator("#login-screen")).to_be_hidden()

    def test_already_logged_in_skips_login(self, page_with_login: Page):
        page_with_login.reload()
        expect(page_with_login.locator("#dashboard")).to_be_visible(timeout=8000)

    def test_logout_returns_to_login(self, page_with_login: Page):
        page_with_login.click("#logout-btn")
        expect(page_with_login.locator("#login-screen")).to_be_visible(timeout=5000)


class TestWebSocketConnection:
    def test_ws_status_shows_live_after_login(self, page_with_login: Page):
        expect(page_with_login.locator("#ws-label")).to_have_text("Live", timeout=8000)
        expect(page_with_login.locator("#ws-dot")).to_have_class("dot connected", timeout=8000)

    def test_ws_reconnects_after_disconnect(self, page_with_login: Page):
        # Simulate disconnect by navigating away and back
        page_with_login.goto(BASE_URL)
        expect(page_with_login.locator("#dashboard")).to_be_visible(timeout=8000)
        expect(page_with_login.locator("#ws-label")).to_have_text("Live", timeout=8000)


class TestLiveMetricsUpdate:
    def test_chart_updates_on_metrics_post(self, page_with_login: Page):
        # Wait for WS to be live
        expect(page_with_login.locator("#ws-label")).to_have_text("Live", timeout=8000)

        # Get the selected node ID from the dropdown
        node_id = page_with_login.eval_on_selector(
            "#node-select", "el => el.value"
        )
        assert node_id, "No node selected — register a node first"

        # POST metrics via fetch from within the page context
        cpu = 88.8
        result = page_with_login.evaluate(f"""
            async () => {{
                const res = await fetch("{BASE_URL}/api/v1/metrics", {{
                    method: "POST",
                    headers: {{
                        "Content-Type": "application/json",
                        "Authorization": "Bearer {os.environ.get('E2E_API_KEY', '')}"
                    }},
                    body: JSON.stringify({{
                        node_id: "{node_id}",
                        cpu_pct: {cpu},
                        ram_pct: 44.4,
                        disk_pct: 22.2
                    }})
                }});
                return res.status;
            }}
        """)
        assert result == 201

        # Wait for the CPU value to update in the UI
        expect(page_with_login.locator("#cpu-value")).to_contain_text("88", timeout=5000)
