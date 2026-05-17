#!/usr/bin/env python3
"""Replicate EXACT test_08 flow and measure rect."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"], timeout=20000)
    ctx = b.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    page.on("console", lambda m: None)
    page.on("pageerror", lambda e: None)

    BASE_URL = "http://localhost:8080"

    print("Step 1: set_viewport to 960")
    page.set_viewport_size({"width": 1280, "height": 960})
    print("  viewport:", page.evaluate("() => ({w: innerWidth, h: innerHeight})"))

    print("Step 2: goto with domcontentloaded")
    resp = page.goto(BASE_URL, wait_until="domcontentloaded")
    print("  resp:", resp)

    print("Step 3: wait_for_selector")
    try:
        page.wait_for_selector("#sites-grid", timeout=8000)
        print("  #sites-grid FOUND")
    except Exception as e:
        print("  #sites-grid TIMEOUT:", e)

    print("Step 4: wait_for_timeout(800)")
    page.wait_for_timeout(800)

    print("Step 5: check all three elements")
    for sel in ["#header", "#main-content", "#search-input"]:
        rect = page.evaluate(f"""sel => {{
            const el = document.querySelector(sel);
            if (!el) return 'ELEM_NOT_FOUND';
            const r = el.getBoundingClientRect();
            return JSON.stringify({{
                w: +r.width, h: +r.height, x: +r.x, y: +r.y,
                display: window.getComputedStyle(el).display
            }});
        }}""", sel)
        print(f"  {sel}: {rect}")

    ctx.close()
    b.close()
