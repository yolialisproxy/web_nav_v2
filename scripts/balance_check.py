#!/usr/bin/env python3
"""
Category Balance Analysis and Improvement Plan
Analyzes website category distribution and identifies underfilled categories.
"""

import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path("/home/yoli/GitHub/web_nav_v2")
WEBSITES_PATH = PROJECT_ROOT / "websites.json"
REPORTS_PATH = PROJECT_ROOT / "reports"
REPORTS_PATH.mkdir(exist_ok=True)

# Configuration
MIN_REQUIRED = 9   # Categories with fewer than this are considered underfilled
MAX_ALLOWED = 50  # Categories with more than this are considered overfilled

def load_websites():
    """Load websites.json"""
    with open(WEBSITES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_balance(websites):
    """Analyze category balance"""
    cat_counts = Counter()
    for site in websites:
        cat = site.get('category', 'Uncategorized')
        if cat and cat.strip():
            cat_counts[cat] += 1
        else:
            cat_counts['Uncategorized'] += 1

    total_sites = len(websites)
    total_categories = len(cat_counts)

    underfilled = {}
    overfilled = {}
    balanced = {}

    for cat, count in cat_counts.items():
        if count < MIN_REQUIRED:
            underfilled[cat] = count
        elif count > MAX_ALLOWED:
            overfilled[cat] = count
        else:
            balanced[cat] = count

    return {
        'total_sites': total_sites,
        'total_categories': total_categories,
        'min_required': MIN_REQUIRED,
        'max_allowed': MAX_ALLOWED,
        'category_counts': dict(cat_counts),
        'underfilled': underfilled,
        'overfilled': overfilled,
        'balanced': balanced,
        'stats': {
            'underfilled_count': len(underfilled),
            'overfilled_count': len(overfilled),
            'balanced_count': len(balanced),
            'empty_count': cat_counts.get('Uncategorized', 0) if 'Uncategorized' in cat_counts else 0
        }
    }

def generate_improvement_plan(analysis):
    """Generate actionable improvement plan for underfilled categories"""
    underfilled = analysis['underfilled']
    improvement_plan = {}

    for cat, current_count in sorted(underfilled.items()):
        gap = MIN_REQUIRED - current_count
        # Target: reach MIN_REQUIRED (9 sites)
        improvement_plan[cat] = {
            'current_count': current_count,
            'target_count': MIN_REQUIRED,
            'gap': gap,
            'priority': 'high' if gap >= 5 else 'medium' if gap >= 3 else 'low'
        }

    return improvement_plan

def main():
    print("=== Category Balance Analysis ===\n")

    # Load data
    print("Loading websites.json...")
    websites = load_websites()
    print(f"  Total sites loaded: {len(websites)}")

    # Analyze
    print("\nAnalyzing category distribution...")
    analysis = analyze_balance(websites)

    # Print summary
    print(f"\n📊 Balance Summary:")
    print(f"  Total categories: {analysis['total_categories']}")
    print(f"  Total sites: {analysis['total_sites']}")
    print(f"  Balanced (9-50): {analysis['stats']['balanced_count']}")
    print(f"  Underfilled (<9): {analysis['stats']['underfilled_count']}")
    print(f"  Overfilled (>50): {analysis['stats']['overfilled_count']}")

    # Show top underfilled categories
    print(f"\n🔴 Underfilled Categories (need <{MIN_REQUIRED} sites):")
    sorted_under = sorted(analysis['underfilled'].items(), key=lambda x: x[1])
    for cat, count in sorted_under[:20]:
        gap = MIN_REQUIRED - count
        print(f"  {cat}: {count} sites (need {gap} more)")

    if len(sorted_under) > 20:
        print(f"  ... and {len(sorted_under) - 20} more")

    # Show overfilled categories
    if analysis['overfilled']:
        print(f"\n🟡 Overfilled Categories (>{MAX_ALLOWED} sites):")
        for cat, count in sorted(analysis['overfilled'].items(), key=lambda x: -x[1]):
            print(f"  {cat}: {count} sites (excess: {count - MAX_ALLOWED})")
    else:
        print(f"\n🟢 No overfilled categories (all ≤{MAX_ALLOWED} sites)")

    # Generate improvement plan
    print(f"\n📋 Generating improvement plan...")
    improvement_plan = generate_improvement_plan(analysis)

    # Save reports
    balance_report_path = REPORTS_PATH / "balance_analysis_report.json"
    improvement_plan_path = REPORTS_PATH / "balance_improvement_plan.json"

    # Full analysis report
    with open(balance_report_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    # Improvement plan (only actionable targets)
    with open(improvement_plan_path, 'w', encoding='utf-8') as f:
        json.dump(improvement_plan, f, indent=2, ensure_ascii=False)

    print(f"  Full analysis: {balance_report_path}")
    print(f"  Improvement plan: {improvement_plan_path}")

    # Summary stats
    total_gap = sum(v['gap'] for v in improvement_plan.values())
    print(f"\n✅ Improvement Plan Summary:")
    print(f"  Categories needing sites: {len(improvement_plan)}")
    print(f"  Total sites needed: {total_gap}")
    print(f"  Average gap per category: {total_gap / len(improvement_plan):.1f}" if improvement_plan else "  N/A")

    return improvement_plan

if __name__ == "__main__":
    main()
