#!/usr/bin/env python3
"""
GitHub类站点智能分类脚本
基于网站名称、URL、描述等特征，自动将206个GitHub类站点分配到16个子类
"""

import json
import re
from pathlib import Path

# 加载数据
WEBSITES_PATH = Path('/home/yoli/GitHub/web_nav_v2/websites.json')
OUTPUT_PATH = Path('/home/yoli/GitHub/web_nav_v2/plans/github_classification_result.json')

def load_websites():
    with open(WEBSITES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def classify_github_site(site):
    """
    对单个GitHub类站点进行分类
    返回子类ID (1-16)
    """
    name = (site.get('name') or '').lower()
    url = (site.get('url') or '').lower()
    desc = (site.get('description') or '').lower()
    text = f"{name} {url} {desc}"

    # 规则1: GitHub本体服务
    if any(keyword in text for keyword in [
        'github.com/blog', 'github.blog', 'github.com/security', 'securitylab',
        'github.com/support', 'support.github', 'github.com/education',
        'github.com/training', 'github.com/enterprise', 'changelog',
        'github.com/features', 'github.com/pricing', 'github.com/customer-story',
        'github.com/safety', 'github.com/contact', 'github.com/about'
    ]):
        return 1  # GitHub本体服务

    # 规则2: GitHub客户端工具
    if any(keyword in text for keyword in [
        'desktop.github', 'github.com/desktop', 'cli.github', 'cli.github.com',
        'github.com/mobile', 'github.com/copilot', 'copilot.github'
    ]):
        return 2  # GitHub客户端工具

    # 规则3: GitHub Actions与CI/CD
    if any(keyword in text for keyword in [
        'github.com/features/actions', 'actions.github', 'github actions',
        'ci/cd', 'continuous integration', 'workflow', 'pipeline'
    ]):
        return 3

    # 规则4: GitHub Packages
    if any(keyword in text for keyword in [
        'packages.github', 'github.com/packages', 'npm.pkg.github',
        'container registry', 'docker.pkg.github'
    ]):
        return 4

    # 规则5: GitHub Pages
    if any(keyword in text for keyword in [
        'pages.github', 'github.com/pages', 'github.io'
    ]):
        return 5

    # 规则6: 开源项目索引 (Awesome列表)
    if any(keyword in text for keyword in [
        'awesome-', 'awesome selfhosted', 'awesome-selfhosted',
        'awesome-list', 'awesome collection', 'list of '
    ]) or (name.startswith('awesome') or 'awesome' in name.split()[:2]):
        return 6

    # 规则7: 代码托管替代平台
    if any(keyword in text for keyword in [
        'gitlab', 'gitee', 'bitbucket', 'sourceforge', 'codeberg',
        'gitlab.com', 'gitee.com', 'bitbucket.org', 'sourceforge.net'
    ]):
        return 7

    # 规则8: GitHub镜像/缓存
    if any(keyword in text for keyword in [
        'ghproxy', 'gitclone', 'mirror', 'github proxy', 'github加速',
        'fastgit', 'kgithub', 'gh.api', 'gharchive', 'gh go github'
    ]) or 'github.com/assets/' in url or 'github.githubassets.com' in url:
        return 8

    # 规则9: IDE集成
    if any(keyword in text for keyword in [
        'visual studio code', 'vscode', 'jetbrains', 'intellij', 'pycharm',
        'vscode extension', 'github plugin', 'github extension'
    ]):
        return 9

    # 规则10: 开发工具集成 (各类框架、工具的GitHub集成)
    if any(keyword in text for keyword in [
        'github integration', 'github app', 'github for ', 'github connect'
    ]):
        return 10

    # 规则11: 教程与学习
    if any(keyword in text for keyword in [
        'tutorial', 'guide', 'learn github', 'github course', 'github docs',
        'docs.github', 'github.com/explore', 'github.com/training'
    ]):
        return 11

    # 规则12: 开发者社区
    if any(keyword in text for keyword in [
        'community.github', 'github.community', 'github forum',
        'discussions.github', 'github.com/discussions'
    ]):
        return 12

    # 规则13: GitHub API服务
    if any(keyword in text for keyword in [
        'api.github', 'github api', 'github rest api', 'graphql.github'
    ]) and 'copilot' not in text:
        return 13

    # 规则14: 知名开源项目 (需要更智能的判断)
    # 检查是否为特定知名项目
    well_known_orgs = ['tensorflow', 'microsoft', 'google', 'facebook', 'apple',
                      'apache', 'linux', 'kubernetes', 'docker', 'nodejs', 'react',
                      'vuejs', 'python', 'golang', 'rust-lang', 'rust-lang/rust']
    if any(org in url or org in name for org in well_known_orgs):
        return 14

    # 规则15: 资源素材 (图标、主题、模板等)
    if any(keyword in text for keyword in [
        'theme', 'template', 'icon', 'font', 'resource', 'asset', '素材',
        'github theme', 'github template', 'github icon'
    ]):
        return 15

    # 默认规则16: 其他GitHub相关
    return 16


def main():
    print("开始GitHub类站点分类...")
    websites = load_websites()

    # 筛选GitHub类站点
    github_sites = [w for w in websites if w.get('category') == '开发工具/平台开源/GitHub']
    print(f"GitHub类站点总数: {len(github_sites)}")

    # 分类统计
    category_counts = {i: 0 for i in range(1, 17)}
    classified = []

    for site in github_sites:
        cat_id = classify_github_site(site)
        category_counts[cat_id] += 1
        classified.append({
            'name': site.get('name', ''),
            'url': site.get('url', ''),
            'description': site.get('description', ''),
            'assigned_subcategory_id': cat_id
        })

    # 显示分布
    subcat_names = [
        "GitHub本体服务", "GitHub客户端工具", "GitHub Actions与CI/CD",
        "GitHub Packages与容器", "GitHub Pages", "开源项目索引Awesome",
        "代码托管替代平台", "GitHub镜像/缓存服务", "IDE与编辑器GitHub集成",
        "开发工具GitHub集成", "GitHub教程与学习", "GitHub开发者社区",
        "GitHub API生态服务", "知名开源组织项目", "GitHub资源与素材", "其他GitHub相关"
    ]

    print("\n分类结果分布:")
    print("-" * 60)
    for i in range(1, 17):
        print(f"  [{i:2d}] {subcat_names[i-1]}: {category_counts[i]} 个站点")

    print(f"\n总计: {sum(category_counts.values())} 个站点")

    # 保存结果
    result = {
        "metadata": {
            "total_sites": len(github_sites),
            "classification_date": "2026-04-24",
            "rule_based": True,
            "note": "基于规则的自动分类，需要人工审核和调整"
        },
        "subcategories": [
            {
                "id": i,
                "name": subcat_names[i-1],
                "estimated_count": category_counts[i],
                "sites": [s for s in classified if s['assigned_subcategory_id'] == i]
            }
            for i in range(1, 17)
        ],
        "all_classified_sites": classified
    }

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 分类结果已保存到: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
