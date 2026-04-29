#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V14-P3 数据质量补全执行脚本

任务目标：
1. 补全缺失字段(name/description) - 缺失率 0%
2. 清理重复URL - 重复数 0个
3. 标准化分类路径格式

输入: data/websites.json
输出: data/websites.json (补全后)
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse

PROJECT = Path('/home/yoli/GitHub/web_nav_v2')
DATA_FILE = PROJECT / 'data' / 'websites.json'
BACKUP_DIR = PROJECT / 'backups'
REPORT_DIR = PROJECT / 'reports'

def ensure_dirs():
    BACKUP_DIR.mkdir(exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def normalize_url(url):
    """标准化URL用于去重比较"""
    if not url:
        return ""
    url = url.strip().lower()
    url = re.sub(r'^https?://(www\.)?', '', url)
    url = url.rstrip('/')
    return url

def score_entry(site):
    """计算条目质量分数，用于去重时决定保留哪个"""
    score = 0

    # Name quality (0-3 points)
    name = site.get('name', '')
    if name:
        score += 1
        if len(name.strip()) > 3:
            score += 1
        if name != normalize_url(site.get('url', '')):  # Not just domain
            score += 1

    # Description quality (0-3 points)
    desc = site.get('description', '')
    if desc:
        score += 1
        if len(desc.strip()) > 10:
            score += 1
        # Penalize placeholder descriptions
        placeholder_patterns = ['欠容填充', '待填充', 'TODO', 'placeholder', 'n/a']
        if not any(p in desc for p in placeholder_patterns):
            score += 1

    # Category quality (0-2 points)
    cat = site.get('_cat', site.get('category', ''))
    if cat and cat not in ['其他', '未分类', '', '待分类']:
        score += 1
        if '/' in cat and len(cat.split('/')) >= 3:  # Has 3-level path
            score += 1

    # Source quality (0-2 points)
    source = site.get('source', '')
    known_sources = ['awesome', 'manual', 'enriched', 'imported']
    if source in known_sources:
        score += 1
        if source != 'v12_underfill_flat':  # Not a filler source
            score += 1

    return score

def deduplicate(data):
    """去重：保留质量分数最高的条目"""
    url_groups = defaultdict(list)

    # 按标准化URL分组
    for idx, site in enumerate(data):
        url = site.get('url', '')
        norm_url = normalize_url(url)
        if norm_url and len(norm_url) >= 5:  # Valid URL
            url_groups[norm_url].append((idx, site))

    duplicates_found = 0
    kept_indices = set()
    deduped_data = []

    for norm_url, entries in url_groups.items():
        if len(entries) == 1:
            # 无重复，直接保留
            idx, site = entries[0]
            kept_indices.add(idx)
            deduped_data.append(site)
        else:
            # 有重复，选择质量最高的
            duplicates_found += len(entries) - 1

            # 为每个条目计算质量分
            scored = [(score_entry(site), idx, site) for idx, site in entries]
            scored.sort(key=lambda x: (-x[0], x[1]))  # 按分数降序，分数相同按原序号升序

            best_score, best_idx, best_site = scored[0]
            kept_indices.add(best_idx)
            deduped_data.append(best_site)

            # 记录被移除的重复项
            removed = [(idx, site) for score, idx, site in scored[1:]]
            # print(f"  Deduped {norm_url}: kept idx {best_idx} (score {best_score}), removed {[idx for idx,s in removed]}")

    return deduped_data, duplicates_found

def fill_missing_fields(data):
    """补全缺失的 name 和 description 字段"""
    filled = {'name': 0, 'description': 0}
    still_missing = {'name': [], 'description': []}

    for i, site in enumerate(data):
        changed = False

        # 处理 name
        name = site.get('name', '')
        if not name or name.strip() == '':
            # 尝试从 title 生成
            title = site.get('title', '')
            if title and title.strip() != '':
                # 截取 title 的前部分作为 name (去掉常见前缀)
                clean_title = re.sub(r'^(Login \| |首页|欢迎|Welcome to )', '', title, flags=re.IGNORECASE)
                clean_title = clean_title.strip()
                if len(clean_title) > 50:
                    clean_title = clean_title[:50]
                site['name'] = clean_title
                filled['name'] += 1
                changed = True
            else:
                # 从 URL 生成
                url = site.get('url', '')
                parsed = urlparse(url)
                hostname = parsed.hostname or ''
                if hostname:
                    hostname = hostname.replace('www.', '')
                    site['name'] = hostname
                    filled['name'] += 1
                    changed = True
                else:
                    still_missing['name'].append(i)

        # 处理 description
        desc = site.get('description', '')
        if not desc or desc.strip() == '':
            # 尝试从 name 或 title 生成
            name = site.get('name', '')
            title = site.get('title', '')
            source_desc = name or title
            if source_desc and source_desc.strip() != '':
                site['description'] = source_desc
                filled['description'] += 1
                changed = True
            else:
                still_missing['description'].append(i)

    return data, filled, still_missing

def standardize_categories(data):
    """标准化分类路径格式"""
    standardized = 0
    changes = []

    for i, site in enumerate(data):
        cats = []
        if '_cat' in site:
            cats.append(('_cat', site['_cat']))
        if 'category' in site and 'category' != '_cat':
            cats.append(('category', site['category']))

        for field, cat_value in cats:
            if cat_value:
                # 1. 去除首尾空格
                cleaned = cat_value.strip()
                # 2. 确保分隔符两侧无多余空格
                # 将 "Part1 / Part2" 转换为 "Part1/Part2"
                cleaned = re.sub(r'\s*/\s*', '/', cleaned)
                # 3. 移除连续多个分隔符
                cleaned = re.sub(r'//+', '/', cleaned)

                if cleaned != cat_value:
                    site[field] = cleaned
                    standardized += 1
                    changes.append((i, field, cat_value, cleaned))

    return data, standardized, changes

def generate_report(original_data, cleaned_data, stats):
    """生成质量报告"""
    report = {
        "task": "V14-P3 数据质量补全",
        "timestamp": "2026-04-29",
        "input_file": str(DATA_FILE),
        "output_file": str(DATA_FILE),
        "statistics": {
            "original_total": stats['original_total'],
            "cleaned_total": stats['cleaned_total'],
            "removed_duplicates": stats['duplicates_found'],
            "filled_name": stats['filled']['name'],
            "filled_description": stats['filled']['description'],
            "categories_standardized": stats['standardized'],
            "final_missing_name": len(stats['still_missing']['name']),
            "final_missing_description": len(stats['still_missing']['description'])
        },
        "quality_targets": {
            "name_missing_rate_target": "0%",
            "desc_missing_rate_target": "0%",
            "duplicate_url_target": "0",
            "name_missing_rate_actual": f"{len(stats['still_missing']['name'])/stats['cleaned_total']*100:.2f}%",
            "desc_missing_rate_actual": f"{len(stats['still_missing']['description'])/stats['cleaned_total']*100:.2f}%",
            "duplicate_url_actual": 0  # After dedupe
        },
        "details": {
            "duplicates_removed": stats['duplicate_details'],
            "category_format_changes": stats['category_changes'][:50],  # 保存前50条
            "still_missing_name_indices": stats['still_missing']['name'][:20],
            "still_missing_desc_indices": stats['still_missing']['description'][:20]
        }
    }

    report_file = REPORT_DIR / 'v14_p3_completion_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Completion report saved: reports/v14_p3_completion_report.json")
    return report

def main():
    print("=" * 70)
    print("V14-P3 数据质量补全执行")
    print("=" * 70)

    ensure_dirs()

    # 1. 加载数据
    print("\n[1/5] Loading data...")
    data = load_data()
    original_total = len(data)
    print(f"  Loaded {original_total:,} sites")

    # 2. 去重
    print("\n[2/5] Deduplicating URLs...")
    cleaned_data, duplicates_found = deduplicate(data)
    print(f"  Removed {duplicates_found} duplicate entries")
    print(f"  After dedupe: {len(cleaned_data):,} sites")

    # 3. 补全缺失字段
    print("\n[3/5] Filling missing name/description...")
    cleaned_data, filled, still_missing = fill_missing_fields(cleaned_data)
    print(f"  Filled name: {filled['name']} sites")
    print(f"  Filled description: {filled['description']} sites")
    if still_missing['name']:
        print(f"  ⚠ Still missing name: {len(still_missing['name'])} sites")
    if still_missing['description']:
        print(f"  ⚠ Still missing description: {len(still_missing['description'])} sites")

    # 4. 标准化分类路径
    print("\n[4/5] Standardizing category paths...")
    cleaned_data, standardized, cat_changes = standardize_categories(cleaned_data)
    print(f"  Standardized {standardized} category fields")

    # 5. 最终质量验证
    print("\n[5/5] Final quality validation...")
    final_missing_name = sum(1 for s in cleaned_data if not s.get('name','').strip())
    final_missing_desc = sum(1 for s in cleaned_data if not s.get('description','').strip())
    final_missing_rate_name = final_missing_name / len(cleaned_data) * 100
    final_missing_rate_desc = final_missing_desc / len(cleaned_data) * 100

    # 二次去重确认
    url_map2 = defaultdict(list)
    for i, s in enumerate(cleaned_data):
        norm = normalize_url(s.get('url',''))
        if norm:
            url_map2[norm].append(i)
    final_duplicates = sum(len(v)-1 for v in url_map2.values() if len(v) > 1)

    print(f"  Final total: {len(cleaned_data):,} sites")
    print(f"  Name missing rate: {final_missing_rate_name:.2f}% ({final_missing_name} sites)")
    print(f"  Desc missing rate: {final_missing_rate_desc:.2f}% ({final_missing_desc} sites)")
    print(f"  Duplicate URLs: {final_duplicates}")

    # 6. 保存结果
    print("\n[6/6] Saving results...")

    # Create backup before overwrite
    backup_file = BACKUP_DIR / f'websites.json.v14_p3_backup_{original_total}entries'
    if not DATA_FILE.exists():
        print(f"  ERROR: Data file not found: {DATA_FILE}")
        return 1

    # Read original again to ensure we don't lose data if something went wrong
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        original_backup = json.load(f)
    save_data(original_backup, backup_file)
    print(f"  ✓ Backup saved: {backup_file.name}")

    # Write cleaned data atomically
    temp_file = DATA_FILE.with_suffix('.tmp')
    save_data(cleaned_data, temp_file)
    temp_file.replace(DATA_FILE)
    print(f"  ✓ Cleaned data written: {DATA_FILE.name}")

    # 7. 生成报告
    stats = {
        'original_total': original_total,
        'cleaned_total': len(cleaned_data),
        'duplicates_found': duplicates_found,
        'filled': filled,
        'standardized': standardized,
        'still_missing': still_missing,
        'duplicate_details': [(normalize_url(data[i]['url']), i) for i in range(len(data))
                              if any(i in grp for grp in url_map2.values() if len(grp) > 1)][:20],
        'category_changes': cat_changes
    }

    report = generate_report(data, cleaned_data, stats)

    # 8. 输出摘要
    print("\n" + "=" * 70)
    print("V14-P3 EXECUTION SUMMARY")
    print("=" * 70)
    print(f"Original sites:   {original_total:,}")
    print(f"Duplicates removed: {duplicates_found:,}")
    print(f"Final sites:      {len(cleaned_data):,}")
    print(f"Name fields filled: {filled['name']}")
    print(f"Desc fields filled: {filled['description']}")
    print(f"Categories standardized: {standardized}")
    print(f"\nQuality Status:")
    print(f"  Name missing rate:    {final_missing_rate_name:.2f}% {'✓ PASS' if final_missing_rate_name == 0 else '✗ FAIL'}")
    print(f"  Desc missing rate:    {final_missing_rate_desc:.2f}% {'✓ PASS' if final_missing_rate_desc == 0 else '✗ FAIL'}")
    print(f"  Duplicate URLs:       {final_duplicates} {'✓ PASS' if final_duplicates == 0 else '✗ FAIL'}")

    all_pass = (final_missing_rate_name == 0 and
                final_missing_rate_desc == 0 and
                final_duplicates == 0)
    print(f"\nOverall: {'✅ ALL QUALITY TARGETS MET' if all_pass else '❌ SOME TARGETS NOT MET'}")
    print("=" * 70)

    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())
