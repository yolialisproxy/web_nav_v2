// 详细的E2E调试脚本
const { chromium } = require('playwright');

(async () => {
  // Launch browser
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  const page = await context.newPage();

  // Console error collection
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  // Intercept and log fetch/XMLHttpRequest
  await page.route('**/data/websites.json', async route => {
    console.log('[Debug] Intercepted request to websites.json');
    const response = await route.fetch();
    console.log(`[Debug] Response status: ${response.status()}`);
    const text = await response.text();
    console.log(`[Debug] Response length: ${text.length}`);
    try {
      const data = JSON.parse(text);
      console.log(`[Debug] Parsed ${data.length} items`);
    } catch (e) {
      console.log(`[Debug] JSON parse error: ${e.message}`);
    }
    await route.fulfill({ response });
  });

  // Navigate to page
  console.log('[Debug] Navigating to http://localhost:8080/');
  const response = await page.goto('http://localhost:8080/', {
    waitUntil: 'domcontentloaded',
    timeout: 60000
  });
  console.log(`[Debug] Response status: ${response.status()}`);

  // Wait a bit for initial load
  await page.waitForTimeout(2000);

  // Check what's on the page
  const initialContent = await page.content();
  console.log(`[Debug] Initial content length: ${initialContent.length}`);

  // Check for core objects periodically
  for (let i = 0; i < 120; i++) { // 60 seconds max
    const status = await page.evaluate(() => ({
      renderer: !!window.renderer,
      state: !!window.state,
      dataManager: !!window.dataManager,
      dataManagerIsLoaded: window.dataManager ? window.dataManager.isLoaded : false,
      dataManagerRawLength: window.dataManager ? window.dataManager.raw?.length : -1,
      dataManagerSitesSize: window.dataManager ? window.dataManager.sites?.size : -1,
      stateSitesLength: window.state ? window.state.get('sites')?.length : -1,
      loadingState: window.state ? window.state.get('loading') : undefined
    }));

    console.log(`[Debug] Check ${i}: ${JSON.stringify(status)}`);

    if (status.dataManagerIsLoaded) {
      console.log('[Debug] Data manager is loaded! Breaking...');
      break;
    }

    // Also check for any JS errors in window
    const jsErrors = await page.evaluate(() => {
      return window.getStoredJsErrors ? window.getStoredJsErrors() : [];
    });
    if (jsErrors.length > 0) {
      console.log(`[Debug] JS errors found: ${jsErrors.map(e => e.message || e).join('; ')}`);
    }

    await page.waitForTimeout(500);
  }

  // Final state dump
  const finalState = await page.evaluate(() => {
    try {
      return {
        dataManagerExists: !!window.dataManager,
        dataManagerIsLoaded: window.dataManager ? window.dataManager.isLoaded : false,
        dataManagerRaw: window.dataManager ? !!window.dataManager.raw : false,
        dataManagerRawLength: window.dataManager ? window.dataManager.raw?.length : -1,
        stateExists: !!window.state,
        stateSites: window.state ? !!window.state.get('sites') : false,
        stateSitesLength: window.state ? window.state.get('sites')?.length : -1,
        rendererExists: !!window.renderer,
        skeletonHidden: !document.getElementById('skeleton-screen') ||
          document.getElementById('skeleton-screen').classList.contains('hidden'),
        siteContainerContent: document.getElementById('site-container') ?
          document.getElementById('site-container').innerHTML.substring(0, 200) : 'No container'
      };
    } catch (e) {
      return { error: e.toString() };
    }
  });

  console.log('[Debug] Final state:', JSON.stringify(finalState, null, 2));

  // If we still have issues, let's see what's in the site container
  const siteContainerHtml = await page.evaluate(() => {
    const container = document.getElementById('site-container');
    return container ? container.innerHTML : 'No site-container found';
  });
  console.log(`[Debug] Site container preview: ${siteContainerHtml.substring(0, 500)}`);

  await browser.close();
})();
