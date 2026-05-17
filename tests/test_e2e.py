#!/usr/bin/env python3
"""
E2E browser acceptance tests for web_nav_v2 (啃魂导航 V3).
Uses Playwright sync API.

Run: python3 -m pytest tests/test_e2e.py -v --tb=short
Or:  python3 -m unittest tests.test_e2e
"""

import os
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8080"
PROJECT_ROOT = Path(__file__).parent.parent


class TestE2E(unittest.TestCase):
    """End-to-end browser integration tests."""

    @classmethod
    def setUpClass(cls):
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
        """Navigate to homepage and wait for content."""
        resp = self.page.goto(BASE_URL, wait_until="domcontentloaded")
        self.assertIsNotNone(resp, "No response from server")
        self.assertTrue(resp.ok, f"HTTP {resp.status}")
        # sites-grid is injected by JS — wait for app root or timeout
        try:
            self.page.wait_for_selector("#sites-grid", timeout=8000)
        except Exception:
            pass  # grid may not be rendered if apps fails; test will fail on specific assertions

    # ── Tests ───────────────────────────────────────────

    def test_01_homepage_loads_no_js_errors(self):
        """Homepage loads with 200 and no JS errors."""
        self._load()
        # Filter out favicon/icon warnings
        critical = [
            e for t, e in self.errors
            if "favicon" not in e.lower()
        ]
        self.assertEqual(
            len(critical), 0,
            f"JS errors on page load: {critical}"
        )

    def test_02_critical_elements_exist(self):
        """All critical page elements are present."""
        self._load()
        checks = {
            "header": "#header",
            "sidebar": "#sidebar",
            "main_content": "#main-content",
            "search_input": "#search-input",
            "site_grid": "#sites-grid",
            "view_switcher": "#view-switcher",
            "view_grid": "#view-grid",
            "view_list": "#view-list",
            "sidebar_toggle": "#sidebar-toggle",
        }
        for name, selector in checks.items():
            el = self.page.query_selector(selector)
            self.assertIsNotNone(el, f"Missing element: {name} ({selector})")

    def test_03_search_by_name_returns_results(self):
        """Search by site name returns results."""
        self._load()
        search = self.page.locator("#search-input")
        search.wait_for(state="visible", timeout=5000)
        search.fill("百度")
        self.page.wait_for_timeout(2000)
        count = self.page.locator(".site-card").count()
        self.assertGreater(count, 0, f"Expected search results, got {count}")

    def test_04_search_clear_restores_all(self):
        """Clearing search restores full site list."""
        self._load()
        search = self.page.locator("#search-input")
        search.fill("百度")
        self.page.wait_for_timeout(500)
        search.clear()
        self.page.wait_for_timeout(1500)
        count = self.page.locator(".site-card").count()
        self.assertGreater(count, 0, "Clearing search should show sites")

    def test_05_sidebar_has_nav_items(self):
        """Sidebar has navigation category items."""
        self._load()
        nav_items = self.page.locator("#sidebar-content .nav-item")
        count = nav_items.count()
        self.assertGreater(count, 0, f"No nav items in sidebar, got {count}")
        texts = nav_items.all_inner_texts()
        has_games = any("游戏" in t for t in texts)
        self.assertTrue(has_games, f"Expected 游戏 nav item, got: {texts}")

    def test_06_view_switcher_toggles(self):
        """View switcher buttons toggle active state on click."""
        self._load()
        grid_btn = self.page.locator("#view-grid")
        list_btn = self.page.locator("#view-list")

        # Grid active initially
        self.assertEqual(grid_btn.get_attribute("aria-pressed"), "true")
        self.assertEqual(list_btn.get_attribute("aria-pressed"), "false")

        # Click list view
        list_btn.click()
        self.page.wait_for_timeout(500)

        # States should swap
        self.assertEqual(list_btn.get_attribute("aria-pressed"), "true")
        self.assertEqual(grid_btn.get_attribute("aria-pressed"), "false")

    def test_07_site_cards_have_href(self):
        """Site cards have valid http/https href."""
        self._load()
        cards = self.page.locator(".site-card")
        count = cards.count()
        self.assertGreater(count, 0, "No site cards found")
        href = cards.first.get_attribute("href")
        self.assertTrue(
            href and href.startswith("http"),
            f"Card href missing or invalid: {href}"
        )

    def test_08_desktop_layout(self):
        """Desktop viewport renders all key elements."""
        self.page.set_viewport_size({"width": 1280, "height": 720})
        self._load()
        self.assertTrue(self.page.locator("#header").is_visible())
        self.assertTrue(self.page.locator("#main-content").is_visible())
        self.assertTrue(self.page.locator("#search-input").is_visible())

    def test_09_mobile_layout(self):
        """Mobile viewport renders without breakage."""
        self.page.set_viewport_size({"width": 375, "height": 667})
        self._load()
        self.assertTrue(self.page.locator("#header").is_visible())
        self.assertTrue(self.page.locator("#main-content").is_visible())
        self.assertTrue(self.page.locator("#search-input").is_visible())

    def test_10_no_local_404_resources(self):
        """No 404 errors for local JS/CSS/assets."""
        errors = []
        def on_response(resp):
            if resp.status == 404 and resp.url.startswith(BASE_URL):
                errors.append(resp.url.replace(BASE_URL, ""))
        self.page.on("response", on_response)
        self._load()
        self.page.wait_for_timeout(3000)
        self.assertEqual(
            len(errors), 0,
            f"404 errors for local resources: {errors}"
        )

    def test_11_game_toggle_present(self):
        """Game toggle button in header has correct href."""
        self._load()
        toggle = self.page.locator("#game-toggle")
        self.assertTrue(toggle.is_visible())
        href = toggle.get_attribute("href")
        self.assertEqual(href, "#game", f"Game toggle href: {href}")

    def test_12_favorite_buttons_on_cards(self):
        """Site cards include favorite toggle button."""
        self._load()
        fav_btns = self.page.locator(".site-card .favorite-btn")
        count = fav_btns.count()
        self.assertGreater(count, 0, f"No favorite buttons on cards, got {count}")


if __name__ == "__main__":
    unittest.main()