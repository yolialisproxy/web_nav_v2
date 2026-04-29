#!/usr/bin/env python3
"""Check what sites are actually rendered after leaf category click"""

import asyncio
from playwright.async_api import async_playwright


async def check_sites():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()

        await page.goto("http://localhost:8080", wait_until="load")
        await page.wait_for_timeout(3000)  # Wait for data load

        # Check initial state
        initial_sites = await page.locator("a.site").count()
        print(f"Initial site count: {initial_sites}")

        # Expand categories
        categories = await page.locator(".menu-category").count()
        print(f"Total categories: {categories}")

        for cat_idx in range(min(2, categories)):
            cat = page.locator(".menu-category").nth(cat_idx)
            header = cat.locator(".category-header")
            await header.click()
            await page.wait_for_timeout(500)

            content = cat.locator(".category-content")
            subcats = await content.locator(".menu-subcategory").count()
            print(f"Category {cat_idx+1} has {subcats} subcategories")

            if subcats > 0:
                subcat = content.locator(".menu-subcategory").first
                subheader = subcat.locator(".subcategory-header")
                await subheader.click()
                await page.wait_for_timeout(500)

                subcontent = subcat.locator(".subcategory-content")
                leaves = await subcontent.locator(".menu-leaf").count()
                print(f"  Subcategory has {leaves} leaf categories")

                if leaves > 0:
                    leaf = subcontent.locator(".menu-leaf").first
                    leaf_text = await leaf.text_content()
                    print(f"  Clicking leaf: {leaf_text}")
                    await leaf.click()
                    await page.wait_for_timeout(1000)

                    # Check for sites
                    sites = await page.locator("a.site").count()
                    print(f"  Sites after leaf click: {sites}")

                    # If no sites, check the view container content
                    if sites == 0:
                        view_content = await page.locator("#view-container").text_content()
                        print(f"  View container text: {view_content[:200]}")
                    else:
                        # Show some site links
                        for i in range(min(3, sites)):
                            link = page.locator("a.site").nth(i)
                            href = await link.get_attribute("href")
                            title = await link.text_content()
                            print(f"    Site {i+1}: {title[:60]} - {href[:60]}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(check_sites())
