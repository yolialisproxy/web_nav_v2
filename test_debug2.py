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
            # Check the state and also try to call dataManager.load() manually to see what happens
            state_info = await page.evaluate('''() => {
                // Try to call load again and see if it works
                if (window.dataManager && typeof window.dataManager.load === 'function') {
                    // We can't await from here, but we can check the state after a short time
                    // Let's return the current state and then try to load and check again after a timeout
                    return {
                        initial: {
                            dataManagerIsLoaded: window.dataManager ? window.dataManager.isLoaded : undefined,
                            dataManagerRawLength: window.dataManager ? window.dataManager.raw?.length : undefined,
                            dataManagerSitesSize: window.dataManager ? window.dataManager.sites?.size : undefined,
                            stateSitesLength: window.state ? window.state.get('sites')?.length : undefined,
                            loading: window.state ? window.state.get('loading') : undefined
                        }
                    };
                }
                return { error: 'dataManager.load not found' };
            }''')
            print("Initial state:", state_info)
            # Now wait for the load to complete (if it's in progress) and check again
            await page.wait_for_timeout(3000)
            state_after = await page.evaluate('''() => {
                return {
                    dataManagerIsLoaded: window.dataManager ? window.dataManager.isLoaded : undefined,
                    dataManagerRawLength: window.dataManager ? window.dataManager.raw?.length : undefined,
                    dataManagerSitesSize: window.dataManager ? window.dataManager.sites?.size : undefined,
                    stateSitesLength: window.state ? window.state.get('sites')?.length : undefined,
                    loading: window.state ? window.state.get('loading') : undefined,
                    loadError: window.dataManager ? window.dataManager._loadError : undefined
                };
            }''')
            print("State after wait:", state_after)
            # Print console logs
            print("\nConsole logs (last 30):")
            for log in console_logs[-30:]:
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
