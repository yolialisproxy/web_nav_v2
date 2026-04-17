import json
import os
from hermes_tools import web_search, web_extract

def enrich_website_data(input_path, output_path):
    with open(input_path, 'r') as f:
        data = json.load(f)

    for category, subcats in data.items():
        for subcat in subcats.get('subcategories', []):
            for minor_cat in subcat.get('minor_categories', []):
                for site in minor_cat.get('sites', []):
                    if not site.get('title') or not site.get('description'):
                        query = site.get('url')
                        search_results = web_search(query=query, limit=1)
                        if search_results and search_results['data']['web']:
                            title = search_results['data']['web'][0].get('title', '')
                            description = search_results['data']['web'][0].get('description', '')
                            site['title'] = title
                            site['description'] = description
                        else:
                            try:
                                extract_result = web_extract(urls=[site['url']])
                                if extract_result and extract_result['results']:
                                    content = extract_result['results'][0].get('content', '')
                                    site['title'] = site['title'] or '未命名'
                                    site['description'] = site['description'] or content[:200] if content else '无描述'
                            except Exception as e:
                                site['title'] = site['title'] or '未命名'
                                site['description'] = site['description'] or '无法获取描述'
                    if 'id' not in site:
                        site['id'] = site['url'].replace('https://', '').replace('http://', '').replace('/', '_')

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Enrich website data with titles and descriptions')
    parser.add_argument('--input', required=True, help='Input JSON file path')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    args = parser.parse_args()
    enrich_website_data(args.input, args.output)