#!/usr/bin/env python3
"""Check if any CSS loaded successfully abd test whether tailwind classes work."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"], timeout=20000)
    page = b.new_page(viewport={"width": 1280, "height": 720})

    # Capture resources
    resources = []
    def on_resp(resp):
        ct = resp.headers.get("content-type", "")
        if "css" in ct:
            resources.append({"url": resp.url, "status": resp.status, "type": ct})
    page.on("response", on_resp)

    page.goto("http://localhost:8080/", wait_until="domcontentloaded")
    page.wait_for_timeout(4000)

    print("=== CSS Resources ===")
    for r in resources:
        print(" ", r["url"][:80], "->", r["status"], r["type"])

    # Check header element to see if Tailwind classes are working
    header_info = page.evaluate(
        """sel => {
           const el = document.querySelector(sel);
           if (!el) return 'NOT_FOUND';
           const cs = window.getComputedStyle(el);
           return JSON.stringify({
               display: cs.display,
               flexDirection: cs.flexDirection,
               alignItems: cs.alignItems,
               paddingTop: cs.paddingTop,
           });
       }""",
        "#header",
    )
    print("\n=== #header computed style ===")
    print(header_info)

    # Check a known flex parent
    items = page.evaluate(
        """sel => {
           const el = document.querySelector(sel);
           if (!el) return 'NOT_FOUND';
           const cs = window.getComputedStyle(el);
           return JSON.stringify({
               classes: el.className,
               display: cs.display,
               flexDirection: cs.flexDirection,
               alignItems: cs.alignItems,
               gap: cs.gap,
           });
       }""",
        "#sidebar .nav-list",
    )
    print("\n=== #sidebar .nav-list ===")
    print(items)

    b.close()
