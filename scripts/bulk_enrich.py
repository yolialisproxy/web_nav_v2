#!/usr/bin/env python3
import asyncio
import aiohttp
import json
import time
import os
from collections import defaultdict
from urllib.parse import urlparse

PROJECT_PATH = "/home/yoli/GitHub/web_nav_v2"
DATA_FILE = os.path.join(PROJECT_PATH, "data/websites.json")
CACHE_FILE = os.path.join(PROJECT_PATH, "data/enrich_cache.json")
PROGRESS_FILE = os.path.join(PROJECT_PATH, "data/enrich_progress.txt")

BATCH_SIZE = 120
MAX_WORKERS = 8
TIMEOUT = 7

# Global cache
cache = {}

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE + '.tmp', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(DATA_FILE + '.tmp', DATA_FILE)

def load_cache():
    global cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    else:
        cache = {}

def save_cache():
    with open(CACHE_FILE + '.tmp', 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)
    os.replace(CACHE_FILE + '.tmp', CACHE_FILE)

def get_total_and_done():
    data = load_data()
    total = 0
    done = 0
    for major in data.values():
        for sub in major.get('subcategories', []):
            for mc in sub.get('minor_categories', []):
                for s in mc.get('sites', []):
                    total += 1
                    title = s.get('title', '') or s.get('name', '')
                    if title and title != s.get('url', ''):
                        done += 1
    return total, done

async def fetch_site(session, site):
    url = site['url']

    if url in cache:
        return url, cache[url]

    try:
        async with session.get(url, timeout=TIMEOUT, allow_redirects=True) as resp:
            if resp.status == 200:
                text = await resp.text()
                # Extract title
                title = ""
                if "<title>" in text and "</title>" in text:
                    title = text.split("<title>", 1)[1].split("</title>", 1)[0].strip()
                # Extract meta description
                desc = ""
                if 'name="description"' in text:
                    for part in text.split('name="description"')[1:]:
                        if 'content="' in part:
                            desc = part.split('content="', 1)[1].split('"', 1)[0].strip()
                            break

                cache[url] = {
                    'title': title,
                    'description': desc,
                    'fetched_at': time.time()
                }
                return url, cache[url]

    except Exception:
        pass

    return url, None

async def run_batch():
    data = load_data()

    # Find empty sites
    tasks = []
    total_empty = 0
    total = 0

    for major_name, major in data.items():
        for sub in major.get('subcategories', []):
            for mc in sub.get('minor_categories', []):
                for site in mc.get('sites', []):
                    total += 1
                    url = site.get('url', '')
                    if not url:
                        continue
                    title = site.get('title', '') or site.get('name', '')
                    if not title or title == url:
                        total_empty += 1
                        if len(tasks) < BATCH_SIZE:
                            tasks.append(site)

    if total_empty == 0:
        print("✅ 所有站点已完成填充")
        return

    print(f"总站点: {total}, 空标题: {total_empty}")
    print(f"开始处理本批次 {len(tasks)} 个站点...")

    async with aiohttp.ClientSession() as session:
        sem = asyncio.Semaphore(MAX_WORKERS)

        async def bound_fetch(site):
            async with sem:
                return await fetch_site(session, site)

        results = await asyncio.gather(*[bound_fetch(s) for s in tasks])

    # Update data
    updated = 0
    url_map = {r[0]: r[1] for r in results if r[1]}

    for major_name, major in data.items():
        for sub in major.get('subcategories', []):
            for mc in sub.get('minor_categories', []):
                for site in mc.get('sites', []):
                    url = site.get('url', '')
                    if url in url_map:
                        info = url_map[url]
                        if info.get('title'):
                            site['title'] = info['title']
                        if info.get('description'):
                            site['description'] = info['description']
                        updated += 1

    save_data(data)
    save_cache()

    print(f"✅ 本批次完成: 成功更新 {updated} 个站点")
    print(f"   缓存大小: {len(cache)}")
    return total, total_empty

if __name__ == "__main__":
    print(f"\n🚀 高性能批量内容增强 v2.0")
    print(f"   并发数: {MAX_WORKERS}, 每批: {BATCH_SIZE}")
    print(f"=" * 50)

    load_cache()

    start = time.time()
    total, total_empty = asyncio.run(run_batch())

    elapsed = time.time() - start
    print(f"   耗时: {elapsed:.1f}秒")

    total_total, total_done = get_total_and_done()
    print(f"   总完成度: {total_done} / {total_total} ({total_done*100//total_total}%)\n")
