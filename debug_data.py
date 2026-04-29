#!/usr/bin/env python3
import json

DATA_FILE = "/home/yoli/GitHub/web_nav_v2/data/websites.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Top-level type: {type(data).__name__}")
if isinstance(data, dict):
    print(f"Keys: {list(data.keys())}")
    # Try different possible structures
    if 'categories' in data:
        cats = data['categories']
        print(f"categories count: {len(cats)}")
        total = sum(len(c.get('sites', [])) for c in cats if isinstance(c, dict))
        print(f"sites in categories: {total}")
    if 'sites' in data:
        print(f"direct sites: {len(data['sites'])}")
elif isinstance(data, list):
    print(f"List length: {len(data)}")
    # Check if items are sites or categories
    if data and isinstance(data[0], dict):
        if 'url' in data[0]:
            print("List contains direct site objects")
        elif 'sites' in data[0] or 'subcategories' in data[0]:
            print("List contains category objects")
            total = 0
            for cat in data:
                if 'sites' in cat:
                    total += len(cat['sites'])
                if 'subcategories' in cat:
                    for sub in cat['subcategories']:
                        if 'sites' in sub:
                            total += len(sub['sites'])
            print(f"Total sites from categories: {total}")
