#!/usr/bin/env python3
import json, os

files = [
    "/home/yoli/GitHub/web_nav_v2/.backup/websites.json.20260425_203646",
    "/home/yoli/GitHub/web_nav_v2/.backup/websites.json.20260425_223255",
    "/home/yoli/GitHub/web_nav_v2/backup/websites_20260425_173005.json",
]

for f in files:
    if not os.path.exists(f):
        print(f"NOT FOUND: {f}")
        continue
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    if isinstance(data, dict) and 'websites' in data:
        count = len(data['websites'])
        print(f"{count:4d}  {os.path.basename(f)}  (dict.websites)")
    elif isinstance(data, list):
        print(f"{len(data):4d}  {os.path.basename(f)}  (list)")
    else:
        print(f"  ?    {os.path.basename(f)}  type={type(data).__name__}")
