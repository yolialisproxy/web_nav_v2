#!/usr/bin/env python3
import json
import time
import asyncio
import aiohttp
import re
import os
import sys
from html import unescape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from safe_json_io import safe_read_json, safe_write_json

BATCH_SIZE = 50
MAX_WORKERS = 4
TIMEOUT = 30

def get_total_and_done():
    data = safe_read_json('data/websites.json')
    total = 0
    done = 0
    
    if isinstance(data, dict):
        values = data.values()
    elif isinstance(data, list):
        values = data
    else:
        return 0,0
        
    for major in values:
        if isinstance(major, dict):
            items = major.get('subcategories', [])
        elif isinstance(major, list):
            items = major
        else:
            continue
            
        for sub in items:
            if isinstance(sub, dict):
                mc_items = sub.get('minor_categories', [])
            elif isinstance(sub, list):
                mc_items = sub
            else:
                continue
                
            for mc in mc_items:
                if isinstance(mc, dict):
                    sites = mc.get('sites', [])
                elif isinstance(mc, list):
                    sites = mc
                else:
                    continue
                    
                for site in sites:
                    total += 1
                    if site.get('title') and site['title'].strip() and site['title'] != site['url']:
                        done += 1
    return total, done

def extract_title(html):
    match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE | re.DOTALL)
    if match:
        title = unescape(match.group(1).strip())
        return title[:180]
    return None

async def fetch_single(session, site):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        async with session.get(site['url'], timeout=TIMEOUT, ssl=False, headers=headers) as resp:
            if resp.status != 200:
                return False
            html = await resp.text(errors='ignore')
            title = extract_title(html)
            
            if title and title != site['url']:
                site['title'] = title
                return True
            return False

    except Exception:
        return False

async def run_batch():
    total, done = get_total_and_done()
    
    print(f"总站点: {total}, 已完成: {done}, 待处理: {total-done}")
    
    with open('data/websites.json','r',encoding='utf-8') as f:
        data = json.load(f)
    
    sites_to_process = []
    site_refs = []
    
    if isinstance(data, dict):
        values = data.values()
    elif isinstance(data, list):
        values = data
    else:
        return 0,0
        
    for major in values:
        if isinstance(major, dict):
            items = major.get('subcategories', [])
        elif isinstance(major, list):
            items = major
        else:
            continue
            
        for sub in items:
            if isinstance(sub, dict):
                mc_items = sub.get('minor_categories', [])
            elif isinstance(sub, list):
                mc_items = sub
            else:
                continue
                
            for mc in mc_items:
                if isinstance(mc, dict):
                    sites = mc.get('sites', [])
                elif isinstance(mc, list):
                    sites = mc
                else:
                    continue
                    
                for site in sites:
                    if not site.get('title') or not site['title'].strip() or site['title'] == site['url']:
                        sites_to_process.append(site['url'])
                        site_refs.append(site)
                    if len(sites_to_process) >= BATCH_SIZE:
                        break
                if len(sites_to_process) >= BATCH_SIZE:
                    break
            if len(sites_to_process) >= BATCH_SIZE:
                break
    
    if not sites_to_process:
        print("✅ 没有需要处理的站点")
        return 0, 0
    
    print(f"📦 开始处理 {len(sites_to_process)} 个站点...")
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_single(session, site_refs[i]) for i, url in enumerate(sites_to_process)]
        results = await asyncio.gather(*tasks)
    
    success = sum(1 for r in results if r)
    
    # 安全写入
    safe_write_json('data/websites.json', data)
    
    print(f"✅ 批次完成: 成功 {success}/{len(sites_to_process)}")
    new_total, new_done = get_total_and_done()
    print(f"📊 总进度: {round(new_done/new_total*100, 1)}%")
    
    return success, len(sites_to_process)

if __name__ == "__main__":
    print(f"🚀 批量内容增强 简单稳定版")
    print(f"   并发数: {MAX_WORKERS}, 每批: {BATCH_SIZE}")
    print("="*50)
    
    start = time.time()
    success, total = asyncio.run(run_batch())
    elapsed = time.time() - start
    
    print(f"\n⏱️  总耗时: {elapsed:.1f}秒")
    print(f"✨ 本次增强完成: {success} 个站点")
