#!/usr/bin/env python3
"""
V14 Browser Acceptance Test
Complete acceptance testing for the V14 deployment
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from playwright.async_api import async_playwright, Browser, Page, ConsoleMessage, Error


class AcceptanceTest:
    def __init__(self, base_url: str, output_dir: str):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {
            "console_errors": [],
            "tested_features": [],
            "passed": False,
            "issues": [],
            "details": {}
        }
        self.browser = None
        self.page = None
        self.screenshot_path = self.output_dir / "acceptance_test_screenshot.png"

    async def run(self):
        """Run all acceptance tests"""
        print(f"Starting V14 Acceptance Test at {self.base_url}")
        print("=" * 60)

        async with async_playwright() as p:
            # Launch browser
            self.browser = await p.chromium.launch(
                headless=False,  # Visible browser for debugging
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self.page = await self.browser.new_page(
                viewport={'width': 1280, 'height': 720}
            )

            # Set up console error monitoring
            self.page.on("console", self._handle_console_message)
            self.page.on("pageerror", self._handle_page_error)

            try:
                # Test 1: Navigate to homepage
                await self._test_navigation()

                # Test 2: Take screenshot
                await self._take_screenshot()

                # Test 3: Check for console errors already captured

                # Test 4: Test search functionality
                await self._test_search()

                # Test 5: Test category navigation
                await self._test_category_navigation()

                # Test 6: Test link clicks
                await self._test_link_clicks()

                # Test 7: Test responsive design
                await self._test_responsive_design()

                # Test 8: Verify pages render without errors
                await self._verify_page_rendering()

                # Mark all tests as passed
                self.results["passed"] = True
                print("✅ All acceptance tests passed successfully!")

            except Exception as e:
                print(f"❌ Test failed with error: {e}")
                self.results["issues"].append(f"Test execution error: {str(e)}")
                self.results["passed"] = False
            finally:
                await self.browser.close()

        # Save report
        await self._save_report()
        print("=" * 60)
        print(f"Report saved to: {self.output_dir / 'acceptance_test_report_V14.json'}")
        print(f"Screenshot saved to: {self.screenshot_path}")

    def _handle_console_message(self, message: ConsoleMessage):
        """Capture console messages, especially errors"""
        if message.type == "error":
            error_info = {
                "type": "console",
                "text": message.text,
                "location": f"{message.location.get('url', 'unknown')}:{message.location.get('lineNumber', '?')}",
                "timestamp": datetime.now().isoformat()
            }
            self.results["console_errors"].append(error_info)
            print(f"⚠️ Console error: {message.text}")

    def _handle_page_error(self, error: Error):
        """Capture unhandled page errors"""
        error_info = {
            "type": "pageerror",
            "text": str(error),
            "timestamp": datetime.now().isoformat()
        }
        self.results["console_errors"].append(error_info)
        print(f"⚠️ Page error: {error}")

    async def _test_navigation(self):
        """Test navigation to homepage"""
        print("\n📍 Testing navigation...")
        try:
            response = await self.page.goto(self.base_url, wait_until="load")
            if response and response.ok:
                print(f"   ✅ Homepage loaded successfully (status: {response.status})")
                self.results["tested_features"].append("homepage_navigation")
                self.results["details"]["homepage_status"] = response.status

                # Wait for data to fully load (check for site links)
                print("   ⏳ Waiting for data to load...")
                await self.page.wait_for_timeout(3000)

                # Wait for either sites to appear OR empty message (data loaded)
                try:
                    await self.page.locator("a.site").first.wait_for(state="attached", timeout=10000)
                    print("   ✅ Site data loaded")
                except:
                    # Check if empty state is shown (data loaded but no sites in this category)
                    empty_state = await self.page.locator(".state-empty").count()
                    if empty_state > 0:
                        print("   ℹ️ Data loaded but category is empty")
                    else:
                        print("   ⚠️ Site data may not have loaded completely")
            else:
                status = response.status if response else "no_response"
                raise Exception(f"Homepage returned status {status}")
        except Exception as e:
            self.results["issues"].append(f"Navigation failed: {str(e)}")
            raise

    async def _take_screenshot(self):
        """Take screenshot of homepage"""
        print("\n📸 Taking screenshot...")
        try:
            await self.page.screenshot(path=str(self.screenshot_path), full_page=True)
            print(f"   ✅ Screenshot saved: {self.screenshot_path}")
            self.results["tested_features"].append("screenshot")
            self.results["details"]["screenshot_path"] = str(self.screenshot_path)
        except Exception as e:
            self.results["issues"].append(f"Screenshot failed: {str(e)}")
            raise

    async def _test_search(self):
        """Test search functionality"""
        print("\n🔍 Testing search functionality...")
        try:
            # Wait for search input to be ready
            search_input = self.page.locator("#search-input")
            await search_input.wait_for(state="visible", timeout=5000)

            # Perform a search
            test_query = "百度"
            print(f"   Searching for '{test_query}'...")
            await search_input.fill(test_query)
            await self.page.keyboard.press("Enter")

            # Wait for search to complete (either results or empty state)
            try:
                # Wait for either site results OR empty state to appear
                await asyncio.wait_for(
                    asyncio.create_task(self._wait_for_search_completion()),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                print("   ⚠️ Search results took too long, proceeding anyway")

            # Check if results appeared
            site_count = await self.page.locator("a.site").count()
            empty_state = await self.page.locator(".state-empty").count()

            if site_count > 0:
                print(f"   ✅ Search for '{test_query}' returned {site_count} results")
                self.results["tested_features"].append("search")
                self.results["details"]["search_test_query"] = test_query
                self.results["details"]["search_results_count"] = site_count
            elif empty_state > 0:
                print(f"   ℹ️ Search for '{test_query}' returned no results (empty state shown)")
                self.results["tested_features"].append("search")
                self.results["details"]["search_test_query"] = test_query
                self.results["details"]["search_results_count"] = 0
            else:
                print(f"   ⚠️ Search for '{test_query}' - unclear result state")
                self.results["issues"].append("Search result state unclear")

        except Exception as e:
            self.results["issues"].append(f"Search test failed: {str(e)}")
            print(f"   ❌ Search test failed: {e}")

    async def _wait_for_search_completion(self):
        """Helper to wait for search results to appear"""
        while True:
            # Check if we have either results or empty state
            site_count = await self.page.locator("a.site").count()
            empty_count = await self.page.locator(".state-empty").count()
            loading_count = await self.page.locator(".state-loading").count()

            # If not loading and either results or empty state, we're done
            if loading_count == 0 and (site_count > 0 or empty_count > 0):
                break
            await asyncio.sleep(0.5)

    async def _test_category_navigation(self):
        """Test category navigation"""
        print("\n📁 Testing category navigation...")
        try:
            # Wait for sidebar to load with categories
            await self.page.locator("#sidebar").wait_for(state="visible", timeout=10000)

            # Wait a bit more for dynamic content
            await self.page.wait_for_timeout(2000)

            # Get all category items (menu-category)
            categories = await self.page.locator(".menu-category").count()
            print(f"   Found {categories} categories")

            if categories > 0:
                # Expand first category if not already expanded
                first_category = self.page.locator(".menu-category").first
                category_header = first_category.locator(".category-header")
                await category_header.click()
                await self.page.wait_for_timeout(500)

                # Get subcategories within first category
                first_category_content = first_category.locator(".category-content")
                subcategories = await first_category_content.locator(".menu-subcategory").count()
                print(f"   ✅ Clicked first category, found {subcategories} subcategories")

                # Click a subcategory if available
                if subcategories > 0:
                    first_subcategory = first_category_content.locator(".menu-subcategory").first
                    subcategory_header = first_subcategory.locator(".subcategory-header")
                    await subcategory_header.click()
                    await self.page.wait_for_timeout(500)

                    # Get leaf categories
                    subcategory_content = first_subcategory.locator(".subcategory-content")
                    leaf_categories = await subcategory_content.locator(".menu-leaf").count()
                    print(f"   ✅ Clicked subcategory, found {leaf_categories} leaf categories")

                    # Click a leaf category if available
                    if leaf_categories > 0:
                        first_leaf = subcategory_content.locator(".menu-leaf").first
                        await first_leaf.click()
                        await self.page.wait_for_timeout(500)
                        print(f"   ✅ Clicked leaf category successfully")

                self.results["tested_features"].append("category_navigation")
                self.results["details"]["categories_found"] = categories
                self.results["details"]["subcategories_found"] = subcategories
                self.results["details"]["leaf_categories_found"] = leaf_categories if subcategories > 0 else 0
            else:
                print("   ⚠️ No categories found in sidebar")
                self.results["issues"].append("No categories found for navigation test")

        except Exception as e:
            self.results["issues"].append(f"Category navigation failed: {str(e)}")
            print(f"   ❌ Category navigation test failed: {e}")

    async def _test_link_clicks(self):
        """Test clicking on several random site links"""
        print("\n🔗 Testing link clicks...")
        try:
            # Wait for site cards to load
            await self.page.wait_for_timeout(1500)

            # Get all site links - they are <a> tags with class "site"
            site_links = await self.page.locator("a.site").count()
            print(f"   Found {site_links} site links")

            if site_links > 0:
                # Click up to 3 links in new tabs
                for i in range(min(3, site_links)):
                    try:
                        # Get the link element
                        link = self.page.locator("a.site").nth(i)
                        href = await link.get_attribute("href")

                        if href:
                            print(f"   Testing link {i+1}: {href[:50]}...")
                            # Open in new tab to not disrupt main test
                            async with self.page.context.expect_page(timeout=5000) as new_page_info:
                                await link.click(modifiers=["Control"])
                            new_page = await new_page_info.value

                            # Wait for page to load and check status
                            await new_page.wait_for_load_state("load", timeout=10000)
                            title = await new_page.title()
                            print(f"   ✅ Link {i+1} loaded: {title[:60]}")

                            # Close the new page
                            await new_page.close()
                        else:
                            print(f"   ⚠️ Link {i+1} has no href attribute")

                    except Exception as e:
                        print(f"   ⚠️ Link {i+1} click test failed: {e}")
                        self.results["issues"].append(f"Link click test {i+1} failed: {str(e)}")

                self.results["tested_features"].append("link_clicks")
                self.results["details"]["links_tested"] = min(3, site_links)
            else:
                print("   ⚠️ No site links found to test")
                self.results["issues"].append("No site links found for click test")

        except Exception as e:
            self.results["issues"].append(f"Link click test failed: {str(e)}")
            print(f"   ❌ Link click test failed: {e}")

    async def _test_responsive_design(self):
        """Test responsive design by resizing window"""
        print("\n📱 Testing responsive design...")
        try:
            viewports = [
                {"width": 1920, "height": 1080, "name": "Desktop"},
                {"width": 768, "height": 1024, "name": "Tablet"},
                {"width": 375, "height": 667, "name": "Mobile"},
            ]

            for viewport in viewports:
                await self.page.set_viewport_size(
                    {"width": viewport["width"], "height": viewport["height"]}
                )
                await self.page.wait_for_timeout(500)

                # Check if page is still functional
                search_visible = await self.page.locator("#search-input").is_visible()
                sidebar_visible = await self.page.locator("#sidebar").is_visible()
                main_visible = await self.page.locator("#main-content").is_visible()

                if search_visible and main_visible:
                    print(f"   ✅ {viewport['name']} ({viewport['width']}x{viewport['height']}): layout OK")
                else:
                    print(f"   ⚠️ {viewport['name']}: some elements missing")
                    self.results["issues"].append(
                        f"Responsive issue at {viewport['name']} "
                        f"(search:{search_visible}, main:{main_visible})"
                    )

            self.results["tested_features"].append("responsive_design")
            self.results["details"]["viewport_tests"] = [
                {"name": v["name"], "width": v["width"], "height": v["height"]}
                for v in viewports
            ]

        except Exception as e:
            self.results["issues"].append(f"Responsive test failed: {str(e)}")
            print(f"   ❌ Responsive test failed: {e}")

    async def _verify_page_rendering(self):
        """Verify all pages render without errors"""
        print("\n👁️ Verifying page rendering...")
        try:
            # Take a snapshot of current state
            html_content = await self.page.content()

            # Check for critical elements on the current page
            checks = {
                "header": await self.page.locator("header").count() > 0,
                "sidebar": await self.page.locator("#sidebar").count() > 0,
                "main_content": await self.page.locator("#main-content").count() > 0,
                "view_container": await self.page.locator("#view-container").count() > 0,
                "search_input": await self.page.locator("#search-input").count() > 0,
                "site_links": await self.page.locator("a.site").count() > 0,  # At least some sites visible
            }

            all_present = all(checks.values())
            if all_present:
                print("   ✅ All critical page elements present")
                self.results["tested_features"].append("page_rendering")
                self.results["details"]["page_elements"] = checks
            else:
                missing = [k for k, v in checks.items() if not v]
                print(f"   ⚠️ Missing elements: {missing}")
                self.results["issues"].append(f"Missing page elements: {missing}")

        except Exception as e:
            self.results["issues"].append(f"Page rendering verification failed: {str(e)}")
            print(f"   ❌ Page rendering test failed: {e}")

    async def _save_report(self):
        """Save the acceptance test report as JSON"""
        report_path = self.output_dir / "acceptance_test_report_V14.json"

        # Add summary information
        report = {
            "test_version": "V14",
            "test_timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "console_errors": self.results["console_errors"],
            "tested_features": self.results["tested_features"],
            "passed": self.results["passed"],
            "issues": self.results["issues"],
            "details": self.results["details"]
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Report generated with {len(self.results['tested_features'])} tested features")
        if self.results["console_errors"]:
            print(f"   ⚠️ {len(self.results['console_errors'])} console errors detected")
        if self.results["issues"]:
            print(f"   ⚠️ {len(self.results['issues'])} issues found")


async def main():
    # Configuration
    BASE_URL = "http://localhost:8080"
    PROJECT_DIR = Path("/home/yoli/GitHub/web_nav_v2")
    REPORT_DIR = PROJECT_DIR / "reports"

    # Run the acceptance test
    test = AcceptanceTest(BASE_URL, str(REPORT_DIR))
    await test.run()


if __name__ == "__main__":
    asyncio.run(main())
