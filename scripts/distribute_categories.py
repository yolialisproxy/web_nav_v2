#!/usr/bin/env python3
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from safe_json_io import safe_read_json, safe_write_json

import os
from datetime import datetime

def count_total_sites(data):
    count = 0
    for big_cat in data.values():
        if not isinstance(big_cat, dict): continue
        for mid_cat in big_cat.get('subcategories', []):
            for minor_cat in mid_cat.get('minor_categories', []):
                count += len(minor_cat.get('sites', []))
    return count

def main():
    base_dir = '/home/yoli/GitHub/web_nav_v2'
    data_path = os.path.join(base_dir, 'data/websites.json')
    pool_path = os.path.join(base_dir, 'data/collected_buffer.json')
    backup_dir = os.path.join(base_dir, 'data/.backup')

    os.makedirs(backup_dir, exist_ok=True)

    # 备份
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_path = os.path.join(backup_dir, f'websites.json.backup.{timestamp}')
    os.system(f'cp {data_path} {backup_path}')
    print(f'✅ 已备份到: {backup_path}')

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(pool_path, 'r', encoding='utf-8') as f:
        pool_raw = json.load(f)
        if isinstance(pool_raw, dict):
            pool = list(pool_raw.get('sites', []))
            pool_meta = pool_raw
        else:
            pool = list(pool_raw)
            pool_meta = {}

    print(f'📊 当前主库网站数: {count_total_sites(data)}')
    print(f'📦 待分类池剩余: {len(pool)} 个')

    if len(pool) == 0:
        print('✅ 没有待分类网站，任务完成')
        return

    distributed = 0

    # 遍历所有大类
    for big_name, big_cat in data.items():
        if not isinstance(big_cat, dict): continue
        # 中类是列表
        for mid_cat in big_cat.get('subcategories', []):
            if 'minor_categories' not in mid_cat:
                mid_cat['minor_categories'] = []

            # 小类也是列表
            for minor_cat in mid_cat['minor_categories']:
                if 'sites' not in minor_cat:
                    minor_cat['sites'] = []

                # 每个小类上限100
                while len(minor_cat.get('sites', [])) < 100 and len(pool) > 0:
                    site = pool.pop(0)
                    minor_cat['sites'].append(site)
                    distributed += 1

    print(f'✅ 已分发: {distributed} 个网站')
    print(f'📦 待分类池剩余: {len(pool)} 个')
    print(f'📊 分发后主库网站数: {count_total_sites(data)}')

    # 写回
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(pool_path, 'w', encoding='utf-8') as f:
        if pool_meta:
            pool_meta['siteIds'] = pool
            json.dump(pool_meta, f, ensure_ascii=False, indent=2)
        else:
            json.dump(pool, f, ensure_ascii=False, indent=2)

    print('✅ 数据已保存')

if __name__ == '__main__':
    main()
