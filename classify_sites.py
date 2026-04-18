#!/usr/bin/env python3
import json
import re
import os

def main():
    print("🔍 开始处理网站分类任务，目标处理1000个未分类站点...")

    # 加载数据
    with open('data/websites.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 找到所有待分类站点
    unclassified = []
    classified_count = 0

    # 遍历所有位置收集待分类
    def traverse_collect(node):
        nonlocal unclassified
        if isinstance(node, list):
            keep = []
            for item in node:
                if isinstance(item, dict) and 'source' in item and item.get('source') == 'awesome':
                    unclassified.append(item)
                else:
                    keep.append(item)
            return keep
        elif isinstance(node, dict):
            for k, v in list(node.items()):
                node[k] = traverse_collect(v)
        return node

    data = traverse_collect(data)
    total_remaining = len(unclassified)
    print(f"✅ 找到 {total_remaining} 个待分类站点，将处理前1000个")

    process_count = min(1000, total_remaining)
    processed = 0

    # 分类规则引擎
    category_rules = [
        # AI智能大类
        (r'ai|gpt|llm|chatgpt|生成式|模型|机器学习|深度学习', 'AI智能', 'LLM', '工具'),
        (r'\.ai$|ai\-|artificial|intelligence', 'AI智能', 'LLM', '工具'),
        (r'绘画|画图|生成图片|stable diffusion|midjourney|dalle', 'AI智能', 'AI绘画', '工具'),
        (r'写作|文案|创作|文字生成|summary|总结', 'AI智能', 'AI写作', '工具'),
        (r'视频|video|生成视频|文本转视频|ai视频', 'AI智能', 'AI视频', '工具'),
        (r'音乐|music|audio|声音|合成音频', 'AI智能', 'AI音乐', '工具'),
        (r'开发|框架|库|sdk|api|pytorch|tensorflow', 'AI智能', 'AI开发', '库'),

        # 开发工具大类
        (r'github|git|代码|编程|程序员|coding|program', '开发工具', '开发工具', '工具'),
        (r'框架|library|sdk|api|文档|docs', '开发工具', '开发资源', '资源'),
        (r'部署|docker|服务器|hosting|cloud', '开发工具', '部署运维', '工具'),
        (r'数据库|database|redis|mysql|postgres', '开发工具', '数据库', '工具'),
        (r'前端|html|css|javascript|vue|react', '开发工具', '前端开发', '工具'),

        # 设计绘画大类
        (r'设计|design|ui|ux|原型|figma|sketch', '设计绘画', '设计工具', '工具'),
        (r'图标|icon|字体|font|颜色|配色', '设计绘画', '设计素材', '资源'),
        (r'插画|手绘|绘画|drawing|illustration', '设计绘画', '手绘插画', '工具'),

        # 视频创作大类
        (r'视频|剪辑|pr|剪映|editing|video', '视频创作', '剪辑工具', '工具'),
        (r'特效|ae|动画|animation', '视频创作', '特效动画', '工具'),
        (r'录屏|screen|录制|record', '视频创作', '录屏工具', '工具'),

        # 办公学习大类
        (r'办公|office|excel|word|ppt|表格', '办公学习', '办公软件', '工具'),
        (r'笔记|笔记|notion|笔记软件', '办公学习', '笔记工具', '工具'),
        (r'日历|任务|todo|项目管理', '办公学习', '效率工具', '工具'),

        # 学习社区大类
        (r'教程|课程|学习|edu|learn|教学', '学习社区', '在线课程', '资源'),
        (r'社区|论坛|discord|reddit|stackoverflow', '学习社区', '技术社区', '社区'),
        (r'博客|blog|文章|知识', '学习社区', '博客文章', '资源'),

        # 文字创作大类
        (r'写作|文案|排版|markdown|富文本', '文字创作', '写作工具', '工具'),
        (r'翻译|translate|语言|多语言', '文字创作', '翻译工具', '工具'),

        # 悠闲娱乐大类
        (r'游戏|game|娱乐|玩|休闲', '悠闲娱乐', '游戏娱乐', '其他'),
        (r'音乐|听歌|音乐播放器', '悠闲娱乐', '音乐音频', '工具'),
        (r'电影|影视|追剧|视频', '悠闲娱乐', '影视追剧', '资源'),

        # 素材资源大类
        (r'素材|资源|下载|免费资源|图库', '素材资源', '图片素材', '资源'),
        (r'壁纸|background|wallpaper', '素材资源', '壁纸背景', '资源'),
        (r'字体|font|icon|图标', '素材资源', '字体图标', '资源'),
    ]

    # 找到目标分类位置
    def find_category(major, mid, minor):
        if major not in data:
            return None
        for midcat in data[major]['subcategories']:
            if midcat['name'] == mid:
                for mincat in midcat['minor_categories']:
                    if mincat['name'] == minor:
                        return mincat['sites']
        return None

    # 处理每个站点
    for site in unclassified[:process_count]:
        url = site.get('url', '').lower()
        title = site.get('title', '')
        desc = site.get('description', '')

        # 移除source字段
        if 'source' in site:
            del site['source']

        # 自动填充标题
        if not title or title.strip() == '':
            # 从URL提取域名
            m = re.search(r'https?://(?:www\.)?([^/]+)', url)
            if m:
                domain = m.group(1)
                site['title'] = domain.replace('.', ' ').title()

        # 匹配分类
        matched = False
        for pattern, major_name, mid_name, minor_name in category_rules:
            if re.search(pattern, url + title + desc, re.IGNORECASE):
                target = find_category(major_name, mid_name, minor_name)
                if target is not None:
                    target.append(site)
                    processed += 1
                    matched = True
                    break

        # 未匹配放入默认其他
        if not matched:
            target = find_category('AI智能', 'AI其他', '其他')
            if target is not None:
                target.append(site)
                processed += 1

    # 保存结果
    with open('data/websites.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 分类完成！成功处理 {processed} 个站点")
    print(f"✅ 剩余未分类: {total_remaining - processed}")
    print(f"✅ 分类进度提升: {round(processed / total_remaining * 100, 2)}%")

if __name__ == "__main__":
    main()
