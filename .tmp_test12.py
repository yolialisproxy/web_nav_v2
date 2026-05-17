#!/usr/bin/env python3
"""Reproduce test_12 state exactly."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"], timeout=20000)
    ctx = b.new_context(viewport={"width": 1280, "height": 960})
    page = ctx.new_page()

    # Replicate _load exactly
    resp = page.goto("http://localhost:8080/", wait_until="domcontentloaded")
    assert resp is not None and resp.ok

    # Wait 1000ms only (as test_12 does)
    page.wait_for_timeout(1000)

    count = page.evaluate(
        "() => document.querySelectorAll('.site-card .favorite-btn').length"
    )
    print(f"After 1s wait: .site-card .favorite-btn count = {count}")

    # Now wait 3 more seconds
    page.wait_for_timeout(3000)
    count2 = page.evaluate(
        "() => document.querySelectorAll('.site-card .favorite-btn').length"
    )
    print(f"After 4s total: .site-card .favorite-btn count = {count2}")

    # Check which locator Playwright sees
    loc = page.locator('.site-card .favorite-btn')
    print(f"Playwright count: {loc.count()}")

    ctx.close()
    b.close()
