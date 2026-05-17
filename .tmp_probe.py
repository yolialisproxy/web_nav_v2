#!/usr/bin/env python3
"""Quick visibility probe for e2e flaky elements."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"], timeout=20000)
    page = b.new_page(viewport={"width": 1280, "height": 720})
    page.goto("http://localhost:8080/", wait_until="domcontentloaded")
    page.wait_for_timeout(4000)

    print("URL:", page.url)
    print("readyState:", page.evaluate("() => document.readyState"))

    for sel in ["#view-switcher", "#view-grid", "#view-list", "#game-toggle", "#search-input", "#header"]:
        try:
            info = page.evaluate(
                """sel => {
                   const el = document.querySelector(sel);
                   if (!el) return 'NOT_FOUND';
                   const r = el.getBoundingClientRect();
                   const cs = window.getComputedStyle(el);
                   return JSON.stringify({
                       w: +r.width, h: +r.height, x: +r.x, y: +r.y,
                       display: cs.display, visibility: cs.visibility,
                       opacity: +cs.opacity,
                       parentDisplay: el.parentElement ? window.getComputedStyle(el.parentElement).display : '?',
                       parentHidden: el.parentElement ? window.getComputedStyle(el.parentElement).display === 'none' : false
                   });
               }""",
                sel,
            )
            print(sel + ":", info)
        except Exception as e:
            print(sel + ": err =", e)

    b.close()
