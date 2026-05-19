import asyncio
from playwright.async_api import async_playwright
import subprocess
import time
import sys

async def main():
    server = subprocess.Popen(['python3', '-m', 'http.server', '8080'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        # Wait for server to start
        time.sleep(2)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            # Collect all console messages
            console_logs = []
            page.on("console", lambda msg: console_logs.append(f"{msg.type}: {msg.text}"))
            await page.goto('http://localhost:8080/', wait_until='domcontentloaded')
            # Reset view mode to grid
            await page.evaluate("""() => {
                try { localStorage.setItem('kunhun-nav-view-mode', 'grid'); } catch(e) {}
            }""")
            # Clear stored JS errors to start fresh
            await page.evaluate("window.clearStoredJsErrors && window.clearStoredJsErrors();")
            # Wait a bit for init to run
            await page.wait_for_timeout(1000)
            # Check the state
            state = await page.evaluate('''() => {
                return {
                    dataManagerIsLoaded: window.dataManager ? window.dataManager.isLoaded : undefined,
                    dataManagerRawLength: window.dataManager ? window.dataManager.raw?.length : undefined,
                    dataManagerSitesSize: window.dataManager ? window.dataManager.sites?.size : undefined,
                    stateSitesLength: window.state ? window.state.get('sites')?.length : undefined,
                    loading: window.state ? window.state.get('loading') : undefined,
                    dataManager: !!window.dataManager,
                    state: !!window.state,
                    renderer: !!window.renderer
                };
            }''')
            print("State:", state)
            # Print console logs
            print("\nConsole logs:")
            for log in console_logs[-20:]:  # last 20
                print(log)
            # Also check if there are any errors in the error interceptor
            errors = await page.evaluate('''() => {
                return window.getStoredJsErrors ? window.getStoredJsErrors() : [];
            }''')
            print("\nErrors from interceptor:", errors)
            await browser.close()
    finally:
        server.terminate()
        server.wait()

if __name__ == '__main__':
    asyncio.run(main())
