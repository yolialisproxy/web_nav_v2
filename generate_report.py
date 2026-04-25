#!/usr/bin/env python3
"""生成最终的分析报告JSON"""

import json
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path("/home/yoli/GitHub/web_nav_v2")

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 重新运行完整分析
def analyze():
    websites_data = load_json(BASE_DIR / "websites.json")
    underfill_plan = load_json(BASE_DIR / "plans/V12_UNDER_FILL_PLAN.json")
    cleaned = load_json(BASE_DIR / "data/cleaned_websites.json")
    flat = load_json(BASE_DIR / "data/flat_sites.json")
    ods = load_json(BASE_DIR / "data/ods_raw_sites.json")
    enriched = load_json(BASE_DIR / "data/enriched_websites.json")

    existing_urls = {s['url'].lower() for s in websites_data if isinstance(s, dict) and 'url' in s}
    target_categories = set(underfill_plan.keys())
    total_gap = sum(v['gap'] for v in underfill_plan.values())

    # 映射表
    mapping = {}
    for site in websites_data:
        if isinstance(site, dict):
            _cat = site.get('_cat', '')
            cat = site.get('category', '')
            if _cat and cat and cat in target_categories:
                mapping[_cat] = cat

    ods_mapping = {k.replace('/', '>'): v for k, v in mapping.items()}

    results = {
        "metadata": {
            "task": "啃魂导航 V12 Phase 1 - 欠容填充数据准备",
            "timestamp": "2026-04-25",
            "existing_websites_count": len(existing_urls),
            "underfill_categories_count": len(target_categories),
            "total_gap": total_gap
        },
        "summary": {
            "description": "各数据源可用于填充欠容分类的候选站点统计"
        },
        "data_source_analysis": {},
        "ods_category_mapping": {},
        "total_candidates_by_category": {},
        "category_coverage_detail": {},
        "fillable": False
    }

    # 分析每个数据源
    sources_analysis = {}

    # 1. cleaned_websites
    cleaned_non_existing = [s for s in cleaned if isinstance(s, dict) and s.get('url', '').lower() not in existing_urls]
    cleaned_candidates = []
    cleaned_cats_covered = set()
    for s in cleaned_non_existing:
        _cat = s.get('_cat', '')
        new_cat = mapping.get(_cat)
        if new_cat and new_cat in target_categories:
            cleaned_candidates.append({"url": s['url'], "category": new_cat})
            cleaned_cats_covered.add(new_cat)

    sources_analysis["cleaned_websites"] = {
        "file": "data/cleaned_websites.json",
        "total_items": len(cleaned),
        "url_already_in_websites": len(cleaned) - len(cleaned_non_existing),
        "unique_new_urls": len(cleaned_non_existing),
        "candidate_count": len(cleaned_candidates),
        "categories_covered": len(cleaned_cats_covered),
        "note": "所有URL已在websites.json中，无新增候选"
    }

    # 2. flat_sites
    flat_non_existing = [s for s in flat if isinstance(s, dict) and s.get('url', '').lower() not in existing_urls]
    flat_candidates = []
    flat_cats_covered = defaultdict(int)
    flat_unmapped = set()
    for s in flat_non_existing:
        _cat = s.get('_cat', '')
        new_cat = mapping.get(_cat)
        if new_cat and new_cat in target_categories:
            flat_candidates.append({"url": s['url'], "category": new_cat})
            flat_cats_covered[new_cat] += 1
        else:
            flat_unmapped.add(_cat)

    sources_analysis["flat_sites"] = {
        "file": "data/flat_sites.json",
        "total_items": len(flat),
        "url_already_in_websites": len(flat) - len(flat_non_existing),
        "unique_new_urls": len(flat_non_existing),
        "candidate_count": len(flat_candidates),
        "categories_covered": len(flat_cats_covered),
        "unmapped_categories": list(flat_unmapped)
    }

    # 3. ods_raw_sites
    ods_non_existing = [s for s in ods if isinstance(s, dict) and s.get('url', '').lower() not in existing_urls]
    ods_candidates = []
    ods_cats_covered = defaultdict(int)
    ods_unmapped = set()
    for s in ods_non_existing:
        old_cat = s.get('category', '')
        new_cat = ods_mapping.get(old_cat)
        if new_cat and new_cat in target_categories:
            ods_candidates.append({"url": s['url'], "category": new_cat, "old_category": old_cat})
            ods_cats_covered[new_cat] += 1
        else:
            ods_unmapped.add(old_cat)

    sources_analysis["ods_raw_sites"] = {
        "file": "data/ods_raw_sites.json",
        "total_items": len(ods),
        "url_already_in_websites": len(ods) - len(ods_non_existing),
        "unique_new_urls": len(ods_non_existing),
        "candidate_count": len(ods_candidates),
        "categories_covered": len(ods_cats_covered),
        "unmapped_categories": list(ods_unmapped)[:20]
    }

    # 4. enriched_websites
    enriched_sites = enriched.get('sites', [])
    enriched_non_existing = [s for s in enriched_sites if isinstance(s, dict) and s.get('url', '').lower() not in existing_urls]
    enriched_candidates = []
    enriched_cats_covered = set()
    enriched_unmapped = set()
    for s in enriched_non_existing:
        _cat = s.get('_cat', '')
        new_cat = mapping.get(_cat)
        if new_cat and new_cat in target_categories:
            enriched_candidates.append({"url": s['url'], "category": new_cat})
            enriched_cats_covered.add(new_cat)
        else:
            enriched_unmapped.add(_cat)

    sources_analysis["enriched_websites"] = {
        "file": "data/enriched_websites.json",
        "total_items": len(enriched_sites),
        "url_already_in_websites": len(enriched_sites) - len(enriched_non_existing),
        "unique_new_urls": len(enriched_non_existing),
        "candidate_count": len(enriched_candidates),
        "categories_covered": len(enriched_cats_covered),
        "unmapped_categories": list(enriched_unmapped)
    }

    results["data_source_analysis"] = sources_analysis

    # ODS映射规则
    results["ods_category_mapping"] = {
        "description": "将ods旧格式category (例如 'AI智能>LLM>工具') 转换为新三级分类的映射表",
        "conversion_rule": "将websites.json中的_cat字段的'/'替换为'>'，然后对应到相同的category",
        "mapping_count": len(ods_mapping),
        "sample_mappings": {k: v for i, (k, v) in enumerate(ods_mapping.items()) if i < 20}
    }

    # 汇总所有候选
    all_candidates_by_cat = defaultdict(int)
    for c in flat_candidates:
        all_candidates_by_cat[c['category']] += 1
    for c in ods_candidates:
        all_candidates_by_cat[c['category']] += 1
    for c in enriched_candidates:
        all_candidates_by_cat[c['category']] += 1
    # cleaned为空

    results["total_candidates_by_category"] = dict(sorted(all_candidates_by_cat.items()))
    results["summary"]["total_candidate_sites"] = sum(all_candidates_by_cat.values())

    # 分类详情
    category_detail = {}
    for cat in target_categories:
        current = underfill_plan[cat]['current_count']
        target = underfill_plan[cat]['target_count']
        gap = underfill_plan[cat]['gap']
        candidates = all_candidates_by_cat.get(cat, 0)
        remaining = max(0, gap - candidates)
        status = "filled" if candidates >= gap else ("partial" if candidates > 0 else "empty")
        category_detail[cat] = {
            "current": current,
            "target": target,
            "gap": gap,
            "candidates": candidates,
            "remaining_gap": remaining,
            "status": status
        }

    results["category_coverage_detail"] = category_detail

    # 是否可填满
    results["fillable"] = sum(all_candidates_by_cat.values()) >= total_gap
    results["summary"]["fillable"] = results["fillable"]
    results["summary"]["shortfall"] = max(0, total_gap - sum(all_candidates_by_cat.values()))

    # 统计摘要
    empty_cats = [cat for cat, detail in category_detail.items() if detail['candidates'] == 0]
    partial_cats = [cat for cat, detail in category_detail.items() if 0 < detail['candidates'] < detail['gap']]
    filled_cats = [cat for cat, detail in category_detail.items() if detail['candidates'] >= detail['gap']]

    results["summary"]["empty_categories"] = len(empty_cats)
    results["summary"]["partial_categories"] = len(partial_cats)
    results["summary"]["filled_categories"] = len(filled_cats)

    # 保存报告
    report_path = BASE_DIR / "data/underfill_analysis_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 生成候选文件
    candidates_output = {
        "cleaned_websites": cleaned_candidates,
        "flat_sites": flat_candidates,
        "ods_raw_sites": ods_candidates,
        "enriched_websites": enriched_candidates
    }
    candidates_path = BASE_DIR / "data/underfill_candidates.json"
    with open(candidates_path, 'w', encoding='utf-8') as f:
        json.dump(candidates_output, f, ensure_ascii=False, indent=2)

    # 打印摘要
    print("=" * 60)
    print("欠容填充数据准备 - 分析报告")
    print("=" * 60)
    print(f"\n📊 总体情况:")
    print(f"   - 现有websites.json站点数: {len(existing_urls)}")
    print(f"   - V12欠容分类数: {len(target_categories)}")
    print(f"   - 总缺口数: {total_gap}")

    print(f"\n📁 数据源分析:")
    for src, data in sources_analysis.items():
        print(f"\n   [{src}]")
        print(f"     - 来源文件: {data['file']}")
        print(f"     - 原始条目: {data['total_items']}")
        print(f"     - 已在websites中的URL: {data['url_already_in_websites']}")
        print(f"     - 新增URL数: {data['unique_new_urls']}")
        print(f"     - 候选站点数: {data['candidate_count']}")
        print(f"     - 覆盖分类数: {data['categories_covered']}")

    total_cand = sum(all_candidates_by_cat.values())
    print(f"\n🎯 候选站点汇总:")
    print(f"   - 总候选站点数: {total_cand}")
    print(f"   - 是否可填满缺口: {'✓ 是' if results['fillable'] else ('✗ 否 (短缺 ' + str(results['summary']['shortfall']) + ' 个)')}")

    print(f"\n📋 分类覆盖情况:")
    print(f"   - 完全无候选的分类数: {len(empty_cats)}")
    print(f"   - 部分覆盖的分类数: {len(partial_cats)}")
    print(f"   - 已满足的分类数: {len(filled_cats)}")

    if empty_cats:
        print(f"\n⚠️  仍无候选的10个分类示例:")
        for cat in empty_cats[:10]:
            gap = underfill_plan[cat]['gap']
            print(f"   - {cat} (缺口: {gap})")

    print(f"\n💾 输出文件:")
    print(f"   - 候选站点: {candidates_path}")
    print(f"   - 分析报告: {report_path}")
    print("=" * 60)

    return results

if __name__ == "__main__":
    analyze()
