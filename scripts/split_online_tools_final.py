#!/usr/bin/env python3
"""
V15: Split 其他/杂项/在线工具 (445 sites) - FINAL EXECUTION

GOAL: Reduce online tools from 445 → ≤50 sites
METHOD: Rule-based re-categorization to existing underfilled categories

优先策略 (按gap大小分配)：
1. 大缺口类别优先分配 (gap>=6): 文案优化(7), 面试技巧(7), 库(7), 团队协作(6), API服务(6)…
2. 中等缺口 (gap=5): 数据库(5), 部署服务(5), 笔记(5), 网络安全(5)…
3. 小缺口 (gap=4): 技术写作(4), UI设计开源(5)…
"""

import json, re, sys, shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

base = Path("/home/yoli/GitHub/web_nav_v2")
wp = base / "data" / "websites.json"
bp_dir = base / "backups"
rep_dir = base / "reports"

def load():
    with open(wp) as f:
        return json.load(f)

def save(d):
    with open(wp,'w',encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def backup():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bp = bp_dir / f"websites.json.v15_split_online_final_pre_{ts}"
    shutil.copy2(wp, bp)
    print(f"✅ Backup: {bp}")
    return bp

sites = load()
total_before = len(sites)

online_sites = [s for s in sites if s.get('category') == '其他/杂项/在线工具']
others = [s for s in sites if s.get('category') != '其他/杂项/在线工具']
print(f"在线工具 sites: {len(online_sites)}")

# === COMPREHENSIVE RULE SET ===
# (pattern, target_category)
# Target categories must exist in current schema
RULES = [
    # === ACADEMIC / ONLINE COURSES (gap: 17) ===
    (r'(coursera\.org|udacity\.com|khanacademy\.org|edx\.org|futurelearn\.com|'
     r'skillshare\.com|udemy\.com|mitopen\.|ocw\.|opencourse|iers\.edu|'
     r'lynda\.com|pluralsight\.com|masterclass\.com|domestika\.org)',
     '学术科研/在线课程'),

    # === PROGRAMMING PRACTICE (gap: 12 in 开发工具/学习生成/在线课程) ===
    (r'(codewars\.com|leetcode\.com|hackerrank\.com|codementor\.io|'
     r'exercism\.org|hackerearth\.|topcoder\.|codepen\.io|jsfiddle\.net|'
     r'replit\.com|ideone\.com|paiza\.io|coderbyte\.com)',
     '开发工具/学习生成/在线课程'),

    # === TECH DOCUMENTATION / REFERENCE (gap: 6) ===
    (r'(docs\.)|(readthedocs\.)|(gitbook\.)|(docusaurus\.)|(devdocs\.)|'
     r'(manual/)|(reference/)|(cheatsheet)|(tutorialspoint\.com)',
     '开发工具/文档资源'),

    # === OPEN SOURCE PROJECTS (gap: 12) ===
    (r'(gnu\.org|apache\.org|mozilla\.org|python\.org|nodejs\.org|'
     r'rust-lang\.org|golang\.org|php\.net|kernel\.org|xfce\.org|kde\.org|'
     r'eclipse\.org|gnome\.org|apachefriends|jula|sourceforge)',
     '开发工具/平台开源'),

    # === GIT REPOS (non-GitHub) ===
    (r'(gitlab\.com(?!/ci)|bitbucket\.org|gitea\.io|sr\.ht|launchpad\.net)',
     '开发工具/平台开源'),

    # === PACKAGE / CDN (gap: 7) ===
    (r'(npmjs\.com|pypi\.org|crates\.io|rubygems\.org|'
     r'packagist\.org|nuget\.org|maven\.central|hex\.pm|clojars\.org)',
     '开发工具/包管理'),

    # === IDE / CODE EDITORS (gap: 6) ===
    (r'(vscode\.)|(jetbrains\.)|(sublimetext)|(replit\.)|(gitpod\.)|'
     r'(codesandbox\.)|(stackblitz\.)|(vim\.)|(emacs\.)|(neovim\.)',
     '开发工具/IDE'),

    # === CLOUD / HOSTING (gap: 12+) ===
    (r'(heroku\.com|netlify\.|vercel\.|firebase\.com|cloudflare\.pages|'
     r'github\.io|gitlab\.pages|aws\.amazon\.com|azure\.com|'
     r'cloud\.google\.com|gcloud|ibm\.cloud)',
     '开发工具/云开发平台'),

    # === DATABASE (gap: 5) ===
    (r'(mongodb\.com|postgresql\.org|mysql\.com|redis\.io|etcd\.io|'
     r'cockroachdb\.com|mariadb\.org|elastic\.co|influxdata\.com)',
     '开发工具/数据库'),

    # === MONITORING (gap: 6) ===
    (r'(prometheus\.)|(grafana\.)|(datadog\.)|(newrelic\.)|(sentry\.)|'
     r'(uptimerobot\.)|(statuspage\.)|(pingdom\.)|(statuscake)',
     '开发工具/监控告警'),

    # === CI/CD (gap in parent OK) ===
    (r'(circleci\.com|travis-ci\.org|drone\.io|gitlab\.ci|jenkins\.io|'
     r'woodpecker-ci\.ci|appveyor\.com|buddysuite)',
     '开发工具/CI/CD服务'),

    # === API / HTTP CLIENTS (gap: 6) ===
    (r'(postman\.com|insomnia\.rest|paw\.cloud|httpie\.io|'
     r'advanced-http-client)',
     '开发工具/API服务'),

    # === SECURITY / AUTH (gap: 5) ===
    (r'(1password|lastpass|bitwarden|keepass|vault|auth0|okta|keycloak|'
     r'sso\.|saml\.|oidc|ldap\.|shibboleth)',
     '系统工具/网络安全'),

    # === NETWORK UTILITIES (gap: 6) ===
    (r'(dns\.|whois\.|ipaddress|ping|traceroute|speedtest|dnscrypt|'
     r'ssh\.|vpn\.|openvpn|wireguard|ntfy\.)',
     '系统工具/网络工具'),

    # === CONTAINER / DEVOPS (gap: 6) ===
    (r'(docker\.)|(kubernetes\.)|(podman\.)|(container\.)|(k8s\.)|'
     r'(helm\.sh)|(istio\.)|(linkerd\.)|(rancher\.)',
     '系统工具/容器管理'),

    # === COMMUNICATION (gap: 6) ===
    (r'(slack\.)|(discord\.)|(telegram\.)|(twilio\.)|(sendgrid\.)|'
     r'(mailgun\.)|(smtp\.)|(sendgrid)|(mail\.)',
     '效率办公/团队协作'),

    # === DESIGN / WHITEBOARD (gap: 6) ===
    (r'(figma\.)|(sketch\.)|(canva\.)|(framer\.)|(excalidraw\.)|'
     r'(draw\.io)|(diagrams\.net)|(penpot\.)|(miro\.)|(figjam)',
     '设计工具/在线设计'),

    # === MEDIA STREAMING (parent gap OK) ===
    (r'(youtube\.com)|(vimeo\.)|(twitch\.)|(bilibili\.)|'
     r'(netflix\.)|(spotify\.)|(soundcloud)',
     '多媒体/视频娱乐'),

    # === SEARCH ENGINES (gap: 3) ===
    (r'(google\.com/search)|(bing\.com/search)|(duckduckgo\.com)|'
     r'(baidu\.com/s)|(yahoo\.com)|(search\.)',
     '其他/杂项/搜索引擎'),

    # === E-COMMERCE (gap: need check) ===
    (r'(amazon\.)|(ebay\.)|(aliexpress\.)|(taobao\.)|(shopify\.)|'
     r'(woocommerce)|(etsy\.)|(walmart\.)|(target\.)|(bestbuy)',
     '其他/杂项/平台市场'),

    # === TECH BLOGS / INFO (gap: 6) ===
    (r'(blog\.)|(medium\.com)|(dev\.to)|(hashnode\.)|(wordpress\.com)|'
     r'(substack\.com)|(highscalability\.com)|(infoq\.com)|'
     r'(martinfowler\.)|(codinghorror)|(infocobuild)|(thenewstack)',
     '开发工具/文档资源'),

    # === SPECIFIC HIGH-VALUE SITES ===
    # awesome-selfhosted → 系统工具/实用工具/其他工具 (gap: 6)
    (r'awesome-selfhosted\.net',
     '系统工具/实用工具/其他工具',
     'Awesome self-hosted directory'),
    # zeromq.org → 开发工具/库 (gap: 7)
    (r'zeromq\.org',
     '开发工具/库',
     'ZeroMQ messaging library'),
    # codility.com → 开发工具/学习生成/在线课程 (gap: 12)
    (r'codility\.com',
     '开发工具/学习生成/在线课程',
     'Coding practice platform'),
    # educative.io → 学术科研/在线课程
    (r'educative\.io',
     '学术科研/在线课程',
     'Online course platform'),
    # overleaf.com → 效率办公/简历制作 or 学术科研/工具教程
    (r'overleaf\.com',
     '效率办公/简历制作',
     'LaTeX editor'),
    # eng.uber.com → 效率办公/技术写作 (gap: 5) or 技术博客
    (r'eng\.uber\.com',
     '效率办公/技术写作',
     'Engineering blog'),
]

dry = '--dry-run' in sys.argv
ex = '--execute' in sys.argv

migrations = []
by_target = defaultdict(list)
remain = []

for s in online_sites:
    url = s.get('url','').lower()
    name = s.get('name','').lower()
    combined = f"{url} {name}"

    matched = False
    for rule in RULES:
        pattern = rule[0]
        target = rule[1]
        if re.search(pattern, combined, re.IGNORECASE):
            migrations.append(s)
            by_target[target].append(s)
            matched = True
            break
    if not matched:
        remain.append(s)

print(f"Total online tools: {len(online_sites)}")
print(f"Matched to categories: {len(migrations)}")
print(f"Remaining (stay as 在线工具): {len(remain)}")

print(f"\nMigration targets:")
for cat, slist in sorted(by_target.items(), key=lambda x: -len(x[1]))[:15]:
    print(f"  {cat}: +{len(slist)}")

if remain:
    print(f"\nRemaining domain samples:")
    from urllib.parse import urlparse
    from collections import Counter
    doms = Counter(re.sub(r'^www\.','',urlparse(s['url']).netloc.lower()) for s in remain)
    for d,c in doms.most_common(10):
        print(f"  {d}: {c}")

if dry:
    print(f"\n🔍 DRY RUN")
    print(f"Would reduce 其他/杂项/在线工具: {len(online_sites)} → {len(remain)}")
    print(f"HIGH-VALUE TARGETS FILLED:")
    gap_filled = {k: len(v) for k,v in by_target.items()}
    for cat, add in sorted(gap_filled.items(), key=lambda x: -x[1])[:10]:
        print(f"  {cat}: +{add}")
    sys.exit(0)

if not ex:
    print(f"\nRun with --execute to apply")
    sys.exit(0)

# EXECUTE
print(f"\n⚠️  EXECUTING SPLIT...")
backup()

new_sites = others.copy()
for s in migrations:
    ns = s.copy()
    ns['category'] = target  # target from loop
    new_sites.append(ns)
for s in remain:
    new_sites.append(s)  # keep in original category

tmp = wp.with_suffix('.tmp4')
with open(tmp,'w',encoding='utf-8') as f:
    json.dump(new_sites, f, ensure_ascii=False, indent=2)
tmp.replace(wp)

print(f"✅ Split complete!")
print(f"   Total: {total_before} → {len(new_sites)}")
print(f"   其他/杂项/在线工具: {len(online_sites)} → {len(remain)}")

rep = {
    'operation': 'split_online_tools_final_v15',
    'timestamp': datetime.now().isoformat(),
    'original': len(online_sites),
    'migrated': len(migrations),
    'remaining': len(remain),
    'by_target': {k: len(v) for k,v in by_target.items()},
    'backup': str(backup())
}
rp = rep_dir / "v15_split_online_final_report.json"
with open(rp,'w') as f:
    json.dump(rep, f, ensure_ascii=False, indent=2)
print(f"✅ Report: {rp}")
