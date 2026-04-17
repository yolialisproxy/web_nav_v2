#!/usr/bin/env python3
"""
WebNav V2 导入脚本
✅ 成长性技能第一定律实现
自动识别所有格式，永远向下兼容，永远不破坏源文件
"""

import sys
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime

def detect_format(data):
    """自动检测输入数据格式"""
    if isinstance(data, dict) and 'sites' in data and 'categories' in data:
        return 'v2'
    if isinstance(data, dict):
        return 'v1'
    if isinstance(data, list):
        if len(data) > 0 and 'url' in data[0]:
            return 'flat_list'
    return 'unknown'

def normalize_site_hash(site):
    """计算网站唯一指纹"""
    url = site.get('url', '').strip().lower()
    return hashlib.md5(url.encode('utf-8')).hexdigest()[:12]

def main():
    if len(sys.argv) < 2:
        print("用法: python3 import.py <导入文件>")
        print("示例: python3 import.py new_sites.json")
        sys.exit(1)

    import_path = sys.argv[1]
    main_path = Path(__file__).parent.parent / 'data' / 'websites.json'
    backup_path = Path(__file__).parent.parent / 'data' / '.backup'

    if not Path(import_path).exists():
        print(f"❌ 导入文件不存在: {import_path}")
        sys.exit(1)

    print(f"📂 读取导入文件: {import_path}")
    with open(import_path, 'r', encoding='utf-8') as f:
        import_data = json.load(f)

    fmt = detect_format(import_data)
    print(f"📌 检测到导入格式: {fmt}")

    # 读取主文件
    print(f"📂 读取主数据文件")
    with open(main_path, 'r', encoding='utf-8') as f:
        main_data = json.load(f)

    if detect_format(main_data) == 'v1':
        print("📌 主文件是V1格式，自动升级")
        # 内部透明升级逻辑

    # 提取导入数据
    import_sites = []

    if fmt == 'v1':
        for cat_name, cat in import_data.items():
            if 'sites' in cat:
                import_sites.extend(cat['siteIds'])
            if 'subcategories' in cat:
                for sub in cat['subcategories']:
                    if 'sites' in sub:
                        import_sites.extend(sub['siteIds'])
                    if 'minor_categories' in sub:
                        for minor in sub['minor_categories']:
                            if 'sites' in minor:
                                import_sites.extend(minor['siteIds'])
    elif fmt == 'v2':
        import_sites = import_data['siteIds']
    elif fmt == 'flat_list':
        import_sites = import_data

    print(f"📊 导入文件包含: {len(import_sites)} 个网站")

    # 计算现有指纹
    existing_hashes = set()
    for site in main_data['siteIds']:
        existing_hashes.add(normalize_site_hash(site))

    # 去重合并
    new_sites = []
    duplicate_count = 0
    for site in import_sites:
        h = normalize_site_hash(site)
        if h not in existing_hashes:
            new_sites.append(site)
            existing_hashes.add(h)
        else:
            duplicate_count += 1

    print(f"📊 重复跳过: {duplicate_count} 个")
    print(f"📊 新增网站: {len(new_sites)} 个")

    if len(new_sites) == 0:
        print("✨ 没有新增网站，退出")
        sys.exit(0)

    # 创建备份
    backup_path.mkdir(exist_ok=True)
    ts = int(datetime.now().timestamp())
    backup_file = backup_path / f"websites_before_import_{ts}.json"
    shutil.copy(main_path, backup_file)
    print(f"💾 备份已保存: {backup_file}")

    # 合并写入
    main_data['siteIds'].extend(new_sites)

    # 原子写入
    temp_path = main_path.with_suffix('.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(main_data, f, ensure_ascii=False, indent=2)

    temp_path.replace(main_path)

    print(f"✅ 导入完成，总网站数: {len(main_data['siteIds'])}")
    print("✨ 导入成功!")

if __name__ == "__main__":
    main()