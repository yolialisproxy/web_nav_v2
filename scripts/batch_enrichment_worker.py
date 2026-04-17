#!/usr/bin/env python3
import json
import asyncio
import aiohttp
from aiohttp import ClientTimeout
from bs4 import BeautifulSoup
import os
import time

MAX_CONCURRENT = 8
TIMEOUT = 15
STATE_FILE = "/home/yoli/GitHub/web_nav_v2/.enrich_state.json"
WEBSITES_FILE = "/home/yoli/GitHub/web_nav_v2/data/websites.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(list(state), f)

def load_websites():
    with open(WEBSITES_FILE, 'r') as f:
        return json.load(f)

def save_websites(data):
    with open(WEBSITES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_empty_sites():
    websites = load_websites()
    processed = load_state()
    empty = []
    # 数据现在是 { TOP_CATEGORY: { SUB_CATEGORY: { MINOR_CATEGORY: [sites...] } } } 结构
    for top_name, top_data in websites.items():
        if not isinstance(top_data, dict): continue
        for sub_name, sub_data in top_data.items():
            if not isinstance(sub_data, dict): continue
            for minor_name, sites in sub_data.items():
                if not isinstance(sites, list): continue
                for idx, site in enumerate(sites):
                    if not isinstance(site, dict): continue
                    url = site.get('url', '')
                    if url in processed:
                        continue
                    title = site.get('title', '').strip()
                    desc = site.get('description', '').strip()
                    if not title or not desc or title == url or len(title) < 3:
                        empty.append({
                            'path': (top_level, subcat['name'], minor_cat['name']),
                            'url': url,
                            'index': idx
                        })
    print(f"Found {len(empty)} sites pending enrichment")
    return empty

async def enrich_site(session, site_item):
    url = site_item['url']
    try:
        async with session.get(url, timeout=ClientTimeout(total=TIMEOUT), allow_redirects=True) as resp:
            if resp.status != 200:
                return None
            html = await resp.text()
            soup = BeautifulSoup(html, 'html.parser')

            title = ''
            if soup.title:
                title = soup.title.string.strip()

            desc = ''
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                desc = meta_desc.get('content', '').strip()

            if len(title) > 60:
                title = title[:57] + '...'
            if len(desc) > 80:
                desc = desc[:77] + '...'

            return {
                'url': url,
                'title': title,
                'description': desc
            }
    except Exception as e:
        return None

async def worker(queue, websites, processed, results):
    async with aiohttp.ClientSession() as session:
        while True:
            item = await queue.get()
            try:
                res = await enrich_site(session, item)
                if res and res['title']:
                    top, sub, minor = item['path']
                    for subcat in websites[top]['subcategories']:
                        if subcat['name'] == sub:
                            for mcat in subcat['minor_categories']:
                                if mcat['name'] == minor:
                                    site = mcat['siteIds'][item['index']]
                                    site['title'] = res['title']
                                    if res['description']:
                                        site['description'] = res['description']
                                    processed.add(item['url'])
                                    results['success'] += 1
                                    print(f"✅ [{results['success']}] {res['title']}")
                else:
                    results['failed'] += 1
            finally:
                queue.task_done()

async def main():
    empty = get_empty_sites()
    if not empty:
        print("All sites are enriched!")
        return

    websites = load_websites()
    processed = load_state()
    results = {'success': 0, 'failed': 0}

    queue = asyncio.Queue(maxsize=MAX_CONCURRENT*2)
    workers = [asyncio.create_task(worker(queue, websites, processed, results)) for _ in range(MAX_CONCURRENT)]

    for item in empty:
        await queue.put(item)

    await queue.join()

    for w in workers:
        w.cancel()

    save_websites(websites)
    save_state(processed)

    print(f"\n✅ Batch completed. Success: {results['success']}, Failed: {results['failed']}")

if __name__ == "__main__":
    asyncio.run(main())
