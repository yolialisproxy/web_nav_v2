
import json

file_path = '/home/yoli/GitHub/web_nav_v2/data/websites.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("扫描所有分类的站点数量:")
total_all = 0
biggest = None
biggest_count = 0
biggest_path = ""

for cat_name, cat_data in data.items():
    if 'subcategories' not in cat_data:
        continue
    for subcat in cat_data['subcategories']:
        if 'minor_categories' not in subcat:
            continue
        for minor in subcat['minor_categories']:
            if 'sites' in minor:
                cnt = len(minor['sites'])
                total_all += cnt
                if cnt > biggest_count:
                    biggest_count = cnt
                    biggest = minor
                    biggest_path = f"{cat_name} > {subcat['name']} > {minor['name']}"

print(f"总站点数: {total_all}")
print(f"最大分类: {biggest_path}, 站点数量: {biggest_count}")

if biggest_count > 900:
    print("\n这个就是待分发池！")
