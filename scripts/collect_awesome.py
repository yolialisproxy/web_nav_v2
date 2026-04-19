#!/usr/bin/env python3
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from safe_json_io import safe_read_json, safe_write_json

import os
import sys
import requests
import re
from urllib.parse import urlparse

def web_extract(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        return r.text
    except:
        return ""

AWESOME_LISTS = [
    "https://github.com/awesome-selfhosted/awesome-selfhosted",
    "https://github.com/trimstray/the-book-of-secret-knowledge",
    "https://github.com/sindresorhus/awesome",
    "https://github.com/rstacruz/cheatsheets",
    "https://github.com/jwasham/coding-interview-university",
    "https://github.com/joahking/awesome-ai-tools",
    "https://github.com/awesome-foss/awesome-sysadmin",
    "https://github.com/igorbarinov/awesome-data-engineering",
    "https://github.com/ChristosChristofidis/awesome-deep-learning",
    "https://github.com/aymericdamien/TensorFlow-Examples"
]

def main():
    print("🚀 Starting Awesome Lists collection...")
    buffer_path = "/home/yoli/GitHub/web_nav_v2/data/collected_buffer.json"

    if os.path.exists(buffer_path):
        try:
            with open(buffer_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "sites" in data:
                    buffer = data["sites"]
                elif isinstance(data, list):
                    buffer = data
                else:
                    buffer = []
        except Exception as e:
            print(f"Error loading buffer: {e}")
            buffer = []
    else:
        buffer = []

    for url in AWESOME_LISTS:
        print(f"Processing: {url}")
        try:
            content = web_extract(url)
            if content:
                print(f"Extracted {len(content)} chars")
                # Correctly identify links in the page
                links = re.findall(r'https?://[^\s\)\"\'\>\,]+', content)
                print(f"Found {len(links)} links")

                existing_urls = set()
                for item in buffer:
                    if isinstance(item, dict) and 'url' in item:
                        existing_urls.add(item['url'])

                count_added = 0
                for link in links:
                    # CORRECTED: Use the actual less-than operator '<<'' instead of bit-shift '<<<''
                    if len(link) < 200 and urlparse(link).netloc not in ["github.com", "gist.github.com"]:
                        if link not in existing_urls:
                            buffer.append({"url": link, "title": "", "description": "", "source": "awesome"})
                            existing_urls.add(link)
                            count_added += 1
                print(f"Added {count_added} new links from {url}")
        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue

    final_data = {
        "collected_at": "2026-04-16T19:00:00",
        "source": "awesome_lists",
        "count": len(buffer),
        "sites": buffer
    }

    with open(buffer_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Done. Buffer now has {len(buffer)} entries")

if __name__ == "__main__":
    main()
