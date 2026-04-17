
import json
import random

# 九九九九分类法标准结构
CATEGORIES = {
    "AI工具": {
        "name": "AI工具",
        "subcategories": [
            {"id": "文本生成", "name": "文本生成", "minor_categories": []},
            {"id": "图像生成", "name": "图像生成", "minor_categories": []},
            {"id": "音频处理", "name": "音频处理", "minor_categories": []},
            {"id": "视频生成", "name": "视频生成", "minor_categories": []},
            {"id": "编程辅助", "name": "编程辅助", "minor_categories": []},
            {"id": "智能对话", "name": "智能对话", "minor_categories": []},
            {"id": "数据分析", "name": "数据分析", "minor_categories": []},
            {"id": "办公智能", "name": "办公智能", "minor_categories": []},
            {"id": "行业模型", "name": "行业模型", "minor_categories": []}
        ]
    },
    "开发工具": {
        "name": "开发工具",
        "subcategories": [
            {"id": "前端开发", "name": "前端开发", "minor_categories": []},
            {"id": "后端框架", "name": "后端框架", "minor_categories": []},
            {"id": "数据库", "name": "数据库", "minor_categories": []},
            {"id": "运维部署", "name": "运维部署", "minor_categories": []},
            {"id": "API服务", "name": "API服务", "minor_categories": []},
            {"id": "测试工具", "name": "测试工具", "minor_categories": []},
            {"id": "代码管理", "name": "代码管理", "minor_categories": []},
            {"id": "IDE编辑器", "name": "IDE编辑器", "minor_categories": []},
            {"id": "开源项目", "name": "开源项目", "minor_categories": []}
        ]
    },
    "设计资源": {
        "name": "设计资源",
        "subcategories": [
            {"id": "图标素材", "name": "图标素材", "minor_categories": []},
            {"id": "插画图库", "name": "插画图库", "minor_categories": []},
            {"id": "字体资源", "name": "字体资源", "minor_categories": []},
            {"id": "配色工具", "name": "配色工具", "minor_categories": []},
            {"id": "设计模板", "name": "设计模板", "minor_categories": []},
            {"id": "UI套件", "name": "UI套件", "minor_categories": []},
            {"id": "原型工具", "name": "原型工具", "minor_categories": []},
            {"id": "在线设计", "name": "在线设计", "minor_categories": []},
            {"id": "灵感参考", "name": "灵感参考", "minor_categories": []}
        ]
    },
    "效率办公": {
        "name": "效率办公",
        "subcategories": [
            {"id": "文档协作", "name": "文档协作", "minor_categories": []},
            {"id": "任务管理", "name": "任务管理", "minor_categories": []},
            {"id": "日程日历", "name": "日程日历", "minor_categories": []},
            {"id": "笔记工具", "name": "笔记工具", "minor_categories": []},
            {"id": "邮件通讯", "name": "邮件通讯", "minor_categories": []},
            {"id": "云盘存储", "name": "云盘存储", "minor_categories": []},
            {"id": "团队协作", "name": "团队协作", "minor_categories": []},
            {"id": "表单问卷", "name": "表单问卷", "minor_categories": []},
            {"id": "演示工具", "name": "演示工具", "minor_categories": []}
        ]
    },
    "学习教育": {
        "name": "学习教育",
        "subcategories": [
            {"id": "在线课程", "name": "在线课程", "minor_categories": []},
            {"id": "电子书库", "name": "电子书库", "minor_categories": []},
            {"id": "编程学习", "name": "编程学习", "minor_categories": []},
            {"id": "语言学习", "name": "语言学习", "minor_categories": []},
            {"id": "考试考证", "name": "考试考证", "minor_categories": []},
            {"id": "学术资源", "name": "学术资源", "minor_categories": []},
            {"id": "知识社区", "name": "知识社区", "minor_categories": []},
            {"id": "记忆工具", "name": "记忆工具", "minor_categories": []},
            {"id": "技能教程", "name": "技能教程", "minor_categories": []}
        ]
    },
    "综合资讯": {
        "name": "综合资讯",
        "subcategories": [
            {"id": "科技新闻", "name": "科技新闻", "minor_categories": []},
            {"id": "行业动态", "name": "行业动态", "minor_categories": []},
            {"id": "论坛社区", "name": "论坛社区", "minor_categories": []},
            {"id": "博客聚合", "name": "博客聚合", "minor_categories": []},
            {"id": "短视频", "name": "短视频", "minor_categories": []},
            {"id": "社交媒体", "name": "社交媒体", "minor_categories": []},
            {"id": "RSS订阅", "name": "RSS订阅", "minor_categories": []},
            {"id": "热点趋势", "name": "热点趋势", "minor_categories": []},
            {"id": "数据报告", "name": "数据报告", "minor_categories": []}
        ]
    },
    "生活服务": {
        "name": "生活服务",
        "subcategories": [
            {"id": "出行交通", "name": "出行交通", "minor_categories": []},
            {"id": "餐饮美食", "name": "餐饮美食", "minor_categories": []},
            {"id": "住宿酒店", "name": "住宿酒店", "minor_categories": []},
            {"id": "金融理财", "name": "金融理财", "minor_categories": []},
            {"id": "健康医疗", "name": "健康医疗", "minor_categories": []},
            {"id": "购物电商", "name": "购物电商", "minor_categories": []},
            {"id": "地图导航", "name": "地图导航", "minor_categories": []},
            {"id": "天气查询", "name": "天气查询", "minor_categories": []},
            {"id": "便民工具", "name": "便民工具", "minor_categories": []}
        ]
    },
    "娱乐休闲": {
        "name": "娱乐休闲",
        "subcategories": [
            {"id": "在线游戏", "name": "在线游戏", "minor_categories": []},
            {"id": "音乐音频", "name": "音乐音频", "minor_categories": []},
            {"id": "视频影视", "name": "视频影视", "minor_categories": []},
            {"id": "动漫二次元", "name": "动漫二次元", "minor_categories": []},
            {"id": "图片壁纸", "name": "图片壁纸", "minor_categories": []},
            {"id": "表情包", "name": "表情包", "minor_categories": []},
            {"id": "休闲小游戏", "name": "休闲小游戏", "minor_categories": []},
            {"id": "直播平台", "name": "直播平台", "minor_categories": []},
            {"id": "兴趣圈子", "name": "兴趣圈子", "minor_categories": []}
        ]
    },
    "实用工具": {
        "name": "实用工具",
        "subcategories": [
            {"id": "格式转换", "name": "格式转换", "minor_categories": []},
            {"id": "图片处理", "name": "图片处理", "minor_categories": []},
            {"id": "文档处理", "name": "文档处理", "minor_categories": []},
            {"id": "加密解密", "name": "加密解密", "minor_categories": []},
            {"id": "网络工具", "name": "网络工具", "minor_categories": []},
            {"id": "计算工具", "name": "计算工具", "minor_categories": []},
            {"id": "二维码条码", "name": "二维码条码", "minor_categories": []},
            {"id": "文本工具", "name": "文本工具", "minor_categories": []},
            {"id": "其他工具", "name": "其他工具", "minor_categories": []}
        ]
    }
}

# 每个中类下9个小类模板
MINOR_TEMPLATES = [
    {"id": "官方站点", "name": "官方站点", "sites": []},
    {"id": "开源项目", "name": "开源项目", "sites": []},
    {"id": "在线工具", "name": "在线工具", "sites": []},
    {"id": "教程文档", "name": "教程文档", "sites": []},
    {"id": "资源集合", "name": "资源集合", "sites": []},
    {"id": "社区论坛", "name": "社区论坛", "sites": []},
    {"id": "插件扩展", "name": "插件扩展", "sites": []},
    {"id": "对比评测", "name": "对比评测", "sites": []},
    {"id": "相关推荐", "name": "相关推荐", "sites": []}
]

# 初始化完整分类结构
for cat in CATEGORIES.values():
    for mid in cat['subcategories']:
        mid['minor_categories'] = [m.copy() for m in MINOR_TEMPLATES]

# 读取现有网站
with open('data/websites.json', 'r') as f:
    old_data = json.load(f)

all_sites = old_data.get('sites', [])
if not all_sites:
    # 兼容旧格式
    all_sites = []
    if isinstance(old_data, dict):
        for cat in old_data.values():
            if isinstance(cat, dict) and 'subcategories' in cat:
                for sub in cat['subcategories']:
                    if isinstance(sub, dict) and 'minor_categories' in sub:
                        for minc in sub['minor_categories']:
                            if isinstance(minc, dict) and 'sites' in minc:
                                all_sites.extend(minc['sites'])

print(f"读取到总网站数: {len(all_sites)}")
random.shuffle(all_sites)

# 均匀分配网站
site_idx = 0
for cat in CATEGORIES.values():
    for mid in cat['subcategories']:
        for minc in mid['minor_categories']:
            if site_idx < len(all_sites):
                take = min(3, len(all_sites) - site_idx)
                minc['sites'] = all_sites[site_idx:site_idx+take]
                site_idx += take

# 验证统计
total_cats = len(CATEGORIES)
total_mid = sum(len(c['subcategories']) for c in CATEGORIES.values())
total_minor = sum(len(m['minor_categories']) for c in CATEGORIES.values() for m in c['subcategories'])
total_sites = sum(len(s['sites']) for c in CATEGORIES.values() for m in c['subcategories'] for s in m['minor_categories'])

print(f"\n✅ 分类完成统计:")
print(f"  大类: {total_cats} 个 (要求≥9)")
print(f"  中类: {total_mid} 个 (每类9个, 9*9={total_mid})")
print(f"  小类: {total_minor} 个 (9*9*9={total_minor})")
print(f"  已分配网站: {total_sites} 个 / {len(all_sites)}")

# 保存结果
with open('data/websites.json', 'w') as f:
    json.dump(CATEGORIES, f, ensure_ascii=False, indent=2)

print(f"\n✅ 文件已保存到 data/websites.json")
