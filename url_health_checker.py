#!/usr/bin/env python3
import json
import asyncio
import aiohttp
from typing import List, Dict
from datetime import datetime

DATA_FILE = "/home/yoli/GitHub/web_nav_v2/data/websites.json"
OUTPUT_FILE = "/home/yoli/GitHub/web_nav_v2/url_health_report.json"
CONCURRENT_LIMIT = 15
TIMEOUT = 10


async def check_url(session: aiohttp.ClientSession, url: str, site_info: Dict) -> Dict:
    try:
        async with session.head(url, allow_redirects=True, timeout=TIMEOUT, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }) as response:
            return {
                "id": site_info.get("id"),
                "url": url,
                "title": site_info.get("title"),
                "status_code": response.status,
                "ok": 200 <= response.status < 400,
                "error": None
            }
    except Exception as e:
        return {
            "id": site_info.get("id"),
            "url": url,
            "title": site_info.get("title"),
            "status_code": None,
            "ok": False,
            "error": str(type(e).__name__)
        }


async def main():
    print(f"[{datetime.now()}] 开始加载网站列表...")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        sites = json.load(f)
    total_count = len(sites)
    print(f"[{datetime.now()}] 总共加载 {total_count} 个网站，开始批量检测...")

    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)

    async def bounded_check(site):
        async with semaphore:
            return await check_url(session, site['url'], site)

    async with aiohttp.ClientSession() as session:
        tasks = [bounded_check(site) for site in sites]
        results = await asyncio.gather(*tasks)

    failed = [r for r in results if not r['ok']]
    success_count = total_count - len(failed)

    print(f"\n{'='*50}")
    print(f"检查完成时间: {datetime.now()}")
    print(f"总链接数: {total_count}")
    print(f"正常可用: {success_count} ({success_count/total_count*100:.1f}%)")
    print(f"失效链接: {len(failed)} ({len(failed)/total_count*100:.1f}%)")
    print(f"{'='*50}")

    print("\n失效链接列表:")
    for item in failed:
        code = item['status_code'] if item['status_code'] else 'ERR'
        print(f"  [{code}] {item['id']} | {item['url']} | {item['title'][:40]}")

    report = {
        "generated_at": datetime.now().isoformat(),
        "total": total_count,
        "success": success_count,
        "failed_count": len(failed),
        "failed_sites": failed
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n完整报告已写入: {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
