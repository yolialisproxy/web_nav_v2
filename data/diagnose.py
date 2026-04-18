import json
from collections import Counter

# 读取数据
with open('websites.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_sites = []
empty_title = 0
empty_desc = 0
title_is_url = 0
urls = []

# 遍历所有站点
for main_cat in data.values():
    for subcat in main_cat.get('subcategories', []):
        for minor_cat in subcat.get('minor_categories', []):
            for site in minor_cat.get('sites', []):
                all_sites.append(site)
                url = site.get('url', '').strip()
                title = site.get('title', '').strip()
                desc = site.get('description', '').strip()

                urls.append(url)

                if not title:
                    empty_title +=1
                elif title.startswith(('http://', 'https://', 'www.')) or title == url:
                    title_is_url +=1

                if not desc:
                    empty_desc +=1

# 统计重复URL
url_counts = Counter(urls)
duplicate_urls = sum(1 for cnt in url_counts.values() if cnt >1)
duplicate_total = sum(cnt-1 for cnt in url_counts.values())

total = len(all_sites)

report = f"""=== 网站导航数据质量诊断报告 ===
总站点数: {total}

标题问题:
- 空标题站点: {empty_title} ({empty_title/total*100:.1f}%)
- 标题为URL: {title_is_url} ({title_is_url/total*100:.1f}%)
- 合计标题需优化: {empty_title + title_is_url} ({(empty_title+title_is_url)/total*100:.1f}%)

描述问题:
- 无描述站点: {empty_desc} ({empty_desc/total*100:.1f}%)

重复问题:
- 重复URL数量: {duplicate_urls} 个域名重复
- 重复站点总数: {duplicate_total} 个条目

需要处理站点总计: 约 {max(empty_title+title_is_url, empty_desc)} 个
"""

print(report)

# 保存报告
with open('quality_report.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print("\n报告已保存到 quality_report.txt")
