#!/usr/bin/env python3
import json
import os
import glob

backup_dir = "/home/yoli/GitHub/web_nav_v2/backup"
backup_files = glob.glob(os.path.join(backup_dir, "*.json"))

def count_sites(data):
    sites = []
    if isinstance(data, list):
        return len(data)
    elif isinstance(data, dict):
        def traverse(node):
            if isinstance(node, dict):
                if 'sites' in node and isinstance(node['sites'], list):
                    sites.extend(node['sites'])
                for key in ['subcategories', 'minor_categories', 'categories']:
                    if key in node:
                        for child in node[key]:
                            traverse(child)
        traverse(data)
    return len(sites)

for f in sorted(backup_files):
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
        count = count_sites(data)
        print(f"{count:4d}  {os.path.basename(f)}")
    except Exception as e:
        print(f"  ERR {os.path.basename(f)}: {e}")
