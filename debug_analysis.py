#!/usr/bin/env python3
"""调试脚本：检查各数据源的映射情况"""

import json
from collections import Counter
from pathlib import Path

BASE_DIR = Path("/home/yoli/GitHub/web_nav_v2")

# 加载数据
def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

websites = load_json(BASE_DIR / "websites.json")
cleaned = load_json(BASE_DIR / "data/cleaned_websites.json")
flat = load_json(BASE_DIR / "data/flat_sites.json")
ods = load_json(BASE_DIR / "data/ods_raw_sites.json")
enriched = load_json(BASE_DIR / "data/enriched_websites.json")

# 建立映射
mapping = {}
for site in websites:
    if isinstance(site, dict):
        _cat = site.get('_cat', '')
        cat = site.get('category', '')
        if _cat and cat:
            mapping[_cat] = cat

print(f"映射规则数: {len(mapping)}")

# 检查 cleaned_websites
print("\n=== cleaned_websites 分析 ===")
existing_urls = {s['url'].lower() for s in websites if isinstance(s, dict) and 'url' in s}
print(f"websites.json中URL数: {len(existing_urls)}")

cleaned_non_existing = [s for s in cleaned if isinstance(s, dict) and s.get('url', '').lower() not in existing_urls]
print(f"cleaned中非重复URL数: {len(cleaned_non_existing)}")

cleaned_cats = Counter()
for s in cleaned_non_existing:
    _cat = s.get('_cat', '')
    cleaned_cats[_cat] += 1

print("cleaned中_cat分布（前10）:")
for cat, cnt in cleaned_cats.most_common(10):
    mapped = mapping.get(cat, 'NOT_MAPPED')
    print(f"  {cat} ({cnt}个) -> {mapped}")

# 检查 flat_sites
print("\n=== flat_sites 分析 ===")
flat_non_existing = [s for s in flat if isinstance(s, dict) and s.get('url', '').lower() not in existing_urls]
print(f"flat中非重复URL数: {len(flat_non_existing)}")

flat_cats = Counter()
for s in flat_non_existing:
    _cat = s.get('_cat', '')
    flat_cats[_cat] += 1

print("flat中_cat分布（前15）:")
for cat, cnt in flat_cats.most_common(15):
    mapped = mapping.get(cat, 'NOT_MAPPED')
    print(f"  {cat} ({cnt}个) -> {mapped}")

# 检查 ods_raw_sites
print("\n=== ods_raw_sites 分析 ===")
ods_non_existing = [s for s in ods if isinstance(s, dict) and s.get('url', '').lower() not in existing_urls]
print(f"ods中非重复URL数: {len(ods_non_existing)}")

# 将映射转为ods格式
ods_mapping = {k.replace('/', '>'): v for k, v in mapping.items()}

ods_cats = Counter()
for s in ods_non_existing:
    old_cat = s.get('category', '')
    ods_cats[old_cat] += 1

print("ods中category分布（前15）:")
for cat, cnt in ods_cats.most_common(15):
    mapped = ods_mapping.get(cat, 'NOT_MAPPED')
    print(f"  {cat} ({cnt}个) -> {mapped}")

# 检查 enriched_websites
print("\n=== enriched_websites 分析 ===")
enriched_sites = enriched.get('sites', [])
enriched_non_existing = [s for s in enriched_sites if isinstance(s, dict) and s.get('url', '').lower() not in existing_urls]
print(f"enriched中非重复URL数: {len(enriched_non_existing)}")

enriched_cats = Counter()
for s in enriched_non_existing:
    _cat = s.get('_cat', '')
    enriched_cats[_cat] += 1

print("enriched中_cat分布:")
for cat, cnt in enriched_cats.most_common(10):
    mapped = mapping.get(cat, 'NOT_MAPPED')
    print(f"  {cat} ({cnt}个) -> {mapped}")
