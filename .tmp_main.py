#!/usr/bin/env python3
"""Inspect #main-content visibility."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"], timeout=20000)
    page = b.new_page(viewport={"width": 1280, "height": 720})
    page.goto("http://localhost:8080/", wait_until="domcontentloaded")
    page.wait_for_timeout(4000)

    for sel in ["#main-content", "#sites-grid", "#site-list"]:
        try:
            info = page.evaluate(
                """sel => {
                   const el = document.querySelector(sel);
                   if (!el) return 'NOT_FOUND';
                   const r = el.getBoundingClientRect();
                   return 'FOUND w=' + +r.width + ' h=' + +r.height +
                       ' x=' + +r.x + ' y=' + +r.y;
               }""",
                sel,
            )
            print(sel + ":", info)
        except Exception as e:
            print(sel + ": err =", e)

    b.close()
