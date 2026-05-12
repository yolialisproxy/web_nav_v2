#!/usr/bin/env python3
"""
perf_test.py — 啃魂导航站性能测试小工具

灵感来源：rtk-ai/rtk（GitHub Trending Rust #1, 993 stars/day）
核心思路：模块化 CLI 设计 + 精准性能度量 + 清晰的错误处理

功能：
  1. 通过 Playwright 无头浏览器加载导航站
  2. 采集首屏加载、TTI、资源加载耗时等关键指标
  3. 支持多次运行取平均值，可设置阈值告警
  4. 输出 JSON 报告或终端摘要

用法：
  python tools/perf_test.py                     # 默认单次运行
  python tools/perf_test.py -n 5                # 运行 5 次取均值
  python tools/perf_test.py --threshold 3.0     # 设置 LCP 阈值（秒）
  python tools/perf_test.py --report report.json # 输出 JSON 报告
  python tools/perf_test.py --tracing           # 生成 Chrome trace 文件
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# 自动检测 Playwright 路径
# ---------------------------------------------------------------------------

def find_playwright():
    """从系统路径中定位 Playwright"""
    import importlib
    for mod_path in [
        '/usr/lib/python3.14/site-packages',
    ]:
        if mod_path not in sys.path:
            sys.path.insert(0, mod_path)
    try:
        from playwright.sync_api import sync_playwright
        return sync_playwright
    except ImportError:
        pass
    try:
        from playwright.sync_api import sync_playwright
        return sync_playwright
    except ImportError:
        pass
    # 回退：尝试自动导入
    try:
        import playwright
        from playwright.sync_api import sync_playwright
        return sync_playwright
    except ImportError:
        print("❌ 找不到 Playwright。请运行: pip install playwright && playwright install chromium", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

@dataclass
class PerfMetrics:
    """单次运行的性能指标"""
    navigation_ms: float = 0.0
    dom_content_loaded_ms: float = 0.0
    load_event_ms: float = 0.0
    first_contentful_paint_ms: float = 0.0
    largest_contentful_paint_ms: float = 0.0
    total_blocking_time_ms: float = 0.0
    js_heap_used_mb: float = 0.0
    resource_count: int = 0
    resource_total_bytes: int = 0
    time_to_interactive_ms: float = 0.0
    errors: list = field(default_factory=list)


@dataclass
class PerfReport:
    """汇总的性能报告"""
    url: str = ""
    runs: int = 0
    avg_navigation_ms: float = 0.0
    avg_dom_content_loaded_ms: float = 0.0
    avg_load_event_ms: float = 0.0
    avg_fcp_ms: float = 0.0
    avg_lcp_ms: float = 0.0
    avg_total_blocking_time_ms: float = 0.0
    avg_js_heap_mb: float = 0.0
    avg_tti_ms: float = 0.0
    avg_resource_count: int = 0
    avg_resource_bytes: int = 0
    threshold_lcp_ms: float = 0.0
    lcp_pass: bool = True
    all_metrics: list = field(default_factory=list)
    errors: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# 核心度量引擎
# ---------------------------------------------------------------------------

def _inject_perf_observers(page):
    """注入 Performance Observer 以采集客户端性能指标"""
    return page.evaluate("""
    () => {
        return new Promise((resolve) => {
            const results = {};
            const errors = [];

            // Largest Contentful Paint
            try {
                const lcpObserver = new PerformanceObserver((list) => {
                    try {
                        const entries = list.getEntries();
                        if (entries.length > 0) {
                            const last = entries[entries.length - 1];
                            results.lcp = last.renderTime || last.loadTime || last.startTime;
                        }
                    } catch (e) { errors.push('LCP observer: ' + e.message); }
                });
                lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
            } catch (e) { errors.push('LCP setup: ' + e.message); }

            // First Contentful Paint
            try {
                const fcpObserver = new PerformanceObserver((list) => {
                    try {
                        const entries = list.getEntries();
                        if (entries.length > 0) {
                            results.fcp = entries[0].startTime;
                        }
                    } catch (e) { errors.push('FCP observer: ' + e.message); }
                });
                fcpObserver.observe({ type: 'paint', buffered: true });
            } catch (e) { errors.push('FCP setup: ' + e.message); }

            // Total Blocking Time (Long Tasks)
            let tbt = 0;
            try {
                const longTaskObserver = new PerformanceObserver((list) => {
                    try {
                        for (const entry of list.getEntries()) {
                            tbt += entry.duration;
                        }
                        results.tbt = tbt;
                    } catch (e) { errors.push('TBT observer: ' + e.message); }
                });
                longTaskObserver.observe({ type: 'longtask', buffered: true });
            } catch (e) { errors.push('TBT setup: ' + e.message); }

            // 等待足够时间让所有指标收集完毕
            setTimeout(() => {
                try {
                    const nav = performance.getEntriesByType('navigation')[0];
                    if (nav) {
                        results.navigation = nav.duration;
                        results.domContentLoaded = nav.domContentLoadedEventEnd - nav.startTime;
                        results.loadEvent = nav.loadEventEnd - nav.startTime;
                    }
                } catch (e) { errors.push('Navigation timing: ' + e.message); }

                try {
                    if (performance.memory) {
                        results.jsHeapUsed = Math.round(
                            (performance.memory.usedJSHeapSize / (1024 * 1024)) * 100
                        ) / 100;
                    }
                } catch (e) { /* memory API may not be available */ }

                try {
                    results.resourceCount = performance.getEntriesByType('resource').length;
                } catch (e) { /* ignore */ }

                // TTI 近似估算：最后一个长任务结束时间
                results.tti = results.tbt ? parseFloat(results.tbt.toFixed(0)) : 0;

                resolve({ metrics: results, errors });
            }, 3500);
        });
    }
    """)


def run_single_test(page, url: str, trace: bool = False) -> PerfMetrics:
    """执行单次性能测试并采集指标"""
    metrics = PerfMetrics()
    resources = []

    def on_response(response):
        try:
            resources.append({
                "url": response.url,
                "status": response.status,
                "size": int(response.headers.get("content-length", 0) or 0),
            })
        except Exception:
            pass

    page.on("response", on_response)

    try:
        # 启用网络空闲等待
        page.goto(url, wait_until="load", timeout=15000)
        # 额外等待 JS 执行完成
        page.wait_for_timeout(2000)

        client_result = _inject_perf_observers(page)
        client_metrics = client_result.get("metrics", {})
        client_errors = client_result.get("errors", [])

        metrics.navigation_ms = round(client_metrics.get("navigation", 0), 1)
        metrics.dom_content_loaded_ms = round(client_metrics.get("domContentLoaded", 0), 1)
        metrics.load_event_ms = round(client_metrics.get("loadEvent", 0), 1)
        metrics.first_contentful_paint_ms = round(client_metrics.get("fcp", 0), 1)
        metrics.largest_contentful_paint_ms = round(client_metrics.get("lcp", 0), 1)
        metrics.total_blocking_time_ms = round(client_metrics.get("tbt", 0), 1)
        metrics.time_to_interactive_ms = round(client_metrics.get("tti", 0), 1)
        metrics.js_heap_used_mb = round(client_metrics.get("jsHeapUsed", 0), 2)
        metrics.resource_count = client_metrics.get("resourceCount", 0)
        metrics.errors.extend(client_errors)

        # 计算资源总字节数
        total_bytes = 0
        for r in resources:
            try:
                total_bytes += int(r.get("size", 0) or 0)
            except (ValueError, TypeError):
                pass
        metrics.resource_total_bytes = total_bytes

        # 生成 trace（可选）
        if trace:
            try:
                trace_path = Path("perf-trace-timeline.json")
                page.tracing.stop(path=str(trace_path))
                print(f"  [TRACE] 已保存 trace 文件: {trace_path}")
            except Exception as e:
                metrics.errors.append(f"Trace error: {e}")

    except Exception as e:
        err_msg = f"运行时错误: {type(e).__name__}: {e}"
        metrics.errors.append(err_msg)

    return metrics


def run_perf_tests(
    url: str,
    runs: int = 1,
    threshold_lcp_ms: float = 3000.0,
    trace: bool = False,
    server_proc=None,
    chromium_path: str = None,
) -> PerfReport:
    """运行多次性能测试并汇总结果"""
    find_playwright()
    from playwright.sync_api import sync_playwright

    report = PerfReport(
        url=url,
        runs=runs,
        threshold_lcp_ms=threshold_lcp_ms,
    )

    launch_opts = {"headless": True, "args": ["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]}
    if chromium_path:
        launch_opts["executable_path"] = chromium_path

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_opts)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
        )
        page = context.new_page()

        if server_proc:
            time.sleep(1.5)

        print(f"\n{'='*60}")
        print(f"🔬 开始性能测试: {url}")
        print(f"   运行次数: {runs}")
        if trace:
            print(f"   Tracing: 已启用")
        print(f"{'='*60}\n")

        for i in range(runs):
            print(f"  [{i+1}/{runs}] 运行中...", end=" ", flush=True)

            if trace and i == 0:
                try:
                    page.tracing.start(screenshots=True, snapshots=True)
                except Exception:
                    pass

            m = run_single_test(page, url, trace=(trace and i == 0))
            report.all_metrics.append(asdict(m))

            if m.errors:
                report.errors.extend(m.errors)
                print(f"⚠️  有错误: {m.errors}")
            else:
                print(
                    f"✅ 导航={m.navigation_ms:.0f}ms  "
                    f"DCL={m.dom_content_loaded_ms:.0f}ms  "
                    f"Load={m.load_event_ms:.0f}ms  "
                    f"FCP={m.first_contentful_paint_ms:.0f}ms  "
                    f"LCP={m.largest_contentful_paint_ms:.0f}ms  "
                    f"TBT={m.total_blocking_time_ms:.0f}ms"
                )

        browser.close()

    # 计算均值
    valid = [m for m in report.all_metrics if not m.get("errors")]
    if valid:
        n = len(valid)
        report.avg_navigation_ms = round(sum(m.get("navigation_ms", 0) for m in valid) / n, 1)
        report.avg_dom_content_loaded_ms = round(sum(m.get("dom_content_loaded_ms", 0) for m in valid) / n, 1)
        report.avg_load_event_ms = round(sum(m.get("load_event_ms", 0) for m in valid) / n, 1)
        report.avg_fcp_ms = round(sum(m.get("first_contentful_paint_ms", 0) for m in valid) / n, 1)
        report.avg_lcp_ms = round(sum(m.get("largest_contentful_paint_ms", 0) for m in valid) / n, 1)
        report.avg_total_blocking_time_ms = round(sum(m.get("total_blocking_time_ms", 0) for m in valid) / n, 1)
        report.avg_tti_ms = round(sum(m.get("time_to_interactive_ms", 0) for m in valid) / n, 1)
        report.avg_js_heap_mb = round(sum(m.get("js_heap_used_mb", 0) for m in valid) / n, 2)

        total_resources = sum(m.get("resource_count", 0) for m in valid)
        report.avg_resource_count = total_resources // n if n > 0 else 0
        total_bytes = sum(m.get("resource_total_bytes", 0) for m in valid)
        report.avg_resource_bytes = total_bytes // n if n > 0 else 0
    else:
        report.errors.append("所有运行均有错误，无法计算均值")

    # 阈值检查
    report.lcp_pass = report.avg_lcp_ms <= threshold_lcp_ms

    return report


# ---------------------------------------------------------------------------
# 报告输出
# ---------------------------------------------------------------------------

def print_summary(report: PerfReport):
    """终端摘要输出（参考 rtk 的简洁表格风格）"""
    print(f"\n{'='*60}")
    print("📊 性能测试报告")
    print(f"{'='*60}")
    print(f"  URL:            {report.url}")
    print(f"  运行次数:       {report.runs}")
    print(f"{'─'*40}")
    print(f"  首屏加载:       {report.avg_navigation_ms:.0f} ms")
    print(f"  DOM 完成:       {report.avg_dom_content_loaded_ms:.0f} ms")
    print(f"  Load 事件:      {report.avg_load_event_ms:.0f} ms")
    print(f"  首屏内容绘制(FCP): {report.avg_fcp_ms:.0f} ms")
    print(f"  最大内容绘制(LCP): {report.avg_lcp_ms:.0f} ms")
    print(f"  总阻塞时间(TBT):   {report.avg_total_blocking_time_ms:.0f} ms")
    print(f"  近似 TTI:        {report.avg_tti_ms:.0f} ms")
    print(f"  JS 堆内存:       {report.avg_js_heap_mb:.1f} MB")
    print(f"  资源数量:        {report.avg_resource_count}")
    print(f"  资源总大小:      {report.avg_resource_bytes / 1024:.1f} KB")
    print(f"{'─'*40}")

    # LCP 阈值判断
    status = "✅ PASS" if report.lcp_pass else "❌ FAIL"
    print(f"  LCP 阈值 ({report.threshold_lcp_ms:.0f}ms): {status}")
    print(f"{'='*60}")

    if report.errors:
        print(f"\n⚠️  错误列表:")
        seen = set()
        for err in report.errors:
            if err not in seen:
                print(f"    - {err}")
                seen.add(err)

    # 性能建议
    if report.avg_lcp_ms > 3000:
        print("\n💡 建议: LCP 超过 3s，考虑优化图片加载或减少首屏 JS 体积")
    elif report.avg_lcp_ms > 2500:
        print("\n💡 提示: LCP 接近 2.5s，可以进一步优化首屏渲染")
    if report.avg_total_blocking_time_ms > 300:
        print("💡 建议: TBT 超过 300ms，考虑代码分割或延迟加载非关键 JS")
    if report.avg_resource_bytes > 500 * 1024:
        print("💡 建议: 首屏资源超过 500KB，考虑启用 Gzip/Brotli 压缩")


# ---------------------------------------------------------------------------
# 主程序
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="啃魂导航站性能测试工具（基于 Playwright）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python tools/perf_test.py
  python tools/perf_test.py -n 3 --threshold 2500
  python tools/perf_test.py --report perf_report.json --tracing
        """,
    )
    parser.add_argument(
        "-u", "--url",
        default="http://localhost:8080",
        help="导航站 URL (默认: http://localhost:8080)",
    )
    parser.add_argument(
        "-n", "--runs",
        type=int,
        default=1,
        help="运行次数 (默认: 1)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=3000.0,
        help="LCP 阈值（毫秒），超过则标记为 FAIL (默认: 3000)",
    )
    parser.add_argument(
        "--report",
        type=str,
        default=None,
        help="JSON 报告输出路径",
    )
    parser.add_argument(
        "--tracing",
        action="store_true",
        help="生成 Chrome trace 文件（仅第一次运行）",
    )
    parser.add_argument(
        "--chromium-path",
        type=str,
        default=None,
        help="Chromium 可执行文件路径（自动检测时用）",
    )

    args = parser.parse_args()

    # 尝试自动检测 Chromium
    chromium_path = args.chromium_path
    if not chromium_path:
        default_paths = [
            "/home/yoli/.cache/ms-playwright/chromium-1217/chrome-linux64/chrome",
        ]
        for p in default_paths:
            if os.path.isfile(p) and os.access(p, os.X_OK):
                chromium_path = p
                break

    # 检查服务是否运行
    server_proc = None
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_running = sock.connect_ex(("localhost", 8080)) == 0
    sock.close()

    if not server_running:
        print("🟡 服务未启动，正在自动启动 serve.py...")
        server_proc = subprocess.Popen(
            [sys.executable, "serve.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)) or ".",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    try:
        report = run_perf_tests(
            url=args.url,
            runs=args.runs,
            threshold_lcp_ms=args.threshold,
            trace=args.tracing,
            server_proc=server_proc,
            chromium_path=chromium_path,
        )

        print_summary(report)

        # 输出 JSON 报告
        if args.report:
            report_path = Path(args.report)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(asdict(report), f, ensure_ascii=False, indent=2)
            print(f"\n📄 JSON 报告已保存: {report_path}")

        # 退出码
        if not report.lcp_pass or (report.errors and not all("optional" in e for e in report.errors)):
            sys.exit(1)
        sys.exit(0)

    finally:
        if server_proc:
            print("\n🛑 正在关闭测试服务...")
            server_proc.terminate()
            try:
                server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc.kill()


if __name__ == "__main__":
    main()