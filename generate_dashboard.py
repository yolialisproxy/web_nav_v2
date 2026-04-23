#!/usr/bin/env python3
import json
import os
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = "/home/yoli/GitHub/web_nav_v2"
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
DASHBOARD_PATH = os.path.join(REPORTS_DIR, "dashboard.html")

def load_data():
    # Load all available stats
    data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Load website stats
    with open(os.path.join(PROJECT_ROOT, "data/websites.json"), 'r', encoding='utf-8') as f:
        sites = json.load(f)
        data["total_sites"] = len(sites)

        # Count enriched
        enriched = 0
        for s in sites:
            if s.get('title') and s.get('description') and len(s['description'])>10:
                enriched +=1
        data["enriched_count"] = enriched
        data["enrich_rate"] = round(enriched / len(sites) * 100, 1)

    # Load health report
    health_path = os.path.join(PROJECT_ROOT, "url_health_report.json")
    if os.path.exists(health_path):
        with open(health_path, 'r') as f:
            health = json.load(f)
            data["health"] = health

    # Load category report
    cat_path = os.path.join(REPORTS_DIR, "category_balance_report.json")
    if os.path.exists(cat_path):
        with open(cat_path, 'r') as f:
            cat = json.load(f)
            data["categories"] = cat["summary"]

    return data

def generate_html(data):
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebNav V2 项目统计仪表盘</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }}
        body {{ background: #0f172a; color: #e2e8f0; padding: 2rem; max-width: 1200px; margin: 0 auto; }}
        h1 {{ text-align: center; color: #38bdf8; margin-bottom: 2rem; }}
        .timestamp {{ text-align: center; color: #94a3b8; margin-bottom: 2rem; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 1.5rem; border-left: 4px solid #38bdf8; }}
        .card h3 {{ color: #94a3b8; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem; }}
        .value {{ font-size: 2rem; font-weight: 700; color: #f1f5f9; }}
        .progress-bar {{ width: 100%; height: 8px; background: #334155; border-radius: 4px; overflow: hidden; margin-top: 0.75rem; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #10b981, #34d399); }}
        .good {{ border-color: #10b981; }}
        .warning {{ border-color: #f59e0b; }}
        .danger {{ border-color: #ef4444; }}
        .section {{ margin-bottom: 2rem; }}
        .section h2 {{ margin: 2rem 0 1rem; color: #cbd5e1; padding-bottom: 0.5rem; border-bottom: 1px solid #334155; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ color: #94a3b8; font-weight: 500; }}
    </style>
</head>
<body>
    <h1>📊 WebNav V2 项目状态仪表盘</h1>
    <div class="timestamp">生成时间: {data['generated_at']}</div>

    <div class="grid">
        <div class="card">
            <h3>总站点数量</h3>
            <div class="value">{data.get('total_sites', 0)}</div>
            <div class="progress-bar"><div class="progress-fill" style="width: {round(data.get('total_sites', 0)/9000*100, 1)}%"></div></div>
            <div style="margin-top: 0.5rem; color: #94a3b8; font-size: 0.875rem;">目标: 9,000 个站点</div>
        </div>

        <div class="card good">
            <h3>内容补全率</h3>
            <div class="value">{data.get('enrich_rate', 0)}%</div>
            <div class="progress-bar"><div class="progress-fill" style="width: {data.get('enrich_rate', 0)}%"></div></div>
            <div style="margin-top: 0.5rem; color: #94a3b8; font-size: 0.875rem;">已补全: {data.get('enriched_count', 0)} 个站点</div>
        </div>
"""

    if 'health' in data:
        html += f"""
        <div class="card {'good' if data['health'].get('valid_rate', 0) >= 98 else 'warning'}">
            <h3>链接有效率</h3>
            <div class="value">{data['health'].get('valid_rate', 0)}%</div>
            <div style="margin-top: 0.5rem; color: #94a3b8; font-size: 0.875rem;">失效链接: {data['health'].get('failed', 0)} 个</div>
        </div>
"""

    if 'categories' in data:
        balance_rate = round(data['categories']['balanced'] / data['categories']['total_leaf_categories'] * 100, 1)
        html += f"""
        <div class="card {'good' if balance_rate >= 95 else 'warning'}">
            <h3>分类平衡度</h3>
            <div class="value">{balance_rate}%</div>
            <div style="margin-top: 0.5rem; color: #94a3b8; font-size: 0.875rem;">达标分类: {data['categories']['balanced']} / {data['categories']['total_leaf_categories']}</div>
        </div>
"""

    html += """
    </div>

    <div class="section">
        <h2>📋 详细统计</h2>
        <table>
            <tr><th>指标</th><th>数值</th><th>状态</th></tr>
"""

    if 'categories' in data:
        c = data['categories']
        html += f"""
            <tr><td>✅ 达标分类</td><td>{c['balanced']}</td><td style="color:#10b981">正常</td></tr>
            <tr><td>⚠️ 站点不足</td><td>{c['underfilled']}</td><td style="color:#f59e0b">待补充</td></tr>
            <tr><td>⛔ 站点过多</td><td>{c['overfilled']}</td><td style="color:#f59e0b">待调整</td></tr>
            <tr><td>❌ 空分类</td><td>{c['empty']}</td><td style="color:#ef4444">需填充</td></tr>
            <tr><td>❓ 未分类站点</td><td>{c['uncategorized']}</td><td style="color:#f59e0b">待分类</td></tr>
"""

    html += """
        </table>
    </div>

    <div style="text-align: center; margin-top: 3rem; color: #64748b; font-size: 0.875rem;">
        WebNav V2 自动监控仪表盘 | 自动生成请勿手动修改
    </div>
</body>
</html>
"""
    return html

def main():
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Run pre-reports first
    print("🔄 正在生成基础报告...")
    os.system(f"cd {PROJECT_ROOT} && python3 category_balancer_report.py")
    os.system(f"cd {PROJECT_ROOT} && python3 url_health_checker.py")

    print("🔄 正在生成仪表盘...")
    data = load_data()
    html = generate_html(data)

    with open(DASHBOARD_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n✅ 仪表盘生成成功!")
    print(f"   输出路径: {DASHBOARD_PATH}")
    print(f"   大小: {len(html):,} 字节")

    # Show last 3 lines
    with open(DASHBOARD_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print("\n📄 文件尾部3行:")
        for line in lines[-3:]:
            print(f"   {line.strip()}")
    print(f"\n⏱️ 时间戳: {data['generated_at']}")

if __name__ == "__main__":
    main()
