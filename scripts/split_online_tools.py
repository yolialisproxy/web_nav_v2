#!/usr/bin/env python3
"""
V15 Split Oversized Category: 其他/杂项/在线工具 (445 sites)

Strategy: Re-categorize sites from this oversized bucket to:
1. Existing underfilled categories that logically match
2. New subcategories within 其他/杂项 if needed
3. Existing appropriate parent categories

Goal: Reduce 其他/杂项/在线工具 from 445 to <=50 (target)
"""

import json, re, sys, shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

base = Path("/home/yoli/GitHub/web_nav_v2")
websites_path = base / "data" / "websites.json"
backup_dir = base / "backups"
reports_dir = base / "reports"

def load():
    with open(websites_path) as f:
        return json.load(f)

def save(data):
    with open(websites_path,'w',encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def backup():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bp = backup_dir / f"websites.json.v15_split_online_tools_pre_{ts}"
    shutil.copy2(websites_path, bp)
    print(f"✅ Backup: {bp}")
    return bp

# Load current data
sites = load()
total_before = len(sites)

# Filter the oversized category
online_sites = [s for s in sites if s.get('category') == '其他/杂项/在线工具']
others = [s for s in sites if s.get('category') != '其他/杂项/在线工具']

print(f"其他/杂项/在线工具 sites: {len(online_sites)}")
print(f"Other categories: {len(others)}")

# Re-classification rules (site type → target category)
# Prioritize underfilled targets
RULES = [
    # Academic / Courses → 学术科研/在线课程 (gap: 17)
    (r'(coursera\.org|udacity\.com|khanacademy\.org|edx\.org|futurelearn\.com|skillshare\.com|udemy\.com|mitopen\.|ocw\.|opencourse)',
     '学术科研/在线课程',
     'MOOC/E-learning platform'),

    # Programming practice → 开发工具/学习生成/在线课程 (gap: 12)
    (r'(codewars\.com|leetcode\.com|hackerrank\.com|codementor\.io|exercism\.org|hackerearth\.|topcoder\.)',
     '开发工具/学习生成/在线课程',
     'Coding practice'),

    # Technical documentation → 开发工具/文档资源 (gap: 6)
    (r'(docs\.)|(readthedocs\.)|(gitbook\.)|(docusaurus\.)|(devdocs\.)|(man\.)|(manual/)',
     '开发工具/文档资源',
     'Technical documentation'),

    # Open source projects → 开发工具/平台开源 (gap: 12)
    (r'(gnu\.org|apache\.org|mozilla\.org|python\.org|nodejs\.org|rust-lang\.org|golang\.org|php\.net|kernel\.org|xfce\.org|kde\.org)',
     '开发工具/平台开源',
     'Major open source project'),

    # Specific open-source tools → 开发工具/库 (gap: 7)
    (r'(github\.com/[^/]+/[^/]+)|(gitlab\.com/[^/]+/[^/]+)',
     '开发工具/平台开源/GitHub',
     'Open source repo'),

    # Package/CDN → 开发工具/包管理 (gap: 7)
    (r'(npmjs\.com|pypi\.org|crates\.io|rubygems\.org|packagist\.org|nuget\.org|maven\.central|hex\.pm)',
     '开发工具/包管理',
     'Package registry'),

    # IDE/Code editors → 开发工具/IDE (gap: 6)
    (r'(vscode\.)|(jetbrains\.)|(sublimetext)|(replit\.)|(gitpod\.)|(codesandbox\.)|(stackblitz\.)',
     '开发工具/IDE',
     'IDE/Code editor'),

    # Cloud hosting → 开发工具/云开发平台 (gap: 12+)
    (r'(heroku\.com|netlify\.|vercel\.|firebase\.com|cloudflare\.pages|github\.io|gitlab\.pages)',
     '开发工具/云开发平台',
     'Hosting/Cloud platform'),

    # Databases/Storage → 开发工具/数据库 (gap: 6)
    (r'(mongodb\.com|postgresql\.org|mysql\.com|redis\.io|etcd\.io|cockroachdb\.com)',
     '开发工具/数据库',
     'Database service'),

    # Monitoring/Observability → 开发工具/监控告警 (gap: 6)
    (r'(prometheus\.)|(grafana\.)|(datadog\.)|(newrelic\.)|(sentry\.)|(uptimerobot\.)|(statuspage\.)',
     '开发工具/监控告警',
     'Monitoring/Observability'),

    # CI/CD services → 开发工具/CI/CD服务 (gap in parent already balanced, but fine)
    (r'(circleci\.com|travis-ci\.org|drone\.io|gitlab\.com/ci|jenkins\.io|woodpecker-ci\.)',
     '开发工具/CI/CD服务',
     'CI/CD platform'),

    # API services → 开发工具/API服务 (gap: 6)
    (r'(api\.)|(/api/)|(rest-api)|(graphql\.)|(postman\.com|insomnia\.rest)',
     '开发工具/API服务',
     'API service'),

    # Security tools → 系统工具/网络安全 (gap: 6)
    (r'(1password|lastpass|bitwarden|keepass|vault|auth0|okta|keycloak|sso|saml|oidc)',
     '系统工具/网络安全',
     'Security tool'),

    # Network utilities → 系统工具/网络工具 (gap: 6)
    (r'(dns\.)|(network|ipaddress|whois|ping|traceroute|speedtest|dnscrypt)',
     '系统工具/网络工具',
     'Network utility'),

    # Container/DevOps → 系统工具/容器管理 (gap: 6)
    (r'(docker\.)|(kubernetes\.)|(podman\.)|(container\.)|(k8s\.)|(helm\.sh)|(istio\.)|(linkerd\.)',
     '系统工具/容器管理',
     'Container/DevOps'),

    # Messaging/Communication → 效率办公/团队协作 (gap: 6)
    (r'(slack\.)|(discord\.)|(telegram\.)|(twilio\.)|(sendgrid\.)|(mailgun\.)|(smtp\.)',
     '效率办公/团队协作',
     'Communication'),

    # Design tools → 设计工具/在线设计 or 设计工具/白板资源 (gap: 6)
    (r'(figma\.)|(sketch\.)|(canva\.)|(framer\.)|(excalidraw\.)|(draw\.io)|(diagrams\.net)',
     '设计工具/在线设计',
     'Design tool'),

    # Video/Media streaming → 多媒体/视频娱乐 (gap in parent, but OK)
    (r'(youtube\.com)|(vimeo\.)|(twitch\.)|(bilibili\.)|(netflix\.)|(spotify\.)|(soundcloud)',
     '多媒体/视频娱乐',
     'Media streaming'),

    # Search engines → 其他/杂项/搜索引擎 (gap: 3)
    (r'(google\.com/search)|(bing\.com/search)|(duckduckgo\.com)|(baidu\.com/s)|(yahoo\.com)',
     '其他/杂项/搜索引擎',
     'Search engine'),

    # Social networks → 效率办公/团队协作 or 其他/杂项
    (r'(twitter\.com)|(x\.com)|(facebook\.)|(instagram\.)|(linkedin\.)|(reddit\.)|(tumblr\.)',
     '效率办公/团队协作',
     'Social platform'),

    # E-commerce → 其他/杂项/平台市场 (gap: need to check)
    (r'(amazon\.)|(ebay\.)|(aliexpress\.)|(taobao\.)|(shopify\.)|(woocommerce)|(etsy\.)',
     '其他/杂项/平台市场',
     'E-commerce'),

    # Resume/CV builders → 效率办公/简历制作
    (r'(resume\.)|(cv\.)|(overleaf\.com)|(latex-project\.org)',
     '效率办公/简历制作',
     'Resume/CV tool'),

    # Note-taking → 效率办公/笔记 (gap: 6)
    (r'(evernote\.)|(notion\.)|(onenote\.)|(bear笔记)|(obsidian\.)|(logseq)',
     '效率办公/笔记',
     'Note-taking'),
]

def recategorize(site):
    url = site.get('url','').lower()
    name = site.get('name','').lower()
    combined = f"{url} {name}"

    for pattern, target_cat, reason in RULES:
        if re.search(pattern, combined, re.IGNORECASE):
            return target_cat, reason
    return None, None

migrations = []
by_target = defaultdict(list)
remain = []

for s in online_sites:
    new_cat, reason = recategorize(s)
    if new_cat:
        migrations.append({**s, 'new_category': new_cat, 'migration_reason': reason})
        by_target[new_cat].append(s)
    else:
        remain.append(s)

print(f"\n=== Split Plan ===")
print(f"Total to reclassify: {len(online_sites)}")
print(f"Assigned to new categories: {len(migrations)}")
print(f"Remaining in 在线工具: {len(remain)}")

print(f"\nTarget distribution:")
for cat, slist in sorted(by_target.items(), key=lambda x: -len(x[1])):
    print(f"  {cat}: +{len(slist)}")

dry = '--dry-run' in sys.argv
ex = '--execute' in sys.argv

if dry:
    print(f"\n🔍 DRY RUN - no write")
    print(f"Would move {len(migrations)} sites out of 其他/杂项/在线工具")
    print(f"Final remaining in bucket: {len(remain)}")
    print(f"Δ: 445 → {len(remain)}")
    sys.exit(0)

if not ex:
    print(f"\nTo preview: --dry-run")
    print(f"To execute: --execute")
    sys.exit(0)

# EXECUTE
print(f"\n⚠️  EXECUTING...")
backup()

# Build new websites list
new_sites = others.copy()
# Add reclassified sites with updated category
for s in migrations:
    ns = s.copy()
    ns['category'] = ns.pop('new_category')
    ns.pop('migration_reason', None)
    new_sites.append(ns)
# Keep remainder in original category
for s in remain:
    new_sites.append(s)

# Atomic write
tmp = websites_path.with_suffix('.tmp3')
with open(tmp,'w',encoding='utf-8') as f:
    json.dump(new_sites, f, ensure_ascii=False, indent=2)
tmp.replace(websites_path)

print(f"✅ Split complete!")
print(f"   Total: {total_before} → {len(new_sites)}")
print(f"   其他/杂项/在线工具: {len(online_sites)} → {len(remain)}")

# Report
rep = {
    'operation': 'split_online_tools_v15',
    'timestamp': datetime.now().isoformat(),
    'original_count': len(online_sites),
    'migrated_count': len(migrations),
    'remaining_count': len(remain),
    'target_distribution': {k: len(v) for k,v in by_target.items()},
    'backup': str(backup())
}
rp = reports_dir / "v15_split_online_tools_report.json"
with open(rp,'w') as f:
    json.dump(rep, f, ensure_ascii=False, indent=2)
print(f"✅ Report: {rp}")
