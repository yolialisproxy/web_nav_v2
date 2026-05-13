#!/usr/bin/env python3
"""
Tag extraction pipeline - 从站点描述中提取关键词并生成标签
输出: data/sites_with_tags.json + data/tag_index.json
"""
import json, re, os
from collections import defaultdict, Counter

INPUT = 'data/websites.json'
OUTPUT_SITES = 'data/sites_with_tags.json'
OUTPUT_TAGS = 'data/tag_index.json'

# 中文停用词
STOPWORDS = {
    '的','了','和','是','在','有','我','他','她','它','们','这','那','一','个','也','中',
    '月','日','年','为','到','以','与','及','而','但','或','则','就','都','可','能','得',
    '于','由','向','在','上','下','里','外','前','后','先','后','来','去','用','把','被',
    '让','助','帮','请','要','想','说','话','做','看','听','走','进','出','起','落','开',
    '关','送','收','给','与','合','分','加','减','乘','除','等','应','该','必','定','决',
    '将','已','经','过','才','还','只','而','但','或','因','所','如','若','依','据','根',
    # 英文停用词
    'the','and','for','of','in','to','with','a','an','is','are','was','were','be','been',
    'being','by','on','at','from','as','it','its','that','this','these','those','you','your',
    'we','our','they','them','their','he','him','his','she','her','hers','but','or','if','then',
    'can','could','will','would','shall','should','may','might','must','here','there','where',
    'when','why','how','what','which','who','whom','whose','all','each','every','both','few',
    'some','most','much','many','no','nor','not','only','own','same','so','than','too','very',
    # 领域通用但过滤掉的词
    '网站','工具','软件','在线','免费','平台','服务','系统','官网','官方','关于','帮助','联系',
    '登录','注册','隐私','条款','使用','我们','您','用户','支持','反馈','提交','查看','更多',
}

# 领域词汇权重 Boost
DOMAIN_BOOST = {
    'ai': 1.5, '人工智能': 1.5, '机器学习': 1.4, '深度学习': 1.4,
    '开发': 1.3, '编程': 1.3, '代码': 1.3, 'developer': 1.3,
    '设计': 1.2, 'ui': 1.2, 'ux': 1.2, 'graphic': 1.2,
    '效率': 1.2, '办公': 1.2, 'productivity': 1.2,
    '平台': 0.3, '网站': 0.3, '在线': 0.3, '系统': 0.5,
}

def extract_keywords(text):
    """从文本中提取关键词"""
    if not text:
        return []

    text = text.lower()

    # 提取特殊词汇：英文单词、技术术语、产品名、工具名
    patterns = [
        (r'[A-Za-z][A-Za-z0-9\-_]+', 0.8),     # 英文单词/品牌
        (r'[^\x00-\x7F]{2,6}', 1.0),           # 中文词汇
        (r'[\u4e00-\u9fa5]{2,4}', 1.0),        # 纯中文字符
        (r'\d+\.?\d*\s*[kmg]?b?', 0.1),        # 版本号 - 权重低
    ]

    keywords = []
    for pattern, base_score in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) < 2: continue
            # 过滤常见停用词
            if match.lower() in STOPWORDS:
                continue
            if len(match) == 1: continue
            # 过滤纯数字
            if match.isdigit(): continue
            # 过滤纯标点
            if all(c in '.,;:!?()[]{}<>' for c in match): continue
            keywords.append(match)

    return keywords

def assign_tags(site):
    """为单个站点分配标签"""
    tags = []

    # 从name提取品牌名/产品名
    name = site.get('name', '')
    if name:
        # 品牌特征：2-4个字符，可能是英文或中文
        brand_match = re.match(r'^[A-Za-z][A-Za-z0-9\-\s]{1,20}$', name)
        domain_match = re.match(r'^[^\x00-\x7F]{2,6}$', name)
        short_match = len(name) <= 4 and not name.isdigit()

        if brand_match or domain_match or short_match:
            # 这个品牌名可能就是工具名
            tags.append(name)

    # 从description提取
    desc = site.get('description', '')
    category = site.get('category', '')

    # 添加类别作为标签
    parts = category.split('/')
    for part in parts:
        if part and part not in ('工具', '平台', '资源', '站', '类'):
            tags.append(part)

    # 提取关键词
    keywords = extract_keywords(desc)
    tags.extend(keywords)

    # 去重并排序
    unique_tags = []
    seen = set()
    for tag in tags:
        if tag and tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    return unique_tags[:5]  # 最多5个标签

def main():
    sites = json.load(open(INPUT, encoding='utf-8'))

    tag_to_sites = defaultdict(list)
    site_to_tags = {}

    for s in sites:
        tags = assign_tags(s)
        site_to_tags[s['name']] = tags
        for tag in tags:
            tag_to_sites[tag].append(s['name'])

    # 保存站点数据 (追加tags字段)
    enriched = []
    for s in sites:
        s_with_tags = dict(s)
        s_with_tags['tags'] = site_to_tags.get(s['name'], [])
        enriched.append(s_with_tags)

    # 保存为可编译输出 (压缩)
    with open(OUTPUT_SITES, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    # 生成标签索引 (精简版，用于快速查询)
    tag_index = []
    for tag, site_names in sorted(tag_to_sites.items()):
        tag_index.append({
            'tag': tag,
            'count': len(site_names),
            'sites': site_names[:10]  # 仅保存前10个避免过大
        })

    # 按使用频率排序标签
    tag_index.sort(key=lambda x: -x['count'])

    with open(OUTPUT_TAGS, 'w', encoding='utf-8') as f:
        json.dump(tag_index, f, ensure_ascii=False, indent=2)

    print(f'✅ 标签提取完成: {len(sites)} sites → {len(tag_index)} unique tags')
    print(f'📊 Top 10 tags:')
    for t in tag_index[:10]:
        print(f"  {t['tag']} ({t['count']} sites)")
    print(f'\nOutput: {OUTPUT_SITES}, {OUTPUT_TAGS}')

if __name__ == '__main__':
    main()