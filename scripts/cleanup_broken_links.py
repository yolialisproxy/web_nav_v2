#!/usr/bin/env python3
"""
三平台兼容技能脚本: Hermes / OpenCLAW / Claude Code
断链清理脚本 - 自动检测并移除失效网站链接
"""

import sys
import os
import json
import time
import asyncio
import aiohttp
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from safe_json_io import safe_read_json, safe_write_json

TIMEOUT = 10
MAX_CONCURRENT = 20

def get_agent_workspace(subpath: str = "") -> Path:
    """三平台兼容工作空间路径检测: Hermes / OpenCLAW / Claude Code"""
    from pathlib import Path
    import os
    home = Path.home()
    platform_paths = [
        home / ".hermes" / "workspace",
        home / ".openclaw" / "workspace",
        home / ".claude" / "workspace"
    ]
    for p in platform_paths:
        if p.exists():
            return p / subpath
    return platform_paths[0] / subpath

async def check_url(session, url):
    """异步检查URL是否可访问"""
    try:
        async with session.head(url, timeout=TIMEOUT, allow_redirects=True) as resp:
            return url, resp.status < 400, resp.status
    except Exception as e:
        try:
            async with session.get(url, timeout=TIMEOUT, allow_redirects=True) as resp:
                return url, resp.status < 400, resp.status
        except:
            return url, False, 0

async def check_all_urls(urls):
    """批量异步检查所有URL"""
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [check_url(session, url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

def process_json(input_path):
    print(f"📂 读取数据: {input_path}")

    data = safe_read_json(input_path)

    if not data or 'sites' not in data:
        print("❌ 无效的数据格式")
        return None

    all_sites = data['sites']
    print(f"🔍 正在检查 {len(all_sites)} 个网站...")

    urls = []
    site_map = {}
    for site in all_sites:
        url = site.get('url', '').strip()
        if url:
            urls.append(url)
            site_map[url] = site

    print(f"⚡ 启动异步批量检测...")
    start_time = time.time()

    results = asyncio.run(check_all_urls(urls))

    elapsed = time.time() - start_time
    print(f"✅ 检测完成，耗时 {elapsed:.1f} 秒")

    broken = []
    working = []

    for result in results:
        if isinstance(result, Exception):
            continue
        url, ok, status = result
        if ok:
            working.append(url)
        else:
            broken.append((url, status))
            print(f"❌ 失效链接 [{status}]: {url}")

    print(f"\n📊 统计:")
    print(f"   总数量: {len(all_sites)}")
    print(f"   正常: {len(working)}")
    print(f"   失效: {len(broken)}")
    print(f"   有效率: {(len(working)/len(all_sites))*100:.1f}%")

    if len(broken) == 0:
        print("✅ 没有发现失效链接")
        return data

    # 移除失效链接
    broken_urls = set([u for u, s in broken])
    kept_sites = [s for s in all_sites if s.get('url') not in broken_urls]
    kept_ids = set([s['id'] for s in kept_sites])

    # 清理分类引用
    cleaned_count = 0
    for cat in data['categories']:
        if 'siteIds' in cat:
            original_len = len(cat['siteIds'])
            cat['siteIds'] = [id for id in cat['siteIds'] if id in kept_ids]
            cleaned_count += original_len - len(cat['siteIds'])
        for sub in cat.get('subcategories', []):
            if 'siteIds' in sub:
                original_len = len(sub['siteIds'])
                sub['siteIds'] = [id for id in sub['siteIds'] if id in kept_ids]
                cleaned_count += original_len - len(sub['siteIds'])
            for mc in sub.get('minor_categories', []):
                if 'siteIds' in mc:
                    original_len = len(mc['siteIds'])
                    mc['siteIds'] = [id for id in mc['siteIds'] if id in kept_ids]
                    cleaned_count += original_len - len(mc['siteIds'])

    data['sites'] = kept_sites

    # 备份
    backup_path = Path(input_path).parent / '.backup' / f'websites_broken_clean_{int(time.time())}.json'
    backup_path.parent.mkdir(exist_ok=True)

    safe_write_json(backup_path, data)
    safe_write_json(input_path, data)

    print(f"\n✅ 清理完成")
    print(f"💾 备份已保存: {backup_path}")
    print(f"💾 主文件已更新: {input_path}")

    return data

def main():
    if len(sys.argv) < 2:
        print("用法: python3 cleanup_broken_links.py data/websites.json")
        print(f"示例: python3 cleanup_broken_links.py /home/yoli/GitHub/web_nav_v2/data/websites.json")
        sys.exit(1)

    input_path = sys.argv[1]

    if not Path(input_path).exists():
        print(f"❌ 文件不存在: {input_path}")
        sys.exit(1)

    process_json(input_path)
    print("\n✨ 断链清理完成!")

if __name__ == "__main__":
    main()