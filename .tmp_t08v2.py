#!/usr/bin/env python3
"""Diagnose main-content in test_08: full rect details."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"], timeout=20000)
    ctx = b.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()

    print("Initial viewport:", page.evaluate("() => ({w: innerWidth, h: innerHeight})"))
    page.set_viewport_size({"width": 1280, "height": 960})
    print("After set_viewport 960:", page.evaluate("() => ({w: innerWidth, h: innerHeight})"))

    page.goto("http://localhost:8080/", wait_until="domcontentloaded")
    try:
        page.wait_for_selector("#sites-grid", timeout=8000)
        print("#sites-grid found")
    except Exception:
        print("#sites-grid NOT found")

    page.wait_for_timeout(800)

    mc = page.evaluate("""() => {
       const el = document.querySelector('#main-content');
       if (!el) return 'NOT_FOUND';
       const r = el.getBoundingClientRect();
       const cs = window.getComputedStyle(el);
       return JSON.stringify({
           display: cs.display,
           position: cs.position,
           top: cs.top,
           bottom: cs.bottom,
           w: +r.width, h: +r.height,
           x: +r.x, y: +r.y,
       });
   }""")
    print("\n#main-content:", mc)

    ctx.close()
    b.close()
