#!/usr/bin/env python3
import json, asyncio, aiohttp, time
from datetime import datetime

DATA_FILE = "/home/yoli/GitHub/web_nav_v2/websites.json"
OUTPUT_FILE = "/home/yoli/GitHub/web_nav_v2/data/v12_health_chunk1.json"
START_IDX = 0
END_IDX = 1591
CONCURRENT_LIMIT = 12
TIMEOUT = 4

async def check(session, site):
    try:
        async with session.head(site['url'], allow_redirects=True, timeout=TIMEOUT,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; HermesBot/1.0)'}) as r:
            return {"index": site['index'], "ok": 200 <= r.status < 400}
    except:
        return {"index": site['index'], "ok": False}

async def main():
    start_t = time.time()
    with open(DATA_FILE, 'r') as f:
        all_sites = json.load(f)
    queue = [{"index": j, "url": s['url']} for j,s in enumerate(all_sites[START_IDX:END_IDX], START_IDX)]

    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
    connector = aiohttp.TCPConnector(limit=CONCURRENT_LIMIT, force_close=True)

    async with aiohttp.ClientSession(connector=connector) as session:
        async def bounded(item):
            async with semaphore:
                return await check(session, item)
        tasks = [bounded(item) for item in queue]
        results = []
        for fut in asyncio.as_completed(tasks):
            results.append(await fut)

    healthy = {r['index'] for r in results if r.get('ok')}
    broken = [r for r in results if not r.get('ok')]

    print(f"Chunk1: {len(queue)}站, 健康{len(healthy)}, 坏链{len(broken)}")

    with open(OUTPUT_FILE, 'w') as f:
        json.dump({"range": [START_IDX, END_IDX], "healthy": list(healthy), "broken_count": len(broken)}, f)
    print(f"✓ Chunk1 完成, 用时: {time.time()-start_t:.1f}s")

asyncio.run(main())
