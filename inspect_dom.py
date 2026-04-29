#!/usr/bin/env python3
"""
Quick DOM inspector for the web navigation page
"""

import asyncio
from playwright.async_api import async_playwright


async def inspect_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()

        await page.goto("http://localhost:8080", wait_until="load")
        await page.wait_for_timeout(2000)  # Wait for JS to execute

        # Get all element IDs
        all_elements = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('*'))
                .filter(el => el.id || el.className)
                .map(el => ({
                    id: el.id || null,
                    classes: el.className ? el.className.split(' ').filter(c => c) : [],
                    tag: el.tagName.toLowerCase(),
                    visible: el.offsetParent !== null
                }))
                .filter(el => el.id || (el.classes && el.classes.length > 0))
                .slice(0, 50);
        }""")

        print("Important elements on the page:")
        print("-" * 80)
        for el in all_elements:
            if el['id']:
                print(f"  #{el['id']} ({el['tag']}) - visible: {el['visible']}")
            elif el['classes']:
                print(f"  .{'.'.join(el['classes'][:3])} ({el['tag']}) - visible: {el['visible']}")

        # Check specific containers
        print("\n" + "=" * 80)
        print("Checking key containers:")
        for selector in ["#sidebar", "#category-list", "#main-content", "#view-container", "#search-input"]:
            count = await page.locator(selector).count()
            visible = await page.locator(selector).is_visible() if count > 0 else False
            print(f"  {selector}: count={count}, visible={visible}")

        # Get category items
        print("\n" + "=" * 80)
        print("Category items (first 5):")
        category_items = await page.locator("#category-list > *").all()
        print(f"  Total items in category-list: {len(category_items)}")
        for i, item in enumerate(category_items[:5]):
            text = await item.text_content()
            classes = await item.get_attribute("class")
            print(f"  [{i}] classes={classes}, text={text[:60] if text else 'None'}")

        # Get site cards
        print("\n" + "=" * 80)
        print("Site items:")
        for selector in [".site-card", ".site-link", "[data-site]", ".grid-item", ".card"]:
            count = await page.locator(selector).count()
            print(f"  {selector}: {count}")

        # Sample HTML structure of view container
        print("\n" + "=" * 80)
        print("First few children of view-container:")
        children = await page.locator("#view-container > *").all()
        for i, child in enumerate(children[:3]):
            tag = await child.evaluate("el => el.tagName")
            classes = await child.get_attribute("class") or ""
            text = await child.text_content() or ""
            print(f"  [{i}] <{tag.lower()}> class={classes[:50]}, text={text[:80]}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_page())
