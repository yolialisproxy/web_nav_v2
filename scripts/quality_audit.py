#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from safe_json_io import safe_read_json, safe_write_json
import json

def audit_all(data):
    total = 0
    complete = 0  # 有title且非空+有description且非空
    partial = 0   # 只有一项
    empty = 0     # 两个都没有

    def check(s):
        nonlocal total, complete, partial, empty
        if not isinstance(s, dict):
            return
        total += 1
        title = s.get('title', '')
        desc = s.get('description', '')
        has_title = bool(title and str(title).strip())
        has_desc = bool(desc and str(desc).strip())
        if has_title and has_desc:
            complete += 1
        elif not has_title and not has_desc:
            empty += 1
        else:
            partial += 1

    def traverse(obj):
        if isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict):
                    if 'url' in item:
                        check(item)
                    else:
                        traverse(item)
        elif isinstance(obj, dict):
            for v in obj.values():
                traverse(v)

    traverse(data)
    return total, complete, partial, empty

def main():
    data = safe_read_json('data/websites.json')
    total, complete, partial, empty = audit_all(data)

    print(f"=" * 50)
    print(f"📊 数据质量审计报告")
    print(f"=" * 50)
    print(f"总站点数:     {total}")
    print(f"✅ 完全增强:  {complete:>6} ({complete/total*100:>5.1f}%)")
    print(f"⚠️  部分增强: {partial:>6} ({partial/total*100:>5.1f}%)")
    print(f"❌ 完全空白:  {empty:>6} ({empty/total*100:>5.1f}%)")
    print(f"=" * 50)

    quality_rate = complete / total * 100 if total > 0 else 0
    print(f"质量分数: {quality_rate:.1f}%")

    if quality_rate < 95:
        print(f"⚠️  质量未达标 (需≥95%)，需要继续增强")
    else:
        print(f"✅ 质量达标，可以对外发布")

    return quality_rate

if __name__ == "__main__":
    main()