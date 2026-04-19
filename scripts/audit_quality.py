#!/usr/bin/env python3
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from safe_json_io import safe_read_json, safe_write_json

import os
import sys
from datetime import datetime

def audit_websites(file_path):
    if not os.path.exists(file_path):
        print(f"错误：文件不存在 {file_path}")
        sys.exit(1)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            sys.exit(1)

    total_sites = 0
    missing_title = 0
    missing_desc = 0
    bad_categories = []
    empty_url = 0
    
    print(f"\n=== 导航网站质量审计报告 ===\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n文件: {file_path}\n")

    for big_cat_name, big_cat_val in data.items():
        subcats = big_cat_val.get('subcategories', [])
        if not isinstance(subcats, list): continue
        
        for mid_cat in subcats:
            minor_cats = mid_cat.get('minor_categories', [])
            
            # 部分中类直接包含站点
            sites = mid_cat.get('sites', [])
            for site in sites:
                total_sites += 1
                if not site.get('url', '').strip(): empty_url += 1
                if not site.get('title', '').strip(): missing_title += 1
                if not site.get('description', '').strip(): missing_desc += 1

            if not isinstance(minor_cats, list): continue
            for small_cat in minor_cats:
                small_cat_name = small_cat.get('name', 'Unknown')
                if any(word in small_cat_name for word in ["小类", "默认", "其他1", "其他2", "工具工具", "资源资源"]):
                    bad_categories.append(f"{big_cat_name} -> {mid_cat.get('name', 'Unknown')} -> {small_cat_name}")
                
                sites = small_cat.get('sites', [])
                for site in sites:
                    total_sites += 1
                    if not site.get('url', '').strip(): empty_url += 1
                    if not site.get('title', '').strip(): missing_title += 1
                    if not site.get('description', '').strip(): missing_desc += 1
    
    # 输出报告
    print(f"总站点数:    {total_sites:>6,}")
    print(f"空 URL:      {empty_url:>6,}  {empty_url/total_sites*100:>6.2f}%" if total_sites>0 else 0)
    print(f"标题缺失:    {missing_title:>6,}  {missing_title/total_sites*100:>6.2f}%" if total_sites>0 else 0)
    print(f"描述缺失:    {missing_desc:>6,}  {missing_desc/total_sites*100:>6.2f}%" if total_sites>0 else 0)
    print(f"违规分类:    {len(bad_categories):>6,}")
    if bad_categories:
        print("\n违规分类列表:")
        for bc in bad_categories[:20]:
            print(f"  - {bc}")
        if len(bad_categories) > 20:
            print(f"  ... 还有 {len(bad_categories)-20} 个")

    print(f"\n当前状态: {'❌ 严重不合格' if missing_title/total_sites > 0.05 else '✅ 合格'}\n")

    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} data/websites.json")
        sys.exit(1)
    sys.exit(audit_websites(sys.argv[1]))
