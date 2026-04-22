#!/usr/bin/env python3
import json
import sys
from datetime import datetime

def audit_websites(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n=== 导航网站质量审计报告 ===\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n文件: {file_path}\n")

    total_sites = 0
    with_titles = 0
    with_desc = 0
    with_categories = 0

    # Handle both old dict format and new flat list format
    if isinstance(data, dict):
        site_list = []
        for big_cat_name, big_cat_val in data.items():
            if isinstance(big_cat_val, dict) and 'sites' in big_cat_val:
                site_list.extend(big_cat_val['sites'])
        data = site_list

    for site in data:
        total_sites +=1
        if 'title' in site and site['title']:
            with_titles +=1
        if 'description' in site and site['description']:
            with_desc +=1
        if 'category' in site and site['category']:
            with_categories +=1

    print(f"Total sites:       {total_sites}")
    print(f"With titles:       {with_titles} ({with_titles/total_sites*100:.1f}%)")
    print(f"With descriptions: {with_desc} ({with_desc/total_sites*100:.1f}%)")
    print(f"With categories:   {with_categories} ({with_categories/total_sites*100:.1f}%)")
    print(f"\n✅ Audit completed")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} data/websites.json")
        sys.exit(1)
    sys.exit(audit_websites(sys.argv[1]))
