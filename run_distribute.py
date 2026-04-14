
import json

file_path = '/home/yoli/GitHub/web_nav_v2/data/websites.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 收集所有待分发站点
pending_sites = []
pending_cats = []

# 收集所有大分类作为待分发池
for cat_name, cat_data in data.items():
    if 'subcategories' not in cat_data:
        continue
    for subcat in cat_data['subcategories']:
        if 'minor_categories' not in subcat:
            continue
        for minor in subcat['minor_categories']:
            if 'sites' in minor:
                cnt = len(minor['sites'])
                if cnt >= 100 or minor.get('name') in ['其他', '全部', '待分发']:
                    pending_sites.extend(minor['sites'])
                    pending_cats.append(minor)

print(f"待分发总站点: {len(pending_sites)}")

# 收集所有目标小类
target_cats = []
for cat_name, cat_data in data.items():
    if 'subcategories' not in cat_data:
        continue
    for subcat in cat_data['subcategories']:
        if 'minor_categories' not in subcat:
            continue
        for minor in subcat['minor_categories']:
            if minor in pending_cats:
                continue
            if 'sites' not in minor:
                minor['sites'] = []
            cnt = len(minor['sites'])
            if cnt < 25:
                target_cats.append({
                    'obj': minor,
                    'count': cnt
                })

print(f"可用目标小类: {len(target_cats)}")

# 第一轮: 每个小类补到18个
distributed = 0
for cat in sorted(target_cats, key=lambda x: x['count']):
    if distributed >= len(pending_sites):
        break
    need = max(0, 18 - cat['count'])
    if need <= 0:
        continue
    take = min(need, len(pending_sites) - distributed)
    cat['obj']['sites'].extend(pending_sites[distributed:distributed+take])
    distributed += take
    cat['count'] = len(cat['obj']['sites'])

print(f"第一轮分发: {distributed}")

# 第二轮: 剩余的均匀分配，最多到25个
remaining = len(pending_sites) - distributed
idx = 0
while remaining > 0:
    cat = target_cats[idx]
    if len(cat['obj']['sites']) < 25:
        cat['obj']['sites'].append(pending_sites[distributed])
        distributed += 1
        remaining -= 1
    idx = (idx + 1) % len(target_cats)
    if idx == 0 and all(len(c['obj']['sites']) >= 25 for c in target_cats):
        break

print(f"总计分发: {distributed}")
print(f"剩余未分发: {len(pending_sites) - distributed}")

# 清空待分发分类，放剩余的
remain_sites = pending_sites[distributed:]
for cat in pending_cats:
    cat['sites'] = []
if remain_sites:
    pending_cats[0]['sites'] = remain_sites

# 统计结果
print("\n最终小类数量分布:")
counts = []
for cat in target_cats:
    cnt = len(cat['obj']['sites'])
    counts.append(cnt)
    if cnt < 12 or cnt > 25:
        print(f"⚠️  {cat['obj']['name']}: {cnt}")

print(f"\n范围: {min(counts)} - {max(counts)}")
print(f"平均: {sum(counts)/len(counts):.1f}")

# 保存
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 文件已保存: {file_path}")
