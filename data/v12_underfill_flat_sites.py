#!/usr/bin/env python3
"""
啃魂导航 V12 Phase 1.3 - 欠容填充（flat_sites候选部分）
将 v12_underfill_ready.json 中的候选站点批量导入到 websites.json
"""

import json
import os
from datetime import datetime
from urllib.parse import urlparse

# 路径配置
WORKSPACE = "/home/yoli"
DATA_DIR = os.path.join(WORKSPACE, "GitHub", "web_nav_v2", "data")
WEBSITES_FILE = os.path.join(DATA_DIR, "websites.json")
UNDERFILL_FILE = os.path.join(DATA_DIR, "v12_underfill_ready.json")
BACKUP_FILE = os.path.join(DATA_DIR, "websites.json.v12_underfill_backup")
REPORT_FILE = os.path.join(DATA_DIR, "V12_UNDERFILL_FLAT_SITES_REPORT.md")

def extract_domain(url):
    """从URL提取域名用于生成name"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # 移除www前缀
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return url

def generate_name_from_url(url):
    """从URL生成名称"""
    domain = extract_domain(url)
    # 提取主要部分，如 'github' from 'github.com'
    parts = domain.split('.')
    if len(parts) >= 2:
        # 取倒数第二个部分，如 github from github.com
        name = parts[-2]
        # 首字母大写
        return name.capitalize()
    return domain

def generate_title_from_url(url):
    """从URL生成标题"""
    domain = extract_domain(url)
    # 替换点和连字符为空格，然后首字母大写
    title = domain.replace('.', ' ').replace('-', ' ').title()
    return title

def main():
    print("=" * 60)
    print("啃魂导航 V12 Phase 1.3 - 欠容填充开始")
    print("=" * 60)

    # 1. 读取现有 websites.json
    print("\n[1/6] 读取现有 websites.json...")
    with open(WEBSITES_FILE, 'r', encoding='utf-8') as f:
        websites = json.load(f)
    print(f"  ✓ 当前站点数: {len(websites)}")

    # 构建现有URL集合用于快速去重
    existing_urls = set()
    for site in websites:
        if 'url' in site:
            existing_urls.add(site['url'])
    print(f"  ✓ 已索引 {len(existing_urls)} 个现有URL")

    # 2. 读取 v12_underfill_ready.json
    print("\n[2/6] 读取 v12_underfill_ready.json...")
    with open(UNDERFILL_FILE, 'r', encoding='utf-8') as f:
        underfill_data = json.load(f)

    # 3. 提取所有候选站点
    print("\n[3/6] 提取候选站点...")
    all_candidates = []
    by_category = underfill_data.get('by_category', {})

    for category_path, category_info in by_category.items():
        candidates = category_info.get('candidates', [])
        for candidate in candidates:
            # 确保候选站点有category字段
            if 'category' not in candidate:
                candidate['category'] = category_path
            all_candidates.append(candidate)

    print(f"  ✓ 候选站点总数: {len(all_candidates)}")

    # 4. 处理候选站点：去重、补充字段
    print("\n[4/6] 处理候选站点（去重 + 补充字段）...")
    new_sites = []
    skipped_duplicates = 0
    skipped_no_url = 0

    for candidate in all_candidates:
        url = candidate.get('url', '').strip()
        if not url:
            skipped_no_url += 1
            continue

        # 检查重复
        if url in existing_urls:
            skipped_duplicates += 1
            continue

        # 构建完整站点对象
        new_site = {}

        # URL
        new_site['url'] = url

        # Title: 优先使用候选title，否则从URL生成
        title = candidate.get('title', '').strip()
        if not title:
            title = generate_title_from_url(url)
        new_site['title'] = title

        # Name: 从URL生成
        name = candidate.get('name', '').strip()
        if not name:
            name = generate_name_from_url(url)
        new_site['name'] = name

        # Description: 使用占位符
        description = candidate.get('description', '').strip()
        if not description:
            description = f"欠容填充站点 - {candidate.get('category', '未分类')}"
        new_site['description'] = description

        # Category (来自候选数据)
        new_site['category'] = candidate.get('category', '未分类')

        # _cat: 与category相同（根据websites.json观察）
        new_site['_cat'] = new_site['category']

        # Source: 标记为v12_underfill
        new_site['source'] = 'v12_underfill'

        new_sites.append(new_site)
        existing_urls.add(url)  # 更新existing_urls避免后续重复

    print(f"  ✓ 新增站点数: {len(new_sites)}")
    print(f"  ✓ 跳过重复URL: {skipped_duplicates}")
    print(f"  ✓ 跳过无URL: {skipped_no_url}")

    # 5. 统计新增站点分类分布
    print("\n[5/6] 分类统计...")
    category_stats = {}
    for site in new_sites:
        cat = site['category']
        category_stats[cat] = category_stats.get(cat, 0) + 1

    print(f"  ✓ 覆盖分类数: {len(category_stats)}")
    print("  分类详情:")
    for cat, count in sorted(category_stats.items()):
        print(f"    - {cat}: {count}个")

    # 6. 备份并更新 websites.json
    print("\n[6/6] 备份并更新 websites.json...")
    # 备份原文件
    import shutil
    shutil.copy2(WEBSITES_FILE, BACKUP_FILE)
    print(f"  ✓ 备份已创建: {BACKUP_FILE}")

    # 追加新站点（原子写入：先写临时文件，再重命名）
    updated_websites = websites + new_sites

    temp_file = WEBSITES_FILE + ".tmp"
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(updated_websites, f, ensure_ascii=False, indent=2)

    os.replace(temp_file, WEBSITES_FILE)
    print(f"  ✓ websites.json 已更新，总站点数: {len(updated_websites)}")

    # 7. 生成报告
    print("\n[7/7] 生成填充报告...")
    generate_report(REPORT_FILE, new_sites, category_stats, skipped_duplicates, skipped_no_url)
    print(f"  ✓ 报告已生成: {REPORT_FILE}")

    print("\n" + "=" * 60)
    print("欠容填充完成！")
    print("=" * 60)

def generate_report(report_path, new_sites, category_stats, skipped_duplicates, skipped_no_url):
    """生成填充报告"""
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 啃魂导航 V12 Phase 1.3 - 欠容填充报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        f.write("## 任务概述\n\n")
        f.write("执行V12 Phase 1.3欠容填充操作，将 `flat_sites` 候选站点批量导入到 `websites.json`。\n\n")

        f.write("## 统计数据\n\n")
        f.write(f"- **新增站点总数**: {len(new_sites)} 个\n")
        f.write(f"- **覆盖分类数**: {len(category_stats)} 个\n")
        f.write(f"- **跳过重复URL**: {skipped_duplicates} 个\n")
        f.write(f"- **跳过无效URL**: {skipped_no_url} 个\n\n")

        f.write("## 分类明细\n\n")
        f.write("| 分类 | 新增数量 |\n")
        f.write("|------|----------|\n")
        for cat, count in sorted(category_stats.items()):
            f.write(f"| {cat} | {count} |\n")
        f.write("\n")

        f.write("## 新增站点详情\n\n")
        f.write("| 序号 | URL | 名称 | 标题 | 分类 |\n")
        f.write("|------|-----|------|------|------|\n")
        for i, site in enumerate(new_sites, 1):
            name = site.get('name', '')
            title = site.get('title', '')
            url = site.get('url', '')
            category = site.get('category', '')
            f.write(f"| {i} | [{url}]({url}) | {name} | {title} | {category} |\n")
        f.write("\n")

        f.write("---\n\n")
        f.write("## 任务完成状态\n\n")
        f.write("- [x] 读取现有 websites.json\n")
        f.write("- [x] 提取 v12_underfill_ready.json 候选站点\n")
        f.write("- [x] 去重检查\n")
        f.write("- [x] 补充缺失字段\n")
        f.write("- [x] 原子写入更新 websites.json\n")
        f.write("- [x] 生成填充报告\n\n")

        f.write("**状态**: ✅ 完成\n")

if __name__ == "__main__":
    main()
