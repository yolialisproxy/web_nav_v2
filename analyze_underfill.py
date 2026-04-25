#!/usr/bin/env python3
"""
啃魂导航 V12 Phase 1 - 欠容填充数据准备
分析所有数据源，识别可用于填充132个欠容分类的候选站点
"""

import json
import os
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path("/home/yoli/GitHub/web_nav_v2")

# 文件路径
FILES = {
    "cleaned_websites": BASE_DIR / "data/cleaned_websites.json",
    "flat_sites": BASE_DIR / "data/flat_sites.json",
    "ods_raw_sites": BASE_DIR / "data/ods_raw_sites.json",
    "enriched_websites": BASE_DIR / "data/enriched_websites.json",
    "websites": BASE_DIR / "websites.json",
    "underfill_plan": BASE_DIR / "plans/V12_UNDER_FILL_PLAN.json"
}

def load_json(path):
    """加载JSON文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print("=== 欠容填充数据准备 ===\n")

    # 1. 读取现有websites URLs用于去重
    print("1. 读取现有数据...")
    websites_data = load_json(FILES["websites"])
    existing_urls = set()
    for site in websites_data:
        if isinstance(site, dict) and 'url' in site:
            existing_urls.add(site['url'].lower())
    print(f"   websites.json 现有站点数: {len(existing_urls)}")

    # 2. 读取欠容计划
    underfill_plan = load_json(FILES["underfill_plan"])
    target_categories = set(underfill_plan.keys())
    print(f"   V12欠容分类数: {len(target_categories)}")
    total_gap = sum(v['gap'] for v in underfill_plan.values())
    print(f"   总缺口数: {total_gap}")

    # 3. 建立映射表：从 websites.json 中的 _cat -> category 映射
    print("\n2. 建立映射表 (从websites.json的_cat字段)...")
    mapping_dict = {}  # key: _cat (旧路径格式), value: 新三级分类
    category_examples = defaultdict(list)

    for site in websites_data:
        if not isinstance(site, dict):
            continue
        _cat = site.get('_cat', '')
        cat = site.get('category', '')
        if _cat and cat and cat in target_categories:
            if _cat not in mapping_dict:
                mapping_dict[_cat] = cat
            # 收集示例
            if len(category_examples[_cat]) < 3:
                category_examples[_cat].append({
                    "url": site.get('url', ''),
                    "title": site.get('title', site.get('name', '')),
                    "mapped_to": cat
                })

    print(f"   映射规则数: {len(mapping_dict)}")
    print("   映射示例：")
    for _cat, examples in list(category_examples.items())[:10]:
        print(f"     '{_cat}' -> '{mapping_dict[_cat]}'  ({len(examples)} 个样本)")

    # 4. 分析各数据源
    results = {
        "summary": {
            "total_existing_sites": len(existing_urls),
            "total_underfill_categories": len(target_categories),
            "total_gap": total_gap
        },
        "sources": {},
        "cat_mapping_rules": mapping_dict,
        "category_candidates": defaultdict(int),
        "fillable": False
    }

    # 4.1 cleaned_websites.json - 使用 _cat 映射
    print("\n3. 分析 cleaned_websites.json (使用_cat映射)...")
    cleaned_data = load_json(FILES["cleaned_websites"])
    cleaned_candidates = []
    cleaned_cats_found = set()
    unmapped_cleaned = set()

    for site in cleaned_data:
        if not isinstance(site, dict) or 'url' not in site:
            continue
        url = site['url'].lower()
        if url in existing_urls:
            continue
        _cat = site.get('_cat', '')
        new_cat = mapping_dict.get(_cat)
        if new_cat and new_cat in target_categories:
            cleaned_candidates.append({
                "url": url,
                "title": site.get('title', ''),
                "description": site.get('description', ''),
                "old_category_field": site.get('category', ''),
                "mapped_from_cat": _cat,
                "category": new_cat
            })
            cleaned_cats_found.add(new_cat)
        else:
            unmapped_cleaned.add(_cat)

    results["sources"]["cleaned_websites"] = {
        "total_items": len(cleaned_data),
        "available_candidates": len(cleaned_candidates),
        "categories_covered": len(cleaned_cats_found),
        "unmapped_cat_count": len(unmapped_cleaned)
    }
    print(f"   原始条目: {len(cleaned_data)}")
    print(f"   可用候选: {len(cleaned_candidates)}")
    print(f"   覆盖分类: {len(cleaned_cats_found)}")
    print(f"   未映射_cat数: {len(unmapped_cleaned)}")
    for cat in sorted(cleaned_cats_found):
        results["category_candidates"][cat] += 1

    # 4.2 flat_sites.json - 使用 _cat 映射
    print("\n4. 分析 flat_sites.json (使用_cat映射)...")
    flat_data = load_json(FILES["flat_sites"])
    flat_candidates = []
    flat_cats_found = set()
    unmapped_flat = set()

    for site in flat_data:
        if not isinstance(site, dict) or 'url' not in site:
            continue
        url = site['url'].lower()
        if url in existing_urls:
            continue
        _cat = site.get('_cat', '')
        new_cat = mapping_dict.get(_cat)
        if new_cat and new_cat in target_categories:
            flat_candidates.append({
                "url": url,
                "title": site.get('title', ''),
                "description": site.get('description', ''),
                "old_category_field": site.get('category', ''),
                "mapped_from_cat": _cat,
                "category": new_cat
            })
            flat_cats_found.add(new_cat)
        else:
            unmapped_flat.add(_cat)

    results["sources"]["flat_sites"] = {
        "total_items": len(flat_data),
        "available_candidates": len(flat_candidates),
        "categories_covered": len(flat_cats_found),
        "unmapped_cat_count": len(unmapped_flat)
    }
    print(f"   原始条目: {len(flat_data)}")
    print(f"   可用候选: {len(flat_candidates)}")
    print(f"   覆盖分类: {len(flat_cats_found)}")
    print(f"   未映射_cat数: {len(unmapped_flat)}")
    for cat in sorted(flat_cats_found):
        results["category_candidates"][cat] += 1

    # 4.3 ods_raw_sites.json - 使用 ods格式 > 映射
    print("\n5. 分析 ods_raw_sites.json (使用ods格式映射)...")
    ods_data = load_json(FILES["ods_raw_sites"])

    # 将websites的映射规则转换为ods格式（用>分隔）
    ods_mapping_dict = {}
    for _cat, new_cat in mapping_dict.items():
        ods_format = _cat.replace('/', '>')
        ods_mapping_dict[ods_format] = new_cat

    print(f"   ODS映射规则数: {len(ods_mapping_dict)}")

    ods_candidates = []
    ods_cats_found = set()
    unmapped_ods_cats = set()

    for site in ods_data:
        if not isinstance(site, dict) or 'url' not in site:
            continue
        url = site['url'].lower()
        if url in existing_urls:
            continue
        old_cat = site.get('category', '')
        new_cat = ods_mapping_dict.get(old_cat)
        if new_cat and new_cat in target_categories:
            ods_candidates.append({
                "url": url,
                "title": site.get('title', ''),
                "old_category": old_cat,
                "category": new_cat
            })
            ods_cats_found.add(new_cat)
        else:
            unmapped_ods_cats.add(old_cat)

    results["sources"]["ods_raw_sites"] = {
        "total_items": len(ods_data),
        "available_candidates": len(ods_candidates),
        "categories_covered": len(ods_cats_found),
        "unmapped_categories": list(unmapped_ods_cats)[:20]  # 只显示前20个
    }
    print(f"   原始条目: {len(ods_data)}")
    print(f"   可用候选: {len(ods_candidates)}")
    print(f"   覆盖分类: {len(ods_cats_found)}")
    print(f"   未映射ods分类数: {len(unmapped_ods_cats)}")
    if unmapped_ods_cats:
        print(f"   示例未映射: {sorted(unmapped_ods_cats)[:10]}")
    for cat in sorted(ods_cats_found):
        results["category_candidates"][cat] += 1

    # 4.4 enriched_websites.json - 使用 _cat 映射
    print("\n6. 分析 enriched_websites.json (使用_cat映射)...")
    enriched_data = load_json(FILES["enriched_websites"])
    sites_list = enriched_data.get('sites', [])
    enriched_candidates = []
    enriched_cats_found = set()
    unmapped_enriched = set()

    for site in sites_list:
        if not isinstance(site, dict) or 'url' not in site:
            continue
        url = site['url'].lower()
        if url in existing_urls:
            continue
        _cat = site.get('_cat', '')
        new_cat = mapping_dict.get(_cat)
        if new_cat and new_cat in target_categories:
            enriched_candidates.append({
                "url": url,
                "title": site.get('title', ''),
                "description": site.get('description', ''),
                "old_category_field": site.get('category', ''),
                "mapped_from_cat": _cat,
                "category": new_cat
            })
            enriched_cats_found.add(new_cat)
        else:
            unmapped_enriched.add(_cat)

    results["sources"]["enriched_websites"] = {
        "total_items": len(sites_list),
        "available_candidates": len(enriched_candidates),
        "categories_covered": len(enriched_cats_found),
        "unmapped_cat_count": len(unmapped_enriched)
    }
    print(f"   原始条目: {len(sites_list)}")
    print(f"   可用候选: {len(enriched_candidates)}")
    print(f"   覆盖分类: {len(enriched_cats_found)}")
    print(f"   未映射_cat数: {len(unmapped_enriched)}")
    for cat in sorted(enriched_cats_found):
        results["category_candidates"][cat] += 1

    # 5. 汇总统计
    print("\n=== 汇总统计 ===")
    print(f"{'数据源':<30} {'原始条目':<12} {'可用候选':<12} {'覆盖分类数':<12}")
    print("-" * 70)
    for src, stats in results["sources"].items():
        print(f"{src:<30} {stats['total_items']:<12} {stats['available_candidates']:<12} {stats['categories_covered']:<12}")

    # 6. 检查是否能填满缺口
    total_candidates = sum(results["category_candidates"].values())
    print(f"\n总候选站点数: {total_candidates}")
    print(f"总缺口数: {total_gap}")

    if total_candidates >= total_gap:
        print("✓  候选站点可以填满所有缺口!")
        results["fillable"] = True
    else:
        print("✗  候选站点无法填满所有缺口。")
        print(f"   短缺: {total_gap - total_candidates} 个站点")

    # 7. 按分类输出候选统计
    print("\n=== 欠容分类候选统计 (Top 30) ===")
    uncovered_categories = []
    low_coverage = []
    sorted_cats = sorted(target_categories)
    for i, cat in enumerate(sorted_cats):
        count = results["category_candidates"].get(cat, 0)
        gap = underfill_plan[cat]['gap']
        if count == 0:
            uncovered_categories.append(cat)
        elif count < gap:
            low_coverage.append((cat, count, gap))
        if i < 30:
            status = "✓" if count >= gap else "✗"
            print(f"  {status} {cat:<55} 候选:{count:<5} 缺口:{gap}")

    print(f"\n仍无候选的欠容分类数: {len(uncovered_categories)}")
    if len(uncovered_categories) > 0:
        print("示例:", uncovered_categories[:10])
    print(f"部分覆盖的分类数 (候选<缺口): {len(low_coverage)}")

    results["uncovered_categories"] = uncovered_categories
    results["partial_coverage"] = low_coverage

    # 8. 生成 underfill_candidates.json
    print("\n8. 生成 underfill_candidates.json ...")
    all_candidates = {
        "cleaned_websites": cleaned_candidates,
        "flat_sites": flat_candidates,
        "ods_raw_sites": ods_candidates,
        "enriched_websites": enriched_candidates
    }

    output_path = BASE_DIR / "data/underfill_candidates.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_candidates, f, ensure_ascii=False, indent=2)
    print(f"   已保存到: {output_path}")

    # 保存完整报告
    report_path = BASE_DIR / "data/underfill_analysis_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"   分析报告已保存到: {report_path}")

    print("\n=== 任务完成 ===")
    return results

if __name__ == "__main__":
    main()
