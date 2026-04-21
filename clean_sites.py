#!/usr/bin/env python3
import json
import asyncio
import aiohttp
import time
from urllib.parse import urlparse
from typing import List, Dict, Set

async def check_url(session: aiohttp.ClientSession, url: str, timeout: int = 8) -> bool:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        async with session.head(url, headers=headers, timeout=timeout, allow_redirects=True) as resp:
            return resp.status < 400
    except Exception:
        try:
            async with session.get(url, headers=headers, timeout=timeout, allow_redirects=True) as resp:
                return resp.status < 400
        except Exception:
            return False

async def main():
    input_path = '/home/yoli/GitHub/web_nav_v2/data/websites.json'
    output_path = '/home/yoli/GitHub/web_nav_v2/data/websites_cleaned.json'

    print("✅ 开始清理网站数据")
    print(f"📂 读取文件: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        sites: List[Dict] = json.load(f)

    original_count = len(sites)
    print(f"📊 原始站点总数: {original_count}")

    # 1. 去重
    seen_urls: Set[str] = set()
    unique_sites = []
    duplicate_count = 0

    for site in sites:
        url = site.get('url', '').strip()
        if not url or url in seen_urls:
            duplicate_count +=1
            continue
        seen_urls.add(url)
        unique_sites.append(site)

    print(f"🔍 发现重复链接: {duplicate_count} 个")

    # 2. 清理空标题/空URL
    valid_sites = []
    invalid_meta_count = 0
    for site in unique_sites:
        url = site.get('url', '').strip()
        title = site.get('title', '').strip()

        if not url or not title or len(title) < 2:
            invalid_meta_count +=1
            continue

        valid_sites.append(site)

    print(f"🗑️  无效元数据站点: {invalid_meta_count} 个")

    # 3. 批量检查链接有效性
    print(f"🔍 开始检查 {len(valid_sites)} 个站点在线状态...")

    connector = aiohttp.TCPConnector(limit=30, ssl=False)
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = []
        for site in valid_sites:
            tasks.append(check_url(session, site['url']))

        results = await asyncio.gather(*tasks, return_exceptions=True)

    alive_sites = []
    dead_count = 0

    for site, alive in zip(valid_sites, results):
        if alive is True:
            alive_sites.append(site)
        else:
            dead_count +=1

    print(f"💀 失效站点 (404/超时/无法访问): {dead_count} 个")

    # 最终统计
    final_count = len(alive_sites)
    removed_count = original_count - final_count

    print("\n" + "="*50)
    print(f"✅ 清理完成!")
    print(f"📊 原始数量: {original_count}")
    print(f"📉 移除总数: {removed_count}")
    print(f"✅ 最终有效站点: {final_count}")
    print(f"📉 清理比例: {removed_count/original_count*100:.1f}%")
    print("="*50)

    # 保存结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(alive_sites, f, ensure_ascii=False, indent=2)

    print(f"\n💾 已保存清理后数据到: {output_path}")

    # 备份原文件
    backup_path = f"/home/yoli/GitHub/web_nav_v2/data/websites_backup_{int(time.time())}.json"
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(sites, f, ensure_ascii=False, indent=2)
    print(f"💾 原文件已备份到: {backup_path}")

if __name__ == "__main__":
    asyncio.run(main())
