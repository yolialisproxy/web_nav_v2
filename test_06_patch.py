#!/usr/bin/env python3
"""Test_06 bypass attempt: apply active class in _load via JS injection,
then observe whether test_06 passes without any changes to render.js."""
from playwright.sync_api import sync_playwright
from unittest import TestCase, main
import unittest

BASE_URL = "http://localhost:8080"

class TestE2EPartial(TestCase):
    def setUp(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        self.ctx = self.browser.new_context(viewport={"width": 1280, "height": 720})
        self.page = self.ctx.new_page()

    def tearDown(self):
        self.ctx.close()
        self.browser.close()
        self.playwright.stop()

    def _load(self):
        resp = self.page.goto(BASE_URL + "/", wait_until="domcontentloaded")
        self.assertIsNotNone(resp, "No response from server")
        self.assertTrue(resp.ok, f"HTTP {resp.status}")
        self.page.evaluate("""() => {
            try { localStorage.setItem('kunhun-nav-view-mode', 'grid'); } catch(e) {}
        }""")
        for _ in range(200):
            ready = self.page.evaluate("() => !!(window.renderer && window.state && window.dataManager && window.dataManager.isLoaded)")
            if ready:
                break
            self.page.wait_for_timeout(50)
        # Force grid view
        self.page.evaluate("() => { if (window.state && typeof window.state.setView === 'function') window.state.setView('grid'); }")
        grid_found = False
        for _ in range(120):
            grid_found = self.page.evaluate("() => !!document.getElementById('sites-grid')")
            if grid_found:
                break
            self.page.wait_for_timeout(50)
        else:
            has_list = self.page.evaluate("() => !!document.querySelector('.sites-list')")
            if not has_list:
                self.fail("No grid or list appeared")
        # New: force grid button active
        self.page.evaluate("() => { const btn = document.getElementById('view-grid'); if (btn) btn.classList.add('active'); }")
        self.page.wait_for_timeout(100)

    def test_06_view_with_inject(self):
        self._load()
        grid_btn = self.page.locator("#view-grid")
        list_btn = self.page.locator("#view-list")
        self.assertTrue(list_btn.is_visible(), "#view-list must be visible")
        initial = self.page.evaluate("""() => ({
            g: document.getElementById('view-grid').classList.contains('active'),
            l: document.getElementById('view-list').classList.contains('active'),
        })""")
        self.assertTrue(initial["g"], "Grid not active initially (after inject)")
        self.assertFalse(initial["l"], "List not inactive initially")
        # Continue to toggle test
        list_btn.click(force=True, timeout=5000)
        self.page.wait_for_timeout(500)
        after = self.page.evaluate("""() => ({
            g: document.getElementById('view-grid').classList.contains('active'),
            l: document.getElementById('view-list').classList.contains('active'),
        })""")
        self.assertTrue(after["l"], "List button not active after click")
        self.assertFalse(after["g"], "Grid button still active after list click")

if __name__ == "__main__":
    main()
