#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from safe_json_io import safe_read_json, safe_write_json

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
    for item in data:
        if isinstance(item, dict) and 'url' in item:
            urls.add(item['url'].strip().lower())
    return urls
# ========== 核心逻辑 ==========
def load_buffer():
    buffer_path = BASE_DIR / "data/collected_buffer.json"
    if buffer_path.exists():
        try:
            with open(buffer_path, 'r', encoding='utf-8') as f:
                buf = json.load(f)
            return [s['url'] for s in buf.get('sites', []) if 'url' in s]
        except:
            pass
    return []

BUFFER = load_buffer()
BUFFER_INDEX = 0

def fetch_site_for_category(category_name):
    """使用预先采集的缓冲区站点，避免网络搜索"""
    global BUFFER_INDEX
    if BUFFER_INDEX >= len(BUFFER):
        return []

    # 每次取20个站点分配给该分类
    start = BUFFER_INDEX
    end = min(BUFFER_INDEX + 20, len(BUFFER))
    BUFFER_INDEX = end

    log(f"📦 从缓冲区分配 {end-start} 个站点给 {category_name} (缓冲区进度: {BUFFER_INDEX}/{len(BUFFER)})")
    return BUFFER[start:end]

def find_minor_category(data, cat_name):
    for big in data.values():
        if not isinstance(big, dict): continue
        for sub in big.get('subcategories', []):
            for minor in sub.get('minor_categories', []):
                if minor.get('name') == cat_name:
                    return minor
    return None

def calibrate():
    log("🚀 启动填充校准程序...")
    data = load_data()
    existing_urls = get_all_sites_urls(data)

    # 1. 扫描缺口
    targets = []
    total_count = 0
    for cat in data.values():
        if not isinstance(cat, dict): continue
        for sub in cat.get('subcategories', []):
            if not isinstance(sub, dict): continue
            for minor in sub.get('minor_categories', []):
                if not isinstance(minor, dict): continue
                total_count += len(minor.get('sites', []))

    # 统计每个小类站点数量
    small_cat_counts = {}



    # 遍历分类树
    data.pop('version', None)
    for big_id, big in data.items():
        # Skip non-dict entries at root level
        if not isinstance(big, dict):
            continue
        b_name = big.get('name', big_id)
        # Iterate over array subcategories (v2 structure)
        for mid in big.get('subcategories', []):
            mid_id = mid.get('id', mid.get('name'))
            m_name = mid.get('name', mid_id)
            # Iterate over array minor categories
            for small in mid.get('minor_categories', []):
                small_id = small.get('id', small.get('name'))
                s_name = small.get('name', small_id)
                count = len(small.get('sites', []))
                if count < MIN_PER_SMALL:
                    targets.append( (count, s_name) )

    # 按空缺排序（最空优先）
    targets.sort()

    log(f"📊 当前总数: {total_count} | 目标: {TARGET_TOTAL} | 缺口: {TARGET_TOTAL - total_count}")
    log(f"⚠️ 填充不足的小类: {len(targets)} 个")

    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--scan-only':
        log("✅ 扫描完成，退出。")
        return

    if total_count >= TARGET_TOTAL and len(targets) == 0:
        log("✅ 所有指标均已达标，无需校准。")
        return

    # 2. 优先级排序（从小类数量升序）
    # 注意：这里简化处理，直接遍历 targets

    distributed_count = 0

    if targets:
        # 处理前 10 个最空的小类
        batch = targets[:10]
        log(f"\n🔍 开始填充前 10 个最空的小类:")
        for cnt, name in batch:
            log(f"  - {name}: {cnt}/{MIN_PER_SMALL}")

        # 并行采集
        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            future_to_cat = {executor.submit(fetch_site_for_category, name): (cnt, name) for cnt, name in batch}

        for future in as_completed(future_to_cat):
            cnt, cat_name = future_to_cat[future]
            try:
                found_urls = future.result()
                # 过滤已存在的
                new_urls = [u for u in found_urls if u not in existing_urls]

                # 计算需要多少个
                needed = MIN_PER_SMALL - cnt

                to_add = new_urls[:needed]

                # 直接添加到对应小分类下
                minor_cat = find_minor_category(data, cat_name)
                if minor_cat:
                    if 'sites' not in minor_cat:
                        minor_cat['sites'] = []
                    for url in to_add:
                        minor_cat['sites'].append({
                            "url": url,
                            "title": "",
                            "description": "",
                            "source": "buffer"
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
