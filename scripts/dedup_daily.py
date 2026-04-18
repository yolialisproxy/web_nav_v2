#!/usr/bin/env python3
import json
import os
from datetime import datetime
import hashlib
import copy

def generate_site_hash(site):
    if 'url' in site and site['url']:
        return hashlib.md5(site['url'].strip().lower().encode('utf-8')).hexdigest()
    else:
        name = site.get('name', site.get('title','')).strip().lower()
        desc = site.get('description', '').strip().lower()
        return hashlib.md5(f"{name}|{desc}".encode('utf-8')).hexdigest()

def main():
    input_path = "/home/yoli/GitHub/web_nav_v2/data/websites.json"
    backup_dir = "/home/yoli/GitHub/web_nav_v2/backups"
    report_dir = "/home/yoli/GitHub/web_nav_v2/reports"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f"websites_before_dedup_{timestamp}.json")
    os.system(f"cp {input_path} {backup_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_sites = 0
    seen_hashes = set()
    duplicate_sites = []
    cleaned_data = copy.deepcopy(data)

    # 遍历所有分类
    for category_name, category in cleaned_data.items():
        if 'subcategories' not in category:
            continue
        for subcat in category['subcategories']:
            if 'minor_categories' not in subcat:
                continue
            for minor in subcat['minor_categories']:
                if 'sites' not in minor:
                    continue
                # 去重处理此分类下的站点
                original_sites = minor['sites']
                total_sites += len(original_sites)
                unique_sites = []
                for site in original_sites:
                    if not isinstance(site, dict):
                        continue
                    h = generate_site_hash(site)
                    if h not in seen_hashes:
                        seen_hashes.add(h)
                        unique_sites.append(site)
                    else:
                        duplicate_sites.append(site)
                minor['sites'] = unique_sites

    duplicate_count = len(duplicate_sites)
    remaining_count = total_sites - duplicate_count
    duplicate_rate = (duplicate_count / total_sites) * 100 if total_sites > 0 else 0

    report = []
    report.append("=" * 60)
    report.append("🔍 导航网站每日去重清理报告")
    report.append("=" * 60)
    report.append(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"📊 统计结果:")
    report.append(f"  原始站点总数: {total_sites}")
    report.append(f"  发现重复站点: {duplicate_count}")
    report.append(f"  清理后剩余: {remaining_count}")
    report.append(f"  重复率: {duplicate_rate:.2f}%")
    report.append("-" * 60)

    cleaned = False
    if duplicate_rate > 5.0:
        report.append("✅ 重复率超过阈值(5%)，执行清理操作")
        with open(input_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        report.append(f"✅ 已更新 websites.json 文件")
        cleaned = True
    else:
        report.append("ℹ️  重复率低于5%，不执行覆盖写入")

    if duplicate_sites:
        report.append("\n📝 重复站点示例(前10个):")
        for i, site in enumerate(duplicate_sites[:10]):
            url = site.get('url','NO_URL')[:60]
            name = site.get('name',site.get('title','N/A'))
            report.append(f"  #{i+1:2d} | {name:<20} | {url}")

    report.append("\n✅ 任务完成")
    report.append(f"📦 原始文件备份: {backup_path}")

    report_content = "\n".join(report)
    print(report_content)

    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"dedup_report_{timestamp}.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    with open(os.path.join(report_dir, "latest_dedup_stats.json"), 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "total_before": total_sites,
            "duplicates": duplicate_count,
            "total_after": remaining_count,
            "duplicate_rate": round(duplicate_rate,2),
            "cleaned": cleaned,
            "backup_file": backup_path,
            "report_file": report_path
        }, f, ensure_ascii=False, indent=2)

    print(f"\n📄 完整报告已保存: {report_path}")

if __name__ == "__main__":
    main()
