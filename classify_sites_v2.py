#!/usr/bin/env python3
import json
import re

def main():
    print("🔍 开始处理网站分类任务...")

    with open('data/websites.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    unclassified = []

    # 正确遍历所有站点
    for major_name, major_node in data.items():
        if 'subcategories' not in major_node:
            continue
        for midcat in major_node['subcategories']:
            if 'minor_categories' not in midcat:
                continue
            for mincat in midcat['minor_categories']:
                if 'sites' not in mincat:
                    continue
                # 过滤出待分类站点
                keep_sites = []
                for site in mincat['sites']:
                    if isinstance(site, dict) and site.get('source') == 'awesome':
                        unclassified.append(site)
                    else:
                        keep_sites.append(site)
                mincat['sites'] = keep_sites

    total_remaining = len(unclassified)
    print(f"✅ 共找到 {total_remaining} 个待分类站点")

    if total_remaining == 0:
        print("✅ 没有需要分类的站点")
        return

    process_count = min(1000, total_remaining)
    processed = 0

    # 分类规则
    category_rules = [
        (r'ai|gpt|llm|chatgpt|model|机器学习', 'AI智能', 'LLM', '工具'),
        (r'绘画|图片|sd|midjourney|dall', 'AI智能', 'AI绘画', '工具'),
        (r'写作|文案|总结|文章', 'AI智能', 'AI写作', '工具'),
        (r'视频|video|剪辑', 'AI智能', 'AI视频', '工具'),
        (r'音乐|audio|声音|合成', 'AI智能', 'AI音乐', '工具'),
        (r'github|git|代码|编程|coding', '开发工具', '开发工具', '工具'),
        (r'docker|服务器|部署|运维', '开发工具', '部署运维', '工具'),
        (r'数据库|mysql|redis|postgres', '开发工具', '数据库', '工具'),
        (r'设计|ui|ux|figma|原型', '设计绘画', '设计工具', '工具'),
        (r'图标|icon|字体|font', '设计绘画', '设计素材', '资源'),
        (r'笔记|notion|文档', '办公学习', '笔记工具', '工具'),
        (r'任务|todo|效率|日历', '办公学习', '效率工具', '工具'),
        (r'教程|课程|学习|edu', '学习社区', '在线课程', '资源'),
        (r'论坛|社区|discord|知乎', '学习社区', '技术社区', '社区'),
        (r'游戏|娱乐|休闲|玩', '悠闲娱乐', '游戏娱乐', '其他'),
        (r'素材|图库|壁纸|下载', '素材资源', '图片素材', '资源'),
    ]

    # 获取分类目标
    def get_target(major, mid, minor):
        if major not in data: return None
        for m in data[major]['subcategories']:
            if m['name'] == mid:
                for mc in m['minor_categories']:
                    if mc['name'] == minor:
                        return mc['sites']
        return None

    default_target = get_target('AI智能', 'AI其他', '其他')

    for site in unclassified[:process_count]:
        url = site.get('url', '').lower()
        title = site.get('title', '')
        del site['source']

        # 自动补全标题
        if not title:
            m = re.search(r'https?://(?:www\.)?([^/.]+)', url)
            if m:
                site['title'] = m.group(1).title()

        matched = False
        for pat, mj, md, mn in category_rules:
            if re.search(pat, url + title, re.IGNORECASE):
                tgt = get_target(mj, md, mn)
                if tgt:
                    tgt.append(site)
                    processed += 1
                    matched = True
                    break
        if not matched and default_target:
            default_target.append(site)
            processed +=1

    with open('data/websites.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 成功完成 {processed} 个站点分类")
    print(f"✅ 剩余未分类: {total_remaining - processed}")
    print(f"✅ 本次进度提升: {round(processed / (11616 - 2143) * 100, 2)}%")

if __name__ == "__main__":
    main()
