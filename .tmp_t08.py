#!/usr/bin/env python3
"""Diagnose test_08: #main-content zero-size with 1280x960 viewport."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"], timeout=20000)
    ctx = b.new_context(viewport={"width": 1280, "height": 960})
    page = ctx.new_page()

    print("Initial viewport:", page.evaluate("() => ({w: innerWidth, h: innerHeight})"))

    # Simulate what _load + set_viewport_size does
    page.set_viewport_size({"width": 1280, "height": 960})
    print("After set_viewport (pre-goto):", page.evaluate("() => ({w: innerWidth, h: innerHeight})"))

    page.goto("http://localhost:8080/", wait_until="domcontentloaded")
    print("After goto domcontentloaded:", page.evaluate("() => ({w: innerWidth, h: innerHeight, r: document.readyState})"))

    page.wait_for_timeout(2000)
    print("After 2s wait:", page.evaluate("() => ({w: innerWidth, h: innerHeight})"))

    # Check main-content
    info = page.evaluate("""sel => {
       const el = document.querySelector(sel);
       if (!el) return 'NOT_FOUND';
       const r = el.getBoundingClientRect();
       return JSON.stringify({
           w: +r.width, h: +r.height, x: +r.x, y: +r.y,
           cs: window.getComputedStyle(el).display
       });
   }""", "#main-content")
    print("\n#main-content:", info)

    # Check ALL dimensions
    for sel in ["#header", "#main-content", "#search-input"]:
        i = page.evaluate(f"""() => {{
            const el = document.querySelector("{sel}");
            return el ? el.getBoundingClientRect().toJSON() : null;
        }}""")
        print(f"{sel}: {i}")

    ctx.close()
    b.close()
