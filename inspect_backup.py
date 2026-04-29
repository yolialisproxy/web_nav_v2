#!/usr/bin/env python3
import json

BACKUP_FILE = "/home/yoli/GitHub/web_nav_v2/.backup/websites.json.20260425_223255"

with open(BACKUP_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Type: {type(data).__name__}")
if isinstance(data, dict):
    print(f"Keys: {list(data.keys())}")
    # Print a sample of each key
    for k, v in data.items():
        t = type(v).__name__
        if isinstance(v, list):
            print(f"  {k}: list[{len(v)}]")
            if v and isinstance(v[0], dict):
                print(f"    sample keys: {list(v[0].keys())}")
        elif isinstance(v, dict):
            print(f"  {k}: dict with keys: {list(v.keys())[:5]}")
        else:
            print(f"  {k}: {t}")
elif isinstance(data, list):
    print(f"List length: {len(data)}")
    if data:
        print(f"First item type: {type(data[0]).__name__}")
        if isinstance(data[0], dict):
            print(f"First item keys: {list(data[0].keys())}")
