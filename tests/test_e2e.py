#!/usr/bin/env python3
"""
E2E browser acceptance tests for web_nav_v2 (啃魂导航 V3).
Uses Playwright sync API.

Run manually in a real terminal: python3 -m pytest tests/test_e2e.py -v --tb=short
Or:                           python3 tests/test_e2e.py

Note: Playwright browser binary must be installed and accessible.
      Run: playwright install chromium
"""

import os
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8080"
PROJECT_ROOT = Path(__file__).parent.parent


def _playwright_available():
    """Check if the Playwright Chromium binary exists."""
    import subprocess
    result = subprocess.run(
        ['playwright', 'install', '--dry-run', 'chromium'],
        capture_output=True, text=True, timeout=5
    )
    # playwright install --dry-run is available >= v1.37, fall back to file check
    cache = Path.home() / '.cache' / 'ms-playwright' / 'chromium_headless_shell-1217'
    if not cache.exists():
        # Try alternate version path
        alt = Path.home() / '.cache' / 'ms-playwright' / 'chromium_headless_shell-1223'
        if not alt.exists():
            return False
    return True


class TestE2E(unittest.TestCase):
    """End-to-end browser integration tests."""

    @classmethod
    def setUpClass(cls):
        if not _playwright_available():
            raise unittest.SkipTest("Playwright Chromium binary not found. Run: playwright install chromium")
        cls._playwright = sync_playwright().start()
        cls.browser = cls._playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls._playwright.stop()

    def setUp(self):
        self.ctx = self.browser.new_context(viewport={"width": 1280, "height": 720})
        self.page = self.ctx.new_page()
        self.errors = []
        self.page.on("console", self._capture_error)
        self.page.on("pageerror", self._capture_page_error)

    def tearDown(self):
        self.ctx.close()

    def _capture_error(self, msg):
        if msg.type == "error":
            self.errors.append(("console", msg.text))

    def _capture_page_error(self, err):
        self.errors.append(("page", str(err)))

    def _load(self):
        resp = self.page.goto(BASE_URL, wait_until="domcontentloaded")
        self.assertIsNotNone(resp, "No response from server")
        self.assertTrue(resp.ok, f"HTTP {resp.status}")
        try:
            self.page.wait_for_selector("#sites-grid", timeout=8000)
        except Exception:
            pass

    # ── Tests ───────────────────────────────────────────

    def test_01_homepage_loads_no_js_errors(self):
        self._load()
        critical = [e for t, e in self.errors if "favicon" not in e.lower()]
        self.assertEqual(len(critical), 0, f"JS errors: {critical}")

    def test_02_critical_elements_exist(self):
        self._load()
        checks = {
            "header": "#header",
            "sidebar": "#sidebar",
            "main_content": "#main-content",
            "search_input": "#search-input",
            "view_switcher": "#view-switcher",
            "view_grid": "#view-grid",
            "view_list": "#view-list",
            "sidebar_toggle": "#sidebar-toggle",
        }
        for name, selector in checks.items():
            el = self.page.query_selector(selector)
            self.assertIsNotNone(el, f"Missing element: {name} ({selector})")

    def test_03_search_by_name_returns_results(self):
        self._load()
        search = self.page.locator("#search-input")
        search.wait_for(state="visible", timeout=5000)
        search.fill("百度")
        self.page.wait_for_timeout(2000)
        count = self.page.locator(".site-card").count()
        self.assertGreater(count, 0, f"Expected results, got {count}")

    def test_04_search_clear_restores_all(self):
        self._load()
        search = self.page.locator("#search-input")
        search.fill("百度")
        self.page.wait_for_timeout(500)
        search.clear()
        self.page.wait_for_timeout(1500)
        count = self.page.locator(".site-card").count()
        self.assertGreater(count, 0, "After clear should show sites")

    def test_05_sidebar_has_nav_items(self):
        self._load()
        nav_items = self.page.locator("#sidebar-content .nav-item")
        self.assertGreater(nav_items.count(), 0)
        texts = nav_items.all_inner_texts()
        self.assertTrue(any("游戏" in t for t in texts), f"No game nav: {texts}")

    def test_06_view_switcher_toggles(self):
        self._load()
        grid_btn = self.page.locator("#view-grid")
        list_btn = self.page.locator("#view-list")

        # Grid active initially (via JS to avoid stale-element-attribute races)
        self.assertTrue(list_btn.is_visible(), "#view-list must be visible after md: rules are applied")
        initial = self.page.evaluate("""() => ({
            g: document.getElementById('view-grid').getAttribute('aria-pressed'),
            l: document.getElementById('view-list').getAttribute('aria-pressed'),
        })""")
        self.assertEqual(initial["g"], "true",  f"Grid not active initially")
        self.assertEqual(initial["l"], "false", f"List not inactive initially")

        # Click list — force=True bypasses actionability guard
        for attempt in range(2):
            try:
                list_btn.click(force=True, timeout=5000)
                self.page.wait_for_timeout(200)
                break
            except Exception:
                if attempt == 1:
                    raise

        # Verify via JS (avoids Playwright stale-element refires)
        after = self.page.evaluate("""() => ({
            g: document.getElementById('view-grid').getAttribute('aria-pressed'),
            l: document.getElementById('view-list').getAttribute('aria-pressed'),
        })""")
        self.assertEqual(after["l"], "true",  f"List button not active after click")
        self.assertEqual(after["g"], "false", f"Grid button still active after list click")

    def test_07_site_cards_have_href(self):
        self._load()
        self.page.wait_for_timeout(1000)
        cards = self.page.locator(".site-card")
        self.assertGreater(cards.count(), 0)
        href = cards.first.get_attribute("href")
        self.assertTrue(href and href.startswith("http"), f"Bad href: {href}")

    def test_08_desktop_layout(self):
        # Use large-enough viewport height so header doesn't push main-content below screen
        self.page.set_viewport_size({"width": 1280, "height": 960})
        self._load()
        self.page.wait_for_timeout(800)
        # Assert via bounding-rect: element must have non-zero dimensions (is rendered and on-screen)
        for sel in ["#header", "#main-content", "#search-input"]:
            rect = self.page.evaluate(f"""sel => {{
                const el = document.querySelector(sel);
                if (!el) return null;
                const r = el.getBoundingClientRect();
                return +(r.width) > 0 && +(r.height) > 0;
            }}""", sel)
            self.assertTrue(rect, f"{sel} has zero or negative size in desktop viewport 1280×960")

    def test_09_mobile_layout(self):
        self.page.set_viewport_size({"width": 375, "height": 667})
        self._load()
        self.page.wait_for_timeout(1000)
        self.assertTrue(self.page.locator("#header").is_visible())
        self.assertTrue(self.page.locator("#main-content").is_visible())
        self.assertTrue(self.page.locator("#search-input").is_visible())

    def test_10_no_local_404_resources(self):
        errors = []
        page = self.page
        def on_response(resp):
            if resp.status == 404 and resp.url.startswith(BASE_URL):
                errors.append(resp.url.replace(BASE_URL, ""))
        page.on("response", on_response)
        self._load()
        page.wait_for_timeout(3000)
        self.assertEqual(len(errors), 0, f"404 resources: {errors}")

    def test_11_game_toggle_present(self):
        self._load()
        self.page.wait_for_timeout(500)
        toggle = self.page.locator("#game-toggle")
        self.assertTrue(toggle.is_visible(), "Game toggle must be visible")
        href = toggle.get_attribute("href")
        self.assertEqual(href, "#game", f"Game toggle href mismatch: {href}")

    def test_12_favorite_buttons_on_cards(self):
        self._load()
        # Wait until at least one site-card is rendered before asserting
        self.page.wait_for_selector(".site-card .favorite-btn", timeout=8000)
        fav_btns = self.page.locator(".site-card .favorite-btn")
        self.assertGreater(fav_btns.count(), 0, "No favorite buttons on cards")


if __name__ == "__main__":
    unittest.main()
