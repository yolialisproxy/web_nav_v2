#!/usr/bin/env python3
"""
Phase 1: AI Category Purge - Remove obvious non-AI junk
Based on keyword pattern matching on URLs and names.

This removes ~123 sites from AI工具/人工智能 category.
After this, AI category will drop from 329 → ~206 sites.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/home/yoli/GitHub/web_nav_v2")
WEBSITES_PATH = PROJECT_ROOT / "data" / "websites.json"
BACKUP_DIR = PROJECT_ROOT / "backups"
REPORTS_DIR = PROJECT_ROOT / "reports"

def load_websites():
    with open(WEBSITES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_websites(data):
    with open(WEBSITES_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_backup():
    """Create timestamped backup before modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"websites.json.v15_ai_purge_pre_{timestamp}"
    backup_path = BACKUP_DIR / backup_name
    import shutil
    shutil.copy2(WEBSITES_PATH, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

# Clear non-AI indicators (URL patterns that prove NOT an AI tool)
PURGE_PATTERNS = [
    r'youtube\.com/watch', r'youtu\.be', r'youtube-nocookie',
    r'wikipedia\.org', r'wikimedia\.org',
    r'archive\.org', r'web\.archive\.org',
    r'github\.com/_private', r'raw\.githubusercontent\.com',
    r'\.svg$', r'\.png$', r'\.jpg$', r'\.gif$', r'\.ico$',
    r'fork-button', r'button[?]', r'assets/thanks',
    r'mit\.edu/course', r'stanford\.edu/class', r'berkeley\.edu',
    r'coursera\.org/learn', r'edx\.org/course',
    r'arxiv\.org/abs', r'arxiv\.org/pdf',
    r'researchgate\.net',
    r'cdn\.', r'assets/', r'static/', r'img/', r'images/',
    r'favicon\.ico', r'robots\.txt', r'sitemap\.xml',
]

def is_junk_site(url, name):
    """Returns True if site URL/name matches obvious non-AI junk patterns"""
    combined = f"{url} {name}".lower()
    for pattern in PURGE_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            return True, pattern
    return False, None

def main():
    print("=== Phase 1: AI Category Purge ===\n")

    websites = load_websites()
    original_count = len(websites)
    print(f"Original websites.json: {original_count} sites")

    # Filter AI master category sites
    ai_sites = [s for s in websites if s.get('category') == 'AI工具/人工智能']
    non_ai_sites = [s for s in websites if s.get('category') != 'AI工具/人工智能']

    print(f"AI master category sites: {len(ai_sites)}")
    print(f"Non-AI sites: {len(non_ai_sites)}")

    # Classify AI sites
    to_purge = []
    to_keep = []

    for site in ai_sites:
        url = site.get('url', '')
        name = site.get('name', '')
        is_junk, pattern = is_junk_site(url, name)
        if is_junk:
            to_purge.append({**site, 'purge_reason': f"Pattern: {pattern}"})
        else:
            to_keep.append(site)

    print(f"\nPurge candidates: {len(to_purge)} sites")
    print(f"Keep candidates: {len(to_keep)} sites")

    # Show purge samples
    print(f"\nSample sites to PURGE:")
    for s in to_purge[:10]:
        print(f"  {s.get('name','')[:50]:50s} | {s.get('url','')[:50]}")
        print(f"    Reason: {s.get('purge_reason','')}")

    # Ask for confirmation (dry-run vs actual)
    dry_run = '--dry-run' in sys.argv
    if dry_run:
        print(f"\n🔍 DRY RUN MODE - No changes will be written")
        print(f"Would purge: {len(to_purge)} sites from AI category")
        print(f"Would keep: {len(to_keep)} sites in AI category")
        print(f"AI category reduction: {len(ai_sites)} → {len(to_keep)} ({100*len(to_keep)/len(ai_sites):.1f}%)")
    else:
        print(f"\n⚠️  ABOUT TO MODIFY data/websites.json")
        print(f"This will REMOVE {len(to_purge)} sites permanently.")
        print(f"AI category: {len(ai_sites)} → {len(to_keep)} sites")
        response = input("Type 'YES PURGE' to confirm: ").strip()
        if response != 'YES PURGE':
            print("Aborted.")
            return

        # Create backup
        create_backup()

        # Rebuild websites list (non_ai + keep)
        new_websites = non_ai_sites + to_keep
        save_websites(new_websites)

        print(f"\n✅ Purge complete!")
        print(f"   Total sites: {original_count} → {len(new_websites)}")
        print(f"   Removed: {len(to_purge)} junk AI sites")

    # Save report
    report = {
        'operation': 'ai_category_purge_phase1',
        'timestamp': datetime.now().isoformat(),
        'dry_run': dry_run,
        'original_ai_count': len(ai_sites),
        'purged_count': len(to_purge),
        'kept_count': len(to_keep),
        'purged_sites': [{'url': s['url'], 'name': s.get('name',''), 'reason': s.get('purge_reason','')} for s in to_purge],
        'kept_sites': [{'url': s['url'], 'name': s.get('name','')} for s in to_keep]
    }

    report_path = REPORTS_DIR / "v15_ai_purge_phase1_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Report saved: {report_path}")

if __name__ == '__main__':
    main()
