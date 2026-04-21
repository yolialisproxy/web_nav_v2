#!/usr/bin/env python3
"""
三平台兼容技能脚本: Hermes / OpenCLAW / Claude Code
自动检测运行环境，统一输出格式
"""

import sys
import os
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from safe_json_io import safe_read_json, safe_write_json

import statistics
from pathlib import Path

def detect_agent_platform() -> str:
    """检测当前运行的Agent平台"""
    if os.getenv("HERMES_SESSION_ID"): return "hermes"
    if os.getenv("OPENCLAW_RUNTIME"): return "openclaw"
    if os.getenv("CLAUDE_CODE_UUID"): return "claude"
    return "unknown"

DEFAULT_DATA_PATH = "/home/yoli/GitHub/web_nav_v2/data/websites.json"

# 填充标准（基于九九九九四层级法）
FILL_STANDARD = {
    'category': {'min': 9, 'target': 12, 'ideal': 18}, # 大类
    'subcategory': {'min': 9, 'target': 12, 'ideal': 18}, # 中类
    'minor_category': {'min': 9, 'target': 12, 'ideal': 18}, # 小类
    'site': {'min': 12, 'target': 18, 'ideal': 25} # 网站
}

def analyze_level(data_list, level_name):
    """
    通用层级分析
    data_list: 包含 {name: str, count: int} 的列表
    """
    if not data_list:
        return None

    counts = [i['count'] for i in data_list]
    items = sorted(data_list, key=lambda x: x['count'])

    return {
        'level': level_name,
        'total_items': len(items),
        'total_sites': sum(counts),
        'avg': statistics.mean(counts),
        'median': statistics.median(counts),
        'min': min(counts),
        'max': max(counts),
        'items': items,
        'lowest': items[:10],
        'highest': items[-10:]
    }

def print_analysis(result, level_key):
    """打印分析结果"""
    if not result:
        print(f"\\n❌ {level_key} 层级无数据")
        return

    std = FILL_STANDARD[level_key]

    print(f"\\n{'='*60}")
    print(f"📊 {result['level']} 层级分析")
    print(f"{'='*60}")
    print(f" 总数量: {result['total_items']} 个")
    print(f" 总网站: {result['total_sites']} 个")
    print(f" 平均值: {result['avg']:.1f}")
    print(f" 中位数: {result['median']:.1f}")
    print(f" 范围: {result['min']} - {result['max']}")

    # 填充建议
    low_count = sum(1 for i in result['items'] if i['count'] < std['min'])
    mid_count = sum(1 for i in result['items'] if std['min'] <= i['count'] < std['target'])
    good_count = sum(1 for i in result['items'] if std['target'] <= i['count'] <= std['ideal'])
    high_count = sum(1 for i in result['items'] if i['count'] > std['ideal'])

    print(f"\\n 📈 填充分布:")
    print(f" 🔴 不足({std['min']}以下): {low_count} 个")
    print(f" 🟡 填充中({std['min']}-{std['target']}): {mid_count} 个")
    print(f" 🟢 正常({std['target']}-{std['ideal']}): {good_count} 个")
    print(f" ⚠️ 过多({std['ideal']}以上): {high_count} 个")

    # 最需要填充的
    if result['lowest']:
        print(f"\\n ⬆️ 优先填充 (数量最少的前10个):")
        for item in result['lowest']:
            status = "🔴" if item['count'] == 0 else "🟡"
            print(f" {status} {item['name']}: {item['count']} 个")

def process_json(input_path):
    """
    ✅ WebNav V2 分类统计分析
    """
    print(f"📂 读取数据: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. 格式标准化 (内存中)
    categories = []
    all_sites_count = 0

    if isinstance(data, dict) and not ('sites' in data and 'categories' in data):
        # V1-style nested format: { "Cat": { "subcategories": [...] } }
        for cat_name, cat_val in data.items():
            cat_obj = {'name': cat_name, 'subcategories': []}
            cat_sites = cat_val.get('sites', []) if isinstance(cat_val, dict) else []
            cat_obj['site_count'] = len(cat_sites)
            all_sites_count += len(cat_sites)

            for sub in cat_val.get('subcategories', []) if isinstance(cat_val, dict) else []:
                sub_obj = {'name': sub['name'], 'minor_categories': []}
                sub_sites = sub.get('sites', [])
                sub_obj['site_count'] = len(sub_sites)
                all_sites_count += len(sub_sites)

                for minor in sub.get('minor_categories', []) if isinstance(sub, dict) else []:
                    minor_sites = minor.get('sites', [])
                    minor_obj = {'name': minor['name'], 'count': len(minor_sites)}
                    all_sites_count += len(minor_sites)
                    sub_obj['minor_categories'].append(minor_obj)

                cat_obj['subcategories'].append(sub_obj)
            categories.append(cat_obj)
    elif 'categories' in data:
        # V2 structure: { "categories": [...], "sites": [...] }
        categories = data
        all_sites_count = len(data['siteIds'])
    else:
        print("❌ 未知数据格式")
        return

    # 3. 计算各级统计量
    cat_stats = []
    sub_stats = []
    minor_stats = []

    for cat in categories:
        c_count = cat.get('site_count', 0)
        for sub in cat.get('subcategories', []):
            c_count += sub.get('site_count', 0)
            for minor in sub.get('minor_categories', []):
                c_count += minor.get('count', 0)

        cat_stats.append({'name': cat['name'], 'count': c_count})

        for sub in cat.get('subcategories', []):
            s_count = sub.get('site_count', 0)
            for minor in sub.get('minor_categories', []):
                s_count += minor.get('count', 0)
            sub_stats.append({'name': f"{cat['name']} > {sub['name']}", 'count': s_count})

            for minor in sub.get('minor_categories', []):
                minor_stats.append({'name': f"{cat['name']} > {sub['name']} > {minor['name']}", 'count': minor.get('count', 0)})

    # 4. 执行分析与打印
    print_analysis(analyze_level(cat_stats, '大类 (9)'), 'category')
    print_analysis(analyze_level(sub_stats, '中类 (9×9=81)'), 'subcategory')
    print_analysis(analyze_level(minor_stats, '小类 (9×9×9=729)'), 'minor_category')

    print(f"\\n{'='*60}")
    print(f"📊 网站总数: {all_sites_count}")
    print(f" {'='*60}")
    print("✨ 分析完成!")

def main():
    input_path = DEFAULT_DATA_PATH
    if len(sys.argv) >= 2:
        input_path = sys.argv[1]
    if not Path(input_path).exists():
        print(f"❌ 文件不存在: {input_path}")
        sys.exit(1)

    process_json(input_path)

if __name__ == "__main__":
    main()
