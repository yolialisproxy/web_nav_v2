import json
import os
from collections import defaultdict

BATCH_SIZE = 200
DATA_FILE = "websites.json"
PROGRESS_FILE = "enrich_progress.txt"
BACKUP_DIR = "websites_backup"

def get_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return int(f.read().strip())
    return 0

def save_progress(n):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        f.write(str(n))

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, batch_num):
    # 备份
    backup_path = os.path.join(BACKUP_DIR, f"batch_{batch_num}.json")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # 保存主文件
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def iterate_sites(data):
    for main_name, main_cat in data.items():
        for sub_idx, subcat in enumerate(main_cat.get('subcategories', [])):
            for minor_idx, minor_cat in enumerate(subcat.get('minor_categories', [])):
                for site_idx, site in enumerate(minor_cat.get('sites', [])):
                    yield site, (main_name, sub_idx, minor_idx, site_idx)

def is_need_enrich(site):
    title = site.get('title', '').strip()
    desc = site.get('description', '').strip()
    if not title:
        return True
    if title.startswith(('http://', 'https://', 'www.')):
        return True
    if not desc:
        return True
    return False

def main():
    progress = get_progress()
    data = load_data()

    sites_list = list(iterate_sites(data))
    total = len(sites_list)

    need_enrich = [(site, path) for site, path in sites_list if is_need_enrich(site)]

    batch_start = progress
    batch_end = min(batch_start + BATCH_SIZE, len(need_enrich))
    current_batch = (progress // BATCH_SIZE) + 1

    print(f"[进度] 已完成 {progress}/{total}，当前批次 {current_batch}，本批次处理 {batch_end - batch_start} 个，剩余约 {len(need_enrich) - batch_end} 个")

    # 处理本批次站点
    for i in range(batch_start, batch_end):
        site, path = need_enrich[i]
        url = site.get('url', '')

        # 临时测试填充模式（后续替换为真实web提取）
        domain = url.replace('https://','').replace('http://','').split('/')[0]
        if not site.get('title'):
            site['title'] = f"{domain} 官网"
        if not site.get('description'):
            site['description'] = f"{domain} 官方网站，提供对应服务与功能访问入口。"

    # 保存
    save_data(data, current_batch)
    save_progress(batch_end)

    print(f"[进度] 已完成 {batch_end}/{total}，批次 {current_batch} 完成，剩余约 {len(need_enrich) - batch_end} 个")

if __name__ == "__main__":
    main()
