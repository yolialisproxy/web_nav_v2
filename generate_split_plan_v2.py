#!/usr/bin/env python3
"""
生成超容分类的细粒度拆分计划
针对51个超容分类（>50站点），为V10平衡度优化提供实施蓝图
重点：GitHub类拆分为至少15个子类
"""

import json
from datetime import datetime

# 加载当前统计数据
over_capacity_cats = {
    "开发工具/平台开源/GitHub": 206,
    "AI工具/人工智能/数据分析": 196,
    "多媒体/视频娱乐/教程": 192,
    "AI工具/人工智能/代码助手": 177,
    "AI工具/人工智能/视频生成": 153,
    "AI工具/人工智能/图像识别": 140,
    "设计工具/UI设计工具": 125,
    "系统工具/实用工具/文件工具": 121,
    "AI工具/人工智能/搜索引擎": 104,
    "AI工具/人工智能/AI平台": 100,
    "AI工具/人工智能/知识图谱": 94,
    "AI工具/人工智能/写作助手": 90,
    "AI工具/人工智能/聊天对话": 88,
    "AI工具/人工智能/语音识别": 88,
    "AI工具/人工智能/摘要生成": 88,
    "AI工具/人工智能/情感分析": 86,
    "AI工具/人工智能/推荐系统": 86,
    "AI工具/人工智能/翻译服务": 86,
    "AI工具/人工智能/自动化流程": 86,
    "AI工具/人工智能/预测分析": 86,
    "效率办公/协作工具": 69,
    "AI工具/人工智能/产品图生成": 65,
    "效率办公/博客管理": 65,
    "AI工具/人工智能/文生图": 59,
    "AI工具/人工智能/图生图": 59,
    "AI工具/人工智能/图像修复": 59,
    "AI工具/人工智能/图像扩展": 59,
    "AI工具/人工智能/风格迁移": 59,
    "AI工具/人工智能/超分辨率": 59,
    "AI工具/人工智能/背景移除": 59,
    "AI工具/人工智能/人脸编辑": 59,
    "AI工具/人工智能/3D生成": 59,
    "效率办公/剧本创作": 59,
    "效率办公/总结摘要": 59,
    "效率办公/社交媒体": 59,
    "效率办公/内容写作": 58,
    "效率办公/文案优化": 58,
    "效率办公/AI写作": 58,
    "效率办公/诗歌创作": 58,
    "效率办公/营销文案": 58,
    "AI工具/人工智能/动漫风格": 58,
    "AI工具/人工智能/图像增强": 58,
    "AI工具/人工智能/场景生成": 58,
    "AI工具/人工智能/色彩调整": 58,
    "AI工具/人工智能/草图转图": 58,
    "效率办公/技术写作": 58,
    "效率办公/邮件写作": 57,
    "效率办公/创意激发": 57,
    "效率办公/标题生成": 57,
    "效率办公/改写重述": 57,
    "效率办公/故事生成": 57,
    "系统工具/实用工具/其他工具": 35,
    "AI工具/人工智能/综合平台": 30,
    "AI工具/人工智能/音频生成": 27,
    "多媒体/视频娱乐/国外视频": 24,
    "效率办公/网络小说平台": 23,
    "效率办公/网文作者工具": 23,
    "效率办公/网文投稿平台": 23,
    "效率办公/网文论坛社区": 23,
    "效率办公/网文资源下载": 23,
    "效率办公/网文写作教程": 23,
    "其他/杂项/JSON工具": 23,
    "效率办公/网文阅读应用": 23,
    "效率办公/网文数据分析": 23,
    "效率办公/网文版权交易": 23,
    "效率办公/网文作家协会": 23,
    "效率办公/网文编辑工具": 23,
    "效率办公/网文推广平台": 23,
    "其他/杂项/搜索引擎": 22,
    "其他/杂项/词典翻译": 22,
    "其他/杂项/在线计算": 22,
    "其他/杂项/正则测试": 22,
    "其他/杂项/时间工具": 22,
    "其他/杂项/单位转换": 22,
    "其他/杂项/二维码工具": 22,
    "其他/杂项/短链接": 22,
    "其他/杂项/政府服务": 22,
    "其他/杂项/教育机构": 22,
    "其他/杂项/公共数据": 22,
    "其他/杂项/在线测试": 22,
    "其他/杂项/压力测试": 22,
    "其他/杂项/平台市场": 22,
    "效率办公/网文书评社区": 22,
    "效率办公/网文榜单统计": 22,
    "效率办公/网文辅助工具": 22,
    "多媒体/视频娱乐/国内视频": 21,
    "设计工具/资源/矢量图标": 21,
    "开发工具/学习生成/在线课程": 20,
    "设计工具/资源/图库照片": 20,
    "设计工具/资源/UI套件": 20,
    "设计工具/资源/字体资源": 20,
    "设计工具/资源/PPT模板": 20,
    "设计工具/资源/设计素材": 20,
    "设计工具/资源/配色方案": 19,
}

# ===== 构建拆分计划 =====
split_plan = {
    "plan_metadata": {
        "plan_name": "over_capacity_split_plan_v1",
        "generated_at": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "target_version": "V10",
        "total_over_capacity_categories": 51,
        "focus_category": "开发工具/平台开源/GitHub",
        "goal": "将51个超容分类（>50站点）拆分为10-50站点的子类，提升整体平衡度至80%+",
        "current_balance_rate": "32.7% (89/272)",
        "target_balance_rate": "≥80%"
    },
    "split_categories": []
}

# ===== 1. GitHub类 - 拆分为16个子类 =====
github_plan = {
    "original_name": "开发工具/平台开源/GitHub",
    "current_count": 206,
    "split_dimension": "功能场景与平台类型（GitHub本体、替代平台、集成工具、资源托管、开发工具、文档教程、项目索引、开源社区、应用服务）",
    "complexity": "high",
    "rationale": "GitHub类混杂了GitHub本体、GitLab/Gitee等替代平台、CDN资源、文档站点、Awesome列表、开源项目索引等多种类型，需要按网站性质和功能进行精细化拆分。目标是每个子类10-50个站点。",
    "sub_categories": [
        {"name": "GitHub本体服务", "estimated_count": 35, "description": "GitHub官网、博客、文档、支持中心、安全实验室、新闻等官方服务"},
        {"name": "GitHub客户端工具", "estimated_count": 12, "description": "GitHub Desktop、CLI、Mobile等官方客户端应用"},
        {"name": "GitHub Actions与CI/CD", "estimated_count": 18, "description": "Actions市场、CI/CD集成工具、自动化工作流服务"},
        {"name": "GitHub Packages与容器", "estimated_count": 10, "description": "Packages注册表、容器镜像托管、依赖管理"},
        {"name": "GitHub Pages与静态托管", "estimated_count": 15, "description": "GitHub Pages站点、静态网站托管服务"},
        {"name": "开源项目索引Awesome", "estimated_count": 42, "description": "awesome-selfhosted等awesome列表、开源项目集合索引"},
        {"name": "代码托管替代平台", "estimated_count": 38, "description": "GitLab、Gitee、Bitbucket、SourceForge等竞争性代码托管平台"},
        {"name": "GitHub镜像/缓存服务", "estimated_count": 8, "description": "GitHub镜像站、加速缓存、可访问性服务"},
        {"name": "IDE与编辑器GitHub集成", "estimated_count": 14, "description": "VS Code、JetBrains等IDE的GitHub插件扩展"},
        {"name": "开发工具GitHub集成", "estimated_count": 18, "description": "各类开发框架、工具对GitHub的集成服务"},
        {"name": "GitHub教程与学习", "estimated_count": 11, "description": "GitHub使用教程、学习资源、文档站"},
        {"name": "GitHub开发者社区", "estimated_count": 9, "description": "GitHub社区、论坛、开发者活动平台"},
        {"name": "GitHub API生态服务", "estimated_count": 7, "description": "基于GitHub API构建的第三方服务"},
        {"name": "知名开源组织项目", "estimated_count": 24, "description": "tensorflow、microsoft等知名组织在GitHub的项目"},
        {"name": "GitHub资源与素材", "estimated_count": 6, "description": "GitHub主题、模板、图标等资源文件"},
        {"name": "其他GitHub相关", "estimated_count": 9, "description": "未被明确归类的GitHub相关站点"}
    ],
    "total_sub_count": 206
}

# ===== 2. AI工具/人工智能/数据分析 - 拆分为6个子类 =====
data_analysis_plan = {
    "original_name": "AI工具/人工智能/数据分析",
    "current_count": 196,
    "split_dimension": "应用场景与技术栈（商业智能、数据科学、大数据、数据库、可视化、ETL）",
    "complexity": "medium",
    "rationale": "数据分析涵盖BI可视化、数据科学、大数据处理、数据库工具等多个领域，需按应用场景拆分。",
    "sub_categories": [
        {"name": "商业智能(BI)", "estimated_count": 38, "description": "Tableau、Power BI、Looker、FineReport等BI可视化工具"},
        {"name": "数据科学平台", "estimated_count": 42, "description": "Jupyter、Kaggle、Google Colab、DataCamp等数据科学工作台"},
        {"name": "大数据处理框架", "estimated_count": 32, "description": "Hadoop、Spark、Flink、Databricks等大数据处理框架和服务"},
        {"name": "数据库与数据仓库", "estimated_count": 36, "description": "云数据库、数据仓库（Snowflake、BigQuery）、数据库管理工具"},
        {"name": "数据可视化库/工具", "estimated_count": 24, "description": "ECharts、D3.js、Plotly等可视化库和图表工具"},
        {"name": "数据采集与ETL", "estimated_count": 24, "description": "数据采集、清洗、转换、集成工具"}
    ],
    "total_sub_count": 196
}

# ===== 3. 多媒体/视频娱乐/教程 - 拆分为6个子类 =====
video_tutorial_plan = {
    "original_name": "多媒体/视频娱乐/教程",
    "current_count": 192,
    "split_dimension": "内容领域与平台类型（编程、设计、综合慕课、文档、语言、职业）",
    "complexity": "medium",
    "rationale": "教程类站点过多，按教授领域和平台类型细分，避免单一垂直领域过度集中。",
    "sub_categories": [
        {"name": "编程/开发教程", "estimated_count": 62, "description": "Codecademy、freeCodeCamp、W3Schools、LeetCode等编程学习平台"},
        {"name": "设计/创意教程", "estimated_count": 36, "description": "UI/UX设计、平面设计、视频编辑、3D建模等创意技能教程"},
        {"name": "综合慕课平台", "estimated_count": 40, "description": "Coursera、edX、Udemy、网易云课堂等综合在线教育平台"},
        {"name": "技术文档/手册", "estimated_count": 24, "description": "MDN、各类框架官方文档、技术手册、API文档站"},
        {"name": "语言学习平台", "estimated_count": 16, "description": "多邻国、Busuu、Rosetta Stone等语言学习工具"},
        {"name": "职业技能培训", "estimated_count": 14, "description": "商业、金融、管理等职业技能在线课程"}
    ],
    "total_sub_count": 192
}

# ===== 4. AI工具/人工智能/代码助手 - 拆分为6个子类 =====
code_assistant_plan = {
    "original_name": "AI工具/人工智能/代码助手",
    "current_count": 177,
    "split_dimension": "功能定位（AI生成、智能补全、低代码、API工具、代码审查、代码转换）",
    "complexity": "medium",
    "rationale": "代码助手涵盖AI编程、自动补全、代码生成、低代码等多种类型，按功能细分。",
    "sub_categories": [
        {"name": "AI代码生成器", "estimated_count": 48, "description": "GitHub Copilot、Cursor、Windsurf、Tabnine等AI代码生成工具"},
        {"name": "智能代码补全", "estimated_count": 28, "description": "Kite、IntelliCode等智能代码补全工具"},
        {"name": "低代码/无代码平台", "estimated_count": 34, "description": "Bubble、Webflow、Retool、OutSystems等低代码开发平台"},
        {"name": "API设计与管理", "estimated_count": 26, "description": "Postman、Swagger、Apifox、Insomnia等API工具"},
        {"name": "代码质量与审查", "estimated_count": 20, "description": "SonarQube、CodeQL、DeepSource等代码审查和质量工具"},
        {"name": "代码转换/重构", "estimated_count": 21, "description": "代码转换、重构、优化、文档生成工具"}
    ],
    "total_sub_count": 177
}

# ===== 5. AI工具/人工智能/视频生成 - 拆分为6个子类 =====
video_gen_plan = {
    "original_name": "AI工具/人工智能/视频生成",
    "current_count": 153,
    "split_dimension": "生成方式与应用场景（文生、图生、编辑、数字人、增强、平台）",
    "complexity": "medium",
    "rationale": "视频生成技术路线多样，按输入方式和应用场景细分。",
    "sub_categories": [
        {"name": "文生视频", "estimated_count": 40, "description": "Runway、Pika、Sora等文本生成视频工具"},
        {"name": "图生视频/动画", "estimated_count": 32, "description": "图像转视频、动画生成、动态效果工具"},
        {"name": "AI视频编辑", "estimated_count": 28, "description": "智能剪辑、特效、调色、字幕自动生成工具"},
        {"name": "数字人/虚拟主播", "estimated_count": 22, "description": "虚拟形象、数字人、虚拟主播视频生成平台"},
        {"name": "视频增强/修复", "estimated_count": 16, "description": "超分辨率、去噪、去模糊、老片修复工具"},
        {"name": "视频生成平台", "estimated_count": 15, "description": "一站式AI视频生成服务平台"}
    ],
    "total_sub_count": 153
}

# ===== 6. AI工具/人工智能/图像识别 - 拆分为6个子类 =====
image_recognition_plan = {
    "original_name": "AI工具/人工智能/图像识别",
    "current_count": 140,
    "split_dimension": "识别对象与应用领域（通用、人脸、OCR、质检、医疗、特殊）",
    "complexity": "medium",
    "rationale": "图像识别在不同场景有专门优化，按识别对象细分。",
    "sub_categories": [
        {"name": "通用图像识别", "estimated_count": 32, "description": "通用物体、场景、属性识别API和服务"},
        {"name": "人脸识别与分析", "estimated_count": 28, "description": "人脸检测、识别、表情、姿态分析工具"},
        {"name": "OCR文字识别", "estimated_count": 34, "description": "文档OCR、场景文字识别、表格提取、票据识别"},
        {"name": "工业质检与缺陷检测", "estimated_count": 22, "description": "工业视觉检测、缺陷识别、质量监控"},
        {"name": "医疗影像识别", "estimated_count": 14, "description": "医学影像分析、疾病诊断辅助、病理识别"},
        {"name": "专用识别服务", "estimated_count": 10, "description": "车辆识别、车牌识别、手势识别等专用服务"}
    ],
    "total_sub_count": 140
}

# ===== 7. 设计工具/UI设计工具 - 拆分为5个子类 =====
ui_design_plan = {
    "original_name": "设计工具/UI设计工具",
    "current_count": 125,
    "split_dimension": "设计流程阶段（原型、UI、协作、设计系统、交互）",
    "complexity": "medium",
    "rationale": "UI设计包含原型、界面、协作、设计系统等多个阶段工具。",
    "sub_categories": [
        {"name": "原型设计", "estimated_count": 32, "description": "Figma、Sketch、Adobe XD、Axure等原型与线框图工具"},
        {"name": "UI视觉设计", "estimated_count": 34, "description": "高保真界面设计、视觉设计工具"},
        {"name": "设计协作与交付", "estimated_count": 24, "description": "设计评审、标注交付、协作标注平台"},
        {"name": "设计系统管理", "estimated_count": 18, "description": "Design Token、组件库、设计系统管理平台"},
        {"name": "交互与动效设计", "estimated_count": 17, "description": "微交互、动画、交互动效设计工具"}
    ],
    "total_sub_count": 125
}

# ===== 8. 系统工具/实用工具/文件工具 - 拆分为5个子类 =====
file_tools_plan = {
    "original_name": "系统工具/实用工具/文件工具",
    "current_count": 121,
    "split_dimension": "功能类型（压缩、转换、同步、管理、安全）",
    "complexity": "medium",
    "rationale": "文件工具按功能类别细分。",
    "sub_categories": [
        {"name": "文件压缩/解压", "estimated_count": 28, "description": "ZIP、RAR、7z等压缩格式工具和在线压缩服务"},
        {"name": "文件格式转换", "estimated_count": 36, "description": "文档、图片、视频等格式转换工具"},
        {"name": "文件同步与备份", "estimated_count": 24, "description": "云同步、文件备份、共享服务"},
        {"name": "文件管理器", "estimated_count": 18, "description": "文件管理、资源管理增强工具"},
        {"name": "文件安全工具", "estimated_count": 15, "description": "文件加密、解密、安全擦除工具"}
    ],
    "total_sub_count": 121
}

# ===== 剩余的AI相关超容分类（按细分领域拆分） =====
ai_remaining_plans = [
    {
        "original_name": "AI工具/人工智能/搜索引擎",
        "current_count": 104,
        "split_dimension": "搜索方式与应用对象",
        "complexity": "medium",
        "rationale": "AI搜索引擎按搜索方式和对象细分",
        "sub_categories": [
            {"name": "AI原生搜索引擎", "estimated_count": 42, "description": "Perplexity、You、Phind等AI原生搜索引擎"},
            {"name": "语义/向量搜索", "estimated_count": 34, "description": "基于语义理解的向量搜索引擎"},
            {"name": "代码搜索引擎", "estimated_count": 28, "description": "AI增强的代码搜索和检索工具"}
        ],
        "total_sub_count": 104
    },
    {
        "original_name": "AI工具/人工智能/AI平台",
        "current_count": 100,
        "split_dimension": "平台性质与服务模式",
        "complexity": "medium",
        "rationale": "AI平台按模型来源和服务方式细分",
        "sub_categories": [
            {"name": "大模型API平台", "estimated_count": 45, "description": "OpenAI、Anthropic、Google等闭源大模型API平台"},
            {"name": "开源模型社区", "estimated_count": 30, "description": "Hugging Face、ModelScope等开源模型平台"},
            {"name": "AI开发与应用平台", "estimated_count": 25, "description": "模型托管、微调、部署的一站式AI开发平台"}
        ],
        "total_sub_count": 100
    },
    {
        "original_name": "AI工具/人工智能/知识图谱",
        "current_count": 94,
        "split_dimension": "知识领域与应用方向",
        "complexity": "medium",
        "rationale": "知识图谱按覆盖领域和应用方向细分",
        "sub_categories": [
            {"name": "通用知识图谱", "estimated_count": 35, "description": "通用百科、综合知识图谱服务"},
            {"name": "垂直领域知识图谱", "estimated_count": 38, "description": "医疗、金融、法律等垂直行业知识图谱"},
            {"name": "知识管理与推理", "estimated_count": 21, "description": "个人/组织知识管理、知识推理工具"}
        ],
        "total_sub_count": 94
    },
    {
        "original_name": "AI工具/人工智能/写作助手",
        "current_count": 90,
        "split_dimension": "写作场景与内容长度",
        "complexity": "medium",
        "rationale": "写作助手按应用场景和内容类型细分",
        "sub_categories": [
            {"name": "通用写作助手", "estimated_count": 36, "description": "Grammarly、QuillBot等通用语法检查与改写工具"},
            {"name": "长文本创作", "estimated_count": 30, "description": "文章、博客、故事、小说的创作助手"},
            {"name": "营销文案生成", "estimated_count": 24, "description": "广告文案、营销邮件、产品描述生成工具"}
        ],
        "total_sub_count": 90
    },
    {
        "original_name": "AI工具/人工智能/聊天对话",
        "current_count": 88,
        "split_dimension": "对话类型与应用场景",
        "complexity": "medium",
        "rationale": "聊天对话AI按对话类型和应用场景细分",
        "sub_categories": [
            {"name": "通用聊天助手", "estimated_count": 42, "description": "ChatGPT、Claude、文心一言等通用对话模型"},
            {"name": "智能客服机器人", "estimated_count": 28, "description": "面向客户服务的对话机器人和自动化客服"},
            {"name": "角色/社交聊天", "estimated_count": 18, "description": "角色扮演、情感陪伴、社交聊天机器人"}
        ],
        "total_sub_count": 88
    },
    {
        "original_name": "AI工具/人工智能/语音识别",
        "current_count": 88,
        "split_dimension": "语音任务与应用场景",
        "complexity": "medium",
        "rationale": "语音识别技术按任务类型和应用场景细分",
        "sub_categories": [
            {"name": "语音转文本(ASR)", "estimated_count": 40, "description": "语音识别、听写、录音转文字工具"},
            {"name": "实时语音字幕", "estimated_count": 26, "description": "实时字幕生成、多语言翻译字幕工具"},
            {"name": "语音助手接口", "estimated_count": 22, "description": "语音控制、智能语音助手交互接口"}
        ],
        "total_sub_count": 88
    },
    {
        "original_name": "AI工具/人工智能/摘要生成",
        "current_count": 88,
        "split_dimension": "摘要内容类型",
        "complexity": "medium",
        "rationale": "摘要生成按处理的内容类型细分",
        "sub_categories": [
            {"name": "文档摘要", "estimated_count": 36, "description": "长文档、报告的自动摘要和关键点提取"},
            {"name": "新闻摘要", "estimated_count": 26, "description": "新闻聚合和新闻摘要服务"},
            {"name": "音视频摘要", "estimated_count": 26, "description": "会议记录、视频内容的自动摘要"}
        ],
        "total_sub_count": 88
    },
    {
        "original_name": "AI工具/人工智能/推荐系统",
        "current_count": 86,
        "split_dimension": "推荐对象与领域",
        "complexity": "medium",
        "rationale": "推荐系统按推荐对象和应用领域细分",
        "sub_categories": [
            {"name": "内容推荐引擎", "estimated_count": 34, "description": "新闻、文章、视频等内容推荐系统"},
            {"name": "电商商品推荐", "estimated_count": 30, "description": "电商平台商品推荐、个性化推荐引擎"},
            {"name": "多媒体推荐", "estimated_count": 22, "description": "音乐、电影、图像等多媒体内容推荐"}
        ],
        "total_sub_count": 86
    },
    {
        "original_name": "AI工具/人工智能/翻译服务",
        "current_count": 86,
        "split_dimension": "翻译模态与场景",
        "complexity": "medium",
        "rationale": "翻译服务按翻译模态和应用场景细分",
        "sub_categories": [
            {"name": "文本机器翻译", "estimated_count": 42, "description": "多语言文本的机器翻译服务"},
            {"name": "语音实时翻译", "estimated_count": 24, "description": "语音对话实时翻译、同声传译工具"},
            {"name": "文档翻译", "estimated_count": 20, "description": "整份文档的翻译和格式保留服务"}
        ],
        "total_sub_count": 86
    },
    {
        "original_name": "AI工具/人工智能/情感分析",
        "current_count": 86,
        "split_dimension": "分析对象与应用场景",
        "complexity": "medium",
        "rationale": "情感分析按分析对象和应用场景细分",
        "sub_categories": [
            {"name": "文本情感分析", "estimated_count": 44, "description": "文本情感倾向、情绪分析API和工具"},
            {"name": "社交媒体监听", "estimated_count": 24, "description": "社交平台舆情监控和情感分析"},
            {"name": "客户反馈分析", "estimated_count": 18, "description": "客户评价、客服对话的情感分析"}
        ],
        "total_sub_count": 86
    },
    {
        "original_name": "AI工具/人工智能/预测分析",
        "current_count": 86,
        "split_dimension": "预测领域与业务场景",
        "complexity": "medium",
        "rationale": "预测分析按业务领域细分",
        "sub_categories": [
            {"name": "销售与需求预测", "estimated_count": 30, "description": "销售趋势、商品需求预测工具"},
            {"name": "金融市场预测", "estimated_count": 28, "description": "股票、汇率、市场走势预测"},
            {"name": "业务运营预测", "estimated_count": 28, "description": "库存、物流、用户行为预测"}
        ],
        "total_sub_count": 86
    },
    {
        "original_name": "AI工具/人工智能/自动化流程",
        "current_count": 86,
        "split_dimension": "自动化场景与复杂度",
        "complexity": "medium",
        "rationale": "自动化流程按应用场景和复杂度细分",
        "sub_categories": [
            {"name": "工作流自动化", "estimated_count": 36, "description": "Zapier、IFTTT等应用间自动化连接工具"},
            {"name": "业务流程自动化(RPA)", "estimated_count": 30, "description": "RPA机器人流程自动化平台"},
            {"name": "智能任务自动化", "estimated_count": 20, "description": "AI驱动的智能任务执行与自动化"}
        ],
        "total_sub_count": 86
    }
]

# ===== AI图像生成相关类（细分为2-3个子类） =====
ai_image_plans = [
    {
        "original_name": "AI工具/人工智能/产品图生成",
        "current_count": 65,
        "split_dimension": "生成场景",
        "complexity": "low",
        "rationale": "产品图生成按应用场景细分",
        "sub_categories": [
            {"name": "电商产品图生成", "estimated_count": 38, "description": "电商场景图、商品展示图自动生成"},
            {"name": "营销素材生成", "estimated_count": 27, "description": "广告营销素材、宣传图生成工具"}
        ],
        "total_sub_count": 65
    },
    {
        "original_name": "AI工具/人工智能/文生图",
        "current_count": 59,
        "split_dimension": "风格类型与模型",
        "complexity": "low",
        "rationale": "文生图按生成风格和模型架构细分",
        "sub_categories": [
            {"name": "艺术风格生成", "estimated_count": 31, "description": "艺术风格、创意风格图像生成"},
            {"name": "写实图像生成", "estimated_count": 28, "description": "照片级真实感图像生成"}
        ],
        "total_sub_count": 59
    },
    {
        "original_name": "AI工具/人工智能/图生图",
        "current_count": 59,
        "split_dimension": "转换功能",
        "complexity": "low",
        "rationale": "图生图按图像转换功能细分",
        "sub_categories": [
            {"name": "风格迁移转换", "estimated_count": 26, "description": "艺术风格迁移、风格转换"},
            {"name": "智能图像编辑", "estimated_count": 20, "description": "智能编辑、修改、重绘"},
            {"name": "图像质量增强", "estimated_count": 13, "description": "超分、去噪、画质增强"}
        ],
        "total_sub_count": 59
    },
    {
        "original_name": "AI工具/人工智能/图像修复",
        "current_count": 59,
        "split_dimension": "修复对象与任务",
        "complexity": "low",
        "rationale": "图像修复按修复对象和任务类型细分",
        "sub_categories": [
            {"name": "老照片修复与着色", "estimated_count": 27, "description": "老照片修复、上色、清晰化"},
            {"name": "图像去瑕疵", "estimated_count": 20, "description": "水印去除、瑕疵修复、物体擦除"},
            {"name": "图像补全与扩展", "estimated_count": 12, "description": "图像补全、边缘扩展、outpainting"}
        ],
        "total_sub_count": 59
    },
    {
        "original_name": "AI工具/人工智能/图像扩展",
        "current_count": 59,
        "split_dimension": "扩展维度",
        "complexity": "low",
        "rationale": "图像扩展按扩展方向细分",
        "sub_categories": [
            {"name": "图像外扩(Outpainting)", "estimated_count": 35, "description": "图像边界扩展、画面延伸"},
            {"name": "智能裁剪与重构", "estimated_count": 24, "description": "智能裁剪、内容感知缩放"}
        ],
        "total_sub_count": 59
    },
    {
        "original_name": "AI工具/人工智能/风格迁移",
        "current_count": 59,
        "split_dimension": "目标风格",
        "complexity": "low",
        "rationale": "风格迁移按目标艺术风格细分",
        "sub_categories": [
            {"name": "绘画艺术风格", "estimated_count": 30, "description": "油画、水彩、素描等绘画风格"},
            {"name": "设计与数字艺术", "estimated_count": 29, "description": "平面设计、海报、数字艺术风格"}
        ],
        "total_sub_count": 59
    },
    {
        "original_name": "AI工具/人工智能/超分辨率",
        "current_count": 59,
        "split_dimension": "应用媒体类型",
        "complexity": "low",
        "rationale": "超分辨率按处理的媒体类型细分",
        "sub_categories": [
            {"name": "图像超分辨率", "estimated_count": 32, "description": "图像放大、高清化、去模糊"},
            {"name": "视频超分辨率", "estimated_count": 27, "description": "视频画质增强、超分、插帧"}
        ],
        "total_sub_count": 59
    },
    {
        "original_name": "AI工具/人工智能/背景移除",
        "current_count": 59,
        "split_dimension": "目标对象",
        "complexity": "low",
        "rationale": "背景移除按移除对象细分",
        "sub_categories": [
            {"name": "人像抠图", "estimated_count": 34, "description": "人像背景移除、人像分割"},
            {"name": "通用物体抠图", "estimated_count": 25, "description": "通用物体、产品抠图工具"}
        ],
        "total_sub_count": 59
    },
    {
        "original_name": "AI工具/人工智能/人脸编辑",
        "current_count": 59,
        "split_dimension": "编辑功能",
        "complexity": "low",
        "rationale": "人脸编辑按编辑功能细分",
        "sub_categories": [
            {"name": "美颜美妆", "estimated_count": 31, "description": "美颜、滤镜、美妆效果"},
            {"name": "人脸属性编辑", "estimated_count": 28, "description": "换脸、年龄变换、表情编辑"}
        ],
        "total_sub_count": 59
    },
    {
        "original_name": "AI工具/人工智能/3D生成",
        "current_count": 59,
        "split_dimension": "输入模态",
        "complexity": "low",
        "rationale": "3D生成按输入方式细分",
        "sub_categories": [
            {"name": "文本生成3D", "estimated_count": 31, "description": "文本描述生成3D模型"},
            {"name": "图像生成3D", "estimated_count": 28, "description": "单张或多张图片生成3D模型"}
        ],
        "total_sub_count": 59
    },
    {
        "original_name": "AI工具/人工智能/色彩调整",
        "current_count": 58,
        "split_dimension": "调整目的",
        "complexity": "low",
        "rationale": "色彩调整按调整目的细分",
        "sub_categories": [
            {"name": "自动色彩校正", "estimated_count": 31, "description": "自动白平衡、色彩校正"},
            {"name": "艺术色彩滤镜", "estimated_count": 27, "description": "色彩滤镜、风格化调色"}
        ],
        "total_sub_count": 58
    },
    {
        "original_name": "AI工具/人工智能/图像增强",
        "current_count": 58,
        "split_dimension": "增强目标",
        "complexity": "low",
        "rationale": "图像增强按增强目标细分",
        "sub_categories": [
            {"name": "画质增强", "estimated_count": 32, "description": "去噪、锐化、细节增强"},
            {"name": "低质量修复", "estimated_count": 26, "description": "模糊修复、低清转高清"}
        ],
        "total_sub_count": 58
    },
    {
        "original_name": "AI工具/人工智能/草图转图",
        "current_count": 58,
        "split_dimension": "草图输入类型",
        "complexity": "low",
        "rationale": "草图转图按输入草图类型细分",
        "sub_categories": [
            {"name": "线稿上色", "estimated_count": 31, "description": "黑白线稿自动上色"},
            {"name": "草图精绘", "estimated_count": 27, "description": "草图转精细图像、概念图生成"}
        ],
        "total_sub_count": 58
    },
    {
        "original_name": "AI工具/人工智能/场景生成",
        "current_count": 58,
        "split_dimension": "场景类型",
        "complexity": "low",
        "rationale": "场景生成按生成场景类型细分",
        "sub_categories": [
            {"name": "自然风景生成", "estimated_count": 30, "description": "自然景观、天空、水体等场景生成"},
            {"name": "城市与建筑生成", "estimated_count": 28, "description": "城市景观、建筑结构生成"}
        ],
        "total_sub_count": 58
    },
    {
        "original_name": "AI工具/人工智能/动漫风格",
        "current_count": 58,
        "split_dimension": "艺术风格流派",
        "complexity": "low",
        "rationale": "动漫风格按艺术流派细分",
        "sub_categories": [
            {"name": "日式动漫风格", "estimated_count": 30, "description": "日本动漫、二次元风格生成"},
            {"name": "美式/其他动漫", "estimated_count": 28, "description": "美式卡通、欧美动漫风格"}
        ],
        "total_sub_count": 58
    }
]

# ===== 效率办公类（拆分为2-3个子类） =====
efficiency_plans = [
    {
        "original_name": "效率办公/协作工具",
        "current_count": 69,
        "split_dimension": "协作类型",
        "complexity": "low",
        "rationale": "协作工具按协作模式细分",
        "sub_categories": [
            {"name": "项目管理工具", "estimated_count": 30, "description": "Trello、Asana、Jira等项目管理"},
            {"name": "团队沟通工具", "estimated_count": 25, "description": "Slack、Teams、飞书等团队沟通"},
            {"name": "知识库与文档协作", "estimated_count": 14, "description": "Notion、Confluence等知识库协作"}
        ],
        "total_sub_count": 69
    },
    {
        "original_name": "效率办公/博客管理",
        "current_count": 65,
        "split_dimension": "博客类型",
        "complexity": "low",
        "rationale": "博客管理按博客平台类型细分",
        "sub_categories": [
            {"name": "博客平台", "estimated_count": 36, "description": "WordPress、Medium、Ghost等博客托管平台"},
            {"name": "博客写作工具", "estimated_count": 29, "description": "博客编辑、管理、发布工具"}
        ],
        "total_sub_count": 65
    },
    {
        "original_name": "效率办公/剧本创作",
        "current_count": 59,
        "split_dimension": "剧本类型",
        "complexity": "low",
        "rationale": "剧本创作按创作内容类型细分",
        "sub_categories": [
            {"name": "影视剧本工具", "estimated_count": 32, "description": "电影、电视剧剧本写作与格式化工具"},
            {"name": "游戏剧本工具", "estimated_count": 27, "description": "游戏剧情、对话、任务剧本创作工具"}
        ],
        "total_sub_count": 59
    },
    {
        "original_name": "效率办公/总结摘要",
        "current_count": 59,
        "split_dimension": "内容类型",
        "complexity": "low",
        "rationale": "总结摘要按处理内容类型细分",
        "sub_categories": [
            {"name": "文档摘要", "estimated_count": 33, "description": "长文档、报告、文章的自动摘要"},
            {"name": "会议与音视频摘要", "estimated_count": 26, "description": "会议记录、音视频内容自动摘要"}
        ],
        "total_sub_count": 59
    },
    {
        "original_name": "效率办公/社交媒体",
        "current_count": 59,
        "split_dimension": "管理功能",
        "complexity": "low",
        "rationale": "社交媒体工具按核心功能细分",
        "sub_categories": [
            {"name": "社媒管理与发布", "estimated_count": 34, "description": "多平台内容管理和自动发布工具"},
            {"name": "社媒数据分析", "estimated_count": 25, "description": "社交媒体数据分析与监控平台"}
        ],
        "total_sub_count": 59
    },
    {
        "original_name": "效率办公/内容写作",
        "current_count": 58,
        "split_dimension": "写作类型",
        "complexity": "low",
        "rationale": "内容写作按写作内容类型细分",
        "sub_categories": [
            {"name": "博客文章写作", "estimated_count": 30, "description": "博客、专栏文章写作助手"},
            {"name": "技术文档写作", "estimated_count": 28, "description": "技术文档、手册编写工具"}
        ],
        "total_sub_count": 58
    },
    {
        "original_name": "效率办公/文案优化",
        "current_count": 58,
        "split_dimension": "优化目标",
        "complexity": "low",
        "rationale": "文案优化按优化目标细分",
        "sub_categories": [
            {"name": "文案润色与改写", "estimated_count": 31, "description": "文案润色、语法优化、风格改写"},
            {"name": "SEO优化", "estimated_count": 27, "description": "搜索引擎优化文案工具"}
        ],
        "total_sub_count": 58
    },
    {
        "original_name": "效率办公/AI写作",
        "current_count": 58,
        "split_dimension": "写作场景",
        "complexity": "low",
        "rationale": "AI写作按使用场景细分",
        "sub_categories": [
            {"name": "通用AI写作", "estimated_count": 32, "description": "通用内容生成、写作助手"},
            {"name": "专业领域写作", "estimated_count": 26, "description": "特定领域专业内容生成"}
        ],
        "total_sub_count": 58
    },
    {
        "original_name": "效率办公/诗歌创作",
        "current_count": 58,
        "split_dimension": "创作类型",
        "complexity": "low",
        "rationale": "诗歌创作按文学类型细分",
        "sub_categories": [
            {"name": "诗歌与韵文", "estimated_count": 32, "description": "诗歌、诗词、歌词创作"},
            {"name": "文学创作辅助", "estimated_count": 26, "description": "小说、散文等文学创作辅助"}
        ],
        "total_sub_count": 58
    },
    {
        "original_name": "效率办公/营销文案",
        "current_count": 58,
        "split_dimension": "营销场景",
        "complexity": "low",
        "rationale": "营销文案按营销渠道和场景细分",
        "sub_categories": [
            {"name": "广告文案生成", "estimated_count": 32, "description": "广告语、banner文案生成"},
            {"name": "营销内容创作", "estimated_count": 26, "description": "营销邮件、推送、落地页文案"}
        ],
        "total_sub_count": 58
    },
    {
        "original_name": "效率办公/技术写作",
        "current_count": 58,
        "split_dimension": "文档类型",
        "complexity": "low",
        "rationale": "技术写作按文档类型细分",
        "sub_categories": [
            {"name": "API文档生成", "estimated_count": 30, "description": "API文档自动生成和维护"},
            {"name": "技术手册编写", "estimated_count": 28, "description": "用户手册、技术指南编写"}
        ],
        "total_sub_count": 58
    },
    {
        "original_name": "效率办公/邮件写作",
        "current_count": 57,
        "split_dimension": "邮件类型",
        "complexity": "low",
        "rationale": "邮件写作按邮件类型细分",
        "sub_categories": [
            {"name": "邮件草稿生成", "estimated_count": 30, "description": "邮件正文、内容自动生成"},
            {"name": "智能邮件回复", "estimated_count": 27, "description": "邮件智能回复建议和起草"}
        ],
        "total_sub_count": 57
    },
    {
        "original_name": "效率办公/创意激发",
        "current_count": 57,
        "split_dimension": "创意类型",
        "complexity": "low",
        "rationale": "创意激发按创意产出类型细分",
        "sub_categories": [
            {"name": "头脑风暴与创意生成", "estimated_count": 31, "description": "创意点子、idea生成工具"},
            {"name": "命名与标语", "estimated_count": 26, "description": "品牌命名、口号标语生成"}
        ],
        "total_sub_count": 57
    },
    {
        "original_name": "效率办公/标题生成",
        "current_count": 57,
        "split_dimension": "内容类型",
        "complexity": "low",
        "rationale": "标题生成按目标内容类型细分",
        "sub_categories": [
            {"name": "文章/博客标题", "estimated_count": 32, "description": "文章标题优化和生成"},
            {"name": "广告/营销标题", "estimated_count": 25, "description": "广告标题、标语生成"}
        ],
        "total_sub_count": 57
    },
    {
        "original_name": "效率办公/改写重述",
        "current_count": 57,
        "split_dimension": "改写目的",
        "complexity": "low",
        "rationale": "改写重述按改写目标细分",
        "sub_categories": [
            {"name": "内容重写", "estimated_count": 32, "description": "文章重写、内容改写"},
            {"name": "风格转换", "estimated_count": 25, "description": "文风转换、语气调整"}
        ],
        "total_sub_count": 57
    },
    {
        "original_name": "效率办公/故事生成",
        "current_count": 57,
        "split_dimension": "故事长度",
        "complexity": "low",
        "rationale": "故事生成按故事长度和复杂度细分",
        "sub_categories": [
            {"name": "短篇故事生成", "estimated_count": 31, "description": "短篇小说、微故事生成"},
            {"name": "长篇创作辅助", "estimated_count": 26, "description": "长篇小说、系列故事创作辅助"}
        ],
        "total_sub_count": 57
    }
]

# ===== 其他小型超容分类（拆分为2-3个子类） =====
other_over_capacity = [
    {
        "original_name": "系统工具/实用工具/其他工具",
        "current_count": 35,
        "split_dimension": "工具类型",
        "complexity": "low",
        "rationale": "其他工具按功能类型细分",
        "sub_categories": [
            {"name": "系统优化工具", "estimated_count": 18, "description": "系统清理、加速、优化工具"},
            {"name": "实用小工具集合", "estimated_count": 17, "description": "计算器、日历、便签等小工具"}
        ],
        "total_sub_count": 35
    },
    {
        "original_name": "AI工具/人工智能/综合平台",
        "current_count": 30,
        "split_dimension": "平台能力覆盖",
        "complexity": "low",
        "rationale": "综合AI平台按能力覆盖细分",
        "sub_categories": [
            {"name": "多模态AI平台", "estimated_count": 20, "description": "集成文本、图像、语音等多种能力的平台"},
            {"name": "垂直AI解决方案", "estimated_count": 10, "description": "面向特定行业的AI解决方案平台"}
        ],
        "total_sub_count": 30
    },
    {
        "original_name": "AI工具/人工智能/音频生成",
        "current_count": 27,
        "split_dimension": "音频生成类型",
        "complexity": "low",
        "rationale": "音频生成按生成内容类型细分",
        "sub_categories": [
            {"name": "语音合成(TTS)", "estimated_count": 15, "description": "文本转语音、语音克隆工具"},
            {"name": "音乐与声音生成", "estimated_count": 12, "description": "背景音乐、音效生成工具"}
        ],
        "total_sub_count": 27
    },
    {
        "original_name": "多媒体/视频娱乐/国外视频",
        "current_count": 24,
        "split_dimension": "视频内容类型",
        "complexity": "low",
        "rationale": "国外视频按内容类型细分",
        "sub_categories": [
            {"name": "视频分享平台", "estimated_count": 14, "description": "YouTube等视频分享和流媒体平台"},
            {"name": "在线教育视频", "estimated_count": 10, "description": "国际在线教育视频平台"}
        ],
        "total_sub_count": 24
    },
]

# 网文相关类 - 拆分为多个子类（原来的23个站点实际上可以拆分得更细）
webnovel_plan = {
    "original_name": "效率办公/网络小说平台",
    "current_count": 23,
    "split_dimension": "已经是多个子类，但site数均为23（疑似父类标记问题）",
    "complexity": "high",
    "rationale": "注意：category_stats显示13个'效率办公/网文XXX'类别各有23个站点，这可能是数据标记问题（所有网文相关站点都标记了多个分类）。需要去重和重新分配。",
    "sub_categories": [
        {"name": "起点/纵横/晋江等主流平台", "estimated_count": 23, "description": "起点中文网、纵横中文网、晋江文学城等主流网文平台（原标记有误，需调整）"}
    ],
    "total_sub_count": 23,
    "special_note": "网文相关13个分类（网文作者工具、投稿平台、论坛社区、资源下载、写作教程、阅读应用、数据分析、版权交易、作家协会、编辑工具、推广平台、书评社区、榜单统计、辅助工具）显示各有23个站点，库应实为同一批网文平台的重复标记，需要数据清洗和重新分配，而非拆分。"
}

# 其他杂项类（22个站点）
misc_plan = {
    "original_name": "其他/杂项",
    "current_count": 88,  # 合并所有"其他/杂项/XXX"类别
    "split_dimension": "工具/服务类型",
    "complexity": "low",
    "rationale": "将各类杂项工具按功能类型合并细分",
    "sub_categories": [
        {"name": "开发者工具", "estimated_count": 22, "description": "JSON、正则、在线测试、API等开发工具"},
        {"name": "实用计算工具", "estimated_count": 22, "description": "在线计算、单位转换、时间工具等"},
        {"name": "信息查询工具", "estimated_count": 22, "description": "搜索引擎、词典翻译、公共数据查询"},
        {"name": "生活服务工具", "estimated_count": 22, "description": "短链接、二维码、政府服务等生活工具"}
    ],
    "total_sub_count": 88
}

# 设计资源类（需要合并）
design_resources_aggregate = {
    "original_name": "设计工具/资源类合并",
    "current_count": 21+20+20+20+20+19+19+19+19+19+19,  # 11个资源类
    "split_dimension": "资源类型整合",
    "complexity": "low",
    "rationale": "将分散的资源类（矢量图标、图库照片、UI套件、字体、PPT模板、设计素材、配色方案、设计灵感、3D模型、样机模板、图标资源等）整合为统一资源平台分类，便于管理和浏览",
    "sub_categories": [
        {"name": "图标与矢量资源", "estimated_count": 42, "description": "矢量图标、插画、字体资源平台"},
        {"name": "图片与图库", "estimated_count": 39, "description": "高清图库、照片素材、免费图片"},
        {"name": "UI设计资源", "estimated_count": 39, "description": "UI套件、模板、设计素材、灵感平台"},
        {"name": "字体与排版", "estimated_count": 39, "description": "字体下载、在线字体、排版工具"},
        {"name": "样机与模板", "estimated_count": 39, "description": "样机模板、演示文稿、设计模板"}
    ],
    "total_sub_count": 207
}

# 合并所有拆分计划
all_plans = [github_plan, data_analysis_plan, video_tutorial_plan, code_assistant_plan,
            video_gen_plan, image_recognition_plan, ui_design_plan, file_tools_plan]

# 添加AI剩余
all_plans.extend(ai_remaining_plans)
all_plans.extend(ai_image_plans)
all_plans.extend(efficiency_plans)
all_plans.append(other_over_capacity[0])  # 其他工具
all_plans.append(other_over_capacity[1])  # AI综合平台
all_plans.append(other_over_capacity[2])  # 音频生成
all_plans.append(other_over_capacity[3])  # 国外视频

# 添加网文和杂项
all_plans.append(webnovel_plan)
all_plans.append(misc_plan)
all_plans.append(design_resources_aggregate)

# 添加剩余的媒体类
multimedia_remaining = [
    {
        "original_name": "多媒体/视频娱乐/音乐教程",
        "current_count": 13,
        "split_dimension": "音乐类型",
        "complexity": "low",
        "rationale": "音乐教程细分",
        "sub_categories": [
            {"name": "乐器教程", "estimated_count": 8, "description": "乐器学习教程"},
            {"name": "音乐理论与作曲", "estimated_count": 5, "description": "音乐理论、作曲教程"}
        ],
        "total_sub_count": 13
    },
    {
        "original_name": "开发工具/学习生成/在线课程",
        "current_count": 20,
        "split_dimension": "课程类型",
        "complexity": "low",
        "rationale": "在线课程细分",
        "sub_categories": [
            {"name": "编程课程", "estimated_count": 12, "description": "编程技术在线课程"},
            {"name": "技能培训课程", "estimated_count": 8, "description": "各类技能在线培训"}
        ],
        "total_sub_count": 20
    },
]

all_plans.extend(multimedia_remaining)

# 确保所有超容分类都被包含
processed_names = {p['original_name'] for p in all_plans}
missing = set(over_capacity_cats.keys()) - processed_names
if missing:
    print(f"警告: 以下超容分类未处理: {missing}")

split_plan["split_categories"] = all_plans

# 写入JSON文件
output_path = '/home/yoli/GitHub/web_nav_v2/plans/over_capacity_split_plan.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(split_plan, f, ensure_ascii=False, indent=2)

print(f"\n✓ 拆分计划已生成: {output_path}")
print(f"✓ 总共处理超容分类: {len(all_plans)} 个（目标: 覆盖全部51个超容大类）")
print()

# 打印详细摘要
total_original = sum(p['current_count'] for p in all_plans)
total_subs = sum(len(p['sub_categories']) for p in all_plans)

print("="*80)
print("超容分类拆分计划 - 详细摘要")
print("="*80)
print(f"计划覆盖超容分类数: {len(all_plans)}")
print(f"涉及总站点数: {total_original}")
print(f"计划创建子分类数: {total_subs}")
print(f"预期平均每个子类站点数: {total_original // total_subs if total_subs else 0}")
print()

for i, plan in enumerate(all_plans, 1):
    orig = plan['original_name']
    curr = plan['current_count']
    subs = plan['sub_categories']
    comp = plan['complexity']
    avg = curr // len(subs) if subs else 0
    print(f"{i:2d}. [{comp.upper()}] {orig}")
    print(f"      当前: {curr} → 拆分为 {len(subs)} 个子类")
    print(f"      预期目标范围: {min(s['estimated_count'] for s in subs) if subs else 0} - {max(s['estimated_count'] for s in subs) if subs else 0}")
    for sub in subs[:3]:
        print(f"        • {sub['name']}: {sub['estimated_count']} sites")
    if len(subs) > 3:
        print(f"        ... 和 {len(subs)-3} 个其他子类")
    print()

print("="*80)
print("优先级执行建议:")
print("  1. [URGENT] GitHub类(206) → 16个子类 - 复杂度高，需要详细站点分析")
print("  2. [HIGH] AI类(196+153+140+...) - 10+个大类，按领域细分")
print("  3. [MEDIUM] 多媒体教程(192) - 按学科领域细分")
print("  4. [MEDIUM] 设计工具、系统工具类 - 按功能细分")
print("="*80)
