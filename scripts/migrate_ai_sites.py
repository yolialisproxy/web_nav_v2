#!/usr/bin/env python3
"""
AI Category Migration Execution - V15 Critical Fix

Migrates all 329 mis-categorized AI sites to correct categories.
Resolves overfill and fills underfilled categories simultaneously.

WARNING: This MODIFIES data/websites.json in-place.
Backup will be created automatically before changes.
"""

import json
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = Path("/home/yoli/GitHub/web_nav_v2")
WEBSITES_PATH = PROJECT_ROOT / "data" / "websites.json"
BACKUP_DIR = PROJECT_ROOT / "backups"
REPORTS_DIR = PROJECT_ROOT / "reports"

def load_websites():
    with open(WEBSITES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_websites(data):
    with open(WEBSITES_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"websites.json.v15_ai_migration_pre_{timestamp}"
    shutil.copy2(WEBSITES_PATH, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

#Migration rules: (pattern, target_category, reason)
# Target categories MUST exist in current schema
MIGRATION_RULES = [
    # 1. University / Course Materials
    (r'(mit\.edu|stanford\.edu|berkeley\.edu|harvard\.edu|cmu\.edu|'
     r'cornell\.edu|nyu\.edu|ox\.ac\.uk|cam\.ac\.uk|ed\.ac\.uk|'
     r'ethz\.ch|epfl\.ch|tum\.de|kth\.se|uu\.nl|dtu\.dk)',
     '学术科研/教材',
     'University course material'),

    # 2. YouTube video tutorials
    (r'youtube\.com/watch|youtu\.be|youtube-nocookie',
     '多媒体/视频娱乐/教程',
     'YouTube video'),

    # 3. Wikipedia / Wikis
    (r'wikipedia\.org|wikimedia\.org|wiktionary\.org|wikibooks\.org',
     '其他/杂项/搜索引擎',
     'Wikipedia or wiki'),

    # 4. Archive / Historical backups
    (r'archive\.org|web\.archive\.org|wayback\.machine',
     '系统工具/备份工具',
     'Archive.org backup'),

    # 5. GitHub raw assets - keep in GitHub but mark as resource
    (r'github\.com/_private|raw\.githubusercontent\.com|githubassets\.com',
     '开发工具/平台开源/GitHub',
     'GitHub asset (keep)'),

    # 6. CI/CD platforms
    (r'woodpecker-ci\.org|gitlab\.com/(ci|pipelines)|'
     r'jenkins\.io|jenkins\.org|circleci\.com|'
     r'travis-ci\.org|drone\.io|cloudbuild\.google\.com',
     '开发工具/CI/CD服务',
     'CI/CD platform'),

    # 7. Self-hosted directories
    (r'awesome-selfhosted\.net|selfhosted\.',
     '系统工具/实用工具/其他工具',
     'Self-hosted directory'),

    # 8. Cloud providers
    (r'aws\.amazon\.com|googlecloud\.com|cloud\.google\.com|'
     r'azure\.com|oraclecloud\.com|digitalocean\.com|'
     r'linode\.com|vultr\.com|hetzner\.com|ibm\.cloud',
     '开发工具/云开发平台',
     'Cloud provider'),

    # 9. Databases / Storage
    (r'mongodb\.com|postgresql\.org|mysql\.com|'
     r'redis\.io|etcd\.io|cockroachdb\.com|'
     r'mariadb\.org|elastic\.co|influxdata\.com',
     '开发工具/数据库',
     'Database / storage'),

    # 10. Monitoring / Observability
    (r'sensu\.io|prometheus\.io|grafana\.com|'
     r'datadog\.com|newrelic\.com|dynatrace\.com|'
     r'honeycomb\.io|splunk\.com|logz\.io',
     '开发工具/监控告警',
     'Monitoring / observability'),

    # 11. Identity / Auth
    (r'pomerium\.io|goauthentik\.io|keycloak\.org|'
     r'okta\.com|auth0\.com|onelogin\.com|'
     r'fusionauth\.io| circumvent\.org',
     '系统工具/网络安全',
     'Identity / auth'),

    # 12. Documentation / Help platforms
    (r'readthedocs\.io|readthedocs\.org|'
     r'gitbook\.com|docusaurus\.io|docsify\.io|'
     r'mkdocs\.org|antora\.org|'
     r'stackoverflow\.com|serverfault\.com|superuser\.com',
     '开发工具/文档资源',
     'Docs / Q&A platform'),

    # 13. Programming learning / Practice
    (r'roadmap\.sh|freecodecamp\.org|theodinproject\.com|'
     r'codewars\.com|leetcode\.com|hackerrank\.com|'
     r' Exercism\.org|codeproject\.com|tutorialspoint\.com',
     '开发工具/学习生成/在线课程',
     'Coding practice / tutorials'),

    # 14. Package managers / Registries
    (r'npmjs\.com|pypi\.org|crates\.io|rubygems\.org|'
     r'packagist\.org|nuget\.org|clojars\.org|'
     r'maven\.central|nixos\.org/channels',
     '开发工具/包管理',
     'Package registry'),

    # 15. Container / Virtualization
    (r'docker\.com|docker\.io|kubernetes\.io|k8s\.io|'
     r'podman\.io|lxc\.org|vagrantup\.com|'
     r'hashicorp\.com/\(product/virtualbox\)',
     '系统工具/容器管理',
     'Container / VM'),

    # 16. Networking / DNS
    (r'coredns\.io|bind\.isc\.org|nginx\.org|nginx\.com|'
     r'apache\.org|traefik\.io|envoy\.proxy|'
     r'istio\.io|linkerd\.io|konghq\.com',
     '系统工具/网络工具',
     'Networking / proxy'),

    # 17. Serialization / Data formats
    (r'msgpack\.org|protobuf\.dev|yaml\.org|json\.org|'
     r'toml\.io|xml\.com|avro\.apache\.org',
     '开发工具/库',
     'Data format / serialization'),

    # 18. Flashcards / Spaced repetition
    (r'ankiweb\.net|ankisrs\.net|quizlet\.com|'
     r'brainscape\.com|mnemosyne\.pro|supermemo\.com',
     '效率办公/笔记',
     'Flashcards / SRS'),

    # 19. Interview preparation
    (r'interviewing\.io|pramp\.com|leetcode\.com/interview|'
     r'codewars\.com(/kata)?|hackerrank\.com/domains',
     '效率办公/面试技巧',
     'Interview prep'),

    # 20. Diagramming / Whiteboard
    (r'kroki\.io|excalidraw\.com|draw\.io|diagrams\.net|'
     r'lucidchart\.com|whimsical\.com|miro\.com|'
     r'figma\.com|figjam\.com',
     '设计工具/白板资源',
     'Diagram / whiteboard'),

    # 21. Text / Code formatting
    (r'prettier\.io|eslint\.org|black\.dev|'
     r'shellcheck\.net|hadolint\.com|yamllint\.com',
     '开发工具/代码生成',
     'Code formatting / linting'),

    # 22. API / Network debugging
    (r'postman\.com|insomnia\.rest|paw\.cloud|'
     r'httpie\.io|curl\.haxx\.se|wget\.hometools\.org',
     '开发工具/API构建',
     'API / HTTP client'),

    # 23. Terminal / CLI utilities
    (r'htop\.dev|btop\.dev|bottom\.rs|'
     r'cli\.tool|command-line\.com|',
     '系统工具/实用工具/CLI',
     'CLI / terminal tool'),

    # 24. Regex / Text tools
    (r'regex101\.com|regexr\.com|regExr\.com|'
     r'opensource regex|regexpal\.com',
     '其他/杂项/正则测试',
     'Regex tester'),

    # 25. URL / Link tools
    (r'bit\.ly|tinyurl\.com|t\.co|goo\.gl|x\.com',
     '其他/杂项/短链接',
     'URL shortener'),

    # 26. Translation tools
    (r'deep(l|.com)|translate\.google\.com|'
     r'bing\.com/translator|microsofttranslator\.com',
     '其他/杂项/词典翻译',
     'Translation service'),

    # Default fallback to 其他/杂项/[smart-name]
]

FALLBACK_SUBCATEGORIES = [
    '其他/杂项/在线工具',
    '其他/杂项/在线计算',
    '其他/杂项/公共数据',
    '其他/杂项/平台市场',
    '其他/杂项/在线测试',
]

def classify_ai_site(site):
    """Find the best target category for a mis-categorized AI site"""
    url = site.get('url', '').lower()
    name = site.get('name', '').lower()
    combined = f"{url} {name}"

    for pattern, target_cat, reason in MIGRATION_RULES:
        if re.search(pattern, combined, re.IGNORECASE):
            return target_cat, reason

    # Fallback: use 其他/杂项 with a sub-category determined by keywords
    fallback_keywords = {
        r'github': '平台市场',
        r'git': '平台市场',
        r'.*api.*': '在线工具',
        r'.*tool.*': '在线工具',
        r'.*service.*': '平台市场',
        r'.*dev.*': '在线工具',
        r'.*code.*': '在线工具',
    }

    for pattern, subcat in fallback_keywords.items():
        if re.search(pattern, combined, re.IGNORECASE):
            return f"其他/杂项/{subcat}", f"fallback-{subcat}"

    # Ultimate fallback
    return '其他/杂项/在线工具', 'fallback-default'

def main():
    print("=== AI Category Migration Execution ===\n")

    # Load data
    websites = load_websites()
    original_total = len(websites)

    ai_sites = [s for s in websites if s.get('category') == 'AI工具/人工智能']
    non_ai_sites = [s for s in websites if s.get('category') != 'AI工具/人工智能']

    print(f"Total sites: {original_total}")
    print(f"AI category (to migrate): {len(ai_sites)}")
    print(f"Other categories (to preserve): {len(non_ai_sites)}")

    # Classify each AI site
    migrations = []
    by_target = defaultdict(list)
    unmatched = []

    for site in ai_sites:
        new_cat, reason = classify_ai_site(site)
        migrations.append({
            'url': site['url'],
            'name': site.get('name', ''),
            'current_category': 'AI工具/人工智能',
            'new_category': new_cat,
            'reason': reason
        })
        by_target[new_cat].append(site)
        if new_cat == '其他/杂项/在线工具':
            unmatched.append(site)

    print(f"\n=== Migration Summary ===")
    print(f"Total AI sites to migrate: {len(migrations)}")
    print(f"\nTop 10 target categories:")
    for cat, sites_in_cat in sorted(by_target.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"  {cat}: {len(sites_in_cat)} sites")

    if unmatched:
        print(f"\n⚠️  Fallback targets (may need manual review):")
        for s in unmatched[:10]:
            print(f"  {s.get('name','')[:50]:50s} | {s.get('url','')[:50]}")

    # Check if it's a dry run
    dry_run = '--dry-run' in sys.argv or '--plan' in sys.argv
    execute = '--execute' in sys.argv

    if dry_run:
        print(f"\n🔍 DRY RUN - No changes will be written")
        print(f"AI category would go from {len(ai_sites)} → 0 sites")
        print(f"Most expanded category would be: {max(by_target.items(), key=lambda x: len(x[1]))[0]} (+{max(len(v) for v in by_target.values())})")
        return

    if not execute:
        print(f"\nThis will MODIFY data/websites.json")
        print(f"To preview: run with --dry-run")
        print(f"To execute: run with --execute")
        return

    # EXECUTION MODE
    print(f"\n⚠️  EXECUTING MIGRATION...")

    # 1. Create backup
    backup = create_backup()

    # 2. Rebuild sites list: keep non-AI, replace AI with new categories
    new_websites = non_ai_sites.copy()
    for target_cat, sites_in_cat in by_target.items():
        for site in sites_in_cat:
            new_site = site.copy()
            new_site['category'] = target_cat
            # Update _cat too if exists
            if '_cat' in new_site:
                parts = new_site['_cat'].split('/')
                if len(parts) >= 3:
                    # Replace level 2 and 3 (the category part)
                    new_parts = parts[:2] + [target_cat]
                    new_site['_cat'] = '/'.join(new_parts)
            new_websites.append(new_site)

    # 3. Write atomically
    temp_path = WEBSITES_PATH.with_suffix('.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(new_websites, f, ensure_ascii=False, indent=2)
    temp_path.replace(WEBSITES_PATH)

    print(f"✅ Migration complete!")
    print(f"   Total sites: {original_total} → {len(new_websites)}")
    print(f"   AI category removed: {len(ai_sites)} sites redistributed")

    # 4. Save migration report
    report = {
        'operation': 'ai_migration_v15',
        'timestamp': datetime.now().isoformat(),
        'original_ai_count': len(ai_sites),
        'migrated_count': len(migrations),
        'target_distribution': {k: len(v) for k, v in by_target.items()},
        'migrations': migrations,
        'backup_path': str(backup)
    }

    report_path = REPORTS_DIR / "v15_ai_migration_execution_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"✅ Report saved: {report_path}")

    # 5. Suggest next step
    print(f"\n📋 Next steps:")
    print(f"  1. Run balance check: python3 scripts/balance_check.py")
    print(f"  2. Check for empty/bad categories created")
    print(f"  3. Proceed with remaining V15 tasks")

if __name__ == '__main__':
    main()
