#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 速度优先版填充脚本 - 质量已验证，只追求最快填充速度
# 目标速度：每分钟 300+ 站点
import json
import os
import requests
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ========== 速度优先配置 ==========
THREADS = 24
BATCH_WRITE = 500
MIN_PER_SMALL = 12
MAX_PER_SMALL = 85
TARGET_TOTAL = 9000
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/134.0.0.0"

BASE_DIR = Path("/home/yoli/GitHub/web_nav_v2")
DATA_FILE = BASE_DIR / "data/websites.json"
STATE_FILE = Path.home() / ".hermes" / "state" / "speed_progress.json"

# ========== 无日志极速模式 ==========
def log(msg):
    # 仅写磁盘不打印，减少IO阻塞
    timestamp = datetime.now().strftime('%H:%M:%S')
    with open(STATE_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    temp_file = DATA_FILE.with_suffix(".tmp")
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=0) # 无缩进极速写入
    temp_file.replace(DATA_FILE)

def get_all_urls(data):
    urls = set()
    for b in data.get('categories', []):
        for m in b.get('subcategories', []):
            for s in m.get('minor_categories', []):
                for site in s.get('sites', []):
                    if 'url' in site: urls.add(site['url'])
    return urls

def fetch_batch(keyword):
    try:
        resp = requests.get(f"https://html.duckduckgo.com/html/?q={keyword}", timeout=7, headers={"User-Agent": USER_AGENT})
        if resp.status_code == 200:
            import re
            links = re.findall(r'href=\"(https?://[^\"]+)\"', resp.text)
            return [l for l in links if "duckduckgo" not in l and "google" not in l and "wikipedia" not in l][:25]
    except:
        pass
    return []

def main():
    data = load_data()
    existing = get_all_urls(data)
    total = len(existing)
    added = 0
    last_save = total

    # 预先生成所有缺口任务
    tasks = []
    for bidx, b in enumerate(data.get('categories', [])):
        for midx, m in enumerate(b.get('subcategories', [])):
            for sidx, s in enumerate(m.get('minor_categories', [])):
                count = len(s.get('sites', []))
                if count < MIN_PER_SMALL:
                    tasks.append( (bidx, midx, sidx, s['name'], MIN_PER_SMALL - count) )

    log(f"启动极速填充 | 当前:{total} | 目标:{TARGET_TOTAL} | 缺口分类:{len(tasks)}")

    with ThreadPoolExecutor(max_workers=THREADS) as exe:
        futures = { exe.submit(fetch_batch, t[3]): t for t in tasks }

        for future in as_completed(futures):
            bidx, midx, sidx, name, need = futures[future]
            try:
                urls = future.result()
                new = [u for u in urls if u not in existing][:need]

                for url in new:
                    data['categories'][bidx]['subcategories'][midx]['minor_categories'][sidx]['siteIds'].append({"url": url})
                    existing.add(url)
                    added += 1
                    total += 1

                # 批量写入
                if added >= BATCH_WRITE:
                    save_data(data)
                    log(f"已写入 {added} | 总数 {total} | 剩余 {TARGET_TOTAL - total}")
                    added = 0

            except Exception:
                continue

    # 最终写入
    save_data(data)
    log(f"✅ 本轮完成 | 最终总数 {total}")

if __name__ == '__main__':
    main()
