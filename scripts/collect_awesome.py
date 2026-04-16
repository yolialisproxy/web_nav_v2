#!/usr/bin/env python3
import json
import os
from web_extract import web_extract

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
        with open(buffer_path, "r", encoding="utf-8") as f:
            buffer = json.load(f)
    else:
        buffer = []

    for url in AWESOME_LISTS:
        print(f"Processing: {url}")
        try:
            res = web_extract(urls=[url])
            if res and 'results' in res and len(res['results'])>0:
                content = res['results'][0]['content']
                print(f"Extracted {len(content)} chars")
                # Simple link extraction
                import re
                links = re.findall(r'https?://[^\s\)\]]+', content)
                print(f"Found {len(links)} links")
                for link in links:
                    if link not in [x['url'] for x in buffer]:
                        buffer.append({"url": link, "title": "", "description": "", "source": "awesome"})
        except Exception as e:
            print(f"Error: {e}")
            continue

    with open(buffer_path, "w", encoding="utf-8") as f:
        json.dump(buffer, f, indent=2, ensure_ascii=False)

    print(f"✅ Done. Buffer now has {len(buffer)} entries")

if __name__ == "__main__":
    main()
