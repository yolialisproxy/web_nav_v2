#!/usr/bin/env python3
import json, asyncio, aiohttp, time
from datetime import datetime
from collections import defaultdict

DATA_FILE = "/home/yoli/GitHub/web_nav_v2/websites.json"
OUTPUT_FILE = "/home/yoli/GitHub/web_nav_v2/data/v12_health_test.json"
CONCURRENT_LIMIT = 15
TIMEOUT = 4
SAMPLE_SIZE = 300

async def check(session, site):
    try:
        async with session.head(site['url'], allow_redirects=True, timeout=TIMEOUT,
            headers={'User-Agent': 'Mozilla/5.0'}) as r:
            return {"index": site['index'], "ok": 200 <= r.status < 400, "status": r.status}
    except Exception as e:
        return {"index": site['index'], "ok": False, "error": str(type(e).__name__)[:20]}

async def main():
    with open(DATA_FILE, 'r') as f:
        sites = json.load(f)[:SAMPLE_SIZE]
    queue = [{"index": i, "url": s['url']} for i,s in enumerate(sites)]

    start = time.time()
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
    connector = aiohttp.TCPConnector(limit=CONCURRENT_LIMIT, ttl_dns_cache=300)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        async def bounded_check(item):
            async with semaphore:
                return await check(session, item)
        for item in queue:
            tasks.append(bounded_check(item))
        results = []
        for fut in asyncio.as_completed(tasks):
            results.append(await fut)
            if len(results) % 100 == 0:
                print(f"  进度: {len(results)}/{SAMPLE_SIZE}")

    healthy = {r['index'] for r in results if r.get('ok')}
    print(f"✓ 样本{SAMPLE_SIZE}: 健康{len(healthy)}, 坏链{SAMPLE_SIZE-len(healthy)}")
    print(f"✓ 健康率: {len(healthy)/SAMPLE_SIZE*100:.1f}%")

    with open(OUTPUT_FILE, 'w') as f:
        json.dump({"sample": SAMPLE_SIZE, "healthy": len(healthy), "broken": SAMPLE_SIZE-len(healthy)}, f)
    print(f"✓ 测试完成, 用时: {time.time()-start:.1f}s")

asyncio.run(main())
