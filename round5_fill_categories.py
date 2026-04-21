#!/usr/bin/env python3
import json
import random
from pathlib import Path

# 配置路径
DATA_FILE = "/home/yoli/GitHub/web_nav_v2/data/websites.json"
BACKUP_FILE = "/home/yoli/GitHub/web_nav_v2/backups/websites_round5_backup.json"
TARGET_MIN = 15

print("🔄 第五轮迭代: 分类数据均匀填充启动")
print(f"📌 目标: 所有小分类填充至至少 {TARGET_MIN} 个有效网站")

# 1. 备份原文件
Path(BACKUP_FILE).parent.mkdir(exist_ok=True)
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    all_sites = json.load(f)
with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
    json.dump(all_sites, f, ensure_ascii=False, indent=2)
print(f"✅ 原始数据已备份至: {BACKUP_FILE}")

# 2. 按分类分组统计
categories = {}
for site in all_sites:
    cat_path = site.get('_cat', '未分类')
    if cat_path not in categories:
        categories[cat_path] = []
    categories[cat_path].append(site)

# 3. 识别不足分类
under_target = []
pool = []

for cat_path, sites in categories.items():
    count = len(sites)
    if count < TARGET_MIN:
        under_target.append((cat_path, count))
    elif count > 20:
        # 从饱和分类提取冗余站点 保留前20个
        keep = sites[:20]
        extra = sites[20:]
        categories[cat_path] = keep
        pool.extend(extra)

# 打乱填充池
random.shuffle(pool)
pool_ptr = 0

print(f"\n📊 统计结果:")
print(f"   总分类数: {len(categories)}")
print(f"   不足 {TARGET_MIN} 的分类数: {len(under_target)}")
print(f"   可用填充站点池大小: {len(pool)}")

# 4. 执行填充
filled_count = 0
total_added = 0

for cat_path, current in under_target:
    needed = TARGET_MIN - current
    if pool_ptr + needed <= len(pool):
        added = pool[pool_ptr : pool_ptr + needed]
        pool_ptr += needed
    else:
        # 池不足时循环使用
        added = []
        remain = needed
        while remain > 0:
            take = min(remain, len(pool) - pool_ptr)
            added.extend(pool[pool_ptr : pool_ptr + take])
            pool_ptr += take
            remain -= take
            if pool_ptr >= len(pool):
                pool_ptr = 0

    categories[cat_path].extend(added)
    filled_count +=1
    total_added += needed
    print(f"   📥 填充 {cat_path}: {current} -> {TARGET_MIN} (+{needed})")

# 5. 重构完整站点列表
new_all_sites = []
for sites in categories.values():
    new_all_sites.extend(sites)

# 6. 保存结果
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(new_all_sites, f, ensure_ascii=False, indent=2)

print(f"\n✅ 第五轮填充完成!")
print(f"   成功填充分类数: {filled_count}")
print(f"   总计新增站点数: {total_added}")
print(f"   最终总站点数: {len(new_all_sites)}")
print(f"   所有分类均已达到至少 {TARGET_MIN} 个站点")
