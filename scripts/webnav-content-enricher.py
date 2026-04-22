import json
import os
import sys
import time
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from safe_json_io import safe_read_json, safe_write_json

# 中文标题与描述规范：
# 1. 标题：2-12字，准确描述网站核心功能，禁止纯域名
# 2. 描述：15-50字，专业简洁，说明用途、特性、适用场景
# 3. 去除广告、无关后缀，保留真实业务描述

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}

session = requests.Session()
session.timeout = 8

def clean_text(text):
    if not text: return ''
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[|»•·\-].*$', '', text)
    return text.strip()

def fetch_site_info(url):
    try:
        r = session.get(url, headers=HEADERS, allow_redirects=True, timeout=8)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')

        # 获取标题
        title = ''
        if soup.title and soup.title.string:
            title = clean_text(soup.title.string)

        # 获取meta描述
        desc = ''
        meta_desc = soup.find('meta', attrs={'name': ['description', 'og:description']})
        if meta_desc and meta_desc.get('content'):
            desc = clean_text(meta_desc.get('content'))

        return title, desc
    except Exception as e:
        return None, None

def enrich_website_data(input_path, output_path):
    data = safe_read_json(input_path)

    if data is None:
        print(f"❌ 错误: 无法读取输入文件或文件为空")
        return

    processed = 0
    failed = 0
    total_missing = 0

    # 遍历所有分类
    processed_cats = 0
    # ✅ 修复 AttributeError: 现在数据结构是列表不是字典
    # 数据结构: [{'name':'xxx', 'subcategories': [...], 'sites': [...]}, ...]
    for cat_item in data:
        if not isinstance(cat_item, dict):
            continue

        # 处理顶级分类下的站点
        if 'sites' in cat_item and isinstance(cat_item['sites'], list):
            for site in cat_item['sites']:
                if not isinstance(site, dict) or 'url' not in site:
                    continue

                # 处理站点
                total_missing += 1

                current_title = site.get('title', '').strip()
                current_desc = site.get('description', '').strip()
                need_process = True

                if need_process:
                    title, desc = fetch_site_info(site['url'])
                    if title:
                        site['title'] = title[:60]
                    if desc:
                        site['description'] = desc[:150]
                    if title or desc:
                        processed += 1
                    else:
                        failed += 1
                    time.sleep(0.2)

        # 处理子分类
        if 'subcategories' in cat_item and isinstance(cat_item['subcategories'], list):
            for sub_cat in cat_item['subcategories']:
                if not isinstance(sub_cat, dict):
                    continue

                # 处理子分类下的站点
                if 'sites' in sub_cat and isinstance(sub_cat['sites'], list):
                    for site in sub_cat['sites']:
                        if not isinstance(site, dict) or 'url' not in site:
                            continue

                        # 处理站点
                        total_missing += 1

                        current_title = site.get('title', '').strip()
                        current_desc = site.get('description', '').strip()
                        need_process = True

                        if need_process:
                            title, desc = fetch_site_info(site['url'])
                            if title:
                                site['title'] = title[:60]
                            if desc:
                                site['description'] = desc[:150]
                            if title or desc:
                                processed += 1
                            else:
                                failed += 1
                            time.sleep(0.2)

                # 处理小分类
                if 'minor_categories' in sub_cat and isinstance(sub_cat['minor_categories'], list):
                    for minor_cat in sub_cat['minor_categories']:
                        if not isinstance(minor_cat, dict):
                            continue

                        if 'sites' in minor_cat and isinstance(minor_cat['sites'], list):
                            for site in minor_cat['sites']:
                                if not isinstance(site, dict) or 'url' not in site:
                                    continue

                                # 处理站点
                                current_title = site.get('title', '').strip()
                                current_desc = site.get('description', '').strip()

                                # 只处理缺少标题、占位标题或者缺少描述的站点
                                need_process = False
                                # 检测占位文本和空值
                                if not current_title or len(current_title) < 2 or \
                                   current_title in ['', 'Untitled', '首页', 'Welcome', 'Homepage', 'Title'] or \
                                   'placeholder' in current_title.lower() or \
                                   'description will' in current_desc.lower() or \
                                   'baseball-bat-ball' in current_title:
                                    need_process = True

                                if need_process:
                                    total_missing += 1
                                    title, desc = fetch_site_info(site['url'])
                                    if title:
                                        site['title'] = title[:60]
                                    if desc:
                                        site['description'] = desc[:150]
                                    if title or desc:
                                        processed += 1
                                    else:
                                        failed += 1
                                    time.sleep(0.2)

        # 测试只处理前50个站点
        if total_missing >= 50:
            break

    print(f"\n📊 处理完成报告:")
    print(f"   🎯 需要补全的站点: {total_missing}")
    print(f"   ✅ 成功抓取: {processed}")
    print(f"   ❌ 抓取失败: {failed}")
    if total_missing > 0:
        print(f"   成功率: {processed/total_missing*100:.1f}%\n")
    else:
        print(f"   没有需要处理的站点\n")

    safe_write_json(output_path, data)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='WebNav 站点内容自动补全工具')
    parser.add_argument('--input', required=True, help='输入 JSON 文件路径')
    parser.add_argument('--output', required=True, help='输出 JSON 文件路径')
    args = parser.parse_args()

    print("🚀 启动 enrich_site_descriptions 任务...")
    enrich_website_data(args.input, args.output)