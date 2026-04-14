
import json
import os

# 读取文件
file_path = '/home/yoli/GitHub/web_nav_v2/data/websites.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 定位待分发池
pending_sites = []
pending_category = None

# 查找待分发/其他/全部分类
for cat_name, cat_data in data.items():
    if 'subcategories' in cat_data:
        for subcat in cat_data['subcategories']:
            if 'minor_categories' in subcat:
                for minor in subcat['minor_categories']:
                    if minor.get('name') == '全部' or minor.get('name') == '待分发' or minor.get('name') == '其他':
                        if 'sites' in minor and len(minor['sites']) > 900:
                            pending_sites = minor['sites']
                            pending_category = minor
                            print(f"找到待分发池，共有 {len(pending_sites)} 个网站")
                            break
                if pending_sites:
                    break
        if pending_sites:
            break

if not pending_sites:
    print("未找到待分发池")
    exit(1)

# 收集所有可用的小类，统计现有数量
minor_categories = []
for cat_name, cat_data in data.items():
    if 'subcategories' not in cat_data:
        continue
    for subcat in cat_data['subcategories']:
        if 'minor_categories' not in subcat:
            continue
        for minor in subcat['minor_categories']:
            if minor is pending_category:
                continue
            if 'sites' not in minor:
                minor['sites'] = []
            current_count = len(minor['sites'])
            if current_count < 25:
                minor_categories.append({
                    'obj': minor,
                    'count': current_count,
                    'capacity': 25 - current_count
                })

print(f"找到 {len(minor_categories)} 个可用小类")

# 计算每个小类目标数量，均匀分发
total_pending = len(pending_sites)
total_capacity = sum(m['capacity'] for m in minor_categories)

print(f"待分发: {total_pending}, 总容量: {total_capacity}")

# 均匀分发
distributed = 0
for minor in sorted(minor_categories, key=lambda x: x['count']):
    if distributed >= total_pending:
        break
    target = 18
    need = max(0, target - minor['count'])
    if need <= 0:
        continue
        
    take = min(need, total_pending - distributed)
    # 取出对应数量的网站
    sites_to_move = pending_sites[distributed:distributed + take]
    minor['obj']['sites'].extend(sites_to_move)
    distributed += take
    print(f"分配 {take} 个到 {minor['obj'].get('name')}, 现在有 {len(minor['obj']['sites'])} 个")

# 剩余的再均匀分配到容量未满的
remaining = total_pending - distributed
if remaining > 0:
    print(f"剩余 {remaining} 个继续分配")
    i = 0
    while remaining > 0 and i < len(minor_categories):
        minor = minor_categories[i]
        if len(minor['obj']['sites']) < 25:
            minor['obj']['sites'].append(pending_sites[distributed])
            distributed += 1
            remaining -= 1
        i = (i + 1) % len(minor_categories)

# 清空待分发池
pending_category['sites'] = pending_sites[distributed:]

print(f"分发完成: 共分配 {distributed} 个网站, 剩余 {len(pending_category['sites'])} 个")

# 验证每个小类数量
print("\n小类数量统计:")
for minor in minor_categories:
    cnt = len(minor['obj']['sites'])
    print(f"{minor['obj'].get('name')}: {cnt} 个")

# 保存回文件
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n文件已保存到 {file_path}")
