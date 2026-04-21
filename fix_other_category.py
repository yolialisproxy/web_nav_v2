#!/usr/bin/env python3
import json
import sys
from collections import defaultdict

def main():
    # Load website data
    with open('data/websites.json', 'r', encoding='utf-8') as f:
        sites = json.load(f)

    # Count before
    before = sum(1 for s in sites if s.get('category') == '其他')
    print(f"Found {before} sites in '其他' category")

    # Classification rules
    category_map = {
        # AI/ML Frameworks & Models
        'framework': [
            'torch', 'tensorflow', 'keras', 'pytorch', 'mxnet', 'cntk', 'cudnn',
            'singa', 'ml', 'machine learning', 'deep learning', 'neural network',
            'llm', '大模型', '模型', '推理', 'inference', 'bentoml', 'mlem', 'cml'
        ],
        # DevOps & Infrastructure
        'devops': [
            'kubernetes', 'k8s', 'cloud', 'deploy', 'container', 'docker', 'infra',
            'server', 'host', 'cache', 'lancache', 'railway', 'observability',
            'monitoring', 'logs', 'metrics', 'search', 'database', 'storage',
            'zincsearch', 'tidesdb', 'ckan', 'git', 'gitea', 'gogs'
        ],
        # Development Tools & Libraries
        '开发工具': [
            'compiler', 'ide', 'editor', 'library', 'sdk', 'api', 'orm', 'odb',
            'programming', 'c++', 'cpp', 'lua', 'luau', 'programiz', 'dotclear',
            'cml.dev', 'error tracking', 'glitchtip', 'bifröst', 'ssh'
        ],
        # Productivity & Business Tools
        '办公工具': [
            'password', 'manager', 'passbolt', 'ticket', 'helpdesk', 'zammad',
            'collaboration', 'board', 'digiboard', 'wiki', 'feather wiki', 'slides',
            'openslides', 'inventory', 'inventree', 'finance', 'money', 'monetr',
            'lms', 'learning', 'openolat', 'cms', 'silverstripe', 'reservation', 'alf.io'
        ],
        # Media & Reading Tools
        '媒体工具': [
            'read later', 'bookmark', 'readeck', 'audiobook', 'podcast', 'audiobookshelf',
            'file storage', 'cloud storage', 'chibisafe', 'cannery', 'file upload'
        ],
        # Learning & Resources
        '学习资源': [
            'tutorial', 'course', 'blog', 'article', 'symposium', 'c++ stories',
            'andreasfertig', 'fast.ai', 'documentation', 'docs', 'rfc'
        ],
        # Community & Communication
        '通讯社区': [
            'chat', 'messenger', 'tinode', 'im', 'forum', 'discussion', 'golangbridge',
            'indieweb', 'social', 'element', 'wechat'
        ]
    }

    # Track assignments
    assigned = defaultdict(int)
    unassigned = []

    # Process each site in Other category
    for site in sites:
        if site.get('category') != '其他':
            continue

        text = ' '.join([
            site.get('title', ''),
            site.get('description', ''),
            site.get('_cat', ''),
            site.get('url', '')
        ]).lower()

        # Match rules
        new_cat = None
        for cat, keywords in category_map.items():
            if any(k.lower() in text for k in keywords):
                new_cat = cat
                break

        if new_cat:
            site['category'] = new_cat
            assigned[new_cat] += 1
        else:
            unassigned.append(site.get('id', 'unknown'))

    # Handle remaining unassigned with proper categorization
    for site in sites:
        if site.get('category') == '其他':
            if 'ai' in site.get('_cat', '') or 'AI' in site.get('_cat', ''):
                site['category'] = 'AI工具'
                assigned['AI工具'] += 1
            elif '开发' in site.get('_cat', ''):
                site['category'] = '代码工具'
                assigned['代码工具'] += 1
            else:
                site['category'] = '实用工具'
                assigned['实用工具'] += 1

    # Verify zero remaining
    after = sum(1 for s in sites if s.get('category') == '其他')

    # Save updated file
    with open('data/websites.json', 'w', encoding='utf-8') as f:
        json.dump(sites, f, indent=2, ensure_ascii=False)

    # Summary report
    print("\n✅ Classification complete")
    print(f"Sites reclassified: {before}")
    print(f"Remaining in '其他': {after}")
    print("\nNew category distribution:")
    for cat, count in sorted(assigned.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} sites")
    print(f"\nTotal categories added: {len([k for k in assigned if k not in ['AI工具','代码工具','实用工具']])}")

if __name__ == "__main__":
    main()
