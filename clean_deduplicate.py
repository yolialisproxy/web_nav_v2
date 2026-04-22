#!/usr/bin/env python3
import json
import re
from collections import defaultdict, Counter
from urllib.parse import urlparse

def normalize_url(url):
    if not url:
        return ""
    url = url.strip().lower()
    url = re.sub(r'\\[u"\/\\]+', '', url)
    url = re.sub(r'^https?://(www\.)?', '', url)
    url = url.rstrip('/')
    return url

def load_data(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    print("=== 导航站 第一轮迭代 数据去重清洗 ===")
    raw_data = load_data('/home/yoli/GitHub/web_nav_v2/data/websites.json')
    print(f"原始数据总数: {len(raw_data)}")

    seen_urls = set()
    unique_sites = []
    duplicate_count = 0
    invalid_count = 0

    for site in raw_data:
        if not isinstance(site, dict):
            invalid_count +=1
            continue
        url = site.get('url', '')
        norm_url = normalize_url(url)

        if not norm_url or len(norm_url) < 5:
            invalid_count +=1
            continue

        if norm_url in seen_urls:
            duplicate_count +=1
            continue

        seen_urls.add(norm_url)
        unique_sites.append(site)

    print(f"\n✓ 去重完成:")
    print(f"  - 移除重复条目: {duplicate_count}")
    print(f"  - 移除无效URL: {invalid_count}")
    print(f"  - 剩余有效条目: {len(unique_sites)}")

    # 分类统计
    categories = defaultdict(list)
    for site in unique_sites:
        cat = site.get('_cat', '未分类')
        categories[cat].append(site)

    print(f"\n✓ 分类统计:")
    print(f"  - 总分类数: {len(categories)}")

    small_categories = []
    for cat, items in sorted(categories.items()):
        count = len(items)
        if count < 10:
            small_categories.append((cat, count))
        print(f"    {cat}: {count}")

    print(f"\n⚠ 条目不足10个的分类: {len(small_categories)}")
    for cat, cnt in small_categories:
        print(f"    {cat}: {cnt}")

    # 保存清洗后数据
    save_data(unique_sites, '/home/yoli/GitHub/web_nav_v2/data/cleaned_websites.json')
    print(f"\n✓ 清洗后数据已保存: data/cleaned_websites.json")

    # 生成统计报告
    report = {
        "round": 1,
        "before_total": len(raw_data),
        "after_total": len(unique_sites),
        "duplicates_removed": duplicate_count,
        "invalid_removed": invalid_count,
        "categories_total": len(categories),
        "categories_under_10": len(small_categories),
        "timestamp": "2026-04-21"
    }

    save_data(report, '/home/yoli/GitHub/web_nav_v2/reports/round1_report.json')
    print("✓ 迭代报告已生成: reports/round1_report.json")

if __name__ == "__main__":
    main()
