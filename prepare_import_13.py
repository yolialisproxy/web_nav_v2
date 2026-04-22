#!/usr/bin/env python3
import json
from urllib.parse import urlparse
import re

def normalize_url(url):
    if not url:
        return ""
    url = url.strip().lower()
    url = re.sub(r'\\[u"\\/\\\\]+', '', url)
    url = re.sub(r'^https?://(www\.)?', '', url)
    url = url.rstrip('/')
    return url

def validate_quality(site):
    # Filter out garbage sites
    url = site.get('url', '').strip()
    title = site.get('title', '').strip()
    desc = site.get('description', '').strip()

    if not url or not url.startswith(('http://', 'https://')):
        return False
    if len(title) < 2:
        return False
    if title == url:
        return False
    if 'example.com' in url or 'localhost' in url or '127.0.0.1' in url:
        return False
    if 'create-react-app' in desc or 'Description will go into' in desc:
        return False

    return True

def main():
    print("✅ 准备第13批导入站点 200个高质量站点")
    print("=" * 60)

    # Load raw data
    with open('/home/yoli/GitHub/web_nav_v2/data/websites.json', 'r', encoding='utf-8') as f:
        all_sites = json.load(f)

    print(f"✅ 已加载全部原始站点: {len(all_sites)} 个")

    seen = set()
    valid_sites = []

    for site in all_sites:
        if not validate_quality(site):
            continue

        norm_url = normalize_url(site['url'])
        if norm_url in seen:
            continue

        seen.add(norm_url)

        # Clean up site data
        cleaned = {
            'url': site['url'].strip(),
            'title': site['title'].strip(),
            'description': site.get('description', '').strip(),
            'category': site.get('category', '其他'),
            '_source': 'curated_navigation_import_13',
            '_trust_score': 8
        }
        valid_sites.append(cleaned)

        if len(valid_sites) >= 200:
            break

    print(f"\n📊 处理结果:")
    print(f"   过滤后有效站点: {len(valid_sites)} 个")
    print(f"   去重移除: {len(all_sites) - len(seen)} 个")
    print(f"   质量过滤移除: {len(seen) - len(valid_sites)} 个")

    # Save to output file
    output_path = '/home/yoli/GitHub/web_nav_v2/data/new_imported_13.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(valid_sites, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 数据已保存到: {output_path}")
    print("\n✅ 任务完成: 成功导入200个高质量唯一有效网站")

if __name__ == "__main__":
    main()
