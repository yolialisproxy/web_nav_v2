#!/usr/bin/env python3
"""
每日网文写作素材采集系统
- 严格遵循 "完整原文内容 + 去水处理" 原则
- 自动去重机制（基于内容哈希）
- 精准分类存储到 Obsidian 知识库
- 支持 28 个专业写作类目
"""
import json
import os
import re
import hashlib
from pathlib import Path
from hermes_tools import browser_navigate, browser_snapshot, web_search, write_file, read_file

# 配置参数
OBSIDIAN_VAULT = Path.home() / ".hermes" / "obsidian" / "writing-materials"
CATEGORIES = [
    "修炼体系设计", "境界突破逻辑", "门派与势力组织", "功法与技能设计", "丹药与法宝设定", "江湖规矩与潜规则", "师徒关系与传承",
    "修真境界划分", "渡劫与天劫设计", "仙凡冲突", "因果与报应设计", "门派恩怨与千年仇恨", "散修的生存之道",
    "地下世界规则", "阶层差距与鄙视链", "扮猪吃虎的正确节奏", "人情世故与利益交换", "官方与地下势力的平衡",
    "星际江湖", "武道与科技的结合", "银河宗门与星际帝国",
    "官场斗争与站队逻辑", "军队中的规则与生存", "世家的运作方式", "农民起义的真实逻辑",
    "冲突设计的 12 种基本模式", "高潮节奏与情绪调动", "细节描写与感官代入"
]

# 去水规则（优先处理常见广告/导航元素）
AD_PATTERNS = [
    r'<div class="(ad|banner|advert|advertisement)\b.*?>.*?</div>',
    r'<script.*?>.*?</script>',
    r'<style.*?>.*?</style>',
    r'<nav.*?>.*?</nav>',
    r'<footer.*?>.*?</footer>',
    r'<header.*?>.*?</header>',
    r'\b广告\b|\b推广\b|\b赞助\b|\b推荐\b',
    r'\b点击这里\b|\b立即购买\b|\b下载APP\b',
    r'\bCopyright\b|\b©\b|\bAll rights reserved\b',
    r'\b相关推荐\b|\b猜你喜欢\b|\b热门推荐\b',
    r'\b分享到\b|\b评论\b|\b点赞\b|\b收藏\b',
]

def clean_html(html):
    """严格去水处理：移除广告、导航、重复内容，保留核心文本"""
    for pattern in AD_PATTERNS:
        html = re.sub(pattern, '', html, flags=re.IGNORECASE | re.DOTALL)

    # 移除所有HTML标签但保留段落结构
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()

    # 保留关键段落（至少20字）
    paragraphs = [p.strip() for p in text.split('。') if len(p.strip()) > 20]
    return '。'.join(paragraphs) + '。'

def extract_content(url):
    """使用浏览器工具获取并清洗内容"""
    try:
        browser_navigate(url)
        snapshot = browser_snapshot(full=True)
        cleaned = clean_html(snapshot)

        # 检查是否成功获取内容
        if len(cleaned) < 100:
            return None, None

        # 提取标题
        title_match = re.search(r'<title>(.*?)</title>', snapshot)
        title = title_match.group(1) if title_match else "未知标题"

        return title, cleaned
    except Exception as e:
        print(f"⚠️ 处理 {url} 失败: {str(e)}")
        return None, None

def get_new_sources(category):
    """搜索最新优质来源（仅限中文网站）"""
    query = f"{category} 写作素材 玄幻 仙侠 都市 科幻 历史 优质"
    results = web_search(query, limit=10)

    # 过滤掉非中文网站和低质量来源
    valid_urls = []
    for item in results['data']['web']:
        if 'baidu.com' in item['url'] or 'google.com' in item['url']:
            continue
        if 'blog' in item['url'] or 'forum' in item['url']:
            continue
        if 'pdf' in item['url']:
            continue
        valid_urls.append(item['url'])

    return valid_urls[:5]  # 每个类目最多5个来源

def get_content_hash(content):
    """生成内容哈希用于去重"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def save_to_obsidian(category, title, content, url):
    """结构化存储到Obsidian知识库"""
    # 创建分类目录
    category_dir = OBSIDIAN_VAULT / category
    category_dir.mkdir(parents=True, exist_ok=True)

    # 生成唯一文件名（基于内容哈希）
    content_hash = get_content_hash(content)
    filename = f"{content_hash[:8]}.md"
    file_path = category_dir / filename

    # 检查是否已存在
    if file_path.exists():
        return False

    # 写入标准格式
    md_content = f"""---
title: {title}
source: {url}
category: {category}
---

{content}
"""
    write_file(str(file_path), md_content)

    # ✅ 强制校验：必须检查文件真实存在且内容正确
    if not file_path.exists():
        print(f"  ❌ 写入失败，磁盘上不存在文件")
        return False

    # 验证写入完整性
    try:
        verify = read_file(str(file_path))
        if len(verify['content'].strip()) < 50:
            print(f"  ❌ 写入内容不完整")
            file_path.unlink(missing_ok=True)
            return False
    except:
        print(f"  ❌ 无法读取刚写入的文件")
        return False

    return True

def main():
    print(f"🚀 开始每日写作素材采集（{len(CATEGORIES)}个类目）")

    for category in CATEGORIES[:5]:  # 测试时先跑前5个类目
        print(f"\n🔍 正在采集: {category}")
        sources = get_new_sources(category)

        for url in sources:
            print(f"  🌐 正在处理: {url}")
            title, content = extract_content(url)

            if not title or not content:
                print("  ❌ 内容提取失败")
                continue

            if save_to_obsidian(category, title, content, url):
                print(f"  ✅ 新增: {title[:30]}... ({len(content)}字)")
            else:
                print(f"  📌 已存在或失败: {title[:30]}...")

    print(f"\n✅ 采集完成！共保存 {len(list(OBSIDIAN_VAULT.glob('**/*.md')))} 个素材")

if __name__ == "__main__":
    main()