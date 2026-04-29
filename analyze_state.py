#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 web_nav 项目状态 - Phase 2 准备检查
生成分类结构、填充需求报告
"""

import json
from collections import Counter
from pathlib import Path

PROJECT = Path('/home/yoli/GitHub/web_nav_v2')
DATA_FILE = PROJECT / 'websites.json'

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

lines = []
lines.append(f"Total sites: {len(data):,}")
lines.append("")

# 三维分类统计
big, mid, small = Counter(), Counter(), Counter()
for s in data:
    cat = s.get('_cat', s.get('category', '其他'))
    if '/' in cat:
        parts = [p.strip() for p in cat.split('/')]
        if len(parts) >= 1: big[parts[0]] += 1
        if len(parts) >= 2: mid[parts[1]] += 1
        if len(parts) >= 3: small[parts[2]] += 1
    else:
        big[cat] += 1

lines.append(f"Big categories:   {len(big)}")
lines.append(f"Mid categories:   {len(mid)}")
lines.append(f"Small categories: {len(small)}")
lines.append("")

under_small = sorted([(c, n) for c, n in small.items() if n < 9], key=lambda x: x[1])
lines.append(f"Small classes needing fill (<9 sites): {len(under_small)}")
for i, (c, n) in enumerate(under_small, 1):
    lines.append(f"  {i:3d}. {c}  [{n} sites]")

under_mid = sorted([(c, n) for c, n in mid.items() if n < 9], key=lambda x: x[1])
lines.append("")
lines.append(f"Mid classes needing fill (<9): {len(under_mid)}")
for c, n in under_mid[:8]:
    lines.append(f"  {c}: {n}")

under_big = [(c, n) for c, n in big.items() if n < 9]
lines.append("")
lines.append(f"Big classes (<9 - main categories are OK): {len(under_big)}")
for c, n in under_big:
    lines.append(f"  {c}: {n}")

other = sum(1 for s in data if '其他' in s.get('_cat', '') or s.get('category') == '其他')
lines.append("")
lines.append(f'Sites using "其他": {other}')

missing = [i for i, s in enumerate(data) if not all(k in s for k in ['url', 'title', 'name', 'description'])]
lines.append("")
lines.append(f"Missing core fields: {len(missing)}")

lines.append("")
lines.append("=" * 60)
phase2_ready = len(under_small) > 0
lines.append("PHASE 2 STATUS: " + ("READY - Can start filling small classes" if phase2_ready else "All small classes OK"))
lines.append("=" * 60)

output = "\n".join(lines)
print(output)

# Save reports
REPORT = PROJECT / 'phase2_analysis_report.txt'
with open(REPORT, 'w', encoding='utf-8') as f:
    f.write(output + "\n")
print(f"\n[Saved] {REPORT}")

# Also save JSON summary
summary = {
    "total_sites": len(data),
    "categories": {
        "big": len(big),
        "mid": len(mid),
        "small": len(small)
    },
    "needs_fill": {
        "small": len(under_small),
        "mid": len(under_mid),
        "big": len(under_big)
    },
    "other_sites": other,
    "missing_fields": len(missing),
    "phase2_ready": phase2_ready
}
with open(PROJECT / 'phase2_summary.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
print(f"[Saved] {PROJECT / 'phase2_summary.json'}")
