#!/usr/bin/env python3
"""
分析超容分类，生成细粒度拆分方案
"""

import json
import re
from collections import defaultdict

# 加载数据
with open('/home/yoli/GitHub/web_nav_v2/category_stats_V10.json', 'r', encoding='utf-8') as f:
    stats_data = json.load(f)

with open('/home/yoli/GitHub/web_nav_v2/websites.json', 'r', encoding='utf-8') as f:
    websites_data = json.load(f)

# 识别超容分类（>50）
over_capacity = {}
for cat, count in stats_data['category_statistics'].items():
    if count > 50:
        over_capacity[cat] = count

print(f"超容分类总数: {len(over_capacity)}")
print()

# 按类别数和site数排序
sorted_over_capacity = sorted(over_capacity.items(), key=lambda x: (-x[1], x[0]))

print("超容分类列表（按站点数降序）:")
for i, (cat, count) in enumerate(sorted_over_capacity, 1):
    print(f"{i:2d}. {cat}: {count} sites")

print("\n" + "="*80 + "\n")

# 分析GitHub类的所有站点
github_sites = []
for item in websites_data:
    if item.get('category') == '开发工具/平台开源/GitHub':
        github_sites.append({
            'name': item.get('name', ''),
            'url': item.get('url', ''),
            'description': item.get('description', '')
        })

print(f"GitHub类站点数: {len(github_sites)}")
print("\nGitHub类站点列表:")
for i, site in enumerate(github_sites, 1):
    print(f"{i:3d}. {site['name']}")

print("\n" + "="*80 + "\n")

# 分析其他主要超容类
top_categories = [
    ('AI工具/人工智能/数据分析', 196),
    ('多媒体/视频娱乐/教程', 192),
    ('AI工具/人工智能/代码助手', 177),
    ('AI工具/人工智能/视频生成', 153),
]

for cat_name, expected_count in top_categories:
    sites = [item for item in websites_data if item.get('category') == cat_name]
    print(f"\n{cat_name} (期望: {expected_count}, 实际: {len(sites)})")
    for site in sites[:10]:  # 显示前10个
        print(f"  - {site.get('name', '')}")
    if len(sites) > 10:
        print(f"  ... 还有 {len(sites) - 10} 个站点")
