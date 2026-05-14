#!/usr/bin/env python3
"""
批量优化 sites.json 中的 description，增强SEO关键词覆盖
"""
import json, os

repo = "/home/yoli/GitHub/web_nav_v2"
with open(os.path.join(repo, "data/websites.json")) as f:
    sites = json.load(f)

# 主分类关键词映射
cat_keywords = {
    "AI工具": ["AI", "人工智能", "AI工具", "智能助手"],
    "开发工具": ["开发工具", "编程", "开发者", "代码", "开源"],
    "设计工具": ["设计工具", "UI设计", "设计资源", "创意设计"],
    "效率办公": ["效率办公", "生产力", "办公工具", "工作效率"],
    "学术科研": ["学术科研", "学术", "科研", "论文", "研究"],
    "多媒体": ["多媒体", "视频", "音频", "图片", "媒体"],
}

# 副分类关键词
sub_keywords = {
    "聊天对话": ["聊天机器人", "对话AI", "智能对话"],
    "写作助手": ["AI写作", "写作助手", "内容生成", "文本生成"],
    "代码助手": ["AI编程", "代码助手", "编程辅助", "智能编码"],
    "图像处理": ["AI图像", "图像生成", "图片处理", "图像编辑"],
    "视频生成": ["AI视频", "视频生成", "视频制作"],
    "音频生成": ["AI音频", "语音合成", "音频生成", "文字转语音"],
    "搜索引擎": ["AI搜索", "智能搜索", "搜索引擎"],
    "综合平台": ["AI平台", "一站式", "全能AI"],
    "摘要生成": ["文本摘要", "内容摘要", "智能摘要"],
    "知识图谱": ["知识图谱", "知识管理", "知识库"],
    "语音识别": ["语音识别", "语音转文字", "语音输入"],
}

updated = 0
skipped = 0

for site in sites:
    desc = site.get("description", "").strip()
    cat = site.get("category", "")
    
    if len(desc) < 20:
        # 描述太短，需要扩充
        first_cat = cat.split("/")[0].strip() if "/" in cat else cat.strip()
        last_part = cat.split("/")[-1].strip() if "/" in cat else ""
        
        keywords = []
        if first_cat in cat_keywords:
            keywords.extend(cat_keywords[first_cat])
        if last_part in sub_keywords:
            keywords.extend(sub_keywords[last_part])
        
        if keywords:
            kw_str = "、".join(keywords[:3])
            name = site.get("name", "")
            site["description"] = f"{name}，{kw_str}相关的优质工具/资源。{desc}" if desc else f"{name}，{kw_str}相关的优质工具/资源。"
            updated += 1
        else:
            skipped += 1
    elif len(desc) >= 20 and len(desc) <= 30:
        # 描述够长但可能缺少关键词，尝试在开头添加分类关键词
        first_cat = cat.split("/")[0].strip() if "/" in cat else cat.strip()
        if first_cat in cat_keywords and not any(kw in desc for kw in cat_keywords[first_cat][:2]):
            name = site.get("name", "")
            site["description"] = f"{name}，优质{first_cat}工具。" + desc
            updated += 1
    else:
        # 描述已经足够长
        pass

    # 确保描述 >= 15 字符
    if len(site.get("description", "")) < 15:
        site["description"] = site.get("name", "") + " - 优质开发者资源"
        updated += 1

print(f"更新: {updated} | 跳过: {skipped} | 总数: {len(sites)}")

# 统计最终描述长度分布
lengths = [len(s.get("description","")) for s in sites]
print(f"描述长度: 最小={min(lengths)} 最大={max(lengths)} 平均={sum(lengths)//len(lengths)}")
print(f"≥15字符: {sum(1 for l in lengths if l >= 15)}/{len(lengths)}")
print(f"≥30字符: {sum(1 for l in lengths if l >= 30)}/{len(lengths)}")

with open(os.path.join(repo, "data/websites.json"), "w", encoding="utf-8") as f:
    json.dump(sites, f, ensure_ascii=False, indent=2)

print("\n✅ 已保存 data/websites.json")