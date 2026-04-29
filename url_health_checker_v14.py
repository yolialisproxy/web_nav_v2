#!/usr/bin/env python3
import json
import time
import sys
import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Any

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DATA_FILE = "/home/yoli/GitHub/web_nav_v2/data/websites.json"
OUTPUT_FILE = "/home/yoli/GitHub/web_nav_v2/data/url_health_report_V14.json"

# Configurable parameters
CONCURRENT_WORKERS = 20
TIMEOUT = 10
MAX_SITES = 0  # 0 = all sites, otherwise limit to this many
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


def check_url(site: Dict[str, Any]) -> Dict[str, Any]:
    """Check a single URL and return result dict."""
    url = site.get('url', '')
    site_id = site.get('id') or site.get('name', '')
    title = site.get('title', '')

    if not url:
        return {
            "id": site_id,
            "url": url,
            "title": title,
            "status_code": None,
            "ok": False,
            "error": "MISSING_URL"
        }

    try:
        response = requests.head(
            url,
            timeout=TIMEOUT,
            allow_redirects=True,
            verify=False,
            headers={'User-Agent': USER_AGENT}
        )
        status = response.status_code
        is_ok = 200 <= status < 400
        return {
            "id": site_id,
            "url": url,
            "title": title,
            "status_code": status,
            "ok": is_ok,
            "error": None if is_ok else f"HTTP_{status}"
        }
    except requests.exceptions.SSLError as e:
        return {
            "id": site_id,
            "url": url,
            "title": title,
            "status_code": None,
            "ok": False,
            "error": "SSL_ERROR"
        }
    except requests.exceptions.Timeout:
        return {
            "id": site_id,
            "url": url,
            "title": title,
            "status_code": None,
            "ok": False,
            "error": "TIMEOUT"
        }
    except requests.exceptions.ConnectionError:
        return {
            "id": site_id,
            "url": url,
            "title": title,
            "status_code": None,
            "ok": False,
            "error": "CONNECTION_ERROR"
        }
    except Exception as e:
        return {
            "id": site_id,
            "url": url,
            "title": title,
            "status_code": None,
            "ok": False,
            "error": str(type(e).__name__)
        }


def load_sites() -> List[Dict[str, Any]]:
    """Load sites from websites.json."""
    print(f"[{datetime.now()}] 正在加载网站列表...")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle both array format and nested category format
    sites = []

    if isinstance(data, list):
        # Simple array of site objects
        sites = data
    else:
        # Nested category structure: traverse recursively
        def traverse(node):
            if 'sites' in node and isinstance(node['sites'], list):
                sites.extend(node['sites'])
            if 'subcategories' in node:
                for child in node['subcategories']:
                    traverse(child)
            if 'minor_categories' in node:
                for child in node['minor_categories']:
                    traverse(child)

        traverse(data)

    # Filter out entries without URL
    sites = [s for s in sites if s.get('url')]

    # Optional limit
    if MAX_SITES > 0 and len(sites) > MAX_SITES:
        sites = sites[:MAX_SITES]

    print(f"[{datetime.now()}] 加载完成，共 {len(sites)} 个站点")
    return sites


def main():
    start_time = time.time()
    print(f"[{datetime.now()}] ============ URL健康检查 V14 开始 ============")

    sites = load_sites()
    total_count = len(sites)

    if total_count == 0:
        print("错误: 未找到任何站点数据")
        return

    print(f"[{datetime.now()}] 开始批量检测 (并发数: {CONCURRENT_WORKERS})...")

    results = []
    failed = 0
    success = 0

    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        futures = {executor.submit(check_url, site): site for site in sites}
        processed = 0

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

            if result['ok']:
                success += 1
            else:
                failed += 1

            processed += 1
            if processed % 100 == 0:
                print(f"  进度: {processed}/{total_count} ({processed/total_count*100:.1f}%)")

    # Build report
    health_rate = (success / total_count * 100) if total_count > 0 else 0

    print(f"\n{'='*60}")
    print(f"检查完成时间: {datetime.now()}")
    print(f"总检测数: {total_count}")
    print(f"健康站点数: {success}")
    print(f"失效站点: {failed}")
    print(f"健康率: {health_rate:.2f}%")
    print(f"耗时: {time.time() - start_time:.2f}秒")
    print(f"{'='*60}")

    # Print failed details (first 20)
    if failed > 0:
        print("\n失效链接详情 (前20个):")
        failed_items = [r for r in results if not r['ok']]
        for item in failed_items[:20]:
            code = item['status_code'] if item['status_code'] else 'ERR'
            title_short = (item['title'][:50] if item['title'] else 'No title')
            print(f"  [{code}] {item['url']} | {title_short}")
        if len(failed_items) > 20:
            print(f"  ... 还有 {len(failed_items) - 20} 个失效链接")

    # Create output report in required format
    report = {
        "健康站点数": success,
        "总检测数": total_count,
        "健康率": round(health_rate, 2),
        "详细列表": results
    }

    # Save to file
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n完整报告已写入: {OUTPUT_FILE}")


if __name__ == "__main__":
    import os
    main()
