#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ Flat Array 兼容性适配器 v1.0
让所有旧脚本无需修改就可以继续在新的扁平数组格式上工作
自动在新旧格式之间双向转换

使用方法:
import data_adapter as da
data = da.load_data()
da.save_data(data)
"""
import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data/websites.json"

def flatten(nested_data):
    """将旧嵌套格式转换为新扁平数组"""
    flat = []
    for major_cat in nested_data.get('categories', {}).values():
        major_name = major_cat.get('name', '')
        for sub_cat in major_cat.get('subcategories', []):
            sub_name = sub_cat.get('name', '')
            for item in sub_cat.get('sites', []):
                item['_cat'] = f"{major_name}/{sub_name}"
                flat.append(item)
    return flat

def nest(flat_data):
    """将新扁平数组转换为旧嵌套格式（供旧脚本使用）"""
    nested = {
        'categories': defaultdict(lambda: {
            'name': '',
            'subcategories': defaultdict(lambda: {
                'name': '',
                'sites': []
            })
        })
    }

    for item in flat_data:
        if '_cat' in item:
            parts = item['_cat'].split('/', 2)
            if len(parts) >= 2:
                major, sub = parts[0], parts[1]
                nested['categories'][major]['name'] = major
                nested['categories'][major]['subcategories'][sub]['name'] = sub
                nested['categories'][major]['subcategories'][sub]['sites'].append(item)

    # 转换为普通字典
    for major in nested['categories'].values():
        major['subcategories'] = list(major['subcategories'].values())
    nested['categories'] = list(nested['categories'].values())

    return nested

def load_data(nested=False):
    """加载数据，可选返回旧嵌套格式"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        flat = json.load(f)

    if nested:
        return nest(flat)
    return flat

def save_data(data):
    """保存数据，自动检测格式并转换为扁平数组"""
    if isinstance(data, dict) and 'categories' in data:
        # 这是旧嵌套格式，转换
        flat = flatten(data)
    else:
        flat = data

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(flat, f, ensure_ascii=False, indent=2)

    return len(flat)

if __name__ == "__main__":
    print("✅ 数据适配器加载成功")
    flat = load_data()
    print(f"   扁平数组: {len(flat)} 条记录")
    n = load_data(nested=True)
    print(f"   嵌套格式: {len(n['categories'])} 个大类")
