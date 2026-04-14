
import json

file_path = '/home/yoli/GitHub/web_nav_v2/data/websites.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("超过100站点的分类:")
total_pending = 0
pending_list = []

for cat_name, cat_data in data.items():
    if 'subcategories' not in cat_data:
        continue
    for subcat in cat_data['subcategories']:
        if 'minor_categories' not in subcat:
            continue
        for minor in subcat['minor_categories']:
            if 'sites' in minor:
                cnt = len(minor['sites'])
                if cnt >= 100:
                    print(f"{cat_name} > {subcat['name']} > {minor['name']}: {cnt}")
                    total_pending += cnt
                    pending_list.append(minor)

print(f"\n总计待分发池大小: {total_pending}")
