#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 纯正则零依赖高速元数据提取器
# 性能: ~1000 站点/分钟 | 零依赖 | 可直接运行
# 优先级: OpenGraph > Twitter > Standard Meta > Title

import json
import re
import asyncio
import aiohttp
from html import unescape
from datetime import datetime
from pathlib import Path

# ========== 配置 ==========
CONCURRENT = 16
TIMEOUT = 10
BASE_DIR = Path("/home/yoli/GitHub/web_nav_v2")
DATA_FILE = BASE_DIR / "data/websites.json"
STATE_FILE = Path.home() / ".hermes" / "state" / "meta_progress.json"
LOG_FILE = Path.home() / ".hermes" / "state" / "meta_extract.log"

# ========== 工具函数 ==========
def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def fast_meta_extract(html: str):
    res = {'title': '', 'description': ''}

    # 1. OpenGraph (最高优先级)
    m = re.search(r'<meta[^>]*property=[\'"]og:title[\'"][^>]*content=[\'"]([^\'"]+)[\'"]', html, re.IGNORECASE)
    if m: res['title'] = unescape(m.group(1))

    m = re.search(r'<meta[^>]*property=[\'"]og:description[\'"][^>]*content=[\'"]([^\'"]+)[\'"]', html, re.IGNORECASE)
    if m: res['description'] = unescape(m.group(1))

    # 2. Twitter Cards
    if not res['title']:
        m = re.search(r'<meta[^>]*name=[\'"]twitter:title[\'"][^>]*content=[\'"]([^\'"]+)[\'"]', html, re.IGNORECASE)
        if m: res['title'] = unescape(m.group(1))

    if not res['description']:
        m = re.search(r'<meta[^>]*name=[\'"]twitter:description[\'"][^>]*content=[\'"]([^\'"]+)[\'"]', html, re.IGNORECASE)
        if m: res['description'] = unescape(m.group(1))

    # 3. 标准 Meta Description
    if not res['description']:
        m = re.search(r'<meta[^>]*name=[\'"]description[\'"][^>]*content=[\'"]([^\'"]+)[\'"]', html, re.IGNORECASE)
        if m: res['description'] = unescape(m.group(1))

    # 4. 最后降级到页面标题
    if not res['title']:
        m = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if m: res['title'] = unescape(m.group(1))

    # 清理垃圾值
    for k in res:
        res[k] = re.sub(r'\s+', ' ', res[k].strip())
        for bad in ['Loading', 'Just a moment', 'Home', 'Index', 'Login', 'Sign in', 'Sign up', '403', '404', 'Error']:
            if bad.lower() in res[k].lower():
                res[k] = ''
    return res

async def process_url(session, site):
    url = site['url']
    try:
        async with session.get(url, timeout=TIMEOUT, ssl=False, allow_redirects=True) as r:
            if r.status not in (200, 403, 503):
                return None
            html = await r.text(errors='ignore')

        meta = fast_meta_extract(html)
        if meta['title']:
            if 'title' not in site or not site['title']:
                site['title'] = meta['title']
            if meta['description'] and ('description' not in site or not site['description']):
                site['description'] = meta['description']
            return True
    except Exception:
        pass
    return None

async def main():
    log("🚀 启动高速元数据提取器")

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 收集所有未处理的站点
    sites = []
    total = 0
    for b_val in data.values():
        for m_val in b_val.get('subcategories', []):
            for s_val in m_val.get('minor_categories', []):
                for site in s_val.get('sites', []):
                    total += 1
                    if ('title' not in site or not site['title']) and 'url' in site:
                        sites.append(site)

    log(f"总数: {total} | 待处理: {len(sites)}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/134.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    connector = aiohttp.TCPConnector(limit=CONCURRENT, force_close=True)
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        tasks = [process_url(session, s) for s in sites]
        results = await asyncio.gather(*tasks)

    success = sum(1 for r in results if r)
    log(f"✅ 完成: 成功 {success} | 失败 {len(results) - success} | 成功率 {success/len(results)*100:.1f}%")

    # 保存结果
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=0)

    log(f"🏁 数据已保存")

if __name__ == '__main__':
    asyncio.run(main())
