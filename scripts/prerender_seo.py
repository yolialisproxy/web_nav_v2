#!/usr/bin/env python3
"""
 * SEO预渲染脚本 - V3
 * 作用：为每个分类页面生成静态HTML快照，供搜索引擎索引
 * 输出：prerendered/ 目录下的独立HTML文件
 *       sitemap.xml（带真实URL，非hash）
 """

import json
import os
import re
from datetime import datetime
from html import escape

OUTPUT_DIR = "prerendered"
SITEMAP_FILE = "sitemap_generated.xml"
INDEX_FILE = "../index.html"  # 相对路径从prerendered到根

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open("websites.json", 'r', encoding='utf-8') as f:
    sites = json.load(f)

# 构建分类树
categories = {}
for s in sites:
    cat = s.get('category', '未分类').strip()
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(s)

# 按站点数排序分类
sorted_cats = sorted(categories.items(), key=lambda x: -len(x[1]))

BASE_URL = "https://nav.kunhunav.com"

# 读取模板
with open("index.html", 'r', encoding='utf-8') as f:
    template = f.read()

def generate_html(title, h1, content_html, css_active_cat="", description="", nav_html=""):
    """基于模板包装内容"""
    # 替换标题
    html = template.replace(
        "<title>啃魂导航 - 开发者导航 | AI工具·编程资源·设计素材</title>",
        f"<title>{escape(title)}</title>"
    )
    # 替换 meta description
    html = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{escape(description[:160])}">',
        html
    )
    # 替换 Schema.org JSON-LD 中的 description（WebSite 节点）
    html = re.sub(
        r'("description":\s*)"[^"]*?"',
        lambda m: m.group(1) + f'"{escape(description[:150])}"',
        html,
        count=1  # 只替换第一个（WebSite 的 description）
    )
    # 插入预渲染标记
    main_tag_pattern = re.search(r'<(main|div)\s+id="main-content"[^>]*>', html)
    if main_tag_pattern:
        original_tag = main_tag_pattern.group(0)
        new_tag = original_tag.replace('>', ' data-prerendered="true">', 1)
        html = html.replace(original_tag, new_tag)

    # 将导航HTML插入到侧边栏 nav#sidebar-content 中
    if nav_html:
        # 匹配 <nav id="sidebar-content" ...>...</nav>
        sidebar_nav_pattern = re.search(
            r'(<nav\s+id="sidebar-content"[^>]*>)(.*?)(</nav>)',
            html, re.DOTALL
        )
        if sidebar_nav_pattern:
            before, existing, after = sidebar_nav_pattern.groups()
            html = html.replace(
                before + existing + after,
                before + nav_html + existing + after
            )
        else:
            # 降级：尝试插入到 aside 内
            aside_pattern = re.search(
                r'(<aside[^>]*id="sidebar"[^>]*>)(.*?)(</aside>)',
                html, re.DOTALL
            )
            if aside_pattern:
                before, existing, after = aside_pattern.groups()
                html = html.replace(
                    before + existing + after,
                    before + existing + nav_html + after
                )

    return html

# 构建6大主分类导航（匹配 index.html 侧边栏结构）
MAIN_CATEGORIES = [
    ('AI工具', 'ai'),
    ('开发工具', 'develop'),
    ('设计工具', 'design'),
    ('效率办公', 'productivity'),
    ('学术科研', 'academic'),
    ('多媒体', 'media'),
]

# 按主分类聚合子分类
main_cat_subs = {}
for cat_name, sites_list in sorted_cats:
    first = cat_name.split('/')[0].strip()
    if first not in main_cat_subs:
        main_cat_subs[first] = []
    main_cat_subs[first].append((cat_name, sites_list))

def build_sidebar_nav(active_cat=""):
    """生成侧边栏导航HTML（新6分类体系）"""
    html_parts = []
    html_parts.append('<nav class="sidebar-nav" aria-label="主导航">')

    for main_name, main_id in MAIN_CATEGORIES:
        subs = main_cat_subs.get(main_name, [])
        is_active = active_cat == main_name or any(c[0] == active_cat for c in subs)
        nav_class = 'nav-item active' if is_active else 'nav-item'
        count = sum(len(c[1]) for c in subs)
        html_parts.append(
            f'<div class="{nav_class}" data-category="{main_name}">'
            f'<span class="nav-icon">{get_icon(main_name)}</span>'
            f'<span class="nav-text">{main_name}</span>'
            f'<span class="nav-badge">{count}</span>'
            f'</div>'
        )
        if subs:
            html_parts.append(f'<div class="nav-children" data-parent="{main_id}">')
            for sub_name, sub_sites in sorted(subs, key=lambda x: -len(x[1])):
                sub_count = len(sub_sites)
                sub_active = active_cat == sub_name
                sub_class = 'nav-sub-item active' if sub_active else 'nav-sub-item'
                # 生成子分类锚点链接
                anchor = sub_name.replace('/', '_')
                html_parts.append(
                    f'<a class="{sub_class}" data-sub="{sub_name}" '
                    f'href="#{anchor}">'
                    f'<span class="nav-text">{sub_name}</span>'
                    f'<span class="nav-badge">{sub_count}</span>'
                    f'</a>'
                )
            html_parts.append('</div>')
    html_parts.append('</nav>')
    return '\n'.join(html_parts)


def get_icon(cat_name):
    """获取分类图标"""
    icons = {
        'AI工具': '🤖',
        '开发工具': '💻',
        '设计工具': '🎨',
        '效率办公': '⚡',
        '学术科研': '📚',
        '多媒体': '🎬',
    }
    return icons.get(cat_name, '📁')


sitemap_urls = []
generated_files = []
errors = []

for cat_name, cat_sites in sorted_cats:
    # 跳过极小的分类（仅1-2个站点的分类合并后通常无需独立页面）
    # 但保留它们，因为内容虽小仍对SEO有价值

    safe_name = cat_name.replace('/', '_').replace(' ', '_')[:60]
    filename = f"{OUTPUT_DIR}/{safe_name}.html"

    # 构建分类内容HTML
    sites_html = ""
    for site in cat_sites:
        name = site.get('name', '未知')
        url = site.get('url', '#')
        desc = site.get('description', '')
        title_attr = site.get('title', name)

        sites_html += f'''
        <a href="{escape(url)}" class="site site-card" target="_blank" rel="noopener noreferrer"
           aria-label="{escape(name)}">
            <img src="https://www.google.com/s2/favicons?domain={escape(url.split('/')[2] if url.startswith('http') else 'example.com')}&sz=32"
                 class="card-icon" loading="lazy" alt="{escape(name)}"
                 onerror="this.src='assets/images/favicon.png';">
            <span class="card-title">{escape(name)}</span>
            <span class="card-desc">{escape(desc[:120])}</span>
        </a>'''

    # 生成完整的分类页面内容
    cat_parts = cat_name.split('/')
    breadcrumb = ' <span class="bc-sep">›</span> '.join(
        f'<a href="{BASE_URL}/">{p}</a>' if i == 0 else f'<a href="{BASE_URL}/#{cat_parts[:i+1]}" >{p}</a>'
        for i, p in enumerate(cat_parts)
    )

    page_html = f'''
    <div class="view-header">
        <div class="view-breadcrumb">{breadcrumb}</div>
        <div class="view-meta">{len(cat_sites)} 个站点</div>
    </div>
    <div class="view-toolbar">
        <div class="toolbar-left">
            <button class="view-btn view-grid active" aria-label="网格视图">⊞</button>
            <button class="view-btn view-list" aria-label="列表视图">☰</button>
        </div>
    </div>
    <div class="grid" id="sites-grid">
        {sites_html}
    </div>
    ''' if sites_html else '<div class="state-container state-empty"><div class="state-icon">📁</div><div class="state-title">暂无内容</div></div>'

    desc_text = f"{cat_name}分类 - 收录{len(cat_sites)}个优质网站资源"
    title_text = f"{cat_name} - 啃魂导航"

    # 生成侧边栏导航（当前分类高亮）
    nav_html = build_sidebar_nav(cat_name)

    full_html = generate_html(title_text, cat_name, page_html, cat_name, desc_text, nav_html)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(full_html)

    generated_files.append(filename)
    sitemap_urls.append({
        'url': f"{BASE_URL}/{safe_name}.html",
        'lastmod': datetime.now().strftime('%Y-%m-%d'),
        'priority': '0.8' if len(cat_sites) >= 10 else '0.5'
    })

    if len(generated_files) % 10 == 0:
        print(f"  已生成 {len(generated_files)} 个页面...")

# ============ 生成 Sitemap ============
sitemap = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
'''
# 首页
sitemap += f'''  <url>
    <loc>{BASE_URL}/</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
'''

for su in sitemap_urls:
    sitemap += f'''  <url>
    <loc>{su['url']}</loc>
    <lastmod>{su['lastmod']}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>{su['priority']}</priority>
    <xhtml:link rel="alternate" hreflang="zh-CN" href="{su['url']}"/>
  </url>
'''

sitemap += "</urlset>"

with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
    f.write(sitemap)

# ============ 生成报告 ============
report = f"""# SEO预渲染报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 执行摘要

| 指标 | 数值 |
|------|------|
| 分类总数 | {len(categories)} |
| 生成页面 | {len(generated_files)} |
| Sitemap URL数 | {len(sitemap_urls)} |
| 错误数 | {len(errors)} |

## 生成的文件

"""
for f in generated_files:
    report += f"- `{f}`\n"

report += f"\n## Sitemap URL\n\n"
report += f"文件: `{SITEMAP_FILE}`\n\n"
for su in sitemap_urls:
    report += f"- {su['url']} (priority: {su['priority']})\n"

if errors:
    report += f"\n## 错误\n\n"
    for e in errors:
        report += f"- {e}\n"

# 保存预渲染URL列表供后续使用
prerendered_urls = [f"{BASE_URL}/{os.path.basename(f)}" for f in generated_files]
with open("prerendered_urls.json", 'w', encoding='utf-8') as f:
    json.dump(prerendered_urls, f, ensure_ascii=False, indent=2)

print(f"\n✅ 预渲染完成!")
print(f"   生成页面: {len(generated_files)} 个")
print(f"   Sitemap: {SITEMAP_FILE}")
print(f"   URL列表: prerendered_urls.json")