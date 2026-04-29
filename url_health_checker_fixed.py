#!/usr/bin/env python3
import json
import requests
import time
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_session():
    session = requests.Session()
    retry = Retry(
        total=2,
        read=2,
        connect=2,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.verify = False  # Disable SSL verification
    return session

def check_url(url, session):
    try:
        response = session.head(url, timeout=10, allow_redirects=True)
        return url, response.status_code, True
    except Exception as e:
        return url, str(type(e).__name__), False

def main():
    data_path = 'data/websites.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # The JSON has a key "websites"
    sites = data.get('websites', [])
    print(f"Total sites to check: {len(sites)}")

    # We'll check all sites, but we can break if needed.
    # Let's use a session per thread for efficiency.
    def worker(site):
        url = site.get('url')
        if not url:
            return None
        session = create_session()
        return check_url(url, session)

    success = 0
    failed = 0
    failed_urls = []

    # We'll use ThreadPoolExecutor with a reasonable number of workers.
    # Too many workers might cause network issues, too few will be slow.
    # Let's try 20 workers.
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(worker, site): site for site in sites if site.get('url')}
        for future in as_completed(futures):
            site = futures[future]
            try:
                result = future.result(timeout=30)  # Timeout for each future
                if result is None:
                    # Skip sites without URL
                    continue
                url_result, status, ok = result
                if ok:
                    success += 1
                else:
                    failed += 1
                    failed_urls.append((url_result, status))
            except Exception as e:
                failed += 1
                failed_urls.append((site.get('url', 'unknown'), str(e)))

    total = success + failed
    print(f"\n✅ Check completed:")
    print(f"   Success: {success}")
    print(f"   Failed:  {failed}")
    if total > 0:
        print(f"   Success rate: {success/total*100:.1f}%")
    else:
        print("   Success rate: 0%")

    if failed > 0:
        print("\n❌ Failed URLs (first 10):")
        for url, error in failed_urls[:10]:
            print(f"   {url} -> {error}")

    # Save report
    report = {
        "generated_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
        "total": total,
        "success": success,
        "failed_count": failed,
        "success_rate": success/total*100 if total > 0 else 0,
        "failed_urls": [{"url": u, "error": e} for u, e in failed_urls]
    }
    report_path = 'url_health_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nReport saved to {report_path}")

if __name__ == "__main__":
    main()
