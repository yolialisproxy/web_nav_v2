#!/usr/bin/env python3
import json
from collections import defaultdict

def recalibrate_fill():
    print("=== 执行 recalibrate_fill 分类填充校准任务 ===")
    print()

    # 读取标准分类树
    with open('final_standard_categories.json', 'r', encoding='utf-8') as f:
        standard_cats = json.load(f)

    # 读取当前站点数据
    with open('nav_with_sites.json', 'r', encoding='utf-8') as f:
        nav_data = json.load(f)

    report = []
    total_sites = 0
    total_minor_cats = 0
    empty_cats = []
    low_cats = []
    good_cats = []

    report.append("# 分类填充校准报告")
    report.append("## 概览统计")
    report.append(f"- 执行时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 遍历所有标准分类: 大分类 -> 中分类 -> 小分类
    for big_cat in standard_cats:
        big_name = big_cat['name']
        report.append(f"\n## ✅ 大分类: {big_name}")

        for mid_cat in big_cat['subcategories']:
            mid_name = mid_cat['name']
            report.append(f"\n### 📂 中分类: {mid_name}")
            report.append("| 小分类名称 | 站点数量 | 填充状态 |")
            report.append("|------------|----------|----------|")

            for minor_name in mid_cat['children']:
                total_minor_cats += 1
                site_count = 0

                # 查找该小类的站点数
                if minor_name in nav_data:
                    if 'subcategories' in nav_data[minor_name]:
                        for sc in nav_data[minor_name]['subcategories']:
                            if 'minor_categories' in sc:
                                for mc in sc['minor_categories']:
                                    if mc['name'] == '全部' and 'sites' in mc:
                                        site_count = len(mc['sites'])
                                        total_sites += site_count

                # 判断填充状态
                if site_count == 0:
                    status = "🔴 空分类"
                    empty_cats.append(f"{big_name} > {mid_name} > {minor_name}")
                elif site_count < 5:
                    status = "🟡 严重不足"
                    low_cats.append(f"{big_name} > {mid_name} > {minor_name} ({site_count})")
                elif site_count < 15:
                    status = "🟠 填充不足"
                    low_cats.append(f"{big_name} > {mid_name} > {minor_name} ({site_count})")
                else:
                    status = "🟢 达标"
                    good_cats.append(minor_name)

                report.append(f"| {minor_name} | {site_count} | {status} |")

    # 统计汇总
    report.insert(3, f"- 统计小分类总数: {total_minor_cats}")
    report.insert(4, f"- 当前总站点数: {total_sites}")
    report.insert(5, f"- 空分类数量: {len(empty_cats)}")
    report.insert(6, f"- 填充不足分类数量: {len(low_cats)}")
    report.insert(7, f"- 达标分类数量: {len(good_cats)}")
    report.insert(8, f"- 整体填充率: { (len(good_cats)/total_minor_cats*100):.1f}%")

    report.append("\n## 🚨 优先填充目标清单")
    report.append("### 完全空分类 (需要优先采集):")
    for cat in empty_cats:
        report.append(f"- {cat}")

    report.append("\n### 填充不足分类 (需要补充):")
    for cat in low_cats:
        report.append(f"- {cat}")

    report.append("\n## 📋 下一轮定向采集建议")
    report.append(f"1. 优先处理 {len(empty_cats)} 个空分类")
    report.append(f"2. 补充填充 {len(low_cats)} 个不足分类")
    report.append("3. 目标: 每个小分类至少达到15个有效站点")
    report.append("4. 本次校准完成后，可按优先级列表分配采集任务")

    # 保存报告
    report_path = 'reports/recalibrate_fill_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    # 同时输出json格式数据供后续使用
    json_report = {
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'total_minor_categories': total_minor_cats,
        'total_sites': total_sites,
        'empty_categories': empty_cats,
        'low_fill_categories': low_cats,
        'good_categories': good_cats,
        'fill_rate': len(good_cats)/total_minor_cats
    }
    with open('reports/recalibrate_fill_data.json', 'w', encoding='utf-8') as f:
        json.dump(json_report, f, ensure_ascii=False, indent=2)

    print(f"✅ 校准完成")
    print(f"📊 总小分类: {total_minor_cats} | 空分类: {len(empty_cats)} | 不足: {len(low_cats)} | 达标: {len(good_cats)}")
    print(f"📝 报告已保存到: {report_path}")
    print(f"🔍 整体填充率: { (len(good_cats)/total_minor_cats*100):.1f}%")

if __name__ == "__main__":
    recalibrate_fill()
