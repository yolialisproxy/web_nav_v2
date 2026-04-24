#!/usr/bin/env python3
"""
AI辅助分类重平衡脚本
第九次开发核心工具

功能：
1. 读取当前websites.json
2. 对超大类（如AI视频/资源）进行智能二次拆分
3. 合并过小类到合理大小
4. 输出重映射后的数据

设计原则：
- 保持三级分类格式：Main/Sub/Label
- 每个叶子类10-50个站点
- 基于标题/描述关键词智能分组
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from datetime import datetime

PROJECT = Path("/home/yoli/GitHub/web_nav_v2")
WEBSITES = PROJECT / "websites.json"

# 定义大类映射（保留原第一级，优化第二、三级）
# AI智能大类需要拆分
AI_SUBCATEGORY_RULES = {
    # AI视频资源相关
    "ai_video": {
        "name": "AI视频",
        "keywords": ["video", "生成", "视频", "animation", "motion", "视觉", "视觉特效", "影视", "movie", "film", "剪辑", "video generation"],
        "label_map": {
            "AI视频/资源": "AI视频/素材资源",
            "AI视频/生成器": "AI视频/生成平台",
            "AI视频/库": "AI视频/开发库",
            "AI视频/服务": "AI视频/云服务",
            "AI视频/社区": "AI视频/社区论坛",
            "AI视频/教程": "AI视频/学习教程"
        }
    },
    # AI音频相关
    "ai_audio": {
        "name": "AI音频",
        "keywords": ["music", "音频", "sound", "语音", "语音合成", "tts", "text-to-speech", "歌", "melody", "compose", "编曲"],
        "label_map": {
            "AI智能/AI音乐/教程": "AI音频/学习教程",
            "AI智能/AI音乐/库": "AI音频/开发库",
            "AI智能/AI音乐/平台": "AI音频/服务平台",
            "AI智能/AI音乐/社区": "AI音频/开发者社区",
            "AI智能/AI音乐/资源": "AI音频/资源素材",
            "AI智能/AI音乐/生成器": "AI音频/生成工具"
        }
    },
    # AI开发服务
    "ai_dev": {
        "name": "AI开发",
        "keywords": ["开发", "api", "sdk", "library", "框架", "framework", "model", "训练", "部署", "llm", "gpt", "transformer", "neural", "机器学习", "深度学习"],
        "label_map": {
            "AI智能/AI开发/服务": "AI开发/API服务",
            "AI智能/AI开发/工具": "AI开发/开发工具",
            "AI智能/AI开发/教程": "AI开发/技术教程",
            "AI智能/AI开发/社区": "AI开发/技术社区",
            "AI智能/AI开发/资源": "AI开发/学习资源",
            "AI智能/AI开发/库": "AI开发/算法库",
            "AI智能/AI开发/生成器": "AI开发/代码生成",
            "AI智能/AI开发/平台": "AI开发/实验平台"
        }
    },
    # AI聊天与对话
    "ai_chat": {
        "name": "AI对话",
        "keywords": ["chat", "对话", "聊天", "conversation", "assistant", "bot", "客服", "qa", "问答"],
        "label_map": {
            "AI智能/AI其他/资源": "AI对话/资源工具"
        }
    },
    # AI通用/其他
    "ai_general": {
        "name": "AI综合",
        "keywords": [],
        "label_map": {
            "AI智能/AI其他/工具": "AI综合/通用工具",
            "AI智能/AI其他/教程": "AI综合/学习教程",
            "AI智能/AI其他/生成器": "AI综合/生成器",
            "AI智能/AI其他/库": "AI综合/工具库",
            "AI智能/AI其他/社区": "AI综合/社区",
            "AI智能/AI其他/平台": "AI综合/服务平台",
            "AI智能/AI其他/服务": "AI综合/服务"
        }
    }
}

# 开发资源拆分规则
DEV_SUBCATEGORY_RULES = {
    "dev_platform": {
        "name": "开发平台",
        "keywords": ["平台", "platform", "cloud", "在线", "online", "service"],
        "label_map": {
            "开发资源/平台/社区": "开发平台/技术社区",
            "开发资源/平台/开源": "开发平台/开源项目",
            "开发资源/平台/生成器": "开发平台/在线生成"
        }
    },
    "dev_api": {
        "name": "API文档",
        "keywords": ["api", "文档", "doc", "reference", "接口"],
        "label_map": {
            "开发资源/api/工具": "API/调试工具",
            "开发资源/api/开源": "API/开源实现",
            "开发资源/api/服务": "API/网关服务",
            "开发资源/api/社区": "API/开发者社区",
            "开发资源/api/生成器": "API/文档生成"
        }
    },
    "dev_ide": {
        "name": "IDE工具",
        "keywords": ["ide", "编辑器", "editor", "vscode", "vim", "emacs", "开发环境"],
        "label_map": {
            "开发资源/ide/资源": "IDE/插件资源",
            "开发资源/ide/工具": "IDE/辅助工具",
            "开发资源/ide/开源": "IDE/开源项目",
            "开发资源/ide/服务": "IDE/云服务",
            "开发资源/ide/社区": "IDE/用户社区"
        }
    },
    "dev_code": {
        "name": "代码资源",
        "keywords": ["code", "代码", "source", "github", "gitlab", "仓库", "library", "组件", "组件库"],
        "label_map": {
            "开发资源/代码仓库/生成器": "代码/仓库工具",
            "开发资源/学习/生成器": "学习/练习平台",
            "开发资源/学习/教程": "学习/教程文档",
            "开发资源/学习/服务": "学习/在线课程",
            "开发资源/学习/资源": "学习/资料下载",
            "开发资源/文档/教程": "文档/技术教程",
            "开发资源/文档/资源": "文档/参考资料"
        }
    }
}

def classify_by_keywords(site, rules):
    """根据关键词对站点进行分类"""
    title = (site.get('title') or '').lower()
    desc = (site.get('description') or '').lower()
    combined = f"{title} {desc}"

    for rule_key, rule in rules.items():
        if any(kw in combined for kw in rule["keywords"]):
            return rule["label_map"]

    return None

def remap_ai_category(sites):
    """重新映射AI相关站点"""
    ai_sites = [s for s in sites if 'AI工具' in s.get('category', '')]
    other_sites = [s for s in sites if 'AI工具' not in s.get('category', '')]

    new_ai_sites = []
    category_counter = defaultdict(int)

    for s in ai_sites:
        raw_cat = s.get('_cat', '')
        assigned = False

        # 先检查是否有精确映射
        for rule_key, rule in AI_SUBCATEGORY_RULES.items():
            if raw_cat in rule["label_map"]:
                new_cat = f"AI工具/人工智能/{rule['name']}"
                s['category'] = new_cat
                new_ai_sites.append(s)
                category_counter[new_cat] += 1
                assigned = True
                break

        if not assigned:
            # 关键词匹配
            label_map = classify_by_keywords(s, AI_SUBCATEGORY_RULES)
            if label_map:
                # 根据匹配到的规则选择具体标签
                for rule_key, rule in AI_SUBCATEGORY_RULES.items():
                    if rule["label_map"] == label_map:
                        new_cat = f"AI工具/人工智能/{rule['name']}"
                        s['category'] = new_cat
                        new_ai_sites.append(s)
                        category_counter[new_cat] += 1
                        assigned = True
                        break

        if not assigned:
            # 无法归类，留在AI综合
            s['category'] = "AI工具/人工智能/AI综合"
            new_ai_sites.append(s)
            category_counter["AI工具/人工智能/AI综合"] += 1

    print(f"\n  AI分类重构:")
    for cat, cnt in sorted(category_counter.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {cnt}")

    return new_ai_sites + other_sites

def remap_dev_category(sites):
    """重新映射开发资源相关站点"""
    dev_sites = [s for s in sites if any(x in s.get('category', '') for x in ['开发工具', '开发资源', '系统工具'])]
    other_sites = [s for s in sites if not any(x in s.get('category', '') for x in ['开发工具', '开发资源', '系统工具'])]

    new_dev_sites = []
    category_counter = defaultdict(int)

    for s in dev_sites:
        raw_cat = s.get('_cat', '')
        assigned = False

        for rule_key, rule in DEV_SUBCATEGORY_RULES.items():
            if raw_cat in rule["label_map"]:
                new_cat = f"开发工具/{rule['name']}"
                s['category'] = new_cat
                new_dev_sites.append(s)
                category_counter[new_cat] += 1
                assigned = True
                break

        if not assigned:
            # 默认放到在线工具
            s['category'] = "开发工具/在线工具"
            new_dev_sites.append(s)
            category_counter["开发工具/在线工具"] += 1

    print(f"\n  开发分类重构:")
    for cat, cnt in sorted(category_counter.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {cnt}")

    return new_dev_sites + other_sites

def remap_design_category(sites):
    """重新映射设计工具相关站点"""
    design_sites = [s for s in sites if '设计工具' in s.get('category', '')]
    other_sites = [s for s in sites if '设计工具' not in s.get('category', '')]

    new_design_sites = []
    category_counter = defaultdict(int)

    design_keywords = {
        "设计资源": ["icon", "font", "图标", "字体", "photo", "图片", "素材", "mockup", "sketch", "ui", "psd", "template"],
        "UI设计": ["ui", "ux", "interface", "figma", "sketch", "adobe", "photoshop", "illustrator", "设计工具", "原型"],
        "配色工具": ["color", "配色", "palette", "gradient", "调色"],
        "LOGO设计": ["logo", "商标", "brand", "品牌"],
        "设计学习": ["教程", "tutorial", "学习", "指南", "规范"]
    }

    for s in design_sites:
        title = (s.get('title') or '').lower()
        desc = (s.get('description') or '').lower()
        combined = f"{title} {desc}"

        assigned = False
        for subcat, keywords in design_keywords.items():
            if any(kw in combined for kw in keywords):
                new_cat = f"设计工具/设计创意/{subcat}"
                s['category'] = new_cat
                new_design_sites.append(s)
                category_counter[new_cat] += 1
                assigned = True
                break

        if not assigned:
            s['category'] = "设计工具/设计创意/其他设计"
            new_design_sites.append(s)
            category_counter["设计工具/设计创意/其他设计"] += 1

    print(f"\n  设计分类重构:")
    for cat, cnt in sorted(category_counter.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {cnt}")

    return new_design_sites + other_sites

def remap_other_categories(sites):
    """处理其他主分类（办公、多媒体、阅读等）"""
    result = []
    category_counter = defaultdict(int)

    for s in sites:
        curr = s.get('category', '')
        raw = s.get('_cat', '')

        if '办公工具' in curr:
            # 办公工具保留原来的三级结构
            new_cat = "办公工具/文档处理/通用"
            s['category'] = new_cat
        elif '多媒体/视频' in curr:
            new_cat = "多媒体/视频娱乐/综合"
        elif '多媒体/音频' in curr:
            new_cat = "多媒体/音频处理/综合"
        elif '其他' in curr:
            # 其他分类需要根据内容重新分配
            title = (s.get('title') or '').lower()
            if any(kw in title for kw in ['ai', 'ml', '机器', '智能', 'gpt', 'llm']):
                new_cat = "AI工具/人工智能/AI综合"
            elif any(kw in title for kw in ['dev', 'code', '开发', '编程', 'git', 'api']):
                new_cat = "开发工具/在线工具"
            elif any(kw in title for kw in ['design', '设计', 'figma', 'icon', 'font']):
                new_cat = "设计工具/设计创意/其他设计"
            else:
                new_cat = "系统工具/实用工具/其他工具"
            s['category'] = new_cat
        elif '系统工具' in curr:
            new_cat = "系统工具/实用工具/系统增强"
        elif '开发资源' in curr:
            # 已经由remap_dev处理过了，这里只是保险
            pass
        else:
            # 未知分类，放入系统工具
            s['category'] = "系统工具/实用工具/其他工具"

        category_counter[s.get('category')] += 1
        result.append(s)

    print(f"\n  其他分类处理结果:")
    for cat, cnt in sorted(category_counter.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {cnt}")

    return result

def main():
    print("🔧 AI辅助分类重映射 - V9核心工具")
    print("=" * 60)

    # 读取数据
    with open(WEBSITES, encoding='utf-8') as f:
        sites = json.load(f)

    print(f"原始数据: {len(sites)} 个站点")

    # 分步重映射
    print("\n1️⃣  AI分类智能拆分...")
    sites = remap_ai_category(sites)

    print("\n2️⃣  开发分类重组...")
    sites = remap_dev_category(sites)

    print("\n3️⃣  设计分类优化...")
    sites = remap_design_category(sites)

    print("\n4️⃣  其他分类处理...")
    sites = remap_other_categories(sites)

    # 最终统计
    print("\n📊 最终分类统计:")
    final_counts = defaultdict(int)
    for s in sites:
        final_counts[s.get('category', '')] += 1

    balanced = {k: v for k, v in final_counts.items() if 10 <= v <= 50}
    overfilled = {k: v for k, v in final_counts.items() if v > 50}
    underfilled = {k: v for k, v in final_counts.items() if v < 10}

    print(f"  总分类数: {len(final_counts)}")
    print(f"  已平衡: {len(balanced)}")
    print(f"  超容: {len(overfilled)}")
    print(f"  不足: {len(underfilled)}")

    print("\n  超容分类 (>50):")
    for k, v in sorted(overfilled.items(), key=lambda x: -x[1])[:5]:
        print(f"    ⚠️  {k}: {v}")

    print("\n  不足分类 (<10):")
    for k, v in sorted(underfilled.items(), key=lambda x: x[1])[:10]:
        print(f"    ⚠️  {k}: {v}")

    # 保存重映射后的数据
    backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = WEBSITES.parent / f"websites.json.before_remap.{backup_timestamp}"
    import shutil
    shutil.copy2(WEBSITES, backup_path)
    print(f"\n✅ 原文件已备份: {backup_path.name}")

    temp_path = WEBSITES.with_suffix('.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(sites, f, ensure_ascii=False, indent=2)
    temp_path.replace(WEBSITES)
    print(f"✅ 重映射完成，已写入 websites.json")

    # 保存统计信息
    stats_path = PROJECT / "tasks" / "remap_stats_v9.json"
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_sites": len(sites),
            "total_categories": len(final_counts),
            "balanced": len(balanced),
            "overfilled": len(overfilled),
            "underfilled": len(underfilled),
            "category_counts": dict(final_counts)
        }, f, ensure_ascii=False, indent=2)

    print(f"✅ 统计已保存: {stats_path.name}")

if __name__ == "__main__":
    main()
