#!/usr/bin/env python3
"""
V9 完整分类重映射器 - 第二代
覆盖所有225个原始_cat路径，智能合并小类，拆分超大类

策略：
1. 保留第一级作为主分类（约9个）
2. 第二、三级合并重组成100-120个叶子分类，每类10-50站
3. 对于超大类（AI视频/资源 2,664），按标题关键词拆分为8-10个子类
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from datetime import datetime

PROJECT = Path("/home/yoli/GitHub/web_nav_v2")
WEBSITES = PROJECT / "websites.json"

# ========== 超大类拆分规则 ==========

# AI智能大类拆分方案（2,848 → 每组 30-50）
AI_SPLIT_RULES = {
    # AI视频资源：2,664 → 需要~60个子类
    "AI视频": {
        "parent": "AI工具/人工智能",
        "subcats": {
            "AI视频生成": ["video generation", "text-to-video", "video synthesis", "生成", "视频生成"],
            "AI视频编辑": ["video editing", "video effects", "motion graphics", "剪辑", "特效"],
            "AI视频分析": ["video analysis", "object detection", "video understanding", "视觉分析"],
            "AI视频素材": ["video assets", "stock video", "视频素材", " footage"],
            "AI语音视频": ["speech video", "talking head", "数字人", "avatar"],
            "AI视频平台": ["video platform", "video service", "视频平台"]
        }
    },
    # AI音频
    "AI音频": {
        "parent": "AI工具/人工智能",
        "subcats": {
            "AI音乐生成": ["music generation", "text-to-music", "音乐生成", "compose"],
            "AI语音合成": ["text-to-speech", "speech synthesis", "语音合成", "tts"],
            "AI声音克隆": ["voice cloning", "voice synthesis", "声音克隆"]
        }
    },
    # AI开发
    "AI开发": {
        "parent": "AI工具/人工智能",
        "subcats": {
            "AI模型API": ["api", "model api", "inference api"],
            "AI框架": ["framework", "pytorch", "tensorflow", "深度学习框架"],
            "AI库": ["library", "sdks", "工具库"],
            "AI训练平台": ["training", "fine-tuning", "模型训练", "train platform"],
            "AI部署": ["deployment", "serving", "inference", "模型部署"]
        }
    },
    # AI聊天
    "AI对话": {
        "parent": "AI工具/人工智能",
        "subcats": {
            "AI聊天": ["chatbot", "对话", "聊天", "assistant", "助手"],
            "AI客服": ["customer service", "support bot", "客服"]
        }
    },
    # AI其他
    "AI其他": {
        "parent": "AI工具/人工智能",
        "subcats": {
            "AI综合": []  # 剩余所有
        }
    }
}

# 其他主类的基础映射（直接从原始_cat的二级路径映射）
BASE_MAPPINGS = {
    # 视频娱乐类
    "视频娱乐": {
        "parent": "多媒体/视频娱乐",
        "subcats": {
            "直播工具": ["直播/工具", "streaming tool"],
            "直播社区": ["直播/社区", "streaming community"],
            "动漫资源": ["动漫/资源", "anime resource"],
            "动漫教程": ["动漫/教程", "anime tutorial"],
            "国外视频": ["国外视频/工具", "国外视频/社区", "国外视频/教程", "国外视频/开源", "国外视频/服务", "国外视频/资源"],
            "国内视频": ["国内视频/工具", "国内视频/教程", "国内视频/开源", "国内视频/服务", "国内视频/资源", "国内视频/社区"],
            "视频游戏": ["游戏/工具", "游戏/教程", "游戏/服务", "游戏/开源", "游戏/资源", "游戏/社区"],
            "影视资源": ["影视/服务", "影视/生成器", "影视/资源"],
            "音乐工具": ["音乐/工具"],
            "音乐教程": ["音乐/教程"],
            "音乐开源": ["音乐/开源"],
            "音乐服务": ["音乐/服务"],
            "音乐社区": ["音乐/社区"],
            "音乐生成": ["音乐/生成器"]
        }
    },
    # 开发资源类
    "开发资源": {
        "parent": "开发工具",
        "subcats": {
            "平台社区": ["平台/社区"],
            "平台开源": ["平台/开源"],
            "平台生成": ["平台/生成器"],
            "API工具": ["api/工具"],
            "API开源": ["api/开源"],
            "API服务": ["api/服务"],
            "API社区": ["api/社区"],
            "API生成": ["api/生成器"],
            "IDE资源": ["ide/资源"],
            "IDE工具": ["ide/工具"],
            "IDE开源": ["ide/开源"],
            "IDE服务": ["ide/服务"],
            "IDE社区": ["ide/社区"],
            "代码仓库": ["代码仓库/生成器"],
            "学习生成": ["学习/生成器"],
            "学习教程": ["学习/教程"],
            "学习服务": ["学习/服务"],
            "学习资源": ["学习/资源"],
            "文档教程": ["文档/教程"],
            "文档资源": ["文档/资源"],
            "文档开源": ["文档/开源"],
            "文档工具": ["文档/工具"],
            "文档服务": ["文档/服务"],
            "文档社区": ["文档/社区"],
            "部署资源": ["部署/资源"],
            "部署服务": ["部署/服务"]
        }
    },
    # 资源素材类
    "资源素材": {
        "parent": "设计工具",
        "subcats": {
            "图片资源": ["图片/资源"],
            "图片工具": ["图片/工具"],
            "图片社区": ["图片/社区"],
            "模板工具": ["ppt模板/工具"],
            "模板教程": ["ppt模板/教程"],
            "模板开源": ["ppt模板/开源"],
            "模板服务": ["ppt模板/服务"],
            "模板社区": ["ppt模板/社区"],
            "字体工具": ["字体/工具"],
            "字体教程": ["字体/教程"],
            "字体服务": ["字体/服务"],
            "字体社区": ["字体/社区"],
            "字体资源": ["字体/资源"],
            "UI套件": ["ui套件/服务"],
            "资源生成": ["资源/生成器"],
            "资源社区": ["资源/社区"],
            "资源开源": ["资源/开源"],
            "资源教程": ["教程/服务"],
            "平台工具": ["平台/工具"],
            "平台教程": ["平台/教程"],
            "平台资源": ["平台/资源"],
            "平台服务": ["平台/服务"]
        }
    },
    # 阅读写作类
    "阅读写作": {
        "parent": "效率办公",
        "subcats": {
            "网文资源": ["网文/资源"],
            "网文服务": ["网文/服务"],
            "网文社区": ["网文/社区"],
            "博客服务": ["博客/服务"],
            "博客工具": ["博客/工具"],
            "博客教程": ["博客/教程"],
            "创作生成": ["创作/生成器"],
            "创作教程": ["创作/教程"],
            "创作开源": ["创作/开源"],
            "出版工具": ["出版/工具"],
            "出版教程": ["出版/教程"],
            "出版社区": ["出版/社区"],
            "教程工具": ["教程/工具"],
            "教程服务": ["教程/服务"],
            "教程社区": ["教程/社区"],
            "教程生成": ["教程/生成器"],
            "电子书服务": ["电子书/服务"],
            "电子书生成": ["电子书/生成器"],
            "电子书社区": ["电子书/社区"]
        }
    },
    # 学术科研
    "学术科研": {
        "parent": "学术科研",
        "subcats": {
            "数据集资源": ["数据集/资源"],
            "数据集生成": ["数据集/生成器"],
            "数据集教程": ["数据集/教程"],
            "AI学习开源": ["ai学习/开源"],
            "AI学习服务": ["ai学习/服务"],
            "AI学习生成": ["ai学习/生成器"],
            "工具教程": ["工具/教程"],
            "工具社区": ["工具/社区"],
            "教材资源": ["教材/资源"],
            "教材生成": ["教材/生成器"],
            "课程工具": ["课程/工具"],
            "课程生成": ["课程/生成器"],
            "搜索教程": ["搜索/教程"]
        }
    },
    # 创意工具
    "创意工具": {
        "parent": "设计工具",
        "subcats": {
            "UI设计工具": ["ui设计/工具"],
            "UI设计开源": ["ui设计/开源"],
            "UI设计生成": ["ui设计/生成器"],
            "UI设计教程": ["ui设计/教程"],
            "UI设计社区": ["ui设计/社区"],
            "平面设计开源": ["平面设计/开源"],
            "白板教程": ["白板/教程"],
            "白板开源": ["白板/开源"],
            "白板资源": ["白板/资源"],
            "思维导图开源": ["思维导图/开源"],
            "思维导图教程": ["思维导图/教程"],
            "思维导图社区": ["思维导图/社区"],
            "流程图生成": ["流程图/生成器"],
            "流程图社区": ["流程图/社区"],
            "平台教程": ["平台/教程"],
            "平台社区": ["平台/社区"]
        }
    },
    # 视频创作
    "视频创作": {
        "parent": "多媒体",
        "subcats": {
            "剪辑社区": ["剪辑/社区"],
            "剪辑教程": ["剪辑/教程"],
            "录屏资源": ["录屏/资源"],
            "录屏服务": ["录屏/服务"],
            "特效资源": ["特效/资源"],
            "特效教程": ["特效/教程"],
            "特效服务": ["特效/服务"],
            "特效生成": ["特效/生成器"],
            "字幕资源": ["字幕/资源"],
            "字幕教程": ["字幕/教程"],
            "素材资源": ["素材/资源"],
            "素材社区": ["素材/社区"],
            "动画开源": ["动画/开源"],
            "平台开源": ["平台/开源"],
            "平台资源": ["平台/资源"],
            "平台教程": ["平台/教程"],
            "平台服务": ["平台/服务"]
        }
    },
    # 办公效率
    "办公效率": {
        "parent": "办公工具",
        "subcats": {
            "表单社区": ["表单/社区"],
            "协作社区": ["协作/社区"],
            "笔记工具": ["笔记/工具"],
            "笔记开源": ["笔记/开源"],
            "日程生成": ["日程/生成器"],
            "工具教程": ["工具/教程"],
            "工具社区": ["工具/社区"],
            "工具服务": ["工具/服务"]
        }
    }
}

def build_full_mapping():
    """构建完整的raw_cat到新三级的映射表"""
    mapping = {}
    stats = defaultdict(int)

    # 先统计原始分布
    with open(WEBSITES, encoding='utf-8') as f:
        sites = json.load(f)

    for s in sites:
        raw = s.get('_cat', '')
        if raw:
            stats[raw] += 1

    print(f"原始_cat路径数: {len(stats)}")

    # 智能映射
    for raw_cat, count in stats.items():
        parts = raw_cat.split('/')
        first = parts[0]
        second = '/'.join(parts[1:]) if len(parts) > 1 else ''

        assigned = False

        # 1. 检查AI大类（需要智能拆分）
        if first == 'AI智能':
            # AI视频大类特殊处理：需要根据标题关键词拆分
            if raw_cat.startswith('AI智能/AI视频/'):
                assigned = True  # 将在site处理阶段动态分配
                continue
            # 其他AI子类直接映射
            for rule in AI_SPLIT_RULES.values():
                for subcat, patterns in rule["subcats"].items():
                    for pattern in patterns:
                        if pattern in raw_cat:
                            new_cat = f"{rule['parent']}/{subcat}"
                            mapping[raw_cat] = new_cat
                            assigned = True
                            break
                    if assigned:
                        break
                if assigned:
                    break

        # 2. 检查其他大类的固定映射
        if not assigned:
            for main_name, rule in BASE_MAPPINGS.items():
                parent = rule["parent"]
                for subcat_name, patterns in rule["subcats"].items():
                    for pattern in patterns:
                        # pattern可能是部分路径
                        if pattern in raw_cat or raw_cat.endswith(pattern):
                            new_cat = f"{parent}/{subcat_name}"
                            mapping[raw_cat] = new_cat
                            assigned = True
                            break
                    if assigned:
                        break
                if assigned:
                    break

        # 3. 无法映射的归入"其他"
        if not assigned:
            mapping[raw_cat] = "其他/杂项/未分类"

    return mapping

def smart_remap_ai_video(sites, mapping):
    """智能拆分AI视频类站点（2,664个）"""
    print("\n1️⃣  AI视频资源智能拆分...")

    ai_video_sites = [s for s in sites if s.get('_cat', '').startswith('AI智能/AI视频/')]
    other_sites = [s for s in sites if not s.get('_cat', '').startswith('AI智能/AI视频/')]

    print(f"  处理AI视频类站点: {len(ai_video_sites)} 个")

    # ========== AI视频相关关键词（真正的视频生成/编辑/分析工具） ==========
    AI_VIDEO_KEYWORDS = {
        "AI视频生成": [
            "video generation", "text-to-video", "video synthesis", "generate video",
            "video creator", "ai video generator", "video gen",
            "视频生成", "文生视频", "生成视频", "视频创作", "视频制作"
        ],
        "AI视频编辑": [
            "video editing", "video editor", "video effects", "motion graphics",
            "video post-production", "video post",
            "视频编辑", "视频剪辑", "视频特效", "剪辑工具", "视频后期"
        ],
        "AI视频分析": [
            "video analysis", "object detection", "video understanding", "video recognition",
            "visual analysis", "video analytics",
            "视频分析", "视觉分析", "视频识别", "目标检测", "视频理解"
        ],
        "AI视频素材": [
            "stock video", "video footage", "video assets", "video library",
            "视频素材", "视频库", "视频资源", "footage"
        ],
        "AI语音视频": [
            "talking head", "digital human", "avatar", "virtual human",
            "数字人", "虚拟人", "虚拟主播", "数字孪生"
        ],
        "AI视频平台": [
            "video platform", "video hosting", "video streaming", "video service",
            "视频平台", "视频托管", "视频服务", "视频流"
        ]
    }

    # ========== 其他AI子类关键词（用于重新分类非视频站点） ==========
    AI_DEV_KEYWORDS = [
        "model", "training", "deployment", "framework", "pytorch", "tensorflow",
        "llm", "gpt", "transformer", "neural", "machine learning", "deep learning",
        "开发", "训练", "部署", "推理", "模型", "框架", "api", "sdk", "library",
        "机器学习", "深度学习", "神经网络", "代码", "github", "repository",
        "inference", "fine-tuning", "model zoo", "checkpoint", "pretrained"
    ]

    AI_AUDIO_KEYWORDS = [
        "music generation", "text-to-music", "music synthesis", "music composer",
        "speech synthesis", "text-to-speech", "tts", "voice cloning",
        "音乐生成", "语音合成", "音乐创作", "声音克隆", "tts", "音频合成"
    ]

    AI_CHAT_KEYWORDS = [
        "chatbot", "conversation", "assistant", "bot", "customer service",
        "对话", "聊天", "客服", "问答", "qa", "助手"
    ]

    AI_GENERAL_KEYWORDS = [
        "ai tool", "ai platform", "ai service", "人工智能", "智能工具"
    ]

    AI_TUTORIAL_KEYWORDS = [
        "tutorial", "course", "learning", "guide", "lecture", "lesson",
        "教程", "学习", "课程", "指南", "opencourseware"
    ]

    # 统计信息
    counters = defaultdict(int)
    match_details = []  # 记录匹配详情
    unmatched_sites = []  # 记录未匹配站点

    for s in ai_video_sites:
        title = (s.get('title') or '').lower()
        desc = (s.get('description') or '').lower()
        combined = f"{title} {desc}"

        site_id = s.get('title', '')[:50]
        matched = False
        best_subcat = None
        matched_keyword = None

        # Step 1: 尝试匹配AI视频相关子类
        for subcat, keywords in AI_VIDEO_KEYWORDS.items():
            for kw in keywords:
                if kw in combined:
                    best_subcat = subcat
                    matched_keyword = kw
                    matched = True
                    break
            if matched:
                break

        if matched:
            s['category'] = f"AI工具/人工智能/{best_subcat}"
            counters[best_subcat] += 1
            match_details.append({
                'site': site_id,
                'status': 'matched',
                'category': best_subcat,
                'keyword': matched_keyword
            })
            continue

        # Step 2: 尝试匹配其他AI子类（重新分类）
        other_categories = {
            "AI开发": AI_DEV_KEYWORDS,
            "AI音频": AI_AUDIO_KEYWORDS,
            "AI对话": AI_CHAT_KEYWORDS,
            "AI综合": AI_GENERAL_KEYWORDS,
            "AI教程": AI_TUTORIAL_KEYWORDS
        }

        for cat_name, keywords in other_categories.items():
            for kw in keywords:
                if kw in combined:
                    best_subcat = cat_name
                    matched_keyword = kw
                    matched = True
                    break
            if matched:
                break

        if matched:
            s['category'] = f"AI工具/人工智能/{best_subcat}"
            counters[best_subcat] += 1
            match_details.append({
                'site': site_id,
                'status': 'reclassified',
                'category': best_subcat,
                'keyword': matched_keyword
            })
        else:
            # 完全未匹配
            s['category'] = "AI工具/人工智能/AI综合"
            counters["AI综合（默认）"] += 1
            unmatched_sites.append({
                'site': site_id,
                'title': s.get('title', ''),
                'raw_cat': s.get('_cat', ''),
                'combined_text': combined[:200]
            })
            match_details.append({
                'site': site_id,
                'status': 'unmatched',
                'category': 'AI综合（默认）',
                'keyword': None
            })

    # 打印统计
    print("\n  📋 分类统计:")
    for cat, cnt in sorted(counters.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {cnt}")

    # 打印未匹配站点统计
    if unmatched_sites:
        print(f"\n  ⚠️  未匹配站点数: {len(unmatched_sites)}")
        print("  前20个未匹配站点示例:")
        for item in unmatched_sites[:20]:
            print(f"    [{item['raw_cat']}] {item['title']}")

    # 保存详细日志
    log_path = PROJECT / "tasks" / "ai_video_split_log.json"
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "total_sites": len(ai_video_sites),
        "matched_count": len([d for d in match_details if d['status'] != 'unmatched']),
        "unmatched_count": len(unmatched_sites),
        "category_counts": dict(counters),
        "match_details": match_details[:100],  # 保存前100个详情
        "unmatched_sites": unmatched_sites[:50]  # 保存前50个未匹配
    }
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)
    print(f"\n  📝 详细日志已保存: {log_path.name}")

    return ai_video_sites + other_sites

def main():
    print("🤖 V9 完整重映射 - 第二代")
    print("=" * 60)

    # 读取数据
    with open(WEBSITES, encoding='utf-8') as f:
        sites = json.load(f)

    print(f"原始站点: {len(sites)}")

    # Step 1: 拆分AI视频
    sites = smart_remap_ai_video(sites, {})

    # Step 2: 构建完整映射并应用
    mapping = build_full_mapping()
    print(f"\n2️⃣  应用通用映射规则... ({len(mapping)} 个RAW路径已映射)")

    category_counter = defaultdict(int)
    for s in sites:
        raw = s.get('_cat', '')
        if raw and raw in mapping:
            new_cat = mapping[raw]
            if new_cat != "其他/杂项/未分类":
                s['category'] = new_cat
        category_counter[s.get('category', '')] += 1

    # Step 3: 处理剩余"其他"分类的站点（尝试用标题关键词还原）
    print("\n3️⃣  重新处理'其他'分类站点...")
    other_sites = [s for s in sites if s.get('category') == '其他/杂项/未分类']
    other_assigned = 0

    for s in other_sites:
        title = (s.get('title') or '').lower()
        raw = s.get('_cat', '')

        # 基于title的关键词重分类
        new_cat = None
        if any(kw in title for kw in ['video', 'video editing', '剪辑', '特效']):
            new_cat = "多媒体/视频娱乐/视频服务"
        elif any(kw in title for kw in ['music', '音频', 'sound', '语音']):
            new_cat = "多媒体/音频处理/音频服务"
        elif any(kw in title for kw in ['blog', 'writing', '笔记', '出版']):
            new_cat = "阅读写作/综合服务"
        elif any(kw in title for kw in ['research', 'dataset', '科研', '学术']):
            new_cat = "学术科研/数据资源"
        elif any(kw in title for kw in ['design', 'figma', 'icon', 'font', '设计']):
            new_cat = "设计工具/设计创意/设计服务"
        elif any(kw in title for kw in ['collaboration', 'team', '协作', '办公']):
            new_cat = "效率办公/协作服务"

        if new_cat:
            s['category'] = new_cat
            other_assigned += 1

    print(f"  重新分类了 {other_assigned} 个'其他'站点")

    # 重新统计
    category_counter = defaultdict(int)
    for s in sites:
        category_counter[s.get('category', '')] += 1

    print(f"\n📊 重映射后统计:")
    print(f"  总站点: {len(sites)}")
    print(f"  总分类: {len(category_counter)}")
    balanced = {k: v for k, v in category_counter.items() if 10 <= v <= 50}
    over = {k: v for k, v in category_counter.items() if v > 50}
    under = {k: v for k, v in category_counter.items() if v < 10}
    print(f"  已平衡 (10-50): {len(balanced)}")
    print(f"  超容 (>50): {len(over)}")
    print(f"  不足 (<10): {len(under)}")

    print("\n  超容分类:")
    for k, v in sorted(over.items(), key=lambda x: -x[1])[:8]:
        print(f"    ⚠️  {k}: {v}")

    print("\n  不足分类:")
    for k, v in sorted(under.items(), key=lambda x: x[1])[:10]:
        print(f"    ⚠️  {k}: {v}")

    # 保存
    backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = PROJECT / f".backup/websites.json.before_smart_remap.{backup_timestamp}"
    import shutil
    shutil.copy2(WEBSITES, backup_path)
    print(f"\n✅ 备份: {backup_path.name}")

    temp_path = WEBSITES.with_suffix('.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(sites, f, ensure_ascii=False, indent=2)
    temp_path.replace(WEBSITES)

    stats = {
        "timestamp": datetime.now().isoformat(),
        "total_sites": len(sites),
        "total_categories": len(category_counter),
        "balanced": len(balanced),
        "overfilled": len(over),
        "underfilled": len(under),
        "category_counts": dict(category_counter)
    }

    with open(PROJECT / "tasks" / "smart_remap_stats.json", 'w') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print("✅ 统计保存完成")
    print("\n✅ 重映射完成！")
    print(f"\n当前覆盖率: {len(balanced)} 个分类达标，仍需处理 {len(over)} 个超大类和 {len(under)} 个过小类")

if __name__ == "__main__":
    main()
