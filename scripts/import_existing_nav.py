#!/usr/bin/env python3
"""
Mature Navigation Site Bulk Importer
Extracts high quality curated sites from established public navigation websites
Follows webnav-site-importer skill standards: proper schema, rate limiting, deduplication, error handling
"""
import sys
import os
import json
import time
import re
from urllib.parse import urlparse
from typing import List, Dict, Set, Any
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from safe_json_io import safe_read_json, safe_write_json

# Configuration
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.google.com/"
}

REQUEST_DELAY = 1.5  # seconds between requests
MAX_RETRIES = 3
TIMEOUT = 20

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
EXISTING_WEBSITES = os.path.join(DATA_PATH, "websites.json")
OUTPUT_FILE = os.path.join(DATA_PATH, "imported_nav_sites.json")

# Curated trusted navigation sources
IMPORT_TARGETS = [
    {
        "id": "webstack",
        "name": "WebStack 官方导航",
        "url": "https://webstack.cc/",
        "trust_score": 9,
        "description": "7年运营 5000+人工审核高质量站点"
    },
    {
        "id": "geekape",
        "name": "极客猿导航",
        "url": "https://nav.geekape.com/",
        "trust_score": 8,
        "description": "开发者工具与技术资源导航"
    },
    {
        "id": "ai_bot_cn",
        "name": "AI 工具箱",
        "url": "https://ai-bot.cn/",
        "trust_score": 9,
        "description": "最全中文AI工具导航"
    },
    {
        "id": "uisdc_hao",
        "name": "优设导航",
        "url": "https://hao.uisdc.com/",
        "trust_score": 8,
        "description": "设计师专业资源导航"
    },
    {
        "id": "frontendnav",
        "name": "前端导航",
        "url": "https://frontendnav.com/",
        "trust_score": 8,
        "description": "前端开发资源合集"
    },
    {
        "id": "nav_bigo",
        "name": "程序员导航",
        "url": "https://nav.bigo.sg/",
        "trust_score": 7,
        "description": "后端开发与运维资源"
    }
]


def get_existing_urls() -> Set[str]:
    """Get all existing URLs from current dataset for deduplication"""
    existing = set()
    if os.path.exists(EXISTING_WEBSITES):
        try:
            sites = safe_read_json(EXISTING_WEBSITES, default=[])
            for site in sites:
                if 'url' in site:
                    normalized = normalize_url(site['url'])
                    existing.add(normalized)
            print(f"✅ 加载现有站点: {len(existing)} 个唯一URL")
        except Exception as e:
            print(f"⚠️  读取现有站点失败: {e}")
    return existing


def normalize_url(url: str) -> str:
    """Normalize URL for deduplication comparison"""
    if not url:
        return ""
    parsed = urlparse(url.strip())
    # Remove www prefix, trailing slash, query params
    netloc = parsed.netloc.lower().replace('www.', '')
    path = parsed.path.rstrip('/')
    return f"{netloc}{path}"


def validate_site(site: Dict[str, Any]) -> bool:
    """Validate site meets quality standards"""
    if not site.get('url') or not site.get('title'):
        return False

    url = site['url'].strip()
    if not url.startswith(('http://', 'https://')):
        return False

    # Skip placeholder domains
    blacklist = ['example.com', 'localhost', '127.0.0.1', 'test.com']
    for b in blacklist:
        if b in url:
            return False

    # Skip empty/meaningless titles
    title = site['title'].strip()
    if len(title) < 2 or title == '首页' or title == url:
        return False

    return True


def safe_request(url: str) -> requests.Response | None:
    """Safe request with retries and rate limiting"""
    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(REQUEST_DELAY)
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
            return r
        except Exception as e:
            print(f"⚠️  请求失败 [{attempt+1}/{MAX_RETRIES}]: {e}")
            time.sleep(2 ** attempt)
    return None


def extract_webstack() -> List[Dict]:
    """Extract from WebStack.cc"""
    print("\n🔍 正在提取 WebStack 官方数据...")
    sites = []

    r = safe_request("https://webstack.cc/assets/js/all.js")
    if not r:
        return []

    try:
        match = re.search(r'var all_data = (\[.*?\]);', r.text, re.DOTALL)
        if match:
            raw_data = json.loads(match.group(1))
            for item in raw_data:
                site = {
                    'url': item.get('url', '').strip(),
                    'title': item.get('name', '').strip(),
                    'description': item.get('desc', '').strip(),
                    'category': item.get('category', ''),
                    '_source': 'webstack.cc',
                    '_trust': 9
                }
                if validate_site(site):
                    sites.append(site)

            print(f"✅ WebStack 提取成功: {len(sites)} 个有效站点")
        return sites
    except Exception as e:
        print(f"❌ WebStack 解析失败: {e}")
        return []


def extract_ai_bot_cn() -> List[Dict]:
    """Extract from ai-bot.cn"""
    print("\n🔍 正在提取 AI 工具箱数据...")
    sites = []

    r = safe_request("https://ai-bot.cn/")
    if not r:
        return []

    try:
        soup = BeautifulSoup(r.text, 'html.parser')
        for card in soup.select('.tool-item'):
            url_tag = card.select_one('a')
            if not url_tag:
                continue

            site = {
                'url': url_tag.get('href', '').strip(),
                'title': card.select_one('.tool-name').text.strip() if card.select_one('.tool-name') else '',
                'description': card.select_one('.tool-desc').text.strip() if card.select_one('.tool-desc') else '',
                'category': 'AI工具',
                '_source': 'ai-bot.cn',
                '_trust': 9
            }
            if validate_site(site):
                sites.append(site)

        print(f"✅ AI 工具箱 提取成功: {len(sites)} 个有效站点")
        return sites
    except Exception as e:
        print(f"❌ AI 工具箱解析失败: {e}")
        return []


def extract_geekape() -> List[Dict]:
    """Extract from nav.geekape.com"""
    print("\n🔍 正在提取 极客猿导航 数据...")
    sites = []

    r = safe_request("https://nav.geekape.com/api/site/all")
    if not r:
        return []

    try:
        data = r.json()
        if 'data' in data:
            for item in data['data']:
                site = {
                    'url': item.get('url', '').strip(),
                    'title': item.get('name', '').strip(),
                    'description': item.get('desc', '').strip(),
                    'category': item.get('category_name', ''),
                    '_source': 'nav.geekape.com',
                    '_trust': 8
                }
                if validate_site(site):
                    sites.append(site)

            print(f"✅ 极客猿导航 提取成功: {len(sites)} 个有效站点")
        return sites
    except Exception as e:
        print(f"❌ 极客猿导航解析失败: {e}")
        return []


def main():
    print("🚀 高质量导航站点批量导入工具")
    print("=" * 70)

    existing_urls = get_existing_urls()

    all_extracted = []
    sources_count = {}

    # Run all extractors
    extractors = [
        extract_webstack,
        extract_ai_bot_cn,
        extract_geekape
    ]

    for extractor in extractors:
        try:
            sites = extractor()
            source = sites[0]['_source'] if sites else extractor.__name__
            sources_count[source] = len(sites)
            all_extracted.extend(sites)
        except Exception as e:
            print(f"❌ 提取器执行失败: {extractor.__name__}: {e}")

    # Deduplication
    seen = set()
    unique_sites = []
    duplicate_count = 0

    for site in all_extracted:
        norm_url = normalize_url(site['url'])
        if norm_url in existing_urls or norm_url in seen:
            duplicate_count +=1
            continue
        seen.add(norm_url)
        unique_sites.append(site)

    print("\n" + "="*70)
    print("📊 导入统计:")
    for source, cnt in sources_count.items():
        print(f"   {source}: {cnt}")
    print(f"\n   总共提取: {len(all_extracted)} 个站点")
    print(f"   重复跳过: {duplicate_count} 个站点")
    print(f"   新增有效: {len(unique_sites)} 个站点")

    # Save results
    safe_write_json(OUTPUT_FILE, unique_sites)
    print(f"\n✅ 数据已保存到: {OUTPUT_FILE}")
    print("\n💡 下一步操作:")
    print("   1. 运行 python scripts/distribute_categories.py 自动分类")
    print("   2. 运行 python scripts/bulk_enrich.py 补充元信息")
    print("   3. 运行 python scripts/quality_audit.py 质量审核")


if __name__ == "__main__":
    main()
