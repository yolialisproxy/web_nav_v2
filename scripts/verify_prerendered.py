#!/usr/bin/env python3
"""
Pre-rendered pages completeness verification (corrected).
Compares expected category filenames (derived from websites.json)
against actual files in prerendered/.

Expected filename = category_name.replace('/', '_').replace(' ', '_')[:60]

Usage:
    python3 scripts/verify_prerendered.py          # list diffs, exit 0
    python3 scripts/verify_prerendered.py --strict  # exit 1 if any gap
"""

import json
import sys
from pathlib import Path

def slugify(cat: str) -> str:
    """Match prerender_seo.py safe_name logic exactly."""
    return cat.replace('/', '_').replace(' ', '_')[:60]

def load_expected(data_path: str = "data/websites.json") -> set:
    """Return set of expected pre-rendered filenames (without .html)."""
    with open(data_path, 'r', encoding='utf-8') as f:
        sites = json.load(f)
    categories = {site.get('category', '未分类').strip() for site in sites}
    return {slugify(c) for c in categories}

def scan_actual(prerendered_dir: str = "prerendered") -> set:
    """Return set of existing pre-rendered filenames (stem only)."""
    p = Path(prerendered_dir)
    if not p.exists():
        return set()
    return {f.stem for f in p.glob("*.html")}

def main():
    strict = '--strict' in sys.argv
    expected = load_expected()
    actual   = scan_actual()

    missing = sorted(expected - actual)
    extras  = sorted(actual - expected)
    covered = len(expected) - len(missing)

    if missing or extras:
        print(f"Coverage: {covered}/{len(expected)}")
        if missing:
            print(f"❌ Missing ({len(missing)}): {missing}")
        if extras:
            print(f"⚠️  Stale (not in data) ({len(extras)}): {extras}")
        if strict:
            sys.exit(1)
        else:
            print("(run with --strict to fail)")
    else:
        print(f"✅ All {len(expected)} category pages present")

if __name__ == '__main__':
    main()
