#!/usr/bin/env node
/**
 * game_dom_check.js
 * 启动 Headless Chrome（Puppeteer），加载 index.html，
 * 打开游戏大厅，验证 9 款游戏卡片 DOM 存在。
 * 退出码：0 = 全部通过；1 = 有缺失/异常
 */

const { execSync } = require('child_process');
const path = require('path');

const HTML_FILE = path.resolve(__dirname, '..', 'index.html');
const EXPECTED_GAMES = [
  'solitaire', 'tetris', 'go', 'chess', 'mahjong',
  'wuxia', 'dating', 'game2048', 'gomoku'
];

(async () => {
  try {
    const puppeteer = (() => {
      try { return require('puppeteer'); } catch(e) {
        console.error('[game_dom_check] puppeteer 未安装，尝试 npm install');
        process.exit(2);
      }
    })();

    const browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // 监听控制台错误
    const consoleErrors = [];
    page.on('pageerror', err => consoleErrors.push(String(err)));
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });

    await page.goto('file://' + HTML_FILE, { waitUntil: 'domcontentloaded', timeout: 10000 });

    // 等待 DOM 加载
    await page.waitForSelector('#game-grid', { timeout: 5000 });

    // 打开游戏大厅
    await page.click('#game-menu-toggle');
    await page.waitForTimeout(500);

    // 验证 9 款游戏卡片
    const failures = [];
    for (const key of EXPECTED_GAMES) {
      const card = await page.$(`#game-grid .game-card[data-game="${key}"]`).catch(() => null);
      // 游戏卡片 renderGrid 没有设置 data-game 属性，用文本匹配
      const text = await page.evaluate((k) => {
        const cards = document.querySelectorAll('#game-grid .game-card');
        for (const c of cards) {
          const nameEl = c.querySelector('.game-card-name');
          if (nameEl && nameEl.textContent.toLowerCase().includes(k)) return true;
          if (c.textContent.toLowerCase().includes(k)) return true;
        }
        return false;
      }, key).catch(() => false);

      if (!text) {
        failures.push(key);
      } else {
        console.log(`[OK] game card found: ${key}`);
      }
    }

    await browser.close();

    if (failures.length > 0) {
      console.error(`[FAIL] 缺失游戏卡片: ${failures.join(', ')}`);
      process.exit(1);
    }

    if (consoleErrors.length > 0) {
      console.warn(`[WARN] ${consoleErrors.length} 个 JS 错误:`);
      consoleErrors.forEach(e => console.warn('  ', e));
    }

    console.log(`[PASS] 9/9 游戏卡片 DOM 验证通过`);
  } catch (err) {
    console.error('[ERROR]', err.message);
    process.exit(1);
  }
})();
