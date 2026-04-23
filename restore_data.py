#!/usr/bin/env python3
import json

# 加载完整站点数据
with open('websites.json', 'r', encoding='utf-8') as f:
    sites = json.load(f)

print(f"✅ 加载到 {len(sites)} 个站点数据")

# 构建 webstack 标准格式
webstack_data = []
for site in sites:
    item = {
        "name": site.get("name", ""),
        "url": site.get("url", ""),
        "desc": site.get("description", site.get("desc", "")),
        "logo": site.get("logo", ""),
        "category": site.get("category", "未分类"),
        "subcategory": site.get("subcategory", ""),
        "tag": site.get("tag", "")
    }
    webstack_data.append(item)

# 写入数据文件
with open('webstack_data.json', 'w', encoding='utf-8') as f:
    json.dump(webstack_data, f, ensure_ascii=False, indent=2)

print(f"✅ 成功重建 webstack_data.json，包含 {len(webstack_data)} 个站点")
print(f"✅ 文件大小: {f.tell()} 字节")
