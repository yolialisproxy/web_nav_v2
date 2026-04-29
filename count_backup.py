#!/usr/bin/env python3
import json

BACKUP_FILE = "/home/yoli/GitHub/web_nav_v2/.backup/websites.json.20260425_223255"

with open(BACKUP_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Top-level type: {type(data).__name__}")

def count_sites(node):
    total = 0
    if isinstance(node, dict):
        if 'sites' in node and isinstance(node['sites'], list):
            total += len(node['sites'])
        for key in ['subcategories', 'minor_categories', 'categories', 'children']:
            if key in node and isinstance(node[key], list):
                for child in node[key]:
                    total += count_sites(child)
    elif isinstance(node, list) and node and isinstance(node[0], dict):
        # list of categories
        for item in node:
            total += count_sites(item)
    return total

total_sites = count_sites(data)
print(f"Total sites: {total_sites}")
