#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 导航网站批量内容补完后台工作进程

'''
---
## ⚠️ 补充细节（本部分由 document-detail-complement 自动添加）

### ❌ 绝对禁止
1. ❌ 禁止直接在对话循环中手动启动：必须使用 nohup 或后台进程运行，否则会因为 Telegram 超时或会话中断导致进程被杀，造成数据不完整。
2. ❌ 禁止在运行期间手动编辑 websites.json：脚本采用原子写入模式，手动编辑会导致文件锁冲突或数据覆盖。
3. ❌ 禁止将 BATCH_SIZE 调至 500 以上：会导致大量 429 (Too Many Requests) 错误，甚至触发目标网站的 IP 封禁。

### 🚩 失败征兆
如果出现以下情况，说明进程已失效或陷入死循环，请立即 kill 并重启：
- 🚩 进度停滞：enrichment_progress.json 中的 processed 数值在 30 分钟内没有变化。
- 🚩 日志报错激增：enrichment_worker.log 中出现连续 50 条以上的 ConnectionError 或 Timeout。
- 🚩 内存异常：ps aux 显示 python 进程内存占用超过 2GB（可能发生了内存泄漏）。

### ✅ 验收标准
只有满足以下所有条件，才能认为本补完任务完成：
1. ✅ enrichment_progress.json 中的 progress_pct 达到 100%。
2. ✅ 运行 scripts/audit_quality.py data/websites.json 确认 标题缺失率 <<  1% 且 描述缺失率 <<  1%。
3. ✅ /home/yoli/GitHub/web_nav_v2/data/backups/ 下存在至少一个完备的最终备份文件。

### 💀 历史踩坑记录
- [2026-04-14] 发现由于缺乏 User-Agent 导致 40% 的站点被拦截；已通过配置 USER_AGENT 修复。
- [2026-04-14] 发现部分站点使用非 UTF-8 编码导致 resp.text() 崩溃；已通过 errors="ignore" 修复。
---
'''

# 工业级执行标准: 断点续传、原子写入、错误隔离、进度持久化、静默运行

import json
import asyncio
import aiohttp
import time
import logging
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

# ========== 配置常量 ==========
BATCH_SIZE = 120
REQUEST_TIMEOUT = 8
MAX_RETRIES = 2
BATCH_DELAY = 4
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

# 路径配置
STATE_DIR = Path.home() / ".hermes" / "state"
STATE_FILE = STATE_DIR / "enrichment_progress.json"
DATA_FILE = Path("/home/yoli/GitHub/web_nav_v2/data/websites.json")
BACKUP_DIR = Path("/home/yoli/GitHub/web_nav_v2/data/backups")
LOG_FILE = STATE_DIR / "enrichment_worker.log"

# ========== 初始化 ==========
STATE_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== 状态管理 ==========
def load_state() -> Dict[str, Any]:
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            logger.warning("状态文件损坏，从初始状态启动")
    return {
        "processed": 0,
        "success": 0,
        "failed": 0,
        "total_sites": 0,
        "last_run": 0,
        "start_time": time.time(),
        "status": "running"
    }

def save_state(state: Dict[str, Any]) -> None:
    state["last_updated"] = time.time()
    if state["total_sites"] > 0:
        state["progress_pct"] = round(100 * state["processed"] / state["total_sites"], 2)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

# ========== 网页抓取 ==========
async def fetch_site_metadata(session: aiohttp.ClientSession, url: str) -> Optional[Dict[str, str]]:
    for attempt in range(MAX_RETRIES):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT), headers={"User-Agent": USER_AGENT}) as resp:
                if resp.status != 200:
                    await asyncio.sleep(0.5 + attempt)
                    continue

                raw_html = await resp.text(errors="ignore")

                result = {}

                # 快速解析标题
                title_start = raw_html.lower().find("<title>")
                title_end = raw_html.lower().find("</title>")
                if title_start != -1 and title_end != -1 and title_end > title_start:
                    title = raw_html[title_start+7:title_end].strip()
                    if 2 < len(title) < 70:
                        result["title"] = title

                # 快速解析描述
                desc_pos = raw_html.lower().find('<meta name="description"')
                if desc_pos != -1:
                    content_start = raw_html.lower().find('content="', desc_pos)
                    if content_start != -1:
                        content_end = raw_html.find('"', content_start+9)
                        if content_end != -1:
                            desc = raw_html[content_start+9:content_end].strip()
                            if 10 < len(desc) < 200:
                                result["description"] = desc

                if result:
                    return result

        except Exception:
            await asyncio.sleep(1 + attempt)
            continue

    return None

# ========== 备份与原子写入 ==========
def atomic_write_data(data: Any) -> None:
    backup_file = BACKUP_DIR / f"websites_{int(time.time())}.json.bak"
    shutil.copy2(DATA_FILE, backup_file)

    temp_file = DATA_FILE.with_suffix(".tmp")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    temp_file.replace(DATA_FILE)
    logger.info(f"✅ 备份已创建: {backup_file.name}")

# ========== 主工作循环 ==========
async def main():
    logger.info("=" * 60)
    logger.info("🚀 WebNav 内容补完工作进程启动")
    logger.info(f"📂 数据文件: {DATA_FILE}")
    logger.info(f"📊 状态文件: {STATE_FILE}")
    logger.info("=" * 60)

    state = load_state()

    while True:
        # 加载当前数据
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            full_data = json.load(f)

        # 收集待处理站点
        targets = []
        total_count = 0

        # 遍历数据结构
        for cat in full_data:
            if not isinstance(cat, dict) or 'subcategories' not in cat: continue
            for sub in cat['subcategories']:
                if 'minor_categories' not in sub: continue
                for minor in sub['minor_categories']:
                    if 'sites' not in minor: continue
                    for site in minor['sites']:
                        total_count += 1
                        if not site.get('title') and len(targets) < BATCH_SIZE:
                            targets.append(site)

        state["total_sites"] = total_count

        if not targets:
            logger.info("✅ 所有站点处理完成，工作进程正常退出")
            state["status"] = "completed"
            state["finish_time"] = time.time()
            save_state(state)
            return

        logger.info(f"🔄 处理批次: {len(targets)} 个站点 | 已处理: {state['processed']} | 进度: {state.get('progress_pct', 0)}%")

        # 执行批量抓取
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=30, ttl_dns_cache=300)) as session:
            tasks = [fetch_site_metadata(session, s["url"]) for s in targets]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        success = 0
        failed = 0

        # 写入结果
        for site, meta in zip(targets, results):
            if meta and isinstance(meta, dict):
                if "title" in meta:
                    site["title"] = meta["title"]
                if "description" in meta:
                    site["description"] = meta["description"]
                success += 1
            else:
                failed += 1

        # 原子写入磁盘
        atomic_write_data(full_data)

        # 更新状态
        state["processed"] += len(targets)
        state["success"] += success
        state["failed"] += failed
        state["last_run"] = time.time()
        save_state(state)

        logger.info(f"✅ 批次完成: 成功 {success} | 失败 {failed} | 总进度 {state['progress_pct']}%")
        logger.info("")

        await asyncio.sleep(BATCH_DELAY)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ 工作进程收到停止信号，安全退出")
        state = load_state()
        state["status"] = "interrupted"
        save_state(state)
    except Exception as e:
        logger.exception(f"❌ 工作进程异常: {e}")
        state = load_state()
        state["status"] = "error"
        state["error"] = str(e)
        save_state(state)
