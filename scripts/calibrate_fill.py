#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import requests
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ========== 核心配置 ==========
TARGET_TOTAL = 9000
MIN_PER_SMALL = 12
MAX_PER_SMALL = 80
BATCH_SIZE = 10
THREADS = 10
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

# 路径配置
BASE_DIR = Path("/home/yoli/GitHub/web_nav_v2")
DATA_FILE = BASE_DIR / "data/websites.json"
STATE_FILE = Path.home() / ".hermes" / "state" / "calibration_progress.json"
LOG_FILE = Path.home() / ".hermes" / "state" / "calibration_worker.log"

# ========== 辅助功能 ==========
def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    # 原子写入
    temp_file = DATA_FILE.with_suffix(".tmp")
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    temp_file.replace(DATA_FILE)

def get_all_sites_urls(data):
    urls = set()
    if 'categories' not in data:
        return urls
    for big in data['categories']:
        for mid in big.get('subcategories', []):
            for small in mid.get('minor_categories', []):
                for site in small.get('sites', []):
                    if 'url' in site:
                        urls.add(site['url'].strip().lower())
    return urls
# ========== 核心逻辑 ==========
def fetch_site_for_category(category_name):
    """针对特定分类定向采集站点"""
    query = f"免费 {category_name} 在线工具"
    # 简单模拟搜索结果采集 (实际中可调用搜索API或特定目录)
    # 这里实现一个基础的关键词搜索模拟，通过DuckDuckGo或类似接口
    search_url = f"https://duckduckgo.com/html/?q={query}"
    try:
        resp = requests.get(search_url, timeout=10, headers={"User-Agent": USER_AGENT})
        if resp.status_code == 200:
            # 极简解析：提取所有外部链接
            import re
            links = re.findall(r'href=\"(https?://[^\"]+)\"', resp.text)
            # 过滤掉干扰项
            filtered = [l for l in links if "duckduckgo" not in l and "google" not in l]
            return filtered
    except Exception as e:
        log(f"采集 {category_name} 失败: {e}")
    return []

def calibrate():
    log("🚀 启动填充校准程序...")
    data = load_data()
    existing_urls = get_all_sites_urls(data)
    
    # 1. 扫描缺口
    targets = [] # (big_idx, mid_idx, small_idx, category_name)
    total_count = 0
    
    for b_idx, big in enumerate(data.values()):
        b_name = big.get('name', f"大类{b_idx}")
        for m_idx, mid in enumerate(big.get('subcategories', [])):
            for s_idx, small in enumerate(mid.get('minor_categories', [])):
                sites = small.get('sites', [])
                count = len(sites)
                total_count += count
                if count < MIN_PER_SMALL:
                    targets.append((b_idx, m_idx, s_idx, small.get('name', 'Unknown')))
    
    log(f"📊 当前总数: {total_count} | 目标: {TARGET_TOTAL} | 缺口: {TARGET_TOTAL - total_count}")
    log(f"⚠️ 填充不足的小类: {len(targets)} 个")

    if total_count >= TARGET_TOTAL and len(targets) == 0:
        log("✅ 所有指标均已达标，无需校准。")
        return

    # 2. 优先级排序（从小类数量升序）
    # 注意：这里简化处理，直接遍历 targets
    
    distributed_count = 0
    
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        future_to_cat = {executor.submit(fetch_site_for_category, t[3]): t for t in targets}
        
        for future in as_completed(future_to_cat):
            b_name, m_idx, s_idx, cat_name = future_to_cat[future]
            try:
                found_urls = future.result()
                # 过滤已存在的
                new_urls = [u for u in found_urls if u not in existing_urls]
                
                # 计算需要多少个
                current_count = len(data[b_name]['subcategories'][m_idx]['minor_categories'][s_idx]['sites'])
                needed = MIN_PER_SMALL - current_count
                
                to_add = new_urls[:needed]
                for url in to_add:
                    data[b_name]['subcategories'][m_idx]['minor_categories'][s_idx]['sites'].append({
                        "url": url,
                        "title": "", # 等待内容补完脚本处理
                        "description": ""
                    })
                    existing_urls.add(url)
                    distributed_count += 1
                
                log(f"✅ {cat_name}: 补充 {len(to_add)}/{needed} 个站点")
            except Exception as e:
                log(f"❌ {cat_name} 处理异常: {e}")

    # 3. 保存结果
    save_data(data)
    log(f"🏁 校准完成。本次共新增 {distributed_count} 个站点。")
    log(f"📊 最终总数: {total_count + distributed_count}")

if __name__ == '__main__':
    calibrate()
