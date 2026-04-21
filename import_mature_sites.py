#!/usr/bin/env python3
import json
import re
import time
from urllib.parse import urlparse
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data/websites.json"
BUFFER_FILE = BASE_DIR / "data/collected_buffer.json"
BACKUP_DIR = BASE_DIR / "data/.backup"

def normalize_url(url):
    if not url:
        return ""
    url = url.strip().lower()
    url = re.sub(r'^https?://(www\.)?', '', url)
    url = url.rstrip('/')
    return url

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def extract_all_sites(data):
    """递归从分类结构中提取所有站点"""
    sites = []
    if isinstance(data, dict):
        if 'sites' in data and isinstance(data['sites'], list):
            sites.extend(data['sites'])
        for v in data.values():
            sites.extend(extract_all_sites(v))
    elif isinstance(data, list):
        for item in data:
            sites.extend(extract_all_sites(item))
    return sites

def main():
    print("=== import_mature_sites 成熟站点导入任务 ===")

    # 1. 加载现有数据
    raw_data = load_json(DATA_FILE)
    existing_sites = extract_all_sites(raw_data)
    print(f"✅ 当前已有站点数: {len(existing_sites)}")

    # 2. 构建已存在URL集合
    existing_urls = set()
    for site in existing_sites:
        if not isinstance(site, dict):
            continue
        norm_url = normalize_url(site.get('url', ''))
        if norm_url and len(norm_url) >=5:
            existing_urls.add(norm_url)

    print(f"✅ 已收录唯一URL数: {len(existing_urls)}")

    # 3. 加载待导入缓冲数据
    if not BUFFER_FILE.exists():
        print("❌ 没有找到待导入缓冲文件 collected_buffer.json")
        return

    buffer_data = load_json(BUFFER_FILE)
    candidate_sites = buffer_data.get('sites', [])
    print(f"📥 待导入缓冲站点数: {len(candidate_sites)}")

    # 4. 过滤导入
    new_sites = []
    skipped = 0
    invalid = 0

    for site in candidate_sites:
        if not isinstance(site, dict):
            invalid +=1
            continue

        url = site.get('url', '').strip()
        norm_url = normalize_url(url)

        if not norm_url or len(norm_url) <5:
            invalid +=1
            continue

        if norm_url in existing_urls:
            skipped +=1
            continue

        # 符合条件的新站点
        new_sites.append(site)
        existing_urls.add(norm_url)

    print(f"\n📊 导入统计:")
    print(f"  - 重复跳过: {skipped}")
    print(f"  - 无效跳过: {invalid}")
    print(f"  - 新增站点: {len(new_sites)}")

    if len(new_sites) ==0:
        print("\n✅ 没有需要导入的新站点")
        return

    # 5. 自动备份
    backup_path = BACKUP_DIR / f"websites.json.backup.{int(time.time())}"
    save_json(raw_data, backup_path)
    print(f"✅ 原数据已备份: {backup_path}")

    # 6. 新站点暂时放入未分类区域
    if '未分类' not in raw_data:
        raw_data['未分类'] = {
            "name": "未分类",
            "subcategories": [{
                "id": "待分类",
                "name": "待分类",
                "minor_categories": [{
                    "id": "待审核",
                    "name": "待审核",
                    "sites": []
                }]
            }]
        }

    # 追加新站点
    raw_data['未分类']['subcategories'][0]['minor_categories'][0]['sites'].extend(new_sites)

    # 写入新数据
    save_json(raw_data, DATA_FILE)
    print(f"✅ 站点数据已更新")

    # 清空缓冲
    save_json({"sites": [], "imported_at": int(time.time()), "imported_count": len(new_sites)}, BUFFER_FILE)
    print("✅ 缓冲文件已清空")

    print(f"\n🎉 导入任务完成! 成功导入 {len(new_sites)} 个新站点")

if __name__ == "__main__":
    main()