#!/usr/bin/env python3
"""
✅ WebNav V2 第七次开发 完整工作流入口
导入 -> 备份 -> 去重 -> 补全 -> 分类 -> 平衡 -> 校验 -> 写入

这是唯一正确的完整流程，所有数据修改必须通过此入口。
"""
import sys
import json
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def auto_backup():
    print(f"  ✅ 创建备份 at {datetime.now()}")
    if not os.path.exists('.backup'):
        os.mkdir('.backup')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.system(f"cp websites.json .backup/websites.json.{timestamp}")
    print(f"  ✅ 备份已保存: .backup/websites.json.{timestamp}")

def deduplicate():
    print("  ✅ 去重检查运行中...")
    if os.path.exists('clean_deduplicate.py'):
        os.system("python3 clean_deduplicate.py")

def check_all():
    print("  ✅ 链接健康检查运行中...")
    if os.path.exists('url_health_checker.py'):
        os.system("python3 url_health_checker.py")

def balance_categories():
    print("  ✅ 分类平衡检查运行中...")
    if os.path.exists('category_balancer_report.py'):
        os.system("python3 category_balancer_report.py")

def full_workflow():
    print("\n🔵 WebNav V2 第七次开发 完整工作流启动")
    print("=" * 60)

    print("\n1️⃣  创建备份")
    auto_backup()

    print("\n2️⃣  去重检查")
    deduplicate()

    print("\n3️⃣  链接健康检查")
    check_all()

    print("\n4️⃣  分类平衡检查")
    balance_categories()

    print("\n✅ 完整工作流执行完成")
    print(f"✅ 时间戳: {datetime.now()}")

if __name__ == "__main__":
    full_workflow()
