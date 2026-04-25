#!/usr/bin/env python3
"""
执行剩余1,823站健康检查
- 读取 websites.json
- 合并已检查索引（v12_health_chunk[1-4] + v13_health_sample）
- 对剩余未检索引执行批量HEAD检查（aiohttp并发15，超时5s）
- 保存结果到 v13_health_remaining.json
"""

import json
import asyncio
import aiohttp
import time
from pathlib import Path
from typing import Set, List, Dict, Tuple

# 配置
BASE_DIR = Path("/home/yoli/GitHub/web_nav_v2")
DATA_DIR = BASE_DIR / "data"
WEBSITES_FILE = BASE_DIR / "websites.json"
OUTPUT_FILE = DATA_DIR / "v13_health_remaining.json"

CONCURRENT_LIMIT = 15
TIMEOUT = 5

# 加载websites.json
print("正在加载 websites.json...")
with open(WEBSITES_FILE, 'r', encoding='utf-8') as f:
    websites = json.load(f)

total_sites = len(websites)
print(f"总网站数: {total_sites}")

# 收集所有已检查的索引
checked_indices: Set[int] = set()

# 从v12_health_chunk[1-4]加载已检查索引
print("\n正在合并 v12_health_chunk 数据...")
for i in range(1, 5):
    chunk_file = DATA_DIR / f"v12_health_chunk{i}.json"
    if chunk_file.exists():
        with open(chunk_file, 'r', encoding='utf-8') as f:
            chunk_data = json.load(f)

        chunk_range = chunk_data.get('range', [0, 0])
        healthy_list = chunk_data.get('healthy', [])

        start, end = chunk_range
        for idx in range(start, end):
            checked_indices.add(idx)

        print(f"  v12_health_chunk{i}.json: 范围[{start}, {end})，累计已检查索引 {len(checked_indices)} 个")
    else:
        print(f"  警告: {chunk_file} 不存在")

# 从v13_health_sample加载已检查索引
print("\n正在合并 v13_health_sample 数据...")
sample_file = DATA_DIR / "v13_health_sample.json"
if sample_file.exists():
    with open(sample_file, 'r', encoding='utf-8') as f:
        sample_data = json.load(f)

    sample_indices = sample_data.get('sample_indices', [])
    checked_indices.update(sample_indices)
    print(f"  v13_health_sample.json: 添加 {len(sample_indices)} 个样本索引")
else:
    print(f"  警告: {sample_file} 不存在")

print(f"\n已检查索引总数: {len(checked_indices)}")
print(f"已检查索引范围: {min(checked_indices) if checked_indices else 'N/A'} - {max(checked_indices) if checked_indices else 'N/A'}")

# 找出剩余未检查的索引
remaining_indices = [i for i in range(total_sites) if i not in checked_indices]
remaining_count = len(remaining_indices)
print(f"\n剩余未检查站点数: {remaining_count}")
print(f"剩余索引范围: {min(remaining_indices) if remaining_indices else 'N/A'} - {max(remaining_indices) if remaining_indices else 'N/A'}")

if remaining_count == 0:
    print("没有剩余的站点需要检查，退出。")
    exit(0)

# 准备要检查的URL列表
sites_to_check: List[Tuple[int, str]] = []
for idx in remaining_indices:
    if idx < len(websites):
        site = websites[idx]
        url = site.get('url', '')
        if url:
            sites_to_check.append((idx, url))

print(f"实际需要检查的URL数: {len(sites_to_check)}")

# 异步HEAD检查函数
semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)

async def check_url(session: aiohttp.ClientSession, index: int, url: str) -> Tuple[int, bool, str]:
    """检查单个URL，返回(index, is_healthy, error_msg)"""
    async with semaphore:
        try:
            async with session.head(url, allow_redirects=True, timeout=TIMEOUT) as response:
                is_healthy = 200 <= response.status < 400
                return (index, is_healthy, f"status={response.status}")
        except asyncio.TimeoutError:
            return (index, False, "timeout")
        except Exception as e:
            return (index, False, str(e))

async def batch_health_check():
    """执行批量健康检查"""
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    connector = aiohttp.TCPConnector(limit=CONCURRENT_LIMIT, ssl=False)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = [check_url(session, idx, url) for idx, url in sites_to_check]

        print(f"\n开始检查 {len(tasks)} 个站点（并发{CONCURRENT_LIMIT}，超时{TIMEOUT}s）...")
        start_time = time.time()

        results = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed = time.time() - start_time
        print(f"检查完成，耗时: {elapsed:.2f}秒")

        return results

# 运行检查
print("\n" + "="*60)
results = asyncio.run(batch_health_check())

# 处理结果
healthy_indices: List[int] = []
broken_indices: List[int] = []

for result in results:
    if isinstance(result, Exception):
        continue

    idx, is_healthy, msg = result
    if is_healthy:
        healthy_indices.append(idx)
    else:
        broken_indices.append(idx)

print(f"\n检查结果:")
print(f"  健康站点: {len(healthy_indices)}")
print(f"  失效站点: {len(broken_indices)}")
print(f"  总计: {len(healthy_indices) + len(broken_indices)}")

# 保存结果
output_data = {
    "healthy": healthy_indices,
    "broken": broken_indices,
    "total_checked": len(healthy_indices) + len(broken_indices),
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "config": {
        "concurrent": CONCURRENT_LIMIT,
        "timeout": TIMEOUT
    }
}

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"\n结果已保存到: {OUTPUT_FILE}")
print("="*60)
print("健康检查完成！")
