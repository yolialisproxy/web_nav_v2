#!/usr/bin/env python3
"""
V9 全局分类修复脚本 - 解决漫游器核心缺陷

核心缺陷：
1. 漫游器只能根据原始路径映射新站点，无法处理已有的大量错误分类站点
2. AI视频类2664个站点全部堆在"其他/杂项/未分类"
3. 系统工具等超容类未充分拆分
4. 小类不足10个站未合并

修复策略：
1. 遍历全部225个原始_cat路径，统计站点数和关键词分布
2. 对站点数>50的超大路径，按标题关键词智能拆分
3. 创建精细的三级分类映射（目标100-120个叶子类）
4. 合并过小小类（<10站）到父类
5. 全量重映射并生成详细报告
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from datetime import datetime
import shutil

PROJECT = Path("/home/yoli/GitHub/web_nav_v2")
WEBSITES = PROJECT / "websites.json"
TASKS = PROJECT / "tasks"
BACKUP_DIR = PROJECT / ".backup"

# 配置
MIN_SITES_PER_LEAF = 10
MAX_SITES_PER_LEAF = 50
TARGET_LEAF_CATEGORIES = 100  # 目标叶子类数量

def load_sites():
    """加载站点数据"""
    with open(WEBSITES, encoding='utf-8') as f:
        return json.load(f)

def backup_websites():
    """备份原始数据"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"websites.json.before_global_fix.{timestamp}"
    shutil.copy2(WEBSITES, backup_path)
    print(f"✅ 备份: {backup_path.name}")
    return backup_path

def analyze_raw_categories(sites):
    """
    分析所有原始_cat路径
    返回: {
        raw_path: {
            "count": 站点数,
            "sample_titles": [标题样本],
            "keywords": {关键词: 频率},
            "existing_category": 当前category值
        }
    }
    """
    print("\n📊 分析原始_cat路径分布...")

    stats = defaultdict(lambda: {
        "count": 0,
        "sample_titles": [],
        "keywords": defaultdict(int),
        "existing_categories": defaultdict(int)
    })

    for s in sites:
        raw = s.get('_cat', '')
        if not raw:
            continue

        stats[raw]["count"] += 1
        title = s.get('title', '') or ''
        if len(stats[raw]["sample_titles"]) < 5:  # 保留5个样本标题
            stats[raw]["sample_titles"].append(title)

        # 提取关键词（中英文混合提取）
        text = f"{title} {s.get('description', '') or ''}".lower()
        # 提取英文单词
        words = re.findall(r'\b[a-z]{3,}\b', text)
        # 提取中文词组（2-4字）
        cn_words = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)

        for w in words:
            stats[raw]["keywords"][w] += 1
        for w in cn_words:
            stats[raw]["keywords"][w] += 1

        cat = s.get('category', '')
        if cat:
            stats[raw]["existing_categories"][cat] += 1

    print(f"原始路径总数: {len(stats)}")
    print(f"总站点数: {sum(v['count'] for v in stats.values())}")

    # 输出统计
    sorted_items = sorted(stats.items(), key=lambda x: -x[1]["count"])
    print("\n前30个原始路径:")
    for raw, stat in sorted_items[:30]:
        top_kws = sorted(stat["keywords"].items(), key=lambda x: -x[1])[:5]
        kw_str = ", ".join([f"{k}({v})" for k,v in top_kws])
        existing = ", ".join([f"{k}:{v}" for k,v in sorted(stat["existing_categories"].items(), key=lambda x: -x[1])[:2]])
        print(f"  {raw}: {stat['count']}站 | {existing} | 关键词: {kw_str}")

    return stats

def identify_super_categories(raw_stats):
    """识别超大类（>50站）和不足类（<10站）"""
    print("\n🔍 识别超容类和超小类...")

    super_cats = {}  # 需要拆分的超大路径
    tiny_cats = []   # 需要合并的过小路径

    for raw, stat in raw_stats.items():
        count = stat["count"]
        if count > MAX_SITES_PER_LEAF:
            super_cats[raw] = count
        elif count < MIN_SITES_PER_LEAF and count > 0:
            tiny_cats.append((raw, count))

    print(f"\n超容类（>{MAX_SITES_PER_LEAF}站）: {len(super_cats)}个")
    for raw, cnt in sorted(super_cats.items(), key=lambda x: -x[1]):
        print(f"  ⚠️  {raw}: {cnt}站")

    print(f"\n超小类（<{MIN_SITES_PER_LEAF}站）: {len(tiny_cats)}个")
    for raw, cnt in sorted(tiny_cats, key=lambda x: x[1])[:20]:
        print(f"  ⚠️  {raw}: {cnt}站")

    return super_cats, tiny_cats

def build_ai_video_split_rules(super_stats, ai_video_sites):
    """
    基于AI视频类站点的标题分布，构建智能拆分规则
    AI智能/AI视频/资源: 2664站 -> 需要拆分成多个子类
    """
    print("\n🤖 构建AI视频智能拆分规则...")

    # 收集所有AI视频类站点的标题关键词
    keyword_dist = defaultdict(int)
    title_samples = defaultdict(list)

    for s in ai_video_sites:
        title = (s.get('title', '') or '').lower()
        desc = (s.get('description', '') or '').lower()
        text = f"{title} {desc}"

        # 英文关键词提取
        words = re.findall(r'\b[a-z]{3,}\b', text)
        # 中文关键词提取
        cn_words = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)

        for w in words + cn_words:
            keyword_dist[w] += 1

        # 保留样本（每个关键词类别保留一些标题示例）
        if len(title_samples[w]) < 3:
            title_samples[w].append(title)

    # 获取top关键词
    top_keywords = sorted(keyword_dist.items(), key=lambda x: -x[1])[:50]
    print("AI视频类高频关键词TOP20:")
    for kw, cnt in top_keywords[:20]:
        print(f"  {kw}: {cnt}次")

    # 基于关键词聚类，定义子类
    # 根据语义分组：生成、编辑、分析、素材、平台等
    split_rules = {
        "AI视频生成": {
            "parent": "AI工具/人工智能/AI视频",
            "keywords": ["generation", "generate", "text-to-video", "文生视频", "视频生成", "synthesis", "synthesia", "runway", "pika"],
            "expected_count": 600
        },
        "AI视频编辑": {
            "parent": "AI工具/人工智能/AI视频",
            "keywords": ["editing", "editor", "edit", "剪辑", "特效", "effects", "motion", "合成"],
            "expected_count": 500
        },
        "AI视频分析": {
            "parent": "AI工具/人工智能/AI视频",
            "keywords": ["analysis", "analyze", "recognition", "识别", "视觉", "vision", "detection", "tracking", "跟踪"],
            "expected_count": 400
        },
        "AI视频素材": {
            "parent": "AI工具/人工智能/AI视频",
            "keywords": ["stock", "footage", "素材", "assets", "library", "库", "下载"],
            "expected_count": 400
        },
        "AI数字人": {
            "parent": "AI工具/人工智能/AI视频",
            "keywords": ["avatar", "数字人", "talking", "虚拟人", "virtual", "human", "数字形象"],
            "expected_count": 300
        },
        "AI视频平台": {
            "parent": "AI工具/人工智能/AI视频",
            "keywords": ["platform", "云", "cloud", "service", "服务", "在线", "online", "api", "平台"],
            "expected_count": 300
        },
    }

    print("\nAI视频拆分方案:")
    for subcat, rule in split_rules.items():
        print(f"  {subcat}: {rule['expected_count']}站, 关键词: {', '.join(rule['keywords'][:5])}")

    return split_rules

def classify_ai_video_site(site, split_rules):
    """对AI视频站点进行智能分类"""
    title = (site.get('title', '') or '').lower()
    desc = (site.get('description', '') or '').lower()
    combined = f"{title} {desc}"

    best_match = None
    best_score = 0

    for subcat, rule in split_rules.items():
        score = 0
        for kw in rule["keywords"]:
            if kw.lower() in combined:
                score += 1
        if score > best_score:
            best_score = score
            best_match = subcat

    if best_match and best_score >= 1:
        return f"AI工具/人工智能/AI视频/{best_match}"
    else:
        return "AI工具/人工智能/AI视频/其他"  # 兜底

def build_system_tools_split_rules():
    """构建系统工具类的拆分规则（基于语义）"""
    print("\n🔧 构建系统工具拆分规则...")

    # 系统工具类当前有大量站点，需要拆分为多个叶子类
    split_rules = {
        "笔记工具": {
            "parent": "系统工具/效率工具",
            "keywords": ["笔记", "note", "notion", "obsidian", "knowledge", "知识库", "wiki", "文档"],
            "target_count": 80
        },
        "协作工具": {
            "parent": "系统工具/效率工具",
            "keywords": ["协作", "collaboration", "team", "团队", "project", "项目管理", "任务", "task"],
            "target_count": 70
        },
        "开发工具": {
            "parent": "系统工具/开发工具",
            "keywords": ["ide", "编辑器", "editor", "开发", "code", "编程", "git", "版本控制"],
            "target_count": 100
        },
        "API工具": {
            "parent": "系统工具/开发工具",
            "keywords": ["api", "接口", "rest", "graphql", "webhook", "api管理", "接口测试"],
            "target_count": 60
        },
        "设计工具": {
            "parent": "系统工具/设计工具",
            "keywords": ["设计", "design", "ui", "ux", "figma", "sketch", "原型"],
            "target_count": 60
        },
        "资源素材": {
            "parent": "系统工具/资源素材",
            "keywords": ["素材", "resource", "资源", "icon", "font", "字体", "图片", "image", "模板"],
            "target_count": 100
        },
        "平台服务": {
            "parent": "系统工具/平台服务",
            "keywords": ["platform", "平台", "云", "cloud", "hosting", "托管", "部署", "deploy"],
            "target_count": 80
        },
        "实用工具": {
            "parent": "系统工具/通用工具",
            "keywords": ["tool", "工具", "utility", "converter", "转换", "calculator", "计算器"],
            "target_count": 100
        }
    }

    print("系统工具拆分方案:")
    for subcat, rule in split_rules.items():
        print(f"  {subcat}: 预计{rule['target_count']}站, 关键词: {', '.join(rule['keywords'][:4])}")

    return split_rules

def classify_system_tools_site(site, split_rules):
    """对系统工具站点进行智能分类"""
    title = (site.get('title', '') or '').lower()
    desc = (site.get('description', '') or '').lower()
    combined = f"{title} {desc}"

    best_match = None
    best_score = 0

    for subcat, rule in split_rules.items():
        score = 0
        for kw in rule["keywords"]:
            if kw.lower() in combined:
                score += 1
        if score > best_score:
            best_score = score
            best_match = subcat

    if best_match and best_score >= 1:
        return f"系统工具/{best_match}"
    else:
        return "系统工具/其他"  # 兜底

def merge_tiny_categories(tiny_cats, raw_stats):
    """
    合并过小的原始路径（<10站）
    策略：根据语义相似性合并到最近的父类
    """
    print("\n🔗 合并超小类...")

    # 定义合并规则：基于一级分类
    merge_map = {}

    for raw, count in tiny_cats:
        parts = raw.split('/')
        first = parts[0]

        # 根据一级分类确定合并目标
        if first == "AI智能":
            merge_map[raw] = "AI工具/人工智能/其他"  # 合并到AI其他
        elif first == "视频娱乐":
            merge_map[raw] = "多媒体/视频娱乐/其他"
        elif first == "开发资源":
            merge_map[raw] = "开发工具/资源文档/其他"
        elif first == "资源素材":
            merge_map[raw] = "设计工具/设计资源/其他"
        elif first == "阅读写作":
            merge_map[raw] = "阅读写作/综合服务/其他"
        elif first == "学术科研":
            merge_map[raw] = "学术科研/综合资源/其他"
        elif first == "创意工具":
            merge_map[raw] = "设计工具/创意工具/其他"
        elif first == "视频创作":
            merge_map[raw] = "多媒体/视频编辑/其他"
        elif first == "办公效率":
            merge_map[raw] = "效率办公/综合工具/其他"
        else:
            merge_map[raw] = "其他/杂项/未分类"

    merged_count = 0
    for raw, target in merge_map.items():
        cnt = raw_stats[raw]["count"]
        merged_count += cnt
        print(f"  📦 {raw} ({cnt}站) → {target}")

    print(f"\n总计合并: {len(merge_map)}个路径, {merged_count}个站点")
    return merge_map

def generate_final_mapping(raw_stats, ai_video_rules, sys_tools_rules, merge_map):
    """
    生成最终的完整映射表
    返回: {原始_cat路径: 新分类}
    """
    print("\n🗺️  生成最终分类映射表...")

    final_mapping = {}
    category_stats = defaultdict(int)

    for raw, stat in raw_stats.items():
        count = stat["count"]

        # 1. 检查是否在合并列表中
        if raw in merge_map:
            final_mapping[raw] = merge_map[raw]
            category_stats[merge_map[raw]] += count
            continue

        # 2. 解析原始路径
        parts = raw.split('/')
        first = parts[0]
        second = parts[1] if len(parts) > 1 else ''
        third = parts[2] if len(parts) > 2 else ''

        # 3. 特殊处理AI视频（超大类，需要实时判断）
        if raw.startswith('AI智能/AI视频/'):
            # 这些站点会在重映射阶段单独处理
            final_mapping[raw] = "AI工具/人工智能/AI视频/待拆分"
            continue

        # 4. 系统工具需要特殊处理
        if first == "资源素材" or first == "创意工具" or first == "阅读写作" or first == "开发资源" or first == "视频创作":
            # 这些在原始数据中分散，需要映射到新的系统工具或对应大类
            # 这里使用简化映射
            category_mapping = {
                "资源素材": "设计工具/设计资源",
                "创意工具": "设计工具/设计创意",
                "阅读写作": "阅读写作/综合服务",
                "开发资源": "开发工具/开发资源",
                "视频创作": "多媒体/视频编辑",
                "视频娱乐": "多媒体/视频娱乐",
                "学术科研": "学术科研/综合研究",
                "办公效率": "效率办公/综合办公",
                "AI智能": "AI工具/人工智能"
            }

            if first in category_mapping:
                parent = category_mapping[first]
                # 根据第二级路径细化
                subcat_mapping = {
                    "平台": "平台服务",
                    "资源": "资源素材",
                    "工具": "开发工具",
                    "教程": "学习教程",
                    "社区": "社区论坛",
                    "服务": "在线服务",
                    "开源": "开源项目",
                    "生成器": "生成工具"
                }

                subcat = subcat_mapping.get(third, f"{second}类")
                final_mapping[raw] = f"{parent}/{subcat}"
            else:
                final_mapping[raw] = "其他/杂项/未分类"
        else:
            final_mapping[raw] = "其他/杂项/未分类"

        category_stats[final_mapping[raw]] += count

    print(f"映射条目数: {len(final_mapping)}")
    print(f"目标分类数: {len(category_stats)}")

    # 显示容量分布
    print("\n初步映射后分类容量:")
    sorted_cats = sorted(category_stats.items(), key=lambda x: -x[1])
    over_count = 0
    under_count = 0
    balanced_count = 0

    for cat, cnt in sorted_cats:
        if cnt > MAX_SITES_PER_LEAF:
            status = "🔴"
            over_count += 1
        elif cnt < MIN_SITES_PER_LEAF:
            status = "🟡"
            under_count += 1
        else:
            status = "🟢"
            balanced_count += 1
        print(f"  {status} {cat}: {cnt}站")

    print(f"\n平衡状态: {balanced_count}达标, {over_count}超容, {under_count}不足")

    return final_mapping

def apply_remapping(sites, final_mapping, ai_video_rules, sys_tools_rules):
    """
    应用重映射到所有站点
    返回更新后的站点列表和统计信息
    """
    print("\n🔄 执行全量重映射...")

    stats = defaultdict(int)
    ai_video_count = 0
    sys_tools_count = 0
    reassigned_from_other = 0

    for s in sites:
        raw = s.get('_cat', '')
        old_cat = s.get('category', '')

        # 1. AI视频特殊处理
        if raw.startswith('AI智能/AI视频/'):
            new_cat = classify_ai_video_site(s, ai_video_rules)
            ai_video_count += 1
        # 2. 系统工具特殊处理（如果属于系统工具相关的一级类）
        elif raw.split('/')[0] in ["资源素材", "创意工具", "阅读写作", "开发资源", "视频创作", "办公效率", "学术科研"]:
            # 判断是否属于系统工具范畴
            new_cat = classify_system_tools_site(s, sys_tools_rules)
            sys_tools_count += 1
        # 3. 常规映射
        elif raw in final_mapping:
            new_cat = final_mapping[raw]
            # 如果映射到"待拆分"或"其他"，尝试用标题优化
            if new_cat in ["AI工具/人工智能/AI视频/待拆分", "其他/杂项/未分类"]:
                # 兜底分类基于标题
                title = (s.get('title', '') or '').lower()
                if any(kw in title for kw in ['video', '视频', '剪辑']):
                    new_cat = "多媒体/视频娱乐/视频服务"
                elif any(kw in title for kw in ['music', '音乐', 'audio']):
                    new_cat = "多媒体/音频处理/音频服务"
                elif any(kw in title for kw in ['tool', '工具', 'utility']):
                    new_cat = "系统工具/通用工具"
                elif any(kw in title for kw in ['blog', 'writing', '写作']):
                    new_cat = "阅读写作/综合服务"
                elif any(kw in title for kw in ['research', 'dataset', '科研']):
                    new_cat = "学术科研/数据资源"
                elif any(kw in title for kw in ['design', '设计']):
                    new_cat = "设计工具/设计创意"
                else:
                    new_cat = "其他/杂项/未分类"
        else:
            new_cat = "其他/杂项/未分类"

        # 检查是否重新分类（从"其他"类中解救）
        if old_cat == "其他/杂项/未分类" and new_cat != "其他/杂项/未分类":
            reassigned_from_other += 1

        s['category'] = new_cat
        stats[new_cat] += 1

    print(f"AI视频分类: {ai_video_count}站")
    print(f"系统工具相关分类: {sys_tools_count}站")
    print(f"从'其他'类重新分类: {reassigned_from_other}站")

    return stats

def generate_report(sites, stats, raw_stats, final_mapping):
    """生成详细统计报告"""
    print("\n📈 生成统计报告...")

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_sites": len(sites),
        "total_raw_categories": len(raw_stats),
        "mapping_rules": len(final_mapping),
        "total_categories": len(stats),
        "category_distribution": dict(stats),
        "balance_analysis": {
            "balanced": {k: v for k, v in stats.items() if MIN_SITES_PER_LEAF <= v <= MAX_SITES_PER_LEAF},
            "overfilled": {k: v for k, v in stats.items() if v > MAX_SITES_PER_LEAF},
            "underfilled": {k: v for k, v in stats.items() if v < MIN_SITES_PER_LEAF and v > 0}
        },
        "top_categories": dict(sorted(stats.items(), key=lambda x: -x[1])[:20]),
        "saved_from_other": sum(1 for s in sites if s.get('category', '') != "其他/杂项/未分类")
    }

    # 保存统计
    report_path = TASKS / "global_fix_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"✅ 报告: {report_path.name}")

    # 输出摘要
    print("\n" + "="*60)
    print("📊 修复结果摘要:")
    print(f"  总站点: {len(sites)}")
    print(f"  总分类: {len(stats)}")
    print(f"  平衡分类 (10-50站): {len(report['balance_analysis']['balanced'])}")
    print(f"  超容分类 (>50站): {len(report['balance_analysis']['overfilled'])}")
    print(f"  不足分类 (<10站): {len(report['balance_analysis']['underfilled'])}")

    if report['balance_analysis']['overfilled']:
        print("\n  仍需处理的超容类:")
        for cat, cnt in sorted(report['balance_analysis']['overfilled'].items(), key=lambda x: -x[1])[:5]:
            print(f"    {cat}: {cnt}站")

    if report['balance_analysis']['underfilled']:
        print("\n  不足的类（需补充站点）:")
        for cat, cnt in sorted(report['balance_analysis']['underfilled'].items(), key=lambda x: x[1])[:10]:
            print(f"    {cat}: {cnt}站")

    print(f"\n  从'其他'解救站点: {report['saved_from_other']}站")
    print("="*60)

    return report

def main():
    print("🚀 V9 全局分类修复脚本")
    print("="*60)

    # 1. 备份
    backup_path = backup_websites()

    # 2. 加载数据
    sites = load_sites()
    print(f"原始站点: {len(sites)}")

    # 3. 分析原始分类
    raw_stats = analyze_raw_categories(sites)

    # 4. 识别超容类和超小类
    super_cats, tiny_cats = identify_super_categories(raw_stats)

    # 5. 构建拆分规则
    # AI视频类特殊处理（针对2664个站的大类）
    ai_video_sites = [s for s in sites if s.get('_cat', '') == 'AI智能/AI视频/资源']
    ai_video_rules = build_ai_video_split_rules(raw_stats, ai_video_sites)

    # 系统工具类拆分
    sys_tools_rules = build_system_tools_split_rules()

    # 6. 合并超小类
    merge_map = merge_tiny_categories(tiny_cats, raw_stats)

    # 7. 生成映射表
    final_mapping = generate_final_mapping(raw_stats, ai_video_rules, sys_tools_rules, merge_map)

    # 8. 执行重映射
    stats = apply_remapping(sites, final_mapping, ai_video_rules, sys_tools_rules)

    # 9. 保存映射表
    mapping_path = TASKS / "category_mapping_v9_final.json"
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(final_mapping, f, ensure_ascii=False, indent=2)
    print(f"✅ 映射表: {mapping_path.name}")

    # 10. 保存更新后的websites.json
    temp_path = WEBSITES.with_suffix('.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(sites, f, ensure_ascii=False, indent=2)
    temp_path.replace(WEBSITES)
    print(f"✅ Websites数据已更新")

    # 11. 生成报告
    report = generate_report(sites, stats, raw_stats, final_mapping)

    print("\n🎉 全局修复完成！")
    print(f"备份位于: {backup_path}")
    print(f"映射表: {mapping_path}")
    print(f"统计报告: {TASKS / 'global_fix_report.json'}")

    return report

if __name__ == "__main__":
    main()
