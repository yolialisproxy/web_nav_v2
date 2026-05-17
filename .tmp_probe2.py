#!/usr/bin/env python3
"""Debug: inspect specific elements in detail."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"], timeout=20000)
    page = b.new_page(viewport={"width": 1280, "height": 720})
    page.goto("http://localhost:8080/", wait_until="domcontentloaded")
    page.wait_for_timeout(4000)

    for sel in ["#view-switcher", "#view-list", "#game-toggle"]:
        info = page.evaluate(
            """sel => {
               const el = document.querySelector(sel);
               if (!el) return 'NOT_FOUND';
               const cs = window.getComputedStyle(el);
               return JSON.stringify({
                   classes: el.className,
                   display: cs.display,
                   visibility: cs.visibility,
                   opacity: +cs.opacity,
                   zIndex: +cs.zIndex,
               });
           }""",
            sel,
        )
        print(sel + ":", info)

    # Also dump viewport width as seen by JS
    vp = page.evaluate("() => ({w: window.innerWidth, h: window.innerHeight, dw: document.documentElement.clientWidth})")
    print("Viewport:", vp)

    b.close()
