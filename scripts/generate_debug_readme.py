#!/usr/bin/env python3
"""
generate_debug_readme.py - 每日调试日志汇总
自动扫描最近的 Git 提交、错误日志、issue，
并生成 README_DEBUG.md。
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEBUG_README = REPO_ROOT / "README_DEBUG.md"


def get_recent_commits(days=1):
    """获取最近 N 天的提交信息"""
    try:
        result = subprocess.run(
            ["git", "log", f"--since={days} days ago", "--oneline", "-30"],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=15
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception:
        return []


def get_debug_summary():
    """生成调试日志汇总"""
    known_issues = [
        {
            "issue": "Playwright 浏览器路径不匹配",
            "cause": "Python Playwright 驱动版本与已安装 Chromium 版本不一致",
            "fix": "创建符号链接 chromium_headless_shell-1217 -> chromium-1217，或用 executable_path 指定路径",
            "prevention": "固定 playwright 版本，使用 playwright install --with-deps chromium",
            "severity": "high",
            "category": "环境配置",
        },
        {
            "issue": "npm install 超时 (SOCKS 代理)",
            "cause": "HTTPS_PROXY/HTTP_PROXY 设置为 socks5:// 但 socks 模块未安装",
            "fix": "使用 NO_PROXY=* 或清除 proxy 设置，或使用 --registry 指定镜像",
            "prevention": "在 npm 配置中明确设置 proxy=none 或使用镜像源",
            "severity": "medium",
            "category": "网络/代理",
        },
        {
            "issue": "pip install playwright 失败 (SOCKS 依赖)",
            "cause": "pip 检测到 socks 相关依赖缺失",
            "fix": "使用系统级 Python 包 (pip install --break-system-packages) 或使用 uv",
            "prevention": "使用虚拟环境，避免系统包冲突",
            "severity": "medium",
            "category": "环境配置",
        },
        {
            "issue": "导航站页面加载超时 (networkidle)",
            "cause": "Playwright waitFor='networkidle' 在静态页面永远等待不到网络空闲",
            "fix": "改用 wait_until='load' + page.wait_for_timeout(2000)",
            "prevention": "性能测试工具统一使用 'load' 策略",
            "severity": "high",
            "category": "性能测试",
        },
        {
            "issue": "LCP 阈值单位错误",
            "cause": "args.threshold (秒) 被乘以 1000 变成毫秒，但阈值本身已经是 ms 值",
            "fix": "移除多余的 * 1000 转换",
            "prevention": "统一阈值单位为毫秒，命令行参数加单位说明",
            "severity": "low",
            "category": "Bug",
        },
        {
            "issue": "git push 被拒绝 (非快进)",
            "cause": "远程分支有本地没有的提交",
            "fix": "git pull --rebase origin master + git push",
            "prevention": "推送前先拉取，保持分支同步",
            "severity": "medium",
            "category": "Git",
        },
        {
            "issue": "文件移动/重命名导致 Git 误删",
            "cause": "Git 检测到旧路径文件被删除、新路径文件被创建",
            "fix": "使用 git add -A 自动检测重命名，或 git mv 明确移动",
            "prevention": "文件移动使用 git mv，避免手动删除+新建",
            "severity": "medium",
            "category": "Git",
        },
        {
            "issue": "GitHub Trending 页面无法直接抓取",
            "cause": "GitHub 页面需要登录状态，Proxy 连接失败",
            "fix": "通过搜索引擎间接获取 Trending 数据",
            "prevention": "使用 GitHub API 或第三方工具 (gh CLI, ossinsight)",
            "severity": "low",
            "category": "数据采集",
        },
        {
            "issue": "Git 提交信息自动审核规则冲突",
            "cause": "hooks 自动清理产生冲突",
            "fix": "检查 .git/hooks 配置，确保钩子不会删除需要的文件",
            "prevention": "提交前手动检查暂存区，重要文件加锁",
            "severity": "low",
            "category": "Git",
        },
    ]

    # 检查 git log 中的错误关键词
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-50", "--grep=fix|error|bug|repair|broken"],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=10
        )
        recent_fixes = [l for l in result.stdout.strip().split("\n") if l]
    except Exception:
        recent_fixes = []

    return known_issues, recent_fixes


def generate_readme():
    """生成 README_DEBUG.md"""
    issues, recent_fixes = get_debug_summary()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "# README_DEBUG.md - 啃魂导航站调试坑汇总",
        "",
        f"> 自动生成时间: {now}",
        f"> 更新频率: 每日 21:45 自动更新",
        f"> 来源: Git 提交日志 + 已知问题库",
        "",
        "---",
        "",
        "## 写代码前必读",
        "",
        "本文件记录了导航站开发和维护过程中遇到的典型 Bug、踩坑经验和解决方案。",
        "**每次开始编码前，请先阅读本文档，避免重复踩坑。**",
        "",
        "---",
        "",
        "## 高优先级问题",
        "",
    ]

    high = [i for i in issues if i["severity"] == "high"]
    for i, issue in enumerate(high, 1):
        lines.extend([
            f"### {i}. {issue['issue']}",
            f"- **分类**: {issue['category']}",
            f"- **原因**: {issue['cause']}",
            f"- **修复方案**: {issue['fix']}",
            f"- **预防措施**: {issue['prevention']}",
            "",
        ])

    lines.extend(["## 中优先级问题", ""])
    medium = [i for i in issues if i["severity"] == "medium"]
    for i, issue in enumerate(medium, 1):
        lines.extend([
            f"### {i}. {issue['issue']}",
            f"- **分类**: {issue['category']}",
            f"- **原因**: {issue['cause']}",
            f"- **修复方案**: {issue['fix']}",
            f"- **预防措施**: {issue['prevention']}",
            "",
        ])

    lines.extend(["## 低优先级问题", ""])
    low = [i for i in issues if i["severity"] == "low"]
    for i, issue in enumerate(low, 1):
        lines.extend([
            f"### {i}. {issue['issue']}",
            f"- **分类**: {issue['category']}",
            f"- **原因**: {issue['cause']}",
            f"- **修复方案**: {issue['fix']}",
            f"- **预防措施**: {issue['prevention']}",
            "",
        ])

    if recent_fixes:
        lines.extend(["## 最近修复的问题", ""])
        lines.extend([f"- {f}" for f in recent_fixes[:15]])
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 开发规范提醒",
        "",
        "1. **Playwright 使用**: `wait_until='load'` + `wait_for_timeout(2000)`，不要用 `networkidle`",
        "2. **阈值单位**: 统一用毫秒 (ms)，命令行参数需注明",
        "3. **文件操作**: 用 `git mv` 移动文件，避免手动删除+新建",
        "4. **推送前**: 先 `git pull --rebase`，再 `git push`",
        "5. **npm 安装**: 注意 SOCKS 代理问题，必要时用镜像源",
        "6. **数据文件**: websites.json > 10MB 时需分片处理",
        "",
        "---",
        f"*最后更新: {now}*",
    ])

    with open(DEBUG_README, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"README_DEBUG.md generated ({len(lines)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(generate_readme())