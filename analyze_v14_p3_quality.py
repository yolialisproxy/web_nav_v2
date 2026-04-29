#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V14-P3 数据质量补全 - 质量分析脚本
检查 name/description 缺失率、重复URL、分类路径格式
"""

import json
import re
from collections import defaultdict, Counter
from urllib.parse import urlparse
from pathlib import Path

PROJECT = Path('/home/yoli/GitHub/web_nav_v2')
DATA_FILE = PROJECT / 'data' / 'websites.json'

def normalize_url(url):
    """标准化URL用于去重比较"""
    if not url:
        return ""
    url = url.strip().lower()
    # 移除协议和www
    url = re.sub(r'^https?://(www\.)?', '', url)
    # 移除尾部斜杠
    url = url.rstrip('/')
    return url

def analyze_quality():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = len(data)
    print(f" analyzed {total:,} sites\n")

    # 1. 检查 name 和 description 缺失情况
    missing_name = []
    missing_desc = []
    empty_name = []
    empty_desc = []

    for i, site in enumerate(data):
        name = site.get('name', '')
        desc = site.get('description', '')
        url = site.get('url', '')

        if not name:
            missing_name.append((i, url, site.get('title', '')))
        elif name.strip() == '':
            empty_name.append((i, url, name))

        if not desc:
            missing_desc.append((i, url, site.get('title', '')))
        elif desc.strip() == '':
            empty_desc.append((i, url, desc))

    print("=" * 70)
    print("FIELD COMPLETENESS ANALYSIS")
    print("=" * 70)
    print(f"Total sites: {total:,}")
    print(f"Missing name: {len(missing_name)} ({len(missing_name)/total*100:.2f}%)")
    print(f"Empty name:   {len(empty_name)} ({len(empty_name)/total*100:.2f}%)")
    print(f"Missing description: {len(missing_desc)} ({len(missing_desc)/total*100:.2f}%)")
    print(f"Empty description:   {len(empty_desc)} ({len(empty_desc)/total*100:.2f}%)")

    # 2. 检查重复URL
    url_map = defaultdict(list)
    for i, site in enumerate(data):
        url = site.get('url', '')
        norm_url = normalize_url(url)
        if norm_url:
            url_map[norm_url].append(i)

    duplicates = {url: idxs for url, idxs in url_map.items() if len(idxs) > 1}

    print(f"\nDuplicate URLs: {len(duplicates)}")
    dup_count = sum(len(idxs) - 1 for idxs in duplicates.values())
    print(f"Total duplicate entries: {dup_count}")

    # 3. 检查分类路径格式标准化
    print(f"\n" + "=" * 70)
    print("CATEGORY PATH FORMAT ANALYSIS")
    print("=" * 70)

    cat_issues = []
    slash_variants = defaultdict(int)
    other_cats = []

    for i, site in enumerate(data):
        cat = site.get('_cat', site.get('category', ''))
        if cat:
            if '/' in cat:
                # 检查是否有多余空格
                parts = [p.strip() for p in cat.split('/')]
                normalized = '/'.join(parts)
                if normalized != cat:
                    cat_issues.append((i, cat, normalized, 'whitespace'))
                # 统计不同的分隔符使用
                slash_variants[cat] += 1
            elif cat == '其他':
                other_cats.append(i)
            else:
                # 无分隔符但长度过长可能是问题
                if len(cat) > 20:
                    cat_issues.append((i, cat, cat, 'long_unsplit'))

    print(f"Categories with whitespace issues: {len(cat_issues)}")
    print(f"Site using '其他': {len(other_cats)}")
    print(f"Unique category patterns: {len(slash_variants)}")

    # 4. 统计分类层级
    level_counts = defaultdict(int)
    for site in data:
        cat = site.get('_cat', site.get('category', ''))
        if '/' in cat:
            level = len(cat.split('/'))
        else:
            level = 1
        level_counts[level] += 1

    print(f"\nCategory level distribution:")
    for level in sorted(level_counts.keys()):
        print(f"  Level {level}: {level_counts[level]:,} sites")

    # 保存详细报告
    report = {
        "total_sites": total,
        "completeness": {
            "missing_name": len(missing_name),
            "missing_name_pct": round(len(missing_name)/total*100, 2),
            "missing_description": len(missing_desc),
            "missing_description_pct": round(len(missing_desc)/total*100, 2),
            "empty_name": len(empty_name),
            "empty_desc": len(empty_desc)
        },
        "duplicates": {
            "duplicate_url_count": len(duplicates),
            "duplicate_entries": dup_count,
            "duplicate_details": {url: idxs for url, idxs in list(duplicates.items())[:20]}  # 只保存前20个示例
        },
        "category_format": {
            "whitespace_issues": len(cat_issues),
            "other_category_sites": len(other_cats),
            "unique_patterns": len(slash_variants),
            "level_distribution": dict(level_counts)
        },
        "missing_name_samples": missing_name[:10],
        "missing_desc_samples": missing_desc[:10]
    }

    report_file = PROJECT / 'reports' / 'v14_p3_quality_analysis.json'
    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Quality analysis report saved: reports/v14_p3_quality_analysis.json")

    return {
        'data': data,
        'missing_name': missing_name,
        'missing_desc': missing_desc,
        'duplicates': duplicates,
        'cat_issues': cat_issues
    }

if __name__ == '__main__':
    result = analyze_quality()
    print("\n✅ Analysis complete!")
