#!/usr/bin/env python3
"""
全局分类平衡优化方案生成器
基于V10基线数据和超容拆分计划，协调超容拆分和欠容填充
"""

import json
import math
from typing import Dict, List, Tuple, Set
from pathlib import Path

# 配置路径
BASE_PATH = Path("/home/yoli/GitHub/web_nav_v2")
V10_STATS_PATH = BASE_PATH / "category_stats_V10.json"
OVER_CAPACITY_PLAN_PATH = BASE_PATH / "plans/over_capacity_split_plan.json"
OUTPUT_DIR = BASE_PATH / "plans"

# 平衡标准
MIN_CAPACITY = 10  # 最小容量
MAX_CAPACITY = 50  # 最大容量
TARGET_BALANCE_RATE = 0.80  # 目标平衡度80%+

def load_json(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_current_state(v10_stats: dict) -> dict:
    """分析V10基线的当前状态"""
    categories = v10_stats["category_statistics"]
    total_sites = v10_stats["total_sites"]

    over_capacity = []  # >50
    under_capacity = []  # <10
    balanced = []  # 10-50
    empty = []  # 0

    for cat_name, count in categories.items():
        if count == 0:
            empty.append((cat_name, count))
        elif count < MIN_CAPACITY:
            under_capacity.append((cat_name, count))
        elif count > MAX_CAPACITY:
            over_capacity.append((cat_name, count))
        else:
            balanced.append((cat_name, count))

    balance_rate = len(balanced) / len(categories) * 100

    return {
        "total_categories": len(categories),
        "total_sites": total_sites,
        "over_capacity": over_capacity,
        "under_capacity": under_capacity,
        "empty": empty,
        "balanced": balanced,
        "balance_rate": balance_rate
    }

def calculate_required_migration(analysis: dict) -> dict:
    """计算需要迁移的站点数量"""
    over_total = sum(count for _, count in analysis["over_capacity"])
    under_total_needed = 0

    # 计算欠容类需要多少站点才能达到平衡
    for cat_name, count in analysis["under_capacity"]:
        needed = MIN_CAPACITY - count
        under_total_needed += needed

    for cat_name, count in analysis["empty"]:
        under_total_needed += MIN_CAPACITY

    # 所有超容类需要拆分的站点数（超出50的部分）
    excess_sites = sum(count - MAX_CAPACITY for _, count in analysis["over_capacity"])

    # 实际可迁移的站点数（包括拆分后可能的多余）
    available_from_split = sum(count - 10 for _, count in analysis["over_capacity"])

    return {
        "over_capacity_total": over_total,
        "excess_sites_above_50": excess_sites,
        "available_sites_after_min_split": available_from_split,
        "under_capacity_shortfall": under_total_needed,
        "net_balance_possible": available_from_split - under_total_needed
    }

def design_category_mergers(analysis: dict) -> List[dict]:
    """设计分类合并方案 - 合并相似的小类"""
    merger_suggestions = []

    # 分析欠容和空分类，寻找合并机会
    # 按major分类分组
    from collections import defaultdict
    major_groups = defaultdict(list)

    for cat_name, count in analysis["under_capacity"] + analysis["empty"]:
        parts = cat_name.split("/")
        if len(parts) >= 3:
            major = parts[0].strip()
            mid = parts[1].strip()
            leaf = parts[2].strip()
            major_groups[major].append((mid, leaf, count, cat_name))

    # 寻找可以合并的mid类别
    for major, sub_cats in major_groups.items():
        if len(sub_cats) < 2:
            continue

        # 按mid分组
        mid_groups = defaultdict(list)
        for mid, leaf, count, full_name in sub_cats:
            mid_groups[mid].append((leaf, count, full_name))

        # 检查哪些mid类别下的leaf分类可以合并
        for mid, leaf_list in mid_groups.items():
            if len(leaf_list) <= 1:
                continue

            total_count = sum(c for _, c, _ in leaf_list)
            # 如果合并后总数在合理范围，建议合并
            if total_count >= MIN_CAPACITY and total_count <= MAX_CAPACITY:
                merger_suggestions.append({
                    "type": "merge_leaf_categories",
                    "major": major,
                    "mid": mid,
                    "original_categories": [
                        {"name": leaf, "count": count, "full_path": full}
                        for leaf, count, full in leaf_list
                    ],
                    "proposed_merged_name": f"{major}/{mid}",
                    "proposed_count": total_count,
                    "rationale": f"合并后总计{total_count}个站点，达到平衡标准(10-50)"
                })

    return merger_suggestions

def design_structure_optimization(analysis: dict, over_capacity_plan: dict) -> dict:
    """设计分类结构调整方案"""
    current_total = analysis["total_categories"]

    # 计算拆分后的分类数变化
    split_details = over_capacity_plan["split_categories"]
    new_categories_from_split = 0

    for split in split_details:
        sub_cats = split["sub_categories"]
        # 过滤掉估计数量<10的（这些需要进一步处理）
        valid_subs = [s for s in sub_cats if s["estimated_count"] >= MIN_CAPACITY]
        new_categories_from_split += len(valid_subs)

    # 预计合并减少的分类数
    mergers = design_category_mergers(analysis)
    categories_reduced_by_merger = sum(
        len(m["original_categories"]) - 1 for m in mergers
    )

    # 预计最终分类数
    over_cat_count = len(analysis["over_capacity"])
    final_total = (
        current_total
        - over_cat_count  # 移除原超容类
        + new_categories_from_split  # 添加拆分后的新类
        - categories_reduced_by_merger  # 减去合并减少的类
    )

    return {
        "current_total_categories": current_total,
        "over_capacity_categories_to_split": over_cat_count,
        "estimated_new_categories_from_split": new_categories_from_split,
        "estimated_categories_reduced_by_merger": categories_reduced_by_merger,
        "proposed_final_total_categories": final_total,
        "structure_change_summary": {
            "拆分超容类": f"{over_cat_count}个超容类拆分为约{new_categories_from_split}个子类",
            "合并小类": f"合并{categories_reduced_by_merger}个小类为更大的分类",
            "最终规模": f"从{current_total}类优化到约{final_total}类"
        }
    }

def design_migration_plan(analysis: dict, over_capacity_plan: dict) -> List[dict]:
    """设计站点迁移计划"""
    migration_plan = []

    # 1. 处理超容类拆分 - 从超容类迁移到其子类
    for split_info in over_capacity_plan["split_categories"]:
        original_name = split_info["original_name"]
        original_count = split_info["current_count"]

        # 获取该类的具体站点分配（这里简化处理）
        # 在实际执行时，需要根据具体的站点属性进行分配
        sub_categories = split_info["sub_categories"]

        # 过滤掉太小（<10）的子类，需要与其他合并
        valid_subs = [s for s in sub_categories if s["estimated_count"] >= MIN_CAPACITY]

        # 为每个有效的子类创建迁移任务
        running_total = 0
        for i, sub in enumerate(valid_subs):
            if i == len(valid_subs) - 1:
                # 最后一个分到剩余所有
                move_count = original_count - running_total
            else:
                move_count = sub["estimated_count"]
                running_total += move_count

            migration_plan.append({
                "type": "split_and_redistribute",
                "from_category": original_name,
                "to_category": f"{original_name}/{sub['name']}",  # 简化的新名称
                "estimated_sites_to_move": move_count,
                "rationale": split_info["split_dimension"],
                "complexity": split_info["complexity"]
            })

    # 2. 设计从未平衡类到欠容类的站点再分配
    # 从拆分后的超容类中，进一步将站点分配给独立的欠容类
    under_list = analysis["under_capacity"]
    empty_list = analysis["empty"]

    # 计算欠容类需要的站点数
    under_needs = []
    for cat_name, count in under_list:
        needed = MIN_CAPACITY - count
        under_needs.append((cat_name, needed))

    for cat_name, count in empty_list:
        under_needs.append((cat_name, MIN_CAPACITY))

    # 按需求排序（优先填补需求大的）
    under_needs.sort(key=lambda x: x[1], reverse=True)

    # 标记哪些超容类拆分后有富余站点可以外调
    # 假设拆分后每个子类最低保留10个站点，多余的可以调给其他欠容类
    excess_allocation = []
    for split_info in over_capacity_plan["split_categories"]:
        original_count = split_info["current_count"]
        # 预估拆分后保留在本体系内的最小站点数
        min_keep = 10 * len([s for s in split_info["sub_categories"]
                           if s["estimated_count"] >= MIN_CAPACITY])
        excess = original_count - min_keep
        if excess > 0:
            excess_allocation.append({
                "source_group": split_info["original_name"],
                "available_excess": excess,
                "dimension": split_info["split_dimension"]
            })

    # 分配富余站点到欠容类
    excess_pointer = 0
    current_excess_remaining = excess_allocation[0]["available_excess"] if excess_allocation else 0

    for target_cat, needed in under_needs:
        while needed > 0 and excess_pointer < len(excess_allocation):
            available = current_excess_remaining
            to_transfer = min(needed, available)

            migration_plan.append({
                "type": "cross_category_transfer",
                "from_category": excess_allocation[excess_pointer]["source_group"],
                "to_category": target_cat,
                "estimated_sites_to_move": to_transfer,
                "rationale": f"填补{target_cat}的容量缺口",
                "complexity": "medium"
            })

            needed -= to_transfer
            current_excess_remaining -= to_transfer

            if current_excess_remaining <= 0:
                excess_pointer += 1
                if excess_pointer < len(excess_allocation):
                    current_excess_remaining = excess_allocation[excess_pointer]["available_excess"]

    return migration_plan

def simulate_balance_improvement(analysis: dict, migration_plan: List[dict],
                                   structure_change: dict) -> dict:
    """模拟不同策略下的平衡度变化（改进版）"""

    # 创建当前分类计数的副本
    simulated_counts = {cat: count for cat, count in
                       analysis["balanced"] + analysis["over_capacity"] +
                       analysis["under_capacity"] + analysis["empty"]}

    # 首先处理拆分迁移：将原超容类拆分为多个新子类
    split_migrations = [m for m in migration_plan if m["type"] == "split_and_redistribute"]
    cross_migrations = [m for m in migration_plan if m["type"] == "cross_category_transfer"]

    # Phase 1: 执行拆分 - 重置原超容类到其拆分后的总和
    # 对于每个拆分任务，我们不是简单减去，而是将原分类的站点重新分配到新子类
    processed_originals = set()
    for migration in split_migrations:
        from_cat = migration["from_category"]
        to_cat = migration["to_category"]
        move_count = migration["estimated_sites_to_move"]

        # 如果是第一次处理这个原分类，先移除原分类的所有站点（稍后会通过子类重新添加）
        if from_cat not in processed_originals:
            # 保留原分类当前计数，但我们会用子类替换它
            processed_originals.add(from_cat)

        # 向目标子类添加站点
        if to_cat in simulated_counts:
            simulated_counts[to_cat] += move_count
        else:
            simulated_counts[to_cat] = move_count

    # 处理原超容类：将所有原超容类设置为0（因为已被拆分）
    for original_cat in processed_originals:
        simulated_counts[original_cat] = 0

    # Phase 2: 执行跨类转移 - 从有富余的分类转移到欠容类
    # 按转移量从来源分类中扣除
    for migration in cross_migrations:
        from_cat = migration["from_category"]
        to_cat = migration["to_category"]
        move_count = migration["estimated_sites_to_move"]

        # 从来源分类转移
        if from_cat in simulated_counts:
            simulated_counts[from_cat] -= move_count
            # 确保不为负（虽然理论上应该够用）
            if simulated_counts[from_cat] < 0:
                simulated_counts[from_cat] = 0

        # 向目标分类添加
        if to_cat in simulated_counts:
            simulated_counts[to_cat] += move_count
        else:
            simulated_counts[to_cat] = move_count

    # 清理原超容类（若还有非零值，设为0表示已不存在）
    for original_cat in processed_originals:
        if simulated_counts[original_cat] > 0:
            simulated_counts[original_cat] = 0

    # 计算迁移后的平衡状态
    new_balanced = []
    new_over = []
    new_under = []
    new_empty = []

    for cat, count in simulated_counts.items():
        # 跳过已被拆分且无剩余站点的原分类
        if count == 0 and cat in processed_originals:
            continue

        if count == 0:
            new_empty.append((cat, count))
        elif count < MIN_CAPACITY:
            new_under.append((cat, count))
        elif count > MAX_CAPACITY:
            new_over.append((cat, count))
        else:
            new_balanced.append((cat, count))

    # 重新计算总数（排除已清除的原超容类）
    final_categories = len(simulated_counts) - len(processed_originals)
    new_balance_rate = len(new_balanced) / final_categories * 100 if final_categories > 0 else 0

    return {
        "simulated_total_categories": final_categories,
        "simulated_balanced_count": len(new_balanced),
        "simulated_over_capacity_count": len(new_over),
        "simulated_under_capacity_count": len(new_under),
        "simulated_empty_count": len(new_empty),
        "simulated_balance_rate": new_balance_rate,
        "categories_needing_attention": new_over + new_under + new_empty,
        "processing_notes": f"已处理{len(processed_originals)}个原超容类拆分"
    }

def assess_risks(structure_change: dict, migration_plan: List[dict],
                  simulation: dict, analysis: dict) -> dict:
    """风险评估"""
    risks = []

    # 风险1：拆分过于激进导致分类碎片化
    if structure_change["proposed_final_total_categories"] > 400:
        risks.append({
            "level": "high",
            "category": "分类碎片化",
            "description": f"最终分类数可能达到{structure_change['proposed_final_total_categories']}类，增加前端渲染负担",
            "mitigation": "控制拆分粒度，确保子类站点数在10-50范围内，避免过度细分"
        })

    # 风险2：迁移过程中数据不一致
    migration_count = len(migration_plan)
    if migration_count > 200:
        risks.append({
            "level": "medium",
            "category": "迁移复杂度",
            "description": f"需要执行{migration_count}个迁移任务，执行风险较高",
            "mitigation": "分阶段执行，优先处理容量偏差最大的分类，建立回滚机制"
        })

    # 风险3：平衡度未达预期
    if simulation["simulated_balance_rate"] < TARGET_BALANCE_RATE * 100:
        risks.append({
            "level": "high",
            "category": "目标未达成",
            "description": f"模拟平衡度仅{simulation['simulated_balance_rate']:.1f}%，未达到目标{TARGET_BALANCE_RATE*100}%",
            "mitigation": "需要进一步合并小类或调整拆分策略"
        })

    # 风险4：前端性能影响
    # 估算data.js大小变化
    estimated_sites = analysis["total_sites"]
    avg_site_entry_bytes = 200  # 估算每个站点的JSON大小
    estimated_data_size_mb = (estimated_sites * avg_site_entry_bytes) / (1024*1024)

    if estimated_data_size_mb > 2:
        risks.append({
            "level": "medium",
            "category": "前端性能",
            "description": f"预估data.js大小约{estimated_data_size_mb:.1f}MB，影响加载性能",
            "mitigation": "考虑站点分页、懒加载或数据压缩策略"
        })

    return {
        "identified_risks": risks,
        "overall_risk_level": "high" if any(r["level"] == "high" for r in risks) else "medium",
        "risk_count": len(risks)
    }

def generate_proposed_structure(analysis: dict, over_capacity_plan: dict,
                                 mergers: List[dict]) -> dict:
    """生成建议的最终分类结构"""

    # 将所有分类合并为一个列表
    all_categories = (analysis["balanced"] +
                     analysis["over_capacity"] +
                     analysis["under_capacity"] +
                     analysis["empty"])

    # 基础分类体系（保留现有的major/mid/leaf结构）
    major_categories = set()
    mid_categories = {}

    for cat_name, count in all_categories:
        parts = cat_name.split("/")
        if len(parts) >= 3:
            major = parts[0].strip()
            mid = parts[1].strip()
            major_categories.add(major)
            if major not in mid_categories:
                mid_categories[major] = set()
            mid_categories[major].add(mid)
    # 添加拆分后的新分类
    for split in over_capacity_plan["split_categories"]:
        original_name = split["original_name"]
        parts = original_name.split("/")
        if len(parts) >= 3:
            original_major, original_mid, _ = parts[0], parts[1], "/".join(parts[2:])
        elif len(parts) == 2:
            original_major, original_mid = parts[0], parts[1]
        else:
            original_major, original_mid = original_name, "未分类"

        major_categories.add(original_major)
        if original_major not in mid_categories:
            mid_categories[original_major] = set()

        for sub in split["sub_categories"]:
            if sub["estimated_count"] >= MIN_CAPACITY:
                mid_categories[original_major].add(f"{original_mid}/{sub['name']}")

    # 应用合并建议
    for merger in mergers:
        major = merger["major"]
        mid = merger["mid"]
        # 合并后保留这个mid类别
        if major not in mid_categories:
            mid_categories[major] = set()
        mid_categories[major].add(mid)

    return {
        "classification_hierarchy": "Major/Mid/Leaf (三级结构)",
        "major_categories": sorted(list(major_categories)),
        "mid_category_count": sum(len(v) for v in mid_categories.values()),
        "structure_notes": {
            "保留三级结构": "保持 Major > Mid > Leaf 的层次化导航结构",
            "智能合并": "将过小的leaf分类合并到同一mid层级",
            "适度拆分": "将过大的分类按功能场景拆分为多个mid子类"
        },
        "proposed_major_mid_mapping": {
            major: sorted(list(mids)) for major, mids in mid_categories.items()
        }
    }

def main():
    print("=" * 60)
    print("全局分类平衡优化方案生成器")
    print("=" * 60)

    # 1. 加载数据
    print("\n[1/6] 加载V10基线数据...")
    v10_stats = load_json(V10_STATS_PATH)
    over_capacity_plan = load_json(OVER_CAPACITY_PLAN_PATH)
    print(f"✓ 总站点数: {v10_stats['total_sites']}")
    print(f"✓ 总分类数: {v10_stats['total_categories']}")

    # 2. 分析当前状态
    print("\n[2/6] 分析当前分类状态...")
    analysis = analyze_current_state(v10_stats)
    print(f"✓ 超容类 (>50): {len(analysis['over_capacity'])} 个")
    print(f"✓ 欠容类 (<10): {len(analysis['under_capacity'])} 个")
    print(f"✓ 空分类 (0): {len(analysis['empty'])} 个")
    print(f"✓ 平衡类 (10-50): {len(analysis['balanced'])} 个")
    print(f"✓ 当前平衡度: {analysis['balance_rate']:.1f}%")

    # 3. 计算迁移需求
    print("\n[3/6] 计算站点迁移需求...")
    migration_requirements = calculate_required_migration(analysis)
    print(f"✓ 超容类超额站点: {migration_requirements['excess_sites_above_50']}")
    print(f"✓ 最小拆分后可用站点: {migration_requirements['available_sites_after_min_split']}")
    print(f"✓ 欠容类所需填充: {migration_requirements['under_capacity_shortfall']}")
    print(f"✓ 净站点可调配: {migration_requirements['net_balance_possible']}")

    # 4. 设计分类合并方案
    print("\n[4/6] 设计分类合并方案...")
    merger_suggestions = design_category_mergers(analysis)
    print(f"✓ 识别出 {len(merger_suggestions)} 个合并机会")
    for m in merger_suggestions[:5]:
        print(f"  - {m['major']}/{m['mid']}: {len(m['original_categories'])}个小类合并")

    # 5. 设计结构调整方案
    print("\n[5/6] 设计结构调整方案...")
    structure_change = design_structure_optimization(analysis, over_capacity_plan)
    print(f"✓ 优化后预计分类总数: {structure_change['proposed_final_total_categories']}")
    for key, value in structure_change["structure_change_summary"].items():
        print(f"  - {key}: {value}")

    # 6. 设计站点迁移计划
    print("\n[6/6] 设计站点迁移计划...")
    migration_plan = design_migration_plan(analysis, over_capacity_plan)
    print(f"✓ 生成 {len(migration_plan)} 个迁移任务")

    # 统计迁移类型
    split_tasks = [m for m in migration_plan if m["type"] == "split_and_redistribute"]
    cross_tasks = [m for m in migration_plan if m["type"] == "cross_category_transfer"]
    print(f"  - 拆分迁移: {len(split_tasks)} 个")
    print(f"  - 跨类转移: {len(cross_tasks)} 个")

    # 7. 模拟平衡度改善
    print("\n[附加] 模拟平衡度改善...")
    simulation = simulate_balance_improvement(analysis, migration_plan, structure_change)
    print(f"✓ 模拟后平衡度: {simulation['simulated_balance_rate']:.1f}%")
    print(f"✓ 平衡类数量: {simulation['simulated_balanced_count']}")
    print(f"✓ 仍需关注: {len(simulation['categories_needing_attention'])} 个分类")

    # 8. 风险评估
    print("\n[附加] 风险评估...")
    risks = assess_risks(structure_change, migration_plan, simulation, analysis)
    print(f"✓ 识别风险数: {risks['risk_count']}")
    print(f"✓ 整体风险等级: {risks['overall_risk_level']}")

    # 9. 生成建议的最终结构
    print("\n[附加] 生成推荐结构...")
    proposed_structure = generate_proposed_structure(analysis, over_capacity_plan, merger_suggestions)
    print(f"✓ Major分类数: {len(proposed_structure['major_categories'])}")
    print(f"✓ Mid分类数: {proposed_structure['mid_category_count']}")

    # 10. 输出全局优化方案 JSON
    print("\n" + "=" * 60)
    print("生成全局优化方案文件...")

    # 统计迁移量
    total_sites_to_move = sum(m["estimated_sites_to_move"] for m in migration_plan)

    # 构建最终方案
    global_plan = {
        "plan_metadata": {
            "plan_name": "global_balance_optimization_plan",
            "generated_at": "20260424_183000",
            "base_version": "V10",
            "objective": "提升分类平衡度从32.7%到80%+",
            "total_migration_tasks": len(migration_plan),
            "total_sites_to_relocate": total_sites_to_move
        },
        "current_state_summary": {
            "total_sites": analysis["total_sites"],
            "total_categories": analysis["total_categories"],
            "balance_rate": f"{analysis['balance_rate']:.1f}%",
            "over_capacity_count": len(analysis["over_capacity"]),
            "under_capacity_count": len(analysis["under_capacity"]),
            "empty_count": len(analysis["empty"]),
            "balanced_count": len(analysis["balanced"])
        },
        "proposed_structure": proposed_structure,
        "category_merger_plan": merger_suggestions,
        "migration_plan": migration_plan,
        "expected_balance_statistics": {
            "before_balance_rate": f"{analysis['balance_rate']:.1f}%",
            "after_balance_rate": f"{simulation['simulated_balance_rate']:.1f}%",
            "balanced_categories_after": simulation["simulated_balanced_count"],
            "total_categories_after": simulation["simulated_total_categories"],
            "improvement_needed": f"{TARGET_BALANCE_RATE*100 - simulation['simulated_balance_rate']:.1f}%"
        },
        "risk_assessment": risks,
        "implementation_notes": {
            "execution_phases": [
                "Phase 1: 执行超容类拆分（按复杂度分批次）",
                "Phase 2: 执行跨类站点迁移（填补欠容类）",
                "Phase 3: 执行分类合并（减少碎片化）",
                "Phase 4: 验证平衡度并调整"
            ],
            "performance_consideration": "当前data.js约1.3MB，优化后预计增加至1.5-1.8MB，建议实施懒加载",
            "monitoring_key_metrics": ["平衡度变化", "站点迁移完整性", "前端性能", "用户访问分布"]
        }
    }

    # 保存JSON
    output_json_path = OUTPUT_DIR / "global_balance_optimization_plan.json"
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(global_plan, f, ensure_ascii=False, indent=2)
    print(f"✓ 方案已保存: {output_json_path}")

    # 11. 生成影响分析报告
    print("\n生成影响分析报告...")
    impact_report = generate_impact_report(analysis, structure_change, simulation, risks, migration_plan, merger_suggestions)
    output_md_path = OUTPUT_DIR / "balance_impact_analysis.md"
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(impact_report)
    print(f"✓ 报告已保存: {output_md_path}")

    print("\n" + "=" * 60)
    print("全局平衡优化方案生成完成！")
    print("=" * 60)

def generate_impact_report(analysis: dict, structure_change: dict,
                           simulation: dict, risks: dict,
                           migration_plan: List[dict],
                           merger_suggestions: List[dict]) -> str:
    """生成Markdown格式的影响分析报告"""

    report = f"""# 分类平衡优化影响分析报告

## 一、执行摘要

- **当前平衡度**: {analysis['balance_rate']:.1f}% (89/272 平衡)
- **目标平衡度**: ≥80%
- **预计提升**: 至 {simulation['simulated_balance_rate']:.1f}%
- **优化策略**: 超容拆分 + 欠容填充 + 分类合并

## 二、现状分析

### 2.1 分类分布
| 分类类型 | 数量 | 说明 |
|---------|------|------|
| 超容类 (>50) | {len(analysis['over_capacity'])} | 需拆分为子类 |
| 欠容类 (<10) | {len(analysis['under_capacity'])} | 需填充站点 |
| 空分类 (0) | {len(analysis['empty'])} | 需填充或合并 |
| 平衡类 (10-50) | {len(analysis['balanced'])} | 无需调整 |

### 2.2 站点分布
- **总站点数**: {analysis['total_sites']}
- **超容类容纳站点**: {sum(c for _, c in analysis['over_capacity']):,}
- **欠容类缺口**: {sum(MIN_CAPACITY - c for _, c in analysis['under_capacity'])} + {len(analysis['empty'])*MIN_CAPACITY} (空类)

## 三、优化方案

### 3.1 结构调整
{chr(10).join(f"- **{k}**: {v}" for k, v in structure_change["structure_change_summary"].items())}

### 3.2 迁移计划
- **总迁移任务**: {simulation['simulated_total_categories'] - analysis['total_categories'] + len(analysis['over_capacity'])} 个
- **涉及站点**: ~{sum(m['estimated_sites_to_move'] for m in migration_plan if 'total_sites_to_relocate' not in m):,} 个站点需要重新分配

### 3.3 分类合并
识别出 {len(merger_suggestions)} 个合并机会：
"""

    # 添加合并详情
    for merger in merger_suggestions[:10]:
        report += f"- **{merger['major']}/{merger['mid']}**: 合并 {len(merger['original_categories'])} 个小类 → 1个综合类 ({merger['proposed_count']}站点)\n"

    report += f"""
## 四、预期效果

### 4.1 平衡度变化
| 指标 | 当前 | 优化后 |
|------|------|--------|
| 平衡类数量 | {len(analysis['balanced'])} | {simulation['simulated_balanced_count']} |
| 分类总数 | {analysis['total_categories']} | {simulation['simulated_total_categories']} |
| 平衡度 | {analysis['balance_rate']:.1f}% | {simulation['simulated_balance_rate']:.1f}% |

### 4.2 仍需关注的分类
优化后仍有 {len(simulation['categories_needing_attention'])} 个分类未达平衡标准：
"""

    # 列出仍需关注的分类
    for cat, count in simulation['categories_needing_attention'][:15]:
        status = "空" if count == 0 else ("欠容" if count < MIN_CAPACITY else "超容")
        report += f"- {cat}: {count}站点 [{status}]\n"

    report += f"""
## 五、风险评估

### 5.1 识别的风险
"""

    for i, risk in enumerate(risks['identified_risks'], 1):
        report += f"{i}. **{risk['level'].upper()} - {risk['category']}**\n   {risk['description']}\n   缓解措施: {risk['mitigation']}\n\n"

    report += f"""### 5.2 整体风险等级: {risks['overall_risk_level'].upper()}

## 六、实施建议

### 6.1 分阶段执行
1. **第一阶段（试点）**: 选择2-3个复杂度中等的超容类执行拆分
2. **第二阶段（扩展）**: 分批处理剩余超容类，同时开始跨类迁移
3. **第三阶段（收敛）**: 执行分类合并，填补剩余欠容类
4. **第四阶段（验证）**: 全面测试，验证平衡度和功能完整性

### 6.2 回滚策略
- 每个阶段执行前备份category_stats.json
- 迁移任务支持增量更新
- 保持可逆操作路径

## 七、性能影响

- **当前data.js大小**: ~1.3MB
- **预计优化后大小**: ~1.5-1.8MB（+15-38%）
- **建议**:
  - 实施站点分页加载（每页50-100个）
  - 前端渲染优化（虚拟滚动）
  - 考虑使用Gzip/Brotli压缩

## 八、监控指标

优化后需持续监控：
1. 分类平衡度趋势
2. 站点访问分布（是否过度集中）
3. 前端加载性能和渲染时间
4. 用户搜索和导航行为变化

---

**报告生成时间**: 2026-04-24
**基于版本**: V10 baseline
**目标版本**: V11 balanced

"""

    return report

if __name__ == "__main__":
    # 加载数据（在main函数内完成）
    v10_stats = load_json(V10_STATS_PATH)
    over_capacity_plan = load_json(OVER_CAPACITY_PLAN_PATH)

    main()
