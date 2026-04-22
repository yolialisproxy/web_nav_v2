#!/usr/bin/env python3
import json
import os
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = "/home/yoli/GitHub/web_nav_v2"
CATEGORIES_PATH = os.path.join(PROJECT_ROOT, "final_standard_categories.json")
WEBSITES_PATH = os.path.join(PROJECT_ROOT, "data/websites.json")
REPORT_PATH = os.path.join(PROJECT_ROOT, "reports/category_balance_report.json")
REPORT_MD_PATH = os.path.join(PROJECT_ROOT, "reports/category_balance_report.md")

MIN_SITES = 10
MAX_SITES = 50

def main():
    with open(CATEGORIES_PATH, 'r', encoding='utf-8') as f:
        category_tree = json.load(f)

    with open(WEBSITES_PATH, 'r', encoding='utf-8') as f:
        websites_data = json.load(f)
        websites = websites_data.get('sites', [])

    counts = defaultdict(int)
    for site in websites:
        cat = site.get('category', 'Uncategorized')
        counts[cat] += 1

    results = {
        "timestamp": datetime.now().isoformat(),
        "min_required": MIN_SITES,
        "max_allowed": MAX_SITES,
        "summary": {
            "total_leaf_categories": 0,
            "total_sites": len(websites),
            "balanced": 0,
            "underfilled": 0,
            "overfilled": 0,
            "empty": 0,
            "uncategorized": counts.get("Uncategorized", 0)
        },
        "category_details": [],
        "issues": []
    }

    leaf_names = []
    for major in category_tree:
        major_name = major.get("name")
        for mid in major.get("subcategories", []):
            mid_name = mid.get("name")
            for leaf_name in mid.get("children", []):
                leaf_names.append(leaf_name)
                cnt = counts.get(leaf_name, 0)
                results["summary"]["total_leaf_categories"] +=1

                status = "balanced"
                if cnt == 0:
                    status = "empty"
                    results["summary"]["empty"] +=1
                elif cnt < MIN_SITES:
                    status = "underfilled"
                    results["summary"]["underfilled"] +=1
                elif cnt > MAX_SITES:
                    status = "overfilled"
                    results["summary"]["overfilled"] +=1
                else:
                    results["summary"]["balanced"] +=1

                entry = {
                    "major": major_name,
                    "mid": mid_name,
                    "leaf": leaf_name,
                    "count": cnt,
                    "status": status
                }
                results["category_details"].append(entry)

                if status != "balanced":
                    results["issues"].append(entry)

    # Generate markdown report
    md = [
        "# Category Balance Analysis Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"✅ Target rules: **{MIN_SITES} - {MAX_SITES} sites per leaf category**",
        "",
        "## Overall Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total leaf categories | {results['summary']['total_leaf_categories']} |",
        f"| Total indexed websites | {results['summary']['total_sites']} |",
        f"| ✅ Properly balanced | {results['summary']['balanced']} |",
        f"| ⚠️ Underfilled (< {MIN_SITES}) | {results['summary']['underfilled']} |",
        f"| ⛔ Overfilled (> {MAX_SITES}) | {results['summary']['overfilled']} |",
        f"| ❌ Empty (0 sites) | {results['summary']['empty']} |",
        f"| ❓ Uncategorized sites | {results['summary']['uncategorized']} |",
        "",
        "## Issues Requiring Balancing",
        ""
    ]

    if results["issues"]:
        md.append("| Category Path | Site Count | Status | Recommended Action |")
        md.append("|---------------|------------|--------|--------------------|")
        for issue in sorted(results["issues"], key=lambda x: x["count"]):
            path = f"{issue['major']} > {issue['mid']} > {issue['leaf']}"
            if issue["status"] == "empty":
                action = "Fill from pool, minimum 10 sites"
            elif issue["status"] == "underfilled":
                action = f"Add {MIN_SITES - issue['count']} more sites"
            else:
                action = f"Move {issue['count'] - MAX_SITES} sites to other categories or split category"

            md.append(f"| {path} | {issue['count']} | {issue['status']} | {action} |")
    else:
        md.append("✅ Perfect! All categories are within acceptable range.")

    with open(REPORT_MD_PATH, 'w', encoding='utf-8') as f:
        f.write("\n".join(md))

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n✅ Category balance report completed successfully!")
    print(f"   Markdown report: {REPORT_MD_PATH}")
    print(f"   JSON raw data: {REPORT_PATH}")
    print(f"\n📊 Final stats:")
    print(f"   Total categories: {results['summary']['total_leaf_categories']}")
    print(f"   Balanced: {results['summary']['balanced']}")
    print(f"   Underfilled: {results['summary']['underfilled']}")
    print(f"   Overfilled: {results['summary']['overfilled']}")
    print(f"   Empty: {results['summary']['empty']}")
    print(f"   Uncategorized: {results['summary']['uncategorized']}")

if __name__ == "__main__":
    os.makedirs(os.path.join(PROJECT_ROOT, "reports"), exist_ok=True)
    main()
