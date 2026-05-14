#!/usr/bin/env python3
"""
死链检测脚本 — 验证 sitemap.xml 中所有URL的可达性
输出报告：live_links.txt / dead_links.txt
"""
import urllib.request, urllib.error, ssl, time, re, os

repo = "/home/yoli/GitHub/web_nav_v2"
sitemap_path = os.path.join(repo, "sitemap.xml")

# 跳过SSL验证（本地测试环境）
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 解析sitemap中的URL
with open(sitemap_path) as f:
    content = f.read()
urls = re.findall(r'<loc>(.*?)</loc>', content)

print(f"共 {len(urls)} 个URL待检测")

live = []
dead = []
timeout_errors = []

headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; KunHunBot/1.0; +https://nav.kunhunav.com/robots.txt)'
}

for i, url in enumerate(urls, 1):
    try:
        req = urllib.request.Request(url, headers=headers, method='HEAD')
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        code = resp.getcode()
        if code < 400:
            live.append(url)
            if i % 10 == 0:
                print(f"  [{i}/{len(urls)}] ✅ {url} ({code})")
        else:
            dead.append((url, code))
            print(f"  [{i}/{len(urls)}] ❌ {url} ({code})")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            dead.append((url, 404))
            print(f"  [{i}/{len(urls)}] ❌ {url} (404)")
        else:
            timeout_errors.append((url, str(e)))
            print(f"  [{i}/{len(urls)}] ⚠️ {url} ({e.code})")
    except Exception as e:
        timeout_errors.append((url, str(e)[:80]))
        print(f"  [{i}/{len(urls)}] ⚠️ {url} ({str(e)[:50]})")
    time.sleep(0.05)  # 避免请求过快

# 写入报告
report_dir = os.path.join(repo, "scripts")
os.makedirs(report_dir, exist_ok=True)

with open(os.path.join(report_dir, "live_links.txt"), "w") as f:
    for u in live:
        f.write(u + "\n")

with open(os.path.join(report_dir, "dead_links.txt"), "w") as f:
    for u, code in dead:
        f.write(f"{u} (HTTP {code})\n")

with open(os.path.join(report_dir, "timeout_errors.txt"), "w") as f:
    for u, err in timeout_errors:
        f.write(f"{u} ({err})\n")

print(f"\n{'='*50}")
print(f"检测结果:")
print(f"  ✅ 正常: {len(live)}")
print(f"  ❌ 死链: {len(dead)}")
print(f"  ⚠️ 超时/异常: {len(timeout_errors)}")
print(f"\n报告已保存至 scripts/ 目录")

# 如果是本地链接（nav.kunhunav.com），死链需要修复
internal_dead = [(u, c) for u, c in dead if 'nav.kunhunav.com' in u]
if internal_dead:
    print(f"\n⚠️ 检测到 {len(internal_dead)} 个内部死链需要修复:")
    for u, c in internal_dead[:5]:
        print(f"  {u} (HTTP {c})")