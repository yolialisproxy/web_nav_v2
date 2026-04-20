#!/usr/bin/env python3
import sys
import os
import json
import requests
import re
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from safe_json_io import safe_read_json, safe_write_json

TARGETS = [
    {
        "name": "WebStack 官方",
        "url": "https://webstack.cc/",
        "desc": "运营7年 5000+人工审核站点"
    },
    {
        "name": "极客猿导航",
        "url": "https://nav.geekape.com/",
        "desc": "3000+开发者工具站点"
    },
    {
        "name": "前端导航",
        "url": "https://frontendnav.com/",
        "desc": "前端开发资源"
    },
    {
        "name": "AI工具箱导航",
        "url": "https://ai-bot.cn/",
        "desc": "最全AI工具集合"
    },
    {
        "name": "设计导航",
        "url": "https://hao.uisdc.com/",
        "desc": "设计师资源站"
    },
    {
        "name": "程序员导航",
        "url": "https://nav.bigo.sg/",
        "desc": "后端开发资源"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def extract_from_webstack():
    print("🔍 正在提取 WebStack 数据...")
    try:
        r = requests.get("https://webstack.cc/assets/js/all.js", headers=HEADERS, timeout=15)
        r.raise_for_status()
        # 提取JSON数组
        m = re.search(r'var all_data = (\[.*?\]);', r.text, re.DOTALL)
        if m:
            data = json.loads(m.group(1))
            print(f"✅ 成功提取 WebStack: {len(data)} 个站点")
            return data
    except Exception as e:
        print(f"❌ WebStack 提取失败: {e}")
    return []

def main():
    print("🚀 高质量导航站点批量导入工具")
    print("=" * 60)

    total = 0
    all_sites = []

    # 提取各个站点
    webstack_sites = extract_from_webstack()
    all_sites.extend(webstack_sites)

    print("\n✅ 导入完成")
    print(f"总共提取: {len(all_sites)} 个高质量站点")

    # 保存到导入缓冲区
    with open('data/imported_sites.json', 'w', encoding='utf-8') as f:
        json.dump(all_sites, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 数据已保存到 data/imported_sites.json")
    print("接下来运行分发脚本将这些站点自动分类到对应目录中")

if __name__ == "__main__":
    main()
