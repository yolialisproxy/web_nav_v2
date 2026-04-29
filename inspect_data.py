#!/usr/bin/env python3
import json

DATA_FILE = "/home/yoli/GitHub/web_nav_v2/data/websites.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Data type: {type(data).__name__}")

total = 0

def traverse(node, depth=0):
    global total
    indent = "  " * depth
    if isinstance(node, dict):
        if 'sites' in node:
            sites = node['sites']
            print(f"{indent}sites: {len(sites)}")
            total += len(sites)
        for key in ['subcategories', 'minor_categories', 'categories']:
            if key in node:
                print(f"{indent}{key}: {len(node[key])}")
                for child in node[key]:
                    traverse(child, depth+1)
    elif isinstance(node, list):
        # Direct array
        print(f"{indent}direct list: {len(node)} items")
        total += len(node)

if isinstance(data, list):
    print(f"Direct array with {len(data)} sites")
    print(f"Sample: {data[0]}")
else:
    print(f"Dict with keys: {list(data.keys())}")
    traverse(data)
    print(f"\nTotal sites from traversal: {total}")
