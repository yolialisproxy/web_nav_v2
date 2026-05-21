#!/usr/bin/env python3
"""
auto_dev_system.py - 自动化开发系统
支持命令:performance, git-analysis
"""
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

# Import Hermes tools
try:
    from hermes_tools import skill_view, read_file, write_file, terminal
except ImportError:
    # Fallback for when running outside Hermes environment
    def skill_view(*args, **kwargs):
        return {'status': 'error', 'message': 'hermes_tools not available'}
    def read_file(*args, **kwargs):
        return {'status': 'error', 'message': 'hermes_tools not available'}
    def write_file(*args, **kwargs):
        return {'status': 'error', 'message': 'hermes_tools not available'}
    def terminal(*args, **kwargs):
        return {'status': 'error', 'message': 'hermes_tools not available'}

import argparse

# 项目根目录 (必须与 cron 目标一致)
def get_project_root():
    """Get the project root based on script location"""
    return Path(__file__).parent.parent.resolve()

PROJECT_ROOT = get_project_root()
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
    """执行性能审计 - 非侵入式测量，不修改网站代码"""
    log("开始执行性能审计...")
    site_url = "https://yolialisproxy.github.io/web_nav_v2/"
    local_dir = PROJECT_ROOT
    report = {
        "timestamp": datetime.now().isoformat(),
        "site_url": site_url,
        "checks": {}
    }
    
    # 1. 检查关键文件大小
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
        else:
            report["checks"][f"file_size_{name}"] = None
    
    report["checks"]["total_critical_size"] = total_size
    
    # 2. 检查预渲染页面数量
    prerendered_dir = local_dir / 'prerendered'
    if prerendered_dir.exists():
        report["checks"]["prerendered_pages"] = len(list(prerendered_dir.glob('*.html')))
    else:
        report["checks"]["prerendered_pages"] = 0
    
    # 3. 检查JS资源计数与总大小
    js_dir = local_dir / 'assets' / 'js'
    if js_dir.exists():
        js_files = list(js_dir.rglob('*.js'))
        report["checks"]["js_files_count"] = len(js_files)
        report["checks"]["js_total_size"] = sum(f.stat().st_size for f in js_files)
    else:
        report["checks"]["js_files_count"] = 0
        report["checks"]["js_total_size"] = 0
    
    # 4. 检查图片资源
    images_dir = local_dir / 'assets' / 'images'
    if images_dir.exists():
        image_files = [f for f in images_dir.rglob('*') 
                       if f.is_file() and f.suffix in ['.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif']]
        report["checks"]["image_files_count"] = len(image_files)
        report["checks"]["image_total_size"] = sum(f.stat().st_size for f in image_files)
    else:
        report["checks"]["image_files_count"] = 0
        report["checks"]["image_total_size"] = 0
    
    # 5. 检查sitemap
    sitemap = local_dir / 'sitemap.xml'
    report["checks"]["sitemap_size"] = sitemap.stat().st_size if sitemap.exists() else None
    
    # 6. 检查关键SEO标签
    seo_checks = {}
    try:
        index_file = local_dir / 'index.html'
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                html = f.read()
                seo_checks = {
                    "has_meta_description": '<meta name="description"' in html,
                    "has_meta_keywords": '<meta name="keywords"' in html,
                    "has_canonical": 'rel="canonical"' in html,
                    "has_og_title": 'property="og:title"' in html,
                    "has_viewport": 'name="viewport"' in html,
                }
    except Exception:
        pass
    report["checks"]["seo_basic"] = seo_checks
    
    # 7. 计算性能评分
    score = 100
    if total_size > 500_000: score -= 10
    if report["checks"]["js_files_count"] > 20: score -= 5
    if report["checks"]["image_total_size"] > 5_000_000: score -= 10
    if not seo_checks.get("has_meta_description"): score -= 5
    report["performance_score"] = max(0, min(100, score))
    
    # 保存报告
    date_str = datetime.now().strftime('%Y%m%d')
    report_file = REPORTS_DIR / f'performance_audit_{date_str}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    log(f"性能审计完成，评分: {score}/100，报告: {report_file}")
    return report

def analyze_git():
    """分析Git提交历史 (最近10次)"""
    log("开始分析Git提交...")
    try:
        # 获取最近10次提交
        result = subprocess.run(
            ['git', 'log', '--oneline', '-10'],
            cwd=PROJECT_ROOT,
            capture_output=True, text=True
        )
        if result.returncode != 0:
            log(f"git log失败: {result.stderr}")
            return {"commits_analyzed": 0, "commits": [], "guidelines_generated": None}
        commits = [c for c in result.stdout.strip().split('\n') if c]
        log(f"最近{len(commits)}次提交")
        for commit in commits:
            log(f"  {commit}")
        
        # 生成开发准则文件
        guidelines = (
            f"# 开发准则\n\n"
            f"## 最近提交分析 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
            + "\n".join(f"- {c}" for c in commits) +
            "\n\n## 提交约定建议\n\n"
            "- 使用清晰的提交消息\n"
            "- 建议遵循约定式提交: <type>(<scope>): <description>\n"
            "- 主要type: feat, fix, docs, style, refactor, test, chore\n\n"
            "---\n*由 auto_dev_system.py git-analysis 自动生成*\n"
        )
        guidelines_file = PROJECT_ROOT / 'DEVELOPMENT_GUIDELINES.md'
        with open(guidelines_file, 'w', encoding='utf-8') as f:
            f.write(guidelines)
        log(f"开发准则已生成: {guidelines_file}")
        return {
            "commits_analyzed": len(commits),
            "commits": commits,
            "guidelines_generated": str(guidelines_file)
        }
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
    log(f"=== 任务完成: {args.command} ===")

if __name__ == '__main__':
    main()