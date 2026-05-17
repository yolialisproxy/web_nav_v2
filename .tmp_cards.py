#!/usr/bin/env python3
"""Check site-card structure."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"], timeout=20000)
    page = b.new_page(viewport={"width": 1280, "height": 960})
    page.goto("http://localhost:8080/", wait_until="domcontentloaded")
    page.wait_for_timeout(4000)

    count = page.evaluate("() => document.querySelectorAll('.site-card').length")
    print("site-card count:", count)

    htmls = page.evaluate(
        "() => {"
        "  const cards = document.querySelectorAll('.site-card');"
        "  return Array.from(cards).slice(0, 3)"
        "    .map(c => c.innerHTML.substring(0, 400));"
        "}"
    )
    for i, h in enumerate(htmls):
        print(f"\n--- card {i} ---")
        print(h)

    # Also check for any element with 'favorite' in class name
    fav_count = page.evaluate(
        "() => document.querySelectorAll('[class*=favorite]').length"
    )
    fav_types = page.evaluate(
        "() => {"
        "  return Array.from(document.querySelectorAll('[class*=favorite]'))"
        "    .slice(0,5).map(el => el.className + ' | tag=' + el.tagName);"
        "}"
    )
    print(f"\nElements containing 'favorite' in className: {fav_count}")
    for f in fav_types:
        print(" ", f)

    b.close()
