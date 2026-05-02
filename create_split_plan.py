#!/usr/bin/env python3
"""
Phase 2: AI Master Category Split Plan Generator
Goal: Redistribute 1101 AI sites from 30+ fragmented subcategories into 6-8 balanced coherent categories (max 50 each)
"""

import json
from collections import defaultdict
from datetime import datetime

# Load full dataset
with open('/home/yoli/GitHub/web_nav_v2/websites.json', 'r', encoding='utf-8') as f:
    sites = json.load(f)

# Get ALL AI sites
all_ai_sites = [s for s in sites if s.get('category', '').startswith('AI工具/人工智能')]
print(f"Total AI sites to reclassify: {len(all_ai_sites)}")

# NEW COHERENT CATEGORY STRUCTURE
# Based on semantic analysis of existing categories and industry standards
NEW_CATEGORIES = {
    'AI工具/人工智能/机器学习框架': {
        'description': 'TensorFlow, PyTorch, Keras, 等ML框架与开发库',
        'keywords': ['tensorflow', 'pytorch', 'keras', 'mxnet', 'caffe', 'jax', 'scikit', 'sklearn', 'mlflow', 'kubeflow', 'onnx', 'framework', 'library', '开发库', '框架'],
        'sites': []
    },
    'AI工具/人工智能/大语言模型': {
        'description': 'ChatGPT, Claude, 等大语言模型服务平台',
        'keywords': ['llm', 'large language model', 'gpt', 'claude', 'gemini', 'llama', 'mistral', 'qwen', 'deepseek', 'yi', 'baichuan', 'chatgpt', 'openai', 'anthropic', 'moonshot', 'zhipu', 'stepfun', 'huggingface', '模型'],
        'sites': []
    },
    'AI工具/人工智能/模型托管': {
        'description': 'Hugging Face, Replicate 等模型托管与部署平台',
        'keywords': ['hugging face', 'huggingface', 'replicate', 'model hub', 'model zoo', 'deploy', 'deployment', 'hosting', 'civitai', 'weights', 'checkpoint'],
        'sites': []
    },
    'AI工具/人工智能/AI基础设施': {
        'description': 'GPU云服务、算力平台、MLOps基础设施',
        'keywords': ['cloud', 'compute', 'gpu', 'tpu', 'aws', 'gcp', 'azure', 'kubernetes', 'docker', 'k8s', 'inference', 'serving', 'mlops', 'infrastructure', '平台', '算力', '云'],
        'sites': []
    },
    'AI工具/人工智能/计算机视觉': {
        'description': '图像生成、图像识别、视频生成等视觉AI工具',
        'keywords': ['vision', 'image', 'video', 'cv', 'detection', 'segmentation', 'recognition', 'face', 'ocr', 'stable diffusion', 'midjourney', 'dalle', 'flux', 'sdxl', '文生图', '图像', '视频', '视觉', '人脸', '识别', '生成'],
        'sites': []
    },
    'AI工具/人工智能/语音音频': {
        'description': '语音识别、语音合成、音乐生成等音频AI',
        'keywords': ['speech', 'voice', 'audio', 'tts', 'asr', 'whisper', 'music', 'sound', 'sing', 'song', '语音', '音频', '音乐', '语音识别', '语音合成'],
        'sites': []
    },
    'AI工具/人工智能/研究资源': {
        'description': '论文库、学术会议、数据集平台、研究工具',
        'keywords': ['research', 'paper', 'arxiv', 'academic', 'conference', 'dataset', 'neurips', 'icml', 'cvpr', 'acl', 'openreview', 'mlr', '论文', '学术', '会议', '研究', '数据集'],
        'sites': []
    },
    'AI工具/人工智能/综合平台': {
        'description': '多模态AI综合服务平台',
        'keywords': ['comprehensive', 'platform', 'all-in-one', 'multimodal', '综合', '一站式', '多模态'],
        'sites': []
    },
    '其他/杂项/AI工具': {
        'description': '无法归类为AI工具的站点、通用开发工具、噪音数据',
        'keywords': [],
        'sites': []
    }
}

def classify_site(site):
    """Classify a site into one of the new categories based on name, description, URL."""
    name = (site.get('name', '') or site.get('title', '') or '').lower()
    desc = (site.get('description', '') or '').lower()
    url = (site.get('url', '') or '').lower()

    text = f"{name} {desc} {url}"

    # Check each category
    for cat_name, cat_info in NEW_CATEGORIES.items():
        if cat_name == '其他/杂项/AI工具':
            continue
        for kw in cat_info['keywords']:
            if kw.lower() in text:
                return cat_name

    # Special cases based on original category mapping
    original_cat = site.get('category', '')

    # Hierarchy mapping from old to new
    HINTS = {
        'AI工具/人工智能/代码助手': 'AI工具/人工智能/机器学习框架',
        'AI工具/人工智能/写作助手': 'AI工具/人工智能/大语言模型',
        'AI工具/人工智能/写作生成': 'AI工具/人工智能/大语言模型',
        'AI工具/人工智能/摘要生成': 'AI工具/人工智能/大语言模型',
        'AI工具/人工智能/聊天对话': 'AI工具/人工智能/大语言模型',
        'AI工具/人工智能/搜索引擎': 'AI工具/人工智能/AI基础设施',
        'AI工具/人工智能/数据分析': 'AI工具/人工智能/AI基础设施',
        'AI工具/人工智能/知识图谱': 'AI工具/人工智能/大语言模型',
        'AI工具/人工智能/情感分析': 'AI工具/人工智能/大语言模型',
        'AI工具/人工智能/推荐系统': 'AI工具/人工智能/大语言模型',
        'AI工具/人工智能/文档分析': 'AI工具/人工智能/大语言模型',
        'AI工具/人工智能/预测分析': 'AI工具/人工智能/AI基础设施',
        'AI工具/人工智能/图像处理': 'AI工具/人工智能/计算机视觉',
        'AI工具/人工智能/图像扩展': 'AI工具/人工智能/计算机视觉',
        'AI工具/人工智能/图像识别': 'AI工具/人工智能/计算机视觉',
        'AI工具/人工智能/图生图': 'AI工具/人工智能/计算机视觉',
        'AI工具/人工智能/场景生成': 'AI工具/人工智能/计算机视觉',
        'AI工具/人工智能/文生图': 'AI工具/人工智能/计算机视觉',
        'AI工具/人工智能/风格迁移': 'AI工具/人工智能/计算机视觉',
        'AI工具/人工智能/背景移除': 'AI工具/人工智能/计算机视觉',
        'AI工具/人工智能/草图转图': 'AI工具/人工智能/计算机视觉',
        'AI工具/人工智能/视频生成': 'AI工具/人工智能/计算机视觉',
        'AI工具/人工智能/视频工具': 'AI工具/人工智能/计算机视觉',
        'AI工具/人工智能/语音识别': 'AI工具/人工智能/语音音频',
        'AI工具/人工智能/音频生成': 'AI工具/人工智能/语音音频',
        'AI工具/人工智能/自动化流程': 'AI工具/人工智能/AI基础设施',
        'AI工具/人工智能/综合平台': 'AI工具/人工智能/综合平台',
        'AI工具/人工智能/AI视频生成': 'AI工具/人工智能/计算机视觉',
    }

    return HINTS.get(original_cat, '其他/杂项/AI工具')

# Classify all AI sites
mapping = {}
for site in all_ai_sites:
    url = site.get('url', '')
    new_cat = classify_site(site)
    NEW_CATEGORIES[new_cat]['sites'].append(site)
    mapping[url] = {
        'old_category': site.get('category', ''),
        'new_category': new_cat,
        'name': site.get('name', '') or site.get('title', ''),
        'url': url
    }

# Print results
print("\n=== NEW CATEGORY DISTRIBUTION ===")
for cat, info in sorted(NEW_CATEGORIES.items()):
    count = len(info['sites'])
    print(f"  {count:4d}  {cat}")
    if count > 0 and count <= 10:
        for s in info['sites'][:5]:
            name = s.get('name', '') or s.get('title', '')
            print(f"      - {name[:50]}")
        if count > 5:
            print(f"      ... +{count-5} more")

# Save mapping
output_file = '/home/yoli/GitHub/web_nav_v2/reports/ai_master_category_split_plan.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'generated_at': datetime.now().isoformat(),
        'total_sites_reclassified': len(mapping),
        'category_distribution': {k: len(v['sites']) for k, v in NEW_CATEGORIES.items()},
        'mapping': mapping
    }, f, ensure_ascii=False, indent=2)

print(f"\nMapping saved to: {output_file}")

# Summary stats
print("\n=== SUMMARY ===")
print(f"Total AI sites: {len(all_ai_sites)}")
over_50 = {k: v for k, v in NEW_CATEGORIES.items() if len(v['sites']) > 50}
print(f"Categories still over 50: {len(over_50)}")
if over_50:
    for cat, info in sorted(over_50.items(), key=lambda x: -len(x[1]['sites'])):
        print(f"  {len(info['sites']):4d}  {cat}")
EOF
