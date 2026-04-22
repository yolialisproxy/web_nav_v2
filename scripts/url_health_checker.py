#!/usr/bin/env python3
import json
import requests
import time
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_url(url):
    try:
        # Disable SSL verification for old/self-signed certs
        response = requests.head(url, timeout=5, allow_redirects=True, verify=False)
        return url, response.status_code, True
    except Exception as e:
        return url, str(type(e).__name__), False

def main():
    stats = {"success": 0, "failed": 0, "failed_urls": []}
    print("🔍 URL Health Checker starting...")

    with open("data/websites.json", "r", encoding="utf-8") as f:
        sites = json.load(f)

    print(f"Total sites to check: {len(sites)}")

    results = []
    failed = 0
    success = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for site in sites:
            if isinstance(site, dict) and "url" in site:
                futures.append(executor.submit(check_url, site["url"]))
            elif isinstance(site, str):
                # Handle string-only entries (raw URLs)
                futures.append(executor.submit(check_url, site))
        for future in as_completed(futures):
            url, status, ok = future.result()
            if ok:
                success +=1
            else:
                failed +=1
                results.append({"url": url, "error": status})

    print(f"\n✅ Check completed:")
    print(f"   Success: {success}")
    print(f"   Failed:  {failed}")
    print(f"   Success rate: {success/(success+failed)*100:.1f}%")

    if failed > 0:
        print("\n❌ Failed URLs:")
        for item in results[:20]:
            print(f"   {item['url']} -> {item['error']}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # Machine readable JSON output
        results = main()
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        main()
