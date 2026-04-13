#!/usr/bin/env python3
"""
#!/usr/bin/env python3
"""
三平台兼容技能脚本: Hermes / OpenCLAW / Claude Code
自动检测运行环境，统一输出格式
"""

import sys
import os
import json
from pathlib import Path

def get_agent_workspace(subpath: str = "") -> Path:
    """三平台兼容工作空间路径检测: Hermes / OpenCLAW / Claude Code"""
    from pathlib import Path
    import os
    home = Path.home()
    platform_paths = [
        home / ".hermes" / "workspace",
        home / ".openclaw" / "workspace",
        home / ".claude" / "workspace"
    ]
    for p in platform_paths:
        if p.exists():
            return p / subpath
    return platform_paths[0] / subpath

def detect_agent_platform() -> str:
    """检测当前运行的Agent平台"""
    import os
    if os.getenv("HERMES_SESSION_ID"): return "hermes"
    if os.getenv("OPENCLAW_RUNTIME"): return "openclaw"
    if os.getenv("CLAUDE_CODE_UUID"): return "claude"
    return "unknown"
DEFAULT_DATA_PATH = "/home/yoli/GitHub/web_nav/data/websites.json"

# 填充标准（基于九九九九四层级法）
FILL_STANDARD = {
    'category': {'min': 9, 'target': 12, 'ideal': 18},      # 大类
    'subcategory': {'min': 9, 'target': 12, 'ideal': 18},   # 中类
    'minor_category': {'min': 9, 'target': 12, 'ideal': 18}, # 小类
    'site': {'min': 12, 'target': 18, 'ideal': 25}          # 网站
}
def analyze_level(data, level_name, key_getter, site_getter):
    """分析指定层级的分布"""
    items = []
    for item in data:
        content = key_getter(item)
        if content:
            count = len(site_getter(item))
            items.append({'name': content, 'count': count})

    if not items:
        return None

    counts = [i['count'] for i in items]
    items.sort(key=lambda x: x['count'])

    return {
        'level': level_name,
        'total_items': len(items),
        'total_sites': sum(counts),
        'avg': statistics.mean(counts),
        'median': statistics.median(counts),
        'min': min(counts),
        'max': max(counts),
        'items': items,
        'lowest': items[:10],  # 最少的前10个
        'highest': items[-10:]  # 最多的前10个
    }
def print_analysis(result, level_key):
    """打印分析结果"""
    std = FILL_STANDARD[level_key]

    print(f"\n{'='*60}")
    print(f"📊 {result['level']} 层级分析")
    print(f"{'='*60}")
    print(f"  总数量: {result['total_items']} 个")
    print(f"  总网站: {result['total_sites']} 个")
    print(f"  平均值: {result['avg']:.1f}")
    print(f"  中位数: {result['median']:.1f}")
    print(f"  范围: {result['min']} - {result['max']}")

    # 填充建议
    low_count = sum(1 for i in result['items'] if i['count'] < std['min'])
    mid_count = sum(1 for i in result['items'] if std['min'] <= i['count'] < std['target'])
    good_count = sum(1 for i in result['items'] if std['target'] <= i['count'] <= std['ideal'])
    high_count = sum(1 for i in result['items'] if i['count'] > std['ideal'])

    print(f"\n  📈 填充分布:")
    print(f"     🔴 不足({std['min']}以下): {low_count} 个")
    print(f"     🟡 填充中({std['min']}-{std['target']}): {mid_count} 个")
    print(f"     🟢 正常({std['target']}-{std['ideal']}): {good_count} 个")
    print(f"     ⚠️ 过多({std['ideal']}以上): {high_count} 个")

    # 最需要填充的
    if result['lowest']:
        print(f"\n  ⬆️ 优先填充 (数量最少的前10个):")
        for item in result['lowest'][:5]:
            status = "🔴" if item['count'] == 0 else "🟡"
            print(f"     {status} {item['name']}: {item['count']} 个")

    return low_count
def process_json(input_path):
    """
    ✅ WebNav V2 分类统计分析
    仅读取，不修改，无副作用
    """
    print(f"📂 读取数据: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # V2 结构校验
    if 'sites' not in data or 'categories' not in data:
        print("❌ 不是 WebNav V2 数据格式，终止操作")
        sys.exit(1)

    all_sites = data['sites']
    categories = data['categories']

    # 按层级统计
    category_stats = []
    subcategory_stats = []
    minor_stats = []

    for cat in categories:
        site_count = len(cat.get('siteIds', []))
        category_stats.append({'name': cat['name'], 'count': site_count})

        for sub in cat.get('subcategories', []):
            sub_site_count = len(sub.get('siteIds', []))
            subcategory_stats.append({'name': f"{cat['name']} > {sub['name']}", 'count': sub_site_count})

            for minor in sub.get('minor_categories', []):
                minor_site_count = len(minor.get('siteIds', []))
                minor_stats.append({'name': f"{cat['name']} > {sub['name']} > {minor['name']}", 'count': minor_site_count})

    # 打印所有分析
    print_analysis(result_cat, 'category')
    print_analysis(result_sub, 'subcategory')
    print_analysis(result_mc, 'minor_category')

    # 网站层级
    print(f"\n{'='*60}")
    print(f"📊 网站总数: {len(all_sites)}")
    print(f"   平均每小类: {len(all_sites)/len(minor_categories):.1f} 个")
    print(f"   平均每中类: {len(all_sites)/len(subcategories):.1f} 个")
    print(f"   平均每大类: {len(all_sites)/len(categories):.1f} 个")

    # 综合填充建议
    print(f"\n{'='*60}")
    print(f"🎯 综合填充建议")
    print(f"{'='*60}")

    # 找出最需要填充的小类
    critical_mc = [m for m in minor_categories if len(m['data'].get('sites', [])) < 12]
    critical_mc.sort(key=lambda x: len(x['data'].get('sites', [])))

    print(f"\n  🔴 紧急填充 (少于12个网站的小类):")
    for mc in critical_mc[:10]:
        print(f"     - {mc['parent']} > {mc['name']}: {len(mc['data'].get('sites', []))} 个")

    if len(critical_mc) > 10:
        print(f"     ... 还有 {len(critical_mc) - 10} 个需要填充")

    print(f"\n✨ 分析完成!")
def main():
    if len(sys.argv) < 2:
        print("用法: python3 analyze_categories.py <json_file>")
        print(f"示例: python3 analyze_categories.py {DEFAULT_DATA_PATH}")
        sys.exit(1)

    input_path = sys.argv[1]

    if not Path(input_path).exists():
        print(f"❌ 文件不存在: {input_path}")
        sys.exit(1)

    process_json(input_path)
if __name__ == "__main__":
    main()