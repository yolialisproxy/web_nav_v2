#!/usr/bin/env python3
"""Investigate favorite button structure per card."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"], timeout=20000)
    page = b.new_page(viewport={"width": 1280, "height": 960})
    page.goto("http://localhost:8080/", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    cards = page.evaluate("() => document.querySelectorAll('.site-card').length")
    print(f"site-card count: {cards}")

    fav = page.evaluate("() => document.querySelectorAll('.site-card .favorite-btn').length")
    print(f".site-card .favorite-btn count: {fav}")

    raw = page.evaluate(
        "() => {"
        "  const c = document.querySelector('.site-card');"
        "  if (!c) return 'no card';"
        "  const b = c.querySelector('.favorite-btn');"
        "  return b ? b.outerHTML.substring(0,120) : 'no btn IN first card';"
        "}"
    )
    print("\nfirst card favorite-btn HTML:", raw[:200])

    # How many cards have fav btn
    details = page.evaluate(
        "() => {"
        "  const cards = document.querySelectorAll('.site-card');"
        "  return Array.from(cards).map(c => {"
        "    const btn = c.querySelector('.favorite-btn');"
        "    const siteId = c.getAttribute('data-site-id') || '';"
        "    const title = c.querySelector('.card-title');"
        "    const t = title ? title.textContent.substring(0,40) : '';"
        "    return (btn ? 1 : 0) + '|' + siteId + '|' + t;"
        "  }).slice(0,10);"
        "}"
    )
    print("\nFirst 10 cards fav-status:")
    for d in details:
        print(" ", d)

    b.close()
