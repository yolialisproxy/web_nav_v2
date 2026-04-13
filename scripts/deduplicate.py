#!/usr/bin/env python3
"""
三平台兼容技能脚本: Hermes / OpenCLAW / Claude Code
自动检测运行环境，统一输出格式
"""

import sys
import os
import json
import re
import time
from urllib.parse import urlparse
from difflib import SequenceMatcher
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
def extract_root_domain(url):
    """提取根域名（忽略www和子域名）"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        # 移除 www. 前缀
        domain = re.sub(r'^www\.', '', domain)
        # 提取根域名（取最后两个部分）
        parts = domain.split('.')
        if len(parts) >= 2:
            return '.'.join(parts[-2:])
        return domain
    except Exception:
        return ""
def similarity(a, b):
    """计算两个字符串的相似度 (0-1)"""
    return SequenceMatcher(None, a, b).ratio()
def deduplicate_sites(sites):
    """三级去重检测"""
    if not sites:
        return []

    seen_urls = set()
    seen_domains = {}
    result = []

    for site in sites:
        url = site.get('url', '').strip()
        name = site.get('name', '').strip()

        if not url:
            continue

        # 一级检测：精确URL匹配
        if url in seen_urls:
            print(f"[一级去重] 精确URL重复: {url}")
            continue
        seen_urls.add(url)

        # 二级检测：根域名匹配
        root_domain = extract_root_domain(url)
        if root_domain:
            if root_domain in seen_domains:
                print(f"[二级去重] 根域名重复: {root_domain} ({url})")
                continue
            seen_domains[root_domain] = url

        # 三级检测：名称相似度（仅标记，待人工审核）
        is_similar = False
        for existing_name in [s.get('name', '') for s in result]:
            if similarity(name.lower(), existing_name.lower()) > 0.85:
                print(f"[三级警告] 名称相似: '{name}' ≈ '{existing_name}'")
                is_similar = True
                break

        result.append(site)

    return result
def process_json(input_path):
    """
    ✅ WebNav 通用去重脚本
    自动检测 V1/V2 格式，自动升级，透明处理
    没有临时文件，没有中间版本，不需要用户干预
    """
    print(f"📂 读取数据: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 🔍 自动检测格式版本
    if 'sites' in data and 'categories' in data:
        version = 2
        print("✅ 检测到 V2 格式")
    else:
        version = 1
        print("✅ 检测到 V1 格式，正在透明升级")
        # 自动在内存中升级到 V2 格式
        all_sites = []
        all_categories = []
        site_id_counter = 1

        for cat_name, cat_data in data.items():
            cat = {
                'id': cat_name,
                'name': cat_name,
                'siteIds': [],
                'subcategories': []
            }

            for sub in cat_data.get('subcategories', []):
                sub_cat = {
                    'id': sub.get('id', sub['name']),
                    'name': sub['name'],
                    'siteIds': [],
                    'minor_categories': []
                }

                for mc in sub.get('minor_categories', []):
                    minor_cat = {
                        'id': mc.get('id', mc['name']),
                        'name': mc['name'],
                        'siteIds': []
                    }

                    for site in mc.get('sites', []):
                        site['id'] = f"site_{site_id_counter}"
                        site_id_counter += 1
                        all_sites.append(site)
                        minor_cat['siteIds'].append(site['id'])

                    sub_cat['minor_categories'].append(minor_cat)

                cat['subcategories'].append(sub_cat)

            all_categories.append(cat)

        data = {
            'version': 2,
            'sites': all_sites,
            'categories': all_categories
        }
        print(f"✅ 自动升级完成: 共 {len(data['sites'])} 个网站")

    original_count = len(data['sites'])

    # 全量去重，直接操作全局 sites 列表
    deduplicated_sites = deduplicate_sites(data['sites'])
    kept_ids = {site['id'] for site in deduplicated_sites}

    # 清理所有分类中的无效ID引用
    cleaned_count = 0
    for cat in data['categories']:
        if 'siteIds' in cat:
            original_len = len(cat['siteIds'])
            cat['siteIds'] = [id for id in cat['siteIds'] if id in kept_ids]
            cleaned_count += original_len - len(cat['siteIds'])

    data['sites'] = deduplicated_sites

    # 统计
    processed_count = len(data['sites'])
    print(f"\n📊 统计: 原始网站数 {original_count} → 去重后 {processed_count}")
    print(f"   移除: {original_count - processed_count} 个重复项")
    print(f"   清理无效引用: {cleaned_count} 个")

    # ✅ 原子写入 （先完整序列化后再一次性写回磁盘）
    final_json = json.dumps(data, ensure_ascii=False, indent=2)

    # 先写入备份
    backup_path = Path(input_path).parent / '.backup' / f'websites_{int(time.time())}.json'
    backup_path.parent.mkdir(exist_ok=True)
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(final_json)

    # 最后覆盖主文件
    with open(input_path, 'w', encoding='utf-8') as f:
        f.write(final_json)

    print(f"\n✅ 原子写入完成")
    print(f"💾 备份已保存: {backup_path}")
    print(f"💾 主文件已更新: {input_path}")

    return data
def main():
    if len(sys.argv) < 2:
        print("用法: python3 deduplicate.py data/websites.json")
        print(f"示例: python3 deduplicate.py /home/yoli/GitHub/web_nav_v2/data/websites.json")
        sys.exit(1)

    input_path = sys.argv[1]

    if not Path(input_path).exists():
        print(f"❌ 文件不存在: {input_path}")
        sys.exit(1)

    process_json(input_path)
    print("\n✨ 去重完成!")
if __name__ == "__main__":
    main()