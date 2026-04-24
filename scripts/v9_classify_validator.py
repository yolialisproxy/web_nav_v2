#!/usr/bin/env python3
"""
V9分类重构 - 分类验证与统计脚本
用于验证分类映射结果、统计容量分布、识别超大类/空类
"""

import json
import sys
from collections import defaultdict
from typing import Dict, List, Tuple
from datetime import datetime


class V9CategoryValidator:
    """V9分类验证器"""

    def __init__(self, mapping_config_path: str):
        with open(mapping_config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.capacity_limits = self.config['capacity_limits']
        self.main_categories = self.config['main_categories']

    def validate_distribution(self, sites: List[Dict]) -> Dict:
        """验证分类分布是否平衡"""

        # 统计每类站点数
        category_counts = defaultdict(int)
        for site in sites:
            cat = site.get('category_v9', site.get('category', ''))
            if cat:
                category_counts[cat] += 1

        # 分析结果
        results = {
            'total_sites': len(sites),
            'total_categories': len(category_counts),
            'categories': {},
            'overloaded': [],
            'underloaded': [],
            'empty': [],
            'healthy': []
        }

        for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            cat_info = {
                'count': count,
                'status': self._get_status(count)
            }
            results['categories'][cat] = cat_info

            if count > self.capacity_limits['critical_threshold']:
                results['overloaded'].append({'category': cat, 'count': count})
            elif count > self.capacity_limits['warning_threshold']:
                results['overloaded'].append({'category': cat, 'count': count, 'level': 'warning'})
            elif count < self.capacity_limits['empty_threshold'] and count > 0:
                results['underloaded'].append({'category': cat, 'count': count})
            elif count == 0:
                results['empty'].append(cat)
            else:
                results['healthy'].append({'category': cat, 'count': count})

        return results

    def _get_status(self, count: int) -> str:
        """获取容量状态"""
        if count == 0:
            return "empty"
        elif count < self.capacity_limits['normal_min']:
            return "underloaded"
        elif count <= self.capacity_limits['normal_max']:
            return "healthy"
        elif count <= self.capacity_limits['warning_threshold']:
            return "warning"
        else:
            return "critical"

    def suggest_splits(self, overloaded_categories: List[Dict]) -> List[Dict]:
        """为超大类建议拆分方案"""
        suggestions = []

        for cat_info in overloaded_categories:
            cat = cat_info['category']
            count = cat_info['count']

            # 根据类别名建议拆分
            if 'AI' in cat or '人工智能' in cat:
                suggestions.append({
                    'source_category': cat,
                    'current_count': count,
                    'suggested_split': self._suggest_ai_split(cat),
                    'reason': 'AI类站点过多，需按功能细分'
                })
            elif '其他' in cat or '杂项' in cat:
                suggestions.append({
                    'source_category': cat,
                    'current_count': count,
                    'suggested_action': '人工审核并重新分类',
                    'reason': '杂项类需要清理和重新分配'
                })
            elif '系统工具' in cat or '实用工具' in cat:
                suggestions.append({
                    'source_category': cat,
                    'current_count': count,
                    'suggested_split': ['任务管理', '笔记知识库', '文件管理', '自动化工具'],
                    'reason': '系统工具粒度太粗'
                })
            else:
                # 通用建议
                num_splits = (count // 40) + 1
                suggestions.append({
                    'source_category': cat,
                    'current_count': count,
                    'suggested_split_count': num_splits,
                    'reason': '站点数量过多，建议拆分为多个子类'
                })

        return suggestions

    def _suggest_ai_split(self, category: str) -> List[str]:
        """建议AI类拆分"""
        return [
            "AI工具平台",
            "AI代码助手",
            "AI图像生成",
            "AI文本生成",
            "AI语音处理",
            "AI视频生成",
            "AI学习资源",
            "AI模型库",
            "AI API服务",
            "AI数据集",
            "AI研究论文",
            "AI社区论坛"
        ]

    def generate_report(self, validation_results: Dict, output_path: str):
        """生成分类报告"""

        lines = []
        lines.append("# V9 分类重构验证报告")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # 总览
        lines.append("## 一、总览")
        lines.append(f"- 总站点数: {validation_results['total_sites']}")
        lines.append(f"- 分类数: {validation_results['total_categories']}")
        lines.append(f"- 健康分类: {len(validation_results['healthy'])}")
        lines.append(f"- 警告分类: {len([c for c in validation_results['overloaded'] if c.get('level') == 'warning'])}")
        lines.append(f"- 严重超载: {len([c for c in validation_results['overloaded'] if not c.get('level')])}")
        lines.append(f"- 不足分类: {len(validation_results['underloaded'])}")
        lines.append("")

        # 超大类
        if validation_results['overloaded']:
            lines.append("## 二、超载分类（需要拆分）")
            lines.append("| 分类 | 站点数 | 状态 |")
            lines.append("|------|--------|------|")
            for cat_info in validation_results['overloaded']:
                level = cat_info.get('level', 'critical')
                status = "⚠️ 警告" if level == 'warning' else "❌ 严重"
                lines.append(f"| {cat_info['category']} | {cat_info['count']} | {status} |")
            lines.append("")

        # 不足类
        if validation_results['underloaded']:
            lines.append("## 三、容量不足分类（需要补充）")
            lines.append("| 分类 | 站点数 | 建议 |")
            lines.append("|------|--------|------|")
            for cat_info in validation_results['underloaded']:
                lines.append(f"| {cat_info['category']} | {cat_info['count']} | 补充站点 |")
            lines.append("")

        # 健康分类
        if validation_results['healthy']:
            lines.append("## 四、健康分类（20-50站）")
            lines.append("| 分类 | 站点数 |")
            lines.append("|------|--------|")
            for cat_info in sorted(validation_results['healthy'], key=lambda x: -x['count'])[:20]:
                lines.append(f"| {cat_info['category']} | {cat_info['count']} |")
            lines.append("")

        # 建议
        lines.append("## 五、改进建议")
        suggestions = self.suggest_splits(validation_results['overloaded'])
        for i, sug in enumerate(suggestions, 1):
            lines.append(f"{i}. **{sug['source_category']}** ({sug['current_count']}站): {sug['reason']}")
            if 'suggested_split' in sug:
                if isinstance(sug['suggested_split'], list):
                    lines.append(f"   建议拆分为: {', '.join(sug['suggested_split'][:5])}等{suggested_count}个子类")
                else:
                    lines.append(f"   建议: {sug['suggested_split']}")
        lines.append("")

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"报告已生成: {output_path}")

    def export_unmapped_sites(self, sites: List[Dict], output_path: str):
        """导出未映射或低置信度的站点"""
        unmapped = []
        for site in sites:
            cat = site.get('category_v9', '')
            confidence = site.get('category_confidence', 1.0)

            if not cat or cat == '待分类' or confidence < 0.6:
                unmapped.append({
                    'name': site.get('name', site.get('title', '')),
                    'url': site.get('url', ''),
                    'original_category': site.get('category', ''),
                    'current_v9': cat,
                    'confidence': confidence
                })

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(unmapped, f, ensure_ascii=False, indent=2)

        print(f"未映射站点: {len(unmapped)} → {output_path}")


def main():
    """主函数 - 命令行使用示例"""

    if len(sys.argv) < 3:
        print("用法: python3 classify_validator.py <sites.json> <mapping_rules.json> [output_dir]")
        sys.exit(1)

    sites_path = sys.argv[1]
    rules_path = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else '.'

    # 加载数据
    with open(sites_path, 'r', encoding='utf-8') as f:
        sites = json.load(f)

    # 创建验证器
    validator = V9CategoryValidator(rules_path)

    # 验证分布
    results = validator.validate_distribution(sites)

    # 打印摘要
    print("=" * 60)
    print("V9分类验证结果")
    print("=" * 60)
    print(f"总站点: {results['total_sites']}")
    print(f"分类数: {results['total_categories']}")
    print(f"健康分类: {len(results['healthy'])}")
    print(f"超载分类: {len(results['overloaded'])}")
    print(f"不足分类: {len(results['underloaded'])}")

    if results['overloaded']:
        print("\n⚠️  超载分类（需要拆分）:")
        for cat in results['overloaded']:
            print(f"  - {cat['category']}: {cat['count']}站")

    # 生成报告
    report_path = f"{output_dir}/v9_validation_report.md"
    validator.generate_report(results, report_path)

    # 导出未映射站点
    unmapped_path = f"{output_dir}/v9_unmapped_sites.json"
    validator.export_unmapped_sites(sites, unmapped_path)

    print("\n✅ 验证完成")


if __name__ == "__main__":
    main()
