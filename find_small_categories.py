#!/usr/bin/env python3
import json
from pathlib import Path

DATA_FILE = "/home/yoli/GitHub/web_nav_v2/data/websites.json"

print("🔍 正在读取网站数据...")
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

small_categories = []
total_minor = 0

for cat_name, cat in data.items():
    for sub in cat['subcategories']:
        sub_name = sub['name']
        for minor in sub['minor_categories']:
            minor_name = minor['name']
            total_minor +=1
            count = len(minor['sites'])
            if count < 12:
                small_categories.append({
                    'path': f"{cat_name} > {sub_name} > {minor_name}",
                    'count': count,
                    'gap': 12 - count
                })

# 按数量排序
small_categories.sort(key=lambda x: x['count'])

print(f"\n✅ 分析完成!")
print(f"   总计小类: {total_minor} 个")
print(f"   小于12个站点的小类: {len(small_categories)} 个")
print(f"\n📋 缺口清单:")
print("-" * 70)
print(f"{'分类路径':<50} | {'当前数量':>6} | {'缺口':>4}")
print("-" * 70)

for item in small_categories:
    print(f"{item['path']:<50} | {item['count']:>6} | {item['gap']:>4}")

print("-" * 70)

# 保存结果到报告
out_file = "/home/yoli/GitHub/web_nav_v2/reports/small_categories_gap_report.md"
with open(out_file, 'w', encoding='utf-8') as f:
    f.write("# 导航网站小类填充缺口报告\n\n")
    f.write(f"- 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"- 总计小类: {total_minor} 个\n")
    f.write(f"- 填充不足(小于12站点)小类: {len(small_categories)} 个\n\n")
    f.write("## 缺口清单\n\n")
    f.write("| 分类路径 | 当前站点数 | 需要补充 |\n")
    f.write("|----------|-----------|---------|\n")
    for item in small_categories:
        f.write(f"| {item['path']} | {item['count']} | {item['gap']} |\n")

print(f"\n💾 报告已保存至: {out_file}")
