import json
import os
import requests
from urllib.parse import urlparse

def enrich_website_data(input_path, output_path):
    with open(input_path, 'r') as f:
        data = json.load(f)

    processed = 0
    failed = 0

    for site in data.get('sites', []):
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

    data['processed_at'] = '2026-04-18'
    data['processed_count'] = processed
    data['failed_count'] = failed

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Processed: {processed}, Failed: {failed}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Enrich website data with titles and descriptions')
    parser.add_argument('--input', required=True, help='Input JSON file path')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    args = parser.parse_args()
    enrich_website_data(args.input, args.output)