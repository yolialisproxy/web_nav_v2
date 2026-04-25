#!/usr/bin/env python3
import json, asyncio, aiohttp
from datetime import datetime
from collections import defaultdict

DATA_FILE = "/home/yoli/GitHub/web_nav_v2/websites.json"
OUTPUT_FILE = "/home/yoli/GitHub/web_nav_v2/data/v12_health_results.json"
CLEANED_FILE = "/home/yoli/GitHub/web_nav_v2/websites_v12_cleaned.json"
BACKUP_SUFFIX = f".v12_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

CONCURRENT_LIMIT = 20
TIMEOUT = 4

async def check_url(session, site):
    url = site['url']
    try:
        async with session.head(url, allow_redirects=True, timeout=TIMEOUT,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; HermesBot/1.0)'}) as resp:
            return {"index": site['index'], "ok": 200 <= resp.status < 400, "status": resp.status}
    except Exception as e:
        return {"index": site['index'], "ok": False, "error": str(type(e).__name__)}

async def main():
    start = datetime.now()
    print(f"[{start}] Phase2 健康检查开始")

    with open(DATA_FILE, 'r') as f:
        sites = json.load(f)
    queue = [{"index": i, "url": s['url'], "category": s.get('category','')} for i,s in enumerate(sites)]

    results = []
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)

    async def bounded_check(site):
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                return await check_url(session, site)

    # 批量创建任务
    connector = aiohttp.TCPConnector(limit=CONCURRENT_LIMIT, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as global_session:
        async def check_with_session(site):
            async with semaphore:
                return await check_url(global_session, site)

        tasks = [check_with_session(item) for item in queue]
        for i, fut in enumerate(asyncio.as_completed(tasks), 1):
            result = await fut
            results.append(result)
            if i % 500 == 0:
                print(f"  进度: {i}/{len(queue)}")

    healthy = {r['index'] for r in results if r.get('ok')}
    broken = [r for r in results if not r.get('ok')]

    print(f"✓ 健康: {len(healthy)}, ✗ 坏链: {len(broken)}")
    print(f"有效率: {len(healthy)/len(queue)*100:.1f}%")

    # 备份+清理
    import shutil
    shutil.copy2(DATA_FILE, DATA_FILE + BACKUP_SUFFIX)
    cleaned = [sites[i] for i in sorted(healthy)]

    with open(CLEANED_FILE, 'w') as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)
    with open(DATA_FILE, 'w') as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)

    with open(OUTPUT_FILE, 'w') as f:
        json.dump({"total": len(queue), "healthy": len(healthy), "broken": len(broken)}, f)

    print(f"✓ Phase2 完成，耗时: {(datetime.now()-start).total_seconds():.0f}s")

asyncio.run(main())
