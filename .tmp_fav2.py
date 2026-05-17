#!/usr/bin/env python3
"""Check if favorite buttons are rendered with fresh page like the test."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"], timeout=20000)
    ctx = b.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))

    page.goto("http://localhost:8080/", wait_until="domcontentloaded")

    # Check at different wait times
    for wait_ms in [500, 1000, 3000, 5000]:
        page.wait_for_timeout(wait_ms)
        count = page.evaluate("() => document.querySelectorAll('.site-card .favorite-btn').length")
        loc_count = page.locator('.site-card .favorite-btn').count()
        print(f"t={wait_ms}ms: querySelectorAll={count} locator.count()={loc_count}")

    print(f"\nJS errors: {errors[:5]}")
    print(f"Page errors: {errors[:5]}")

    ctx.close()
    b.close()
