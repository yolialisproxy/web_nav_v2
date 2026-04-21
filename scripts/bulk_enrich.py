#!/usr/bin/env python3
import json
import time
import asyncio
import aiohttp
import re
import os
import sys
from html import unescape

BATCH_SIZE = 5
MAX_WORKERS = 1
TIMEOUT = 60

print("🚀 批量内容增强 真实版")
print(f"   并发数: {MAX_WORKERS}, 每批: {BATCH_SIZE}")
print("="*50)

def extract_title(html):
    match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE | re.DOTALL)
    if match:
        title = unescape(match.group(1).strip())
        return title[:180]
    return None

# 全局垃圾特征库，永远不会再碰到同样的垃圾
GARBAGE_PATTERNS = [
    'githubassets.com',
    'avatars.githubusercontent.com',
    'github-cloud.s3.amazonaws.com',
    'user-images.githubusercontent.com',
    'raw.githubusercontent.com',
    'repository-images.githubusercontent.com',
    '.svg',
    '.png',
    '.jpg',
    '.gif',
    '&quot;',
    '\\u0026',
    'utm_campaign',
    'utm_medium',
    'utm_source',
    'api.github.com/_private',
    'opengraph.githubassets.com',
    'w3.org/2000/svg',
    'schema.org/',
    'awesomelists.top',
    'trackawesomelist.com',
    '\\'
]

GARBAGE_TITLES = [
    'GitHub · Change is constant.',
    'Sign in for Software Support and Product Help',
    'GitHub General Privacy Statement',
    'GitHub Terms of Service'
]

async def fetch_single(session, site):
    try:
        # ✅ 前置垃圾检测，根本不去请求
        for pattern in GARBAGE_PATTERNS:
            if pattern in site['url']:
                print(f"  ⏭️  跳过垃圾: {site['url'][:60]}")
                return None

        print(f"  → 正在请求: {site['url'][:60]}")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        async with session.get(site['url'], timeout=TIMEOUT, ssl=False, headers=headers) as resp:
            print(f"    ← 状态码: {resp.status}")
            if resp.status >= 400:
                return False
            html = await resp.text(errors='ignore')
            title = extract_title(html)

            # ✅ 垃圾标题检测
            if title in GARBAGE_TITLES:
                print(f"    ⚠️  垃圾标题: {title[:50]}")
                return None

            if title and title.strip() and title != site['url']:
                print(f"    ✅ 成功: {title[:50]}")
                site['title'] = title
                return True
            return False
    except Exception as e:
        print(f"    ❌ 失败: {type(e).__name__}: {str(e)[:50]}")
        return False

async def main():
    f = open('data/websites.json')
    data = json.load(f)
    f.close()

    sites = []
    for major in data:
        for sub in major['subcategories']:
            for mc in sub['minor_categories']:
                for site in mc['sites']:
                    if not site.get('title') or site['title'].strip() == '' or site['title'] == site['url']:
                        sites.append(site)
                        if len(sites) >= BATCH_SIZE:
                            break
                if len(sites) >= BATCH_SIZE:
                    break
            if len(sites) >= BATCH_SIZE:
                break

    print(f"\n📦 本次处理 {len(sites)} 个站点\n")

    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [fetch_single(session, s) for s in sites]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    success = 0
    garbage = 0
    failed = 0

    # ✅ 永远删除失败和垃圾站点，这才是闭环真正的灵魂
    for major in data:
        for sub in major['subcategories']:
            for mc in sub['minor_categories']:
                keep = []
                for site in mc['sites']:
                    if 'title' in site:
                        keep.append(site)
                    else:
                        # 任何没有标题的站，只要跑过一次，就永远删掉
                        # 不管它是垃圾，是失败，是超时，是403，是404
                        # 我们不会再给它第二次机会
                        garbage += 1
                mc['sites'] = keep

    print(f"\n✅ 批次完成: 成功 {success}  永久删除 {garbage}  失败 {failed}")

    f = open('data/websites.json', 'w')
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.close()

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    elapsed = time.time() - start
    print(f"\n⏱️  总耗时: {elapsed:.1f}秒")
