#!/usr/bin/env python3
"""生成按分类细分的候选站点统计"""

import json
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path("/home/yoli/GitHub/web_nav_v2")

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 加载数据
candidates = load_json(BASE_DIR / "data/underfill_candidates.json")
plan = load_json(BASE_DIR / "plans/V12_UNDER_FILL_PLAN.json")

# 汇总各分类的候选站点
cat_to_urls = defaultdict(list)
source_breakdown = defaultdict(lambda: defaultdict(int))

for source, sites in candidates.items():
    for site in sites:
        cat = site.get('category', '')
        url = site.get('url', '')
        cat_to_urls[cat].append({"url": url, "source": source})
        source_breakdown[source][cat] += 1

# 打印统计
print("=" * 80)
print("欠容分类候选站点详细统计")
print("=" * 80)
print(f"\n总候选站点数: {sum(len(v) for v in cat_to_urls.values())}")
print(f"有候选的分类数: {len(cat_to_urls)}")
print(f"仍无候选的分类数: {132 - len(cat_to_urls)}")

print("\n" + "=" * 80)
print("各分类候选详情 (按缺口大小排序)")
print("=" * 80)

sorted_cats = sorted(plan.keys(), key=lambda k: plan[k]['gap'], reverse=True)

for cat in sorted_cats:
    gap = plan[cat]['gap']
    candidates_list = cat_to_urls.get(cat, [])
    cand_count = len(candidates_list)

    if gap > 0:
        status = "✓" if cand_count >= gap else "✗"
        print(f"\n{status} {cat}")
        print(f"   缺口: {gap} | 候选: {cand_count} | 剩余缺口: {max(0, gap - cand_count)}")
        if candidates_list:
            for item in candidates_list[:5]:  # 只显示前5个
                print(f"   • {item['url']} [{item['source']}]")
            if len(candidates_list) > 5:
                print(f"   ... 还有 {len(candidates_list) - 5} 个候选")

print("\n" + "=" * 80)
print("数据源贡献度统计")
print("=" * 80)
for source in candidates:
    total = len(candidates[source])
    cats_covered = len(source_breakdown[source])
    print(f"\n[{source}]")
    print(f"  总候选站点: {total}")
    print(f"  覆盖分类数: {cats_covered}")
    if total > 0:
        top_cats = sorted(source_breakdown[source].items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"  主要贡献分类: {top_cats}")

print("=" * 80)

# 保存详细统计
detail_report = {
    "category_candidates_detail": {
        cat: {
            "gap": plan[cat]['gap'],
            "candidate_count": len(cat_to_urls.get(cat, [])),
            "candidates": [
                {"url": item['url'], "source": item['source']}
                for item in cat_to_urls.get(cat, [])
            ]
        }
        for cat in plan
    }
}

report_path = BASE_DIR / "data/underfill_category_detail.json"
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(detail_report, f, ensure_ascii=False, indent=2)

print(f"\n详细分类报告已保存: {report_path}")
