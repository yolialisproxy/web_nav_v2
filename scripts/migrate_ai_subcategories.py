#!/usr/bin/env python3
"""
AI Subcategory Cleanup - Phase 2

After Phase 1 cleared the parent category 'AI工具/人工智能' (332→0),
Phase 2 must handle all 769 sites in AI subcategories.

GOAL: Migrate ALL sites from ANY category starting with 'AI工具/人工智能'
to their CORRECT non-AI categories.

STRATEGY: Same keyword-based classification as Phase 1,
but extended to catch AI-adjacent categories too.
"""

import json
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

base = Path("/home/yoli/GitHub/web_nav_v2")
WEBSITES_PATH = base / "data" / "websites.json"
BACKUP_DIR = base / "backups"
REPORTS_DIR = base / "reports"

def load():
    with open(WEBSITES_PATH) as f:
        return json.load(f)

def save(data):
    with open(WEBSITES_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def backup():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bp = BACKUP_DIR / f"websites.json.v15_ai_subcat_pre_{ts}"
    shutil.copy2(WEBSITES_PATH, bp)
    print(f"✅ Backup: {bp}")
    return bp

# Extended rules to catch AI-adjacent mis-categorization
RULES = [
    # University courses → 学术科研/教材
    (r'(mit\.edu|stanford\.edu|berkeley\.edu|harvard\.edu|cmu\.edu|'
     r'cornell\.edu|nyu\.edu|ox\.ac\.uk|cam\.ac\.uk|ed\.ac\.uk|'
     r'ethz\.ch|epfl\.ch|tum\.de|kth\.se|uu\.nl|dtu\.dk|'
     r'\.edu/.*course|\.edu/.*class|\.edu/.*lecture)',
     '学术科研/教材',
     'University course'),

    # YouTube videos → 多媒体/视频娱乐/教程
    (r'youtube\.com/watch|youtu\.be|youtube-nocookie|youtube\.com/playlist',
     '多媒体/视频娱乐/教程',
     'YouTube video'),

    # Wikipedia → 其他/杂项/搜索引擎
    (r'wikipedia\.org|wikimedia\.org|wiktionary\.org|wikibooks\.org',
     '其他/杂项/搜索引擎',
     'Wikipedia'),

    # Archive.org → 系统工具/备份工具
    (r'archive\.org|web\.archive\.org|wayback\.machine',
     '系统工具/备份工具',
     'Archive.org'),

    # GitHub resources → keep but check
    (r'github\.com/_private|raw\.githubusercontent\.com|githubassets\.com',
     '开发工具/平台开源/GitHub',
     'GitHub resource'),

    # CI/CD
    (r'woodpecker-ci\.org|gitlab\.com/(ci|pipelines)|'
     r'jenkins\.io|jenkins\.org|circleci\.com|'
     r'travis-ci\.org|drone\.io|cloudbuild\.google\.com|'
     r'appveyor\.com|circleback\.ai',
     '开发工具/CI/CD服务',
     'CI/CD service'),

    # Cloud providers
    (r'aws\.amazon\.com|googlecloud\.com|cloud\.google\.com|'
     r'azure\.com|oraclecloud\.com|digitalocean\.com|'
     r'linode\.com|vultr\.com|hetzner\.com|ibm\.cloud',
     '开发工具/云开发平台',
     'Cloud provider'),

    # Monitoring
    (r'sensu\.io|prometheus\.io|grafana\.com|'
     r'datadog\.com|newrelic\.com|dynatrace\.com|'
     r'honeycomb\.io|splunk\.com|logz\.io|sentry\.io|'
     r'uptimerobot\.com|statuspage\.io',
     '开发工具/监控告警',
     'Monitoring'),

    # Identity/Auth
    (r'pomerium\.io|goauthentik\.io|keycloak\.org|'
     r'okta\.com|auth0\.com|onelogin\.com|fusionauth\.io',
     '系统工具/网络安全',
     'Identity/Auth'),

    # Documentation
    (r'readthedocs\.io|readthedocs\.org|gitbook\.com|'
     r'docusaurus\.io|docsify\.io|mkdocs\.org|antora\.org|'
     r'stackoverflow\.com|serverfault\.com|superuser\.com|'
     r'stackexchange\.com',
     '开发工具/文档资源',
     'Docs platform'),

    # Coding practice
    (r'roadmap\.sh|freecodecamp\.org|theodinproject\.com|'
     r'codewars\.com|leetcode\.com|hackerrank\.com|'
     r'exercism\.org|codeproject\.com|tutorialspoint\.com|'
     r'w3schools\.com|javatpoint\.com|geeksforgeeks\.org',
     '开发工具/学习生成/在线课程',
     'Coding practice'),

    # Package managers
    (r'npmjs\.com|pypi\.org|crates\.io|rubygems\.org|'
     r'packagist\.org|nuget\.org|clojars\.org|'
     r'maven\.central|nixos\.org/channels|hex\.pm',
     '开发工具/包管理',
     'Package registry'),

    # Container/Virtualization
    (r'docker\.com|docker\.io|kubernetes\.io|k8s\.io|'
     r'podman\.io|lxc\.org|lxc\.com|vagrantup\.com|'
     r'hashicorp\.com/\(product/virtualbox\)|hashicorp\.com/\(product/vagrant\)',
     '系统工具/容器管理',
     'Container/VM'),

    # Networking
    (r'coredns\.io|bind\.isc\.org|nginx\.org|nginx\.com|'
     r'apache\.org|traefik\.io|envoy\.proxy|'
     r'istio\.io|linkerd\.io|konghq\.com|haproxy\.org',
     '系统工具/网络工具',
     'Networking'),

    # Flashcards
    (r'ankiweb\.net|ankisrs\.net|quizlet\.com|'
     r'brainscape\.com|mnemosyne\.pro|supermemo\.com|'
     r'remnote\.io|thinkific\.com',
     '效率办公/笔记',
     'Flashcards'),

    # Diagramming
    (r'kroki\.io|excalidraw\.com|draw\.io|diagrams\.net|'
     r'lucidchart\.com|whimsical\.com|miro\.com|'
     r'figma\.com|figjam\.com|sketch\.com|plex\.info',
     '设计工具/白板资源',
     'Diagram/Whiteboard'),

    # API tools
    (r'postman\.com|insomnia\.rest|paw\.cloud|'
     r'httpie\.io|curl\.haxx\.se|wget\.hometools\.org|'
     r'advanced-http-client\.com',
     '开发工具/API构建',
     'API/HTTP client'),

    # Regex tools
    (r'regex101\.com|regexr\.com|regex\.com|'
     r'regExr\.com|regexpal\.com|debuggex\.com',
     '其他/杂项/正则测试',
     'Regex tester'),

    # URL shorteners
    (r'bit\.ly|tinyurl\.com|t\.co|goo\.gl|x\.com|'
     r'is\.gd|v\.gd|tiny\.cc|ow\.ly',
     '其他/杂项/短链接',
     'URL shortener'),

    # Translation
    (r'deep(l|.com)|translate\.google\.com|'
     r'bing\.com/translator|microsofttranslator\.com|'
     r'baidu\.com/trans|yandex\.ru/translate',
     '其他/杂项/词典翻译',
     'Translation'),

    # DevOps platforms (GitLab, etc.)
    (r'gitlab\.com(?!.*/ci)|gitlab\.net|'
     r'gitea\.io|gogs\.io|sourceforge\.net|'
     r'bitbucket\.org|aws\.codepipeline|azure\.devops',
     '开发工具/平台开源',
     'Git/DevOps platform'),

    # Databases
    (r'mongodb\.com|postgresql\.org|mysql\.com|'
     r'redis\.io|etcd\.io|cockroachdb\.com|'
     r'mariadb\.org|elastic\.co|influxdata\.com|'
     r'cassandra\.apache\.org|druid\.apache\.org',
     '开发工具/数据库',
     'Database'),
]

FALLBACK_CATS = [
    '其他/杂项/在线工具',
    '其他/杂项/在线计算',
    '其他/杂项/公共数据',
    '其他/杂项/平台市场',
    '其他/杂项/在线测试',
    '系统工具/实用工具/其他工具',
    '开发工具/在线工具',
]

def classify(site):
    url = site.get('url','').lower()
    name = site.get('name','').lower()
    combined = f"{url} {name}"

    for pattern, target, reason in RULES:
        if re.search(pattern, combined, re.IGNORECASE):
            return target, reason

    # Fallback: try to guess from domain
    if 'github' in url:
        return '开发工具/平台开源/GitHub', 'fallback-github'
    if 'gitlab' in url:
        return '开发工具/平台开源', 'fallback-gitlab'
    if 'stackoverflow' in url or 'stackexchange' in url:
        return '开发工具/文档资源', 'fallback-stackoverflow'
    if 'google' in url:
        return '其他/杂项/搜索引擎', 'fallback-google'
    if 'microsoft' in url:
        return '系统工具/实用工具/其他工具', 'fallback-microsoft'

    # Last resort
    return FALLBACK_CATS[0], 'fallback-default'

def main():
    print("=== AI Subcategory Cleanup - Phase 2 ===\n")
    sites = load()
    total = len(sites)

    # Find ALL AI-prefixed sites (any depth)
    ai_sites = [s for s in sites if s.get('category','').startswith('AI工具/人工智能')]
    non_ai = [s for s in sites if not s.get('category','').startswith('AI工具/人工智能')]

    print(f"Total sites: {total}")
    print(f"AI-prefixed sites to migrate: {len(ai_sites)}")
    print(f"Other sites: {len(non_ai)}")

    # Classify
    migrations = []
    by_target = defaultdict(list)
    unmatched = []

    for site in ai_sites:
        old_cat = site.get('category','')
        new_cat, reason = classify(site)
        migrations.append({
            'url': site['url'],
            'name': site.get('name',''),
            'old_category': old_cat,
            'new_category': new_cat,
            'reason': reason
        })
        by_target[new_cat].append(site)
        if new_cat.startswith('其他/杂项/在线工具'):
            unmatched.append(site)

    print(f"\n=== Migration Plan ===")
    print(f"AI sites to migrate: {len(migrations)}")
    print(f"\nTarget distribution (top 12):")
    for cat, slist in sorted(by_target.items(), key=lambda x: -len(x[1]))[:12]:
        print(f"  {cat}: {len(slist)}")

    if unmatched:
        print(f"\n⚠️  Fallback targets ({len(unmatched)} sites):")
        for s in unmatched[:5]:
            print(f"  {s.get('name','')[:50]:50s} | {s.get('url','')[:50]}")

    dry = '--dry-run' in sys.argv
    exec_ = '--execute' in sys.argv

    if dry:
        print(f"\n🔍 DRY RUN - no changes")
        print(f"Would migrate {len(ai_sites)} AI sites to {len(by_target)} categories")
        return

    if not exec_:
        print(f"\nTo preview: --dry-run")
        print(f"To execute: --execute")
        return

    # Execute
    print(f"\n⚠️  EXECUTING PHASE 2...")
    backup()

    new_sites = non_ai.copy()
    for target_cat, slist in by_target.items():
        for site in slist:
            ns = site.copy()
            ns['category'] = target_cat
            # Update _cat if exists
            if '_cat' in ns:
                parts = ns['_cat'].split('/')
                if len(parts) >= 2:
                    # Rebuild _cat with new category path
                    # Keep first two levels (top category) if different?
                    # For now, update only 'category' field, leave _cat as-is
                    # (balance_check uses 'category' anyway)
                    pass
            new_sites.append(ns)

    # Atomic write
    tmp = WEBSITES_PATH.with_suffix('.tmp2')
    with open(tmp,'w',encoding='utf-8') as f:
        json.dump(new_sites, f, ensure_ascii=False, indent=2)
    tmp.replace(WEBSITES_PATH)

    print(f"✅ Phase 2 complete!")
    print(f"   Total: {total} → {len(new_sites)}")
    print(f"   AI subcategories cleared: {len(ai_sites)} migrated")

    # Report
    rep = {
        'operation': 'ai_subcategory_migration_v15',
        'timestamp': datetime.now().isoformat(),
        'migrated_count': len(ai_sites),
        'target_distribution': {k: len(v) for k,v in by_target.items()},
        'backup': str(backup())
    }
    rp = REPORTS_DIR / "v15_ai_subcat_migration_report.json"
    with open(rp,'w') as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    print(f"✅ Report: {rp}")

if __name__ == '__main__':
    main()
