#!/usr/bin/env python3
import json
from collections import defaultdict

with open('/home/yoli/GitHub/web_nav_v2/data/websites.json', 'r') as f:
    data = json.load(f)

cat_count = defaultdict(int)

for site in data:
    if '_cat' in site:
        cat_count[site['_cat']] += 1

print("当前各分类站点数量统计：")
print("="*60)
sorted_cats = sorted(cat_count.items(), key=lambda x: x[1], reverse=True)
for cat, cnt in sorted_cats:
    print(f"{cat:<40} | {cnt:>3} 个站点")

print(f"\n总站点数量: {len(data)}")
print(f"总分类数量: {len(cat_count)}")

print("\n✅ 不足10个站点的分类:")
print("="*60)
for cat, cnt in sorted_cats:
    if cnt < 10:
        print(f"{cat:<40} | {cnt:>3} 个站点")
