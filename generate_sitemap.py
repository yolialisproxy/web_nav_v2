#!/usr/bin/env python3
"""
根据分类权重生成分级 sitemap.xml
- 一级分类(根类目) → priority 0.95, changefreq weekly
- 大类(≥50站点) → priority 0.90, changefreq weekly
- 中类(20-49) → priority 0.85, changefreq monthly
- 小类(<20) → priority 0.80, changefreq monthly
- 首页 → priority 1.0, changefreq daily
"""
import json
from datetime import date
from collections import defaultdict

with open('/home/yoli/GitHub/web_nav_v2/data/websites.json', 'r') as f:
    sites = json.load(f)

# 按一级分类聚合
top_cats = defaultdict(list)
for s in sites:
    cat = s.get('category', '')
    parts = cat.split('/')
    top = parts[0] if parts else '其他'
    top_cats[top].append(s)

# 排序：站点数多的在前
sorted_tops = sorted(top_cats.items(), key=lambda x: -len(x[1]))

today = date.today().isoformat()

lines = []
lines.append("<?xml version='1.0' encoding='utf-8'?>")
lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

# 1. 首页 - 最高权重
lines.append(f"  <url>")
lines.append(f"    <loc>https://yolialisproxy.github.io/web_nav_v2/</loc>")
lines.append(f"    <lastmod>{today}</lastmod>")
lines.append(f"    <changefreq>daily</changefreq>")
lines.append(f"    <priority>1.0</priority>")
lines.append(f"  </url>")

# 2. 一级分类页面
for top_name, top_sites in sorted_tops:
    count = len(top_sites)
    if count >= 50:
        pri = "0.95"
        freq = "weekly"
    elif count >= 20:
        pri = "0.90"
        freq = "weekly"
    elif count >= 10:
        pri = "0.85"
        freq = "monthly"
    else:
        pri = "0.80"
        freq = "monthly"

    slug = top_name.lower().replace(' ', '-').replace('/', '-')
    lines.append(f"  <url>")
    lines.append(f"    <loc>https://yolialisproxy.github.io/web_nav_v2/#{slug}</loc>")
    lines.append(f"    <lastmod>{today}</lastmod>")
    lines.append(f"    <changefreq>{freq}</changefreq>")
    lines.append(f"    <priority>{pri}</priority>")
    lines.append(f"  </url>")

# 3. 子分类页面（二级）
cat_counts = defaultdict(int)
for s in sites:
    cat_counts[s.get('category', '')] += 1

for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
    if count >= 50:
        pri = "0.92"
        freq = "weekly"
    elif count >= 20:
        pri = "0.88"
        freq = "weekly"
    elif count >= 10:
        pri = "0.84"
        freq = "monthly"
    else:
        pri = "0.80"
        freq = "monthly"

    slug = cat.lower().replace(' ', '-').replace('/', '-')
    lines.append(f"  <url>")
    lines.append(f"    <loc>https://yolialisproxy.github.io/web_nav_v2/#{slug}</loc>")
    lines.append(f"    <lastmod>{today}</lastmod>")
    lines.append(f"    <changefreq>{freq}</changefreq>")
    lines.append(f"    <priority>{pri}</priority>")
    lines.append(f"  </url>")

lines.append("</urlset>")

output_path = '/home/yoli/GitHub/web_nav_v2/sitemap.xml'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print(f"✅ sitemap.xml 生成完成")
print(f"  首页: 1条")
print(f"  一级分类: {len(sorted_tops)}条")
print(f"  子分类: {len(cat_counts)}条")
print(f"  总URL数: {1 + len(sorted_tops) + len(cat_counts)}")

# 验证
import os
size_kb = os.path.getsize(output_path) / 1024
print(f"  文件大小: {size_kb:.1f} KB")