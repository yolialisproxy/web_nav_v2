import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from safe_json_io import safe_read_json, safe_write_json

import os
import requests
from urllib.parse import urlparse

def enrich_website_data(input_path, output_path):
    with open(input_path, 'r') as f:
        data = json.load(f)

    processed = 0
    failed = 0

    # Support both list format and dict format
    if isinstance(data, list):
        sites = data
        output_data = {"sites": data, "processed_at": None, "processed_count": 0, "failed_count": 0}
    else:
        sites = data.get('sites', [])
        output_data = data

    for site in sites:
        if not site.get('title') or not site.get('description'):
            try:
                parsed = urlparse(site['url'])
                domain = parsed.netloc
                site['title'] = domain
                site['description'] = f"Website at {site['url']}"
                site['id'] = domain.replace('.', '_')
                processed += 1
            except Exception as e:
                failed += 1
                site['title'] = '未命名站点'
                site['description'] = '无法获取站点信息'

        if 'id' not in site:
            site['id'] = site['url'].replace('https://', '').replace('http://', '').replace('/', '_')

    output_data['processed_at'] = '2026-04-21'
    output_data['processed_count'] = processed
    output_data['failed_count'] = failed

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Processed: {processed}, Failed: {failed}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Enrich website data with titles and descriptions')
    parser.add_argument('--input', required=True, help='Input JSON file path')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    args = parser.parse_args()
    enrich_website_data(args.input, args.output)