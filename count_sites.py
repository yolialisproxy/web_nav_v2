#!/usr/bin/env python3
import json

DATA_FILE = "/home/yoli/GitHub/web_nav_v2/data/websites.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract all sites from category hierarchy
sites = []

def traverse(node):
    if isinstance(node, dict):
        if 'sites' in node and isinstance(node['sites'], list):
            sites.extend(node['sites'])
        if 'subcategories' in node:
            for child in node['subcategories']:
                traverse(child)
        if 'minor_categories' in node:
            for child in node['minor_categories']:
                traverse(child)
    elif isinstance(node, list):
        # New format: direct array
        sites.extend(node)

if isinstance(data, list):
    sites = data
else:
    traverse(data)

print(f"Total sites: {len(sites)}")
print(f"First site: {sites[0] if sites else 'None'}")
