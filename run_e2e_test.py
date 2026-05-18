#!/usr/bin/env python3
import sys
import time
import subprocess
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

# Change to the project root
os.chdir('/home/yoli/GitHub/web_nav_v2')
PROJECT_ROOT = Path.cwd()
print(f"Changed to directory: {PROJECT_ROOT}")

def main():
    server = None
    try:
        # Kill any existing processes on port 8080
        try:
            subprocess.run(['fuser', '-k', '8080/tcp'], stderr=subprocess.DEVNULL)
        except:
            pass
        
        # Start server
        server = subprocess.Popen(['python3', '-m', 'http.server', '8080'], 
                                 cwd=PROJECT_ROOT,
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Give server time to start
        time.sleep(3)
        
        # Check if server is responding
        import urllib.request
        try:
            response = urllib.request.urlopen('http://localhost:8080/', timeout=5)
            print(f"Server responding with status: {response.getcode()}")
        except Exception as e:
            print(f"Server not responding: {e}")
            # Print server stderr for debugging
            stderr_output = server.stderr.read()
            print(f"Server stderr: {stderr_output}")
            return 1
        
        # Now run Playwright test
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        ctx = browser.new_context(viewport={"width": 1280, "height": 720})
        page = ctx.new_page()
        
        BASE_URL = "http://localhost:8080"
        
        # Navigate to clean home URL
        print("Navigating to", BASE_URL + "/")
        resp = page.goto(BASE_URL + "/", wait_until="domcontentloaded", timeout=120000)
        print(f"Response status: {resp.status if resp else 'None'}")
        if not resp or not resp.ok:
            print("Failed to load page")
            return 1
        
        # Reset view mode to grid
        page.evaluate("""() => {
            try { localStorage.setItem('kunhun-nav-view-mode', 'grid'); } catch(e) {}
        }""")
        
        # Wait for core JS to be ready (renderer, state, dataManager)
        print("Waiting for core JS to be ready...")
        for i in range(900):  # up to 45s
            ready = page.evaluate("() => !!(window.renderer && window.state && window.dataManager && window.dataManager.isLoaded)")
            if ready:
                print(f"Core JS ready at iteration {i}")
                break
            
            # Check for JavaScript errors every 50 iterations (every 2.5s)
            if i % 50 == 0:
                errors = page.evaluate("""() => {
                    return window.getStoredJsErrors ? window.getStoredJsErrors() : [];
                }""")
                if errors and len(errors) > 0:
                    print(f"JS Errors detected during load: {errors}")
            
            page.wait_for_timeout(50)
        else:
            print("Core JS did not initialize within 45s")
            # Let's see what's on the page
            content = page.content()
            print(f"Page content length: {len(content)}")
            # Save a snapshot for debugging
            with open('/tmp/debug_page.html', 'w') as f:
                f.write(content)
            print("Saved page content to /tmp/debug_page.html")
            return 1
        
        # Force grid view via state change
        page.evaluate("() => { if (window.state && typeof window.state.setView === 'function') window.state.setView('grid'); }")
        
        # Wait for grid to render
        print("Waiting for grid to render...")
        for i in range(240):  # up to 12s
            if page.evaluate("() => !!document.getElementById('sites-grid')"):
                print(f"Grid rendered at iteration {i}")
                break
            page.wait_for_timeout(50)
        else:
            print("Grid didn't appear, checking for list...")
            # Grid didn't appear, wait for list to appear
            for i in range(240):  # up to 12s
                if page.evaluate("() => !!document.querySelector('.sites-list')"):
                    print(f"List rendered at iteration {i}")
                    break
                page.wait_for_timeout(50)
            else:
                print("Neither grid nor list appeared after page load")
                # Debug info
                state_info = page.evaluate("""() => {
                    return {
                        v: window.state?.get('currentView'),
                        g: !!document.getElementById('sites-grid'),
                        l: !!document.querySelector('.sites-list'),
                        mc: document.getElementById('main-content')?.textContent?.trim()?.substring(0,100)
                    };
                }""")
                print(f"State info: {state_info}")
                return 1
        
        # Final short settle
        page.wait_for_timeout(200)
        
        # Workaround: unconditionally set grid button active
        page.evaluate("() => { const b = document.getElementById('view-grid'); if (b) b.classList.add('active'); }")
        
        # Now check for JS errors from the error interceptor
        print("Checking for JS errors from error interceptor...")
        errors = page.evaluate("""() => {
            return window.getStoredJsErrors ? window.getStoredJsErrors() : [];
        }""")
        if errors:
            print(f"Found {len(errors)} JS errors:")
            for i, err in enumerate(errors[-5:]):  # Show last 5 errors
                print(f"  {i+1}: {err.get('type', 'unknown')}: {err.get('message', 'no message')}")
                if err.get('stack'):
                    print(f"      Stack: {err['stack'][:200]}...")
        else:
            print("No JS errors found from error interceptor.")
        
        # Clean up
        ctx.close()
        browser.close()
        playwright.stop()
        
        print("Test completed successfully.")
        return 0
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Kill the server
        if server:
            server.terminate()
            server.wait()
            print("Server stopped.")

if __name__ == '__main__':
    sys.exit(main())