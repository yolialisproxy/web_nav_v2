#!/usr/bin/env python3
# Data cleanup - remove placeholder categories and merge small categories
import json, re
from collections import defaultdict

INPUT = 'data/websites.json'
OUTPUT = 'data/websites_cleaned.json'
REPORT = 'data/cleanup_report.json'

PLACEHOLDER_PATTERNS = [
    r'^.*\u5b50\u7c7b-\d+$',
    r'^.*\u5176\u4ed6$',
    r'^.*\u672a\u5206\u7c7b$',
    r'^.*\u5f85\u5b9a$',
    r'^.*\u6682\u5b58$',
    r'(?i)^.*misc.*$',
    r'(?i)^.*others?$',
]

MIN_SITES_TO_KEEP = 3

def load_data():
    with open(INPUT, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_placeholder(cat_path):
    last = cat_path.split('/')[-1]
    for pat in PLACEHOLDER_PATTERNS:
        if re.match(pat, last):
            return True
    return False

def analyze(sites):
    cats = defaultdict(list)
    for s in sites:
        cats[s.get('category', '')].append(s)

    placeholders = {}
    small_cats = {}
    large_cats = {}

    for cat, items in cats.items():
        if is_placeholder(cat):
            placeholders[cat] = {'count': len(items), 'samples': [s['name'] for s in items[:3]]}
        elif len(items) <= MIN_SITES_TO_KEEP:
            parts = cat.split('/')
            parent = '/'.join(parts[:-1]) if len(parts) >= 2 else cat
            small_cats[cat] = {'count': len(items), 'parent': parent}
        elif len(items) > 50:
            large_cats[cat] = len(items)

    return {
        'total_sites': len(sites),
        'total_categories': len(cats),
        'placeholder_categories': placeholders,
        'placeholder_count': len(placeholders),
        'small_categories': small_cats,
        'small_count': len(small_cats),
        'large_categories': large_cats,
        'large_count': len(large_cats),
    }

def clean_data(sites):
    # Build maps
    placeholder_map = {}
    cat_counts = defaultdict(int)
    for s in sites:
        cat = s.get('category', '')
        cat_counts[cat] += 1
        if is_placeholder(cat):
            parts = cat.split('/')
            parent = '/'.join(parts[:-1]) if len(parts) >= 2 else cat
            placeholder_map[cat] = parent

    small_cat_map = {}
    for cat, count in cat_counts.items():
        if count <= MIN_SITES_TO_KEEP and cat not in placeholder_map:
            parts = cat.split('/')
            parent = '/'.join(parts[:-1]) if len(parts) >= 2 else cat
            small_cat_map[cat] = parent

    cleaned = []
    changes = []
    for s in sites:
        cat = s.get('category', '')
        site = dict(s)
        if cat in placeholder_map:
            changes.append({'name': site.get('name', ''), 'from': cat, 'to': placeholder_map[cat], 'action': 'promoted'})
            site['category'] = placeholder_map[cat]
        elif cat in small_cat_map:
            changes.append({'name': site.get('name', ''), 'from': cat, 'to': small_cat_map[cat], 'action': 'merged'})
            site['category'] = small_cat_map[cat]
        cleaned.append(site)

    return cleaned, changes

if __name__ == '__main__':
    sites = load_data()
    print(f'Original: {len(sites)} sites')

    report = analyze(sites)
    print(f"Categories: {report['total_categories']}, Placeholders: {report['placeholder_count']}, Small: {report['small_count']}, Large(>50): {report['large_count']}")

    cleaned, changes = clean_data(sites)
    post = analyze(cleaned)

    print(f"Cleaned: {len(cleaned)} sites, {len(changes)} changes")
    print(f"Categories after: {post['total_categories']}, Placeholders after: {post['placeholder_count']}")

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    summary = {
        'original_sites': len(sites),
        'cleaned_sites': len(cleaned),
        'original_categories': report['total_categories'],
        'cleaned_categories': post['total_categories'],
        'changes_made': len(changes),
        'placeholder_cats_removed': report['placeholder_count'] - post['placeholder_count'],
        'changes_sample': changes[:50],
    }
    with open(REPORT, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f'Output: {OUTPUT}, Report: {REPORT}')