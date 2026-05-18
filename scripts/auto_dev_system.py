#!/usr/bin/env python3
"""
auto_dev_system.py - 自动化开发系统
支持命令：performance, git-analysis
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 项目根目录（必须在cwd中设置或硬编码）
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
LOGS_DIR = PROJECT_ROOT / 'logs'
REPORTS_DIR = PROJECT_ROOT / 'performance_reports'
BASELINE_DIR = PROJECT_ROOT / 'performance_baselines'

def ensure_dirs():
    """确保必要的目录存在"""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)

def log(message):
    """追加日志"""
    log_file = LOGS_DIR / 'auto_dev_system.log'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")

def audit_performance():
    """执行性能审计"""
    log("开始执行性能审计...")
    
    site_url = "https://yolialisproxy.github.io/web_nav_v2/"
    local_dir = PROJECT_ROOT
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "site_url": site_url,
        "checks": {}
    }
    
    # 1. 检查关键文件大小
    log("检查文件大小...")
    key_files = {
        'index.html': local_dir / 'index.html',
        'core.css': local_dir / 'assets' / 'css' / 'core.css',
        'app.css': local_dir / 'assets' / 'css' / 'app.css',
    }
    
    total_size = 0
    for name, path in key_files.items():
        if path.exists():
            size = path.stat().st_size
            total_size += size
            report["checks"][f"file_size_{name}"] = size
            status = "OK" if size < 500_000 else "WARNING"
            log(f"  {name}: {size:,} bytes [{status}]")
        else:
            report["checks"][f"file_size_{name}"] = None
            log(f"  {name}: MISSING")
    
    report["checks"]["total_critical_size"] = total_size
    
    # 2. 检查预渲染页面数量
    prerendered_dir = local_dir / 'prerendered'
    if prerendered_dir.exists():
        prerendered_count = len(list(prerendered_dir.glob('*.html')))
        report["checks"]["prerendered_pages"] = prerendered_count
        log(f"预渲染页面: {prerendered_count}")
    else:
        report["checks"]["prerendered_pages"] = 0
        log("预渲染目录不存在")
    
    # 3. 检查JS资源
    js_dir = local_dir / 'assets' / 'js'
    if js_dir.exists():
        js_files = list(js_dir.rglob('*.js'))
        total_js_size = sum(f.stat().st_size for f in js_files)
        report["checks"]["js_files_count"] = len(js_files)
        report["checks"]["js_total_size"] = total_js_size
        log(f"JS文件: {len(js_files)}个, 总大小: {total_js_size:,} bytes")
    else:
        report["checks"]["js_files_count"] = 0
        report["checks"]["js_total_size"] = 0
        log("JS目录不存在")
    
    # 4. 检查图片资源
    images_dir = local_dir / 'assets' / 'images'
    if images_dir.exists():
        image_files = list(images_dir.rglob('*'))
        image_files = [f for f in image_files if f.is_file() and f.suffix in ['.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif']]
        total_img_size = sum(f.stat().st_size for f in image_files)
        report["checks"]["image_files_count"] = len(image_files)
        report["checks"]["image_total_size"] = total_img_size
        log(f"图片文件: {len(image_files)}个, 总大小: {total_img_size:,} bytes")
    else:
        report["checks"]["image_files_count"] = 0
        report["checks"]["image_total_size"] = 0
        log("图片目录不存在")
    
    # 5. 检查sitemap
    sitemap = local_dir / 'sitemap.xml'
    if sitemap.exists():
        sitemap_size = sitemap.stat().st_size
        report["checks"]["sitemap_size"] = sitemap_size
        log(f"Sitemap: {sitemap_size:,} bytes")
    else:
        report["checks"]["sitemap_size"] = None
        log("Sitemap不存在")
    
    # 6. 检查关键SEO标签
    log("检查SEO基础标签...")
    seo_checks = {}
    try:
        with open(local_dir / 'index.html', 'r', encoding='utf-8') as f:
            html = f.read()
            seo_checks = {
                "has_meta_description": '<meta name="description"' in html,
                "has_meta_keywords": '<meta name="keywords"' in html,
                "has_canonical": 'rel="canonical"' in html,
                "has_og_title": 'property="og:title"' in html,
                "has_viewport": 'name="viewport"' in html
            }
    except Exception as e:
        log(f"读取HTML失败: {e}")
    
    report["checks"]["seo_basic"] = seo_checks
    
    # 7. 计算性能评分
    score = 100
    if total_size > 500_000:
        score -= 10
    if report["checks"]["js_files_count"] > 20:
        score -= 5
    if report["checks"]["image_total_size"] > 5_000_000:
        score -= 10
    if seo_checks.get("has_meta_description") is False:
        score -= 5
    
    report["performance_score"] = max(0, min(100, score))
    
    # 保存报告
    date_str = datetime.now().strftime('%Y%m%d')
    report_file = REPORTS_DIR / f'performance_audit_{date_str}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    log(f"性能审计完成，评分: {score}/100，报告: {report_file}")
    return report

def analyze_git():
    """分析Git提交历史"""
    log("开始分析Git提交...")
    
    try:
        # 获取最近10次提交
        result = subprocess.run(
            ['git', 'log', '--oneline', '-10'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            log(f"git log失败: {result.stderr}")
            return
        
        commits = result.stdout.strip().split('\n')
        log(f"最近{len(commits)}次提交:")
        for commit in commits:
            log(f"  {commit}")
        
        # 分析提交模式
        commit_types = {}
        for commit in commits:
            parts = commit.split()
            if parts:
                commit_type = parts[0][:7]  # 使用短哈希
                commit_types[commit_type] = commit_types.get(commit_type, 0) + 1
        
        log(f"提交类型分布: {commit_types}")
        
        # 生成开发准则文件
        guidelines = f"""# 开发准则

## 最近提交分析 ({datetime.now().strftime('%Y-%m-%d')})

- 最近10次提交:
{chr(10).join(f"  - {c}" for c in commits)}

## 提交约定建议

- 使用清晰的提交消息
- 建议遵循约定式提交: <type>(<scope>): <description>
- 主要type: feat, fix, docs, style, refactor, test, chore

---
*由 auto_dev_system.py git-analysis 自动生成*
"""
        
        guidelines_file = PROJECT_ROOT / 'DEVELOPMENT_GUIDELINES.md'
        with open(guidelines_file, 'w', encoding='utf-8') as f:
            f.write(guidelines)
        
        log(f"开发准则已生成: {guidelines_file}")
        
        analysis = {
            "commits_analyzed": len(commits),
            "commits": commits,
            "guidelines_generated": str(guidelines_file)
        }
        return analysis
        
    except Exception as e:
        log(f"Git分析失败: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="自动化开发系统")
    parser.add_argument('command', choices=['performance', 'git-analysis'],
                       help='要执行的命令')
    args = parser.parse_args()
    
    ensure_dirs()
    log(f"=== 任务开始: {args.command} ===")
    
    if args.command == 'performance':
        report = audit_performance()
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.command == 'git-analysis':
        result = analyze_git()
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("Git分析完成，请查看日志")
    
    log(f"=== 任务完成: {args.command} ===")

if __name__ == '__main__':
    main()
