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
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    processed = 0
    failed = 0
    total_missing = 0

    # 遍历分类结构
    for cat in data.values():
        for sub in cat['subcategories']:
            for minor in sub['minor_categories']:
                for site in minor['sites']:
                    if not site.get('title') or not site.get('description'):
                        total_missing += 1

                        title, desc = fetch_site_info(site['url'])

                        if title:
                            site['title'] = title[:60]
                        if desc:
                            site['description'] = desc[:150]

                        if title or desc:
                            processed += 1
                        else:
                            # 降级方案：使用域名
                            parsed = urlparse(site['url'])
                            domain = parsed.netloc
                            site['title'] = domain
                            site['description'] = f"专业网站：{domain}"
                            failed += 1

                        # 自动生成唯一ID
                        if 'id' not in site:
                            parsed = urlparse(site['url'])
                            domain = parsed.netloc
                            site['id'] = re.sub(r'[^a-zA-Z0-9]', '_', domain)

                        # 限流防止被封
                        time.sleep(0.2)

    print(f"\n📊 处理完成报告:")
    print(f"   需要处理站点: {total_missing}")
    print(f"   ✅ 成功抓取: {processed}")
    print(f"   ❌ 抓取失败: {failed}")
    print(f"   成功率: {processed/total_missing*100:.1f}%\n")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='WebNav 站点内容自动补全工具')
    parser.add_argument('--input', required=True, help='输入 JSON 文件路径')
    parser.add_argument('--output', required=True, help='输出 JSON 文件路径')
    args = parser.parse_args()

    print("🚀 启动 enrich_site_descriptions 任务...")
    enrich_website_data(args.input, args.output)