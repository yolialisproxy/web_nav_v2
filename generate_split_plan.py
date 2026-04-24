#!/usr/bin/env python3
"""
生成超容分类的细粒度拆分计划
针对51个超容分类（>50站点），为V10平衡度优化提供实施蓝图
重点：GitHub类拆分为至少15个子类
"""

import json
from datetime import datetime

# 基于分析生成的拆分计划
split_plan = {
    "plan_metadata": {
        "plan_name": "over_capacity_split_plan_v1",
        "generated_at": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "target_version": "V10",
        "total_over_capacity_categories": 51,
        "focus_category": "开发工具/平台开源/GitHub",
        "goal": "将51个超容分类（>50站点）拆分为10-50站点的子类，提升整体平衡度至80%+"
    },
    "split_categories": []
}

# ===== 优先级1: GitHub类（206个站点） - 拆分为15+个子类 =====
github_plan = {
    "original_name": "开发工具/平台开源/GitHub",
    "current_count": 206,
    "split_dimension": "功能场景与平台类型（GitHub本体、替代平台、集成工具、资源托管、开发工具、文档教程、项目索引、开源社区）",
    "complexity": "high",
    "rationale": "GitHub类包含大量非GitHub本体站点（GitLab/Gitee等替代平台、CDN资源、文档站点、Awesome列表等），需要按功能、平台类型、内容性质进行多维度细分",
    "sub_categories": [
        {"name": "GitHub本体服务", "estimated_count": 35, "description": "GitHub官方网站、博客、文档、安全实验室、支持中心等官方服务"},
        {"name": "GitHub客户端工具", "estimated_count": 12, "description": "GitHub Desktop、CLI、Mobile等官方客户端"},
        {"name": "GitHub Actions与CI/CD", "estimated_count": 18, "description": "Actions marketplace、CI/CD相关工具和服务集成"},
        {"name": "GitHub Packages与容器", "estimated_count": 10, "description": "Packages、容器注册表、依赖托管服务"},
        {"name": "GitHub Pages与网站托管", "estimated_count": 15, "description": "Pages托管站点、静态网站生成器集成"},
        {"name": "开源项目索引", "estimated_count": 45, "description": "Awesome列表、开源项目集合、awesome-selfhosted等索引站点"},
        {"name": "代码托管替代平台", "estimated_count": 40, "description": "GitLab、Gitee、Bitbucket、SourceForge等竞争平台"},
        {"name": "GitHub替代/镜像", "estimated_count": 8, "description": "GitHub镜像站、缓存服务、替代访问方案"},
        {"name": "IDE与编辑器集成", "estimated_count": 15, "description": "VS Code、JetBrains等IDE的GitHub插件和集成"},
        {"name": "开发工具集成", "estimated_count": 20, "description": "各种开发工具、框架对GitHub的集成（CI、部署、监控等）"},
        {"name": "文档与教程", "estimated_count": 12, "description": "GitHub使用教程、文档站点、学习资源"},
        {"name": "开发者社区资源", "estimated_count": 10, "description": "GitHub开发者社区、论坛、学习平台"},
        {"name": "GitHub API与服务", "estimated_count": 8, "description": "基于GitHub API构建的服务和工具"},
        {"name": "开源组织项目", "estimated_count": 25, "description": "知名开源组织在GitHub托管的项目（如tensorflow、microsoft等）"},
        {"name": "GitHub资源与素材", "estimated_count": 6, "description": "GitHub主题、模板、资源文件"},
        {"name": "其他GitHub相关", "estimated_count": 7, "description": "未能明确归类的GitHub相关站点"}
    ],
    "total_sub_count": 206,
    "note": "需要基于网站实际内容进行精确归类，过滤掉静态资源文件（.js/.css），聚焦真实网站服务"
}

# ===== 优先级2: AI工具/人工智能/数据分析（196） =====
data_analysis_plan = {
    "original_name": "AI工具/人工智能/数据分析",
    "current_count": 196,
    "split_dimension": "数据类型与应用场景（商业智能、数据科学、大数据处理、数据库工具）",
    "complexity": "medium",
    "rationale": "数据分析涵盖范围广，从BI可视化到大数据处理，需要按场景细分",
    "sub_categories": [
        {"name": "商业智能BI", "estimated_count": 35, "description": "Tableau、PowerBI、Looker等BI可视化工具"},
        {"name": "数据科学平台", "estimated_count": 40, "description": "Jupyter、Kaggle、Colab等数据科学工作台"},
        {"name": "大数据处理", "estimated_count": 30, "description": "Hadoop、Spark、Flink等大数据框架和云服务"},
        {"name": "数据库与分析", "estimated_count": 35, "description": "云数据库、数据仓库、SQL工具"},
        {"name": "数据可视化库", "estimated_count": 25, "description": "ECharts、D3.js、Chart.js等可视化库和工具"},
        {"name": "数据采集与ETL", "estimated_count": 31, "description": "数据采集、清洗、转换工具"}
    ],
    "total_sub_count": 196
}

# ===== 优先级3: 多媒体/视频娱乐/教程（192） =====
video_tutorial_plan = {
    "original_name": "多媒体/视频娱乐/教程",
    "current_count": 192,
    "split_dimension": "内容类型与技术领域（编程教程、设计教程、综合平台、特定技能）",
    "complexity": "medium",
    "rationale": "教程类内容过多，需要按教授领域和平台类型拆分",
    "sub_categories": [
        {"name": "编程/开发教程", "estimated_count": 60, "description": "Codecademy、freeCodeCamp、W3Schools等编程学习平台"},
        {"name": "设计/创意教程", "estimated_count": 35, "description": "UI/UX设计、图形设计、视频编辑教程"},
        {"name": "综合慕课平台", "estimated_count": 40, "description": "Coursera、edX、Udemy等综合在线教育平台"},
        {"name": "技术文档/文档站", "estimated_count": 25, "description": "MDN、各种框架官方文档、技术教程站"},
        {"name": "语言学习教程", "estimated_count": 18, "description": "多邻国、Busuu等语言学习平台"},
        {"name": "职业技能培训", "estimated_count": 14, "description": "商业、市场、管理等职业技能课程"}
    ],
    "total_sub_count": 192
}

# ===== 优先级4: AI工具/人工智能/代码助手（177） =====
code_assistant_plan = {
    "original_name": "AI工具/人工智能/代码助手",
    "current_count": 177,
    "split_dimension": "功能定位（AI编程助手、低代码平台、API生成、代码工具）",
    "complexity": "medium",
    "rationale": "代码助手涵盖AI编程、自动补全、代码生成、低代码等多种类型",
    "sub_categories": [
        {"name": "AI代码生成器", "estimated_count": 45, "description": "GitHub Copilot、Cursor、Windsurf等AI代码生成"},
        {"name": "AI代码补全", "estimated_count": 30, "description": "Tabnine、Kite等智能补全工具"},
        {"name": "低代码/无代码", "estimated_count": 35, "description": "Bubble、Webflow、Retool等低代码平台"},
        {"name": "API设计与生成", "estimated_count": 25, "description": "Postman、Swagger、Apifox等API工具"},
        {"name": "代码分析与审查", "estimated_count": 20, "description": "SonarQube、CodeQL等代码质量工具"},
        {"name": "代码转换/重构", "estimated_count": 22, "description": "代码转换、重构、优化工具"}
    ],
    "total_sub_count": 177
}

# ===== 优先级5: AI工具/人工智能/视频生成（153） =====
video_gen_plan = {
    "original_name": "AI工具/人工智能/视频生成",
    "current_count": 153,
    "split_dimension": "功能类型（文生视频、图生视频、视频编辑、数字人）",
    "complexity": "medium",
    "rationale": "视频生成技术路线多样，需按输入方式和应用场景细分",
    "sub_categories": [
        {"name": "文生视频", "estimated_count": 38, "description": "Runway、Pika等文本生成视频工具"},
        {"name": "图生视频/动画", "estimated_count": 32, "description": "图像转视频、动画生成工具"},
        {"name": "AI视频编辑", "estimated_count": 28, "description": "智能剪辑、特效、调色工具"},
        {"name": "数字人/虚拟主播", "estimated_count": 22, "description": "虚拟形象、数字人视频生成"},
        {"name": "视频增强/修复", "estimated_count": 18, "description": "超分辨率、去噪、修复工具"},
        {"name": "视频生成平台", "estimated_count": 15, "description": "综合视频生成服务平台"}
    ],
    "total_sub_count": 153
}

# ===== 优先级6: AI工具/人工智能/图像识别（140） =====
image_recognition_plan = {
    "original_name": "AI工具/人工智能/图像识别",
    "current_count": 140,
    "split_dimension": "应用场景（通用识别、人脸、OCR、质量检测）",
    "complexity": "medium",
    "rationale": "图像识别在不同场景有专门优化，需按识别对象细分",
    "sub_categories": [
        {"name": "通用图像识别", "estimated_count": 30, "description": "通用物体、场景识别API和服务"},
        {"name": "人脸识别与分析", "estimated_count": 28, "description": "人脸检测、识别、表情分析"},
        {"name": "OCR文字识别", "estimated_count": 32, "description": "文档OCR、场景文字识别、表格提取"},
        {"name": "图像质量检测", "estimated_count": 22, "description": "工业质检、缺陷检测、质量评估"},
        {"name": "医疗影像识别", "estimated_count": 18, "description": "医学影像分析、疾病诊断辅助"},
        {"name": " specialized识别", "estimated_count": 10, "description": "车辆、车牌、手势等特殊识别"}
    ],
    "total_sub_count": 140
}

# ===== 优先级7: 设计工具/UI设计工具（125） =====
ui_design_plan = {
    "original_name": "设计工具/UI设计工具",
    "current_count": 125,
    "split_dimension": "设计阶段（原型、UI、协作、设计系统）",
    "complexity": "medium",
    "rationale": "UI设计流程包含多个阶段，可按功能和协作方式细分",
    "sub_categories": [
        {"name": "原型设计", "estimated_count": 30, "description": "Figma、Sketch、Adobe XD等原型工具"},
        {"name": "UI设计工具", "estimated_count": 32, "description": "界面设计、高保真设计工具"},
        {"name": "设计协作", "estimated_count": 25, "description": "设计协作、评审、交付平台"},
        {"name": "设计系统管理", "estimated_count": 20, "description": "设计 token、组件库、设计系统平台"},
        {"name": "交互设计", "estimated_count": 18, "description": "交互动效、微交互设计工具"}
    ],
    "total_sub_count": 125
}

# ===== 优先级8: 系统工具/实用工具/文件工具（121） =====
file_tools_plan = {
    "original_name": "系统工具/实用工具/文件工具",
    "current_count": 121,
    "split_dimension": "功能类型（压缩、转换、同步、管理）",
    "complexity": "medium",
    "rationale": "文件工具功能分散，按具体功能细分",
    "sub_categories": [
        {"name": "文件压缩/解压", "estimated_count": 28, "description": "压缩格式工具、在线压缩服务"},
        {"name": "文件转换", "estimated_count": 35, "description": "格式转换、文档转换、媒体转换"},
        {"name": "文件同步/备份", "estimated_count": 25, "description": "云同步、备份服务、文件共享"},
        {"name": "文件管理", "estimated_count": 18, "description": "文件管理器、资源管理器增强"},
        {"name": "文件安全", "estimated_count": 15, "description": "加密、解密、安全擦除工具"}
    ],
    "total_sub_count": 121
}

# ===== 优先级9-51: 其他超容分类的拆分方案 =====
# 基于AI相关类和效率办公类的聚合特性，设计合理的拆分维度

ai_categories_detail = {
    "sub_categories": [
        {"name": "AI搜索引擎", "est": 40, "desc": "Perplexity、You.com等AI原生搜索"},
        {"name": "语义搜索", "est": 35, "desc": "向量搜索、语义理解搜索工具"},
        {"name": "代码搜索", "est": 29, "desc": "AI增强的代码搜索引擎"}
    ]}
    "AI工具/人工智能/AI平台": {"count": 100, "dimension": "平台类型", "subs": [
        {"name": "大模型平台", "est": 45, "desc": "OpenAI、Claude、Gemini等大模型平台"},
        {"name": "开源模型平台", "est": 30, "desc": "Hugging Face、ModelScope等开源模型社区"},
        {"name": "AI应用开发平台", "est": 25, "desc": "低代码AI开发、模型部署平台"}
    ]},
    "AI工具/人工智能/知识图谱": {"count": 94, "dimension": "领域知识", "subs": [
        {"name": "通用知识图谱", "est": 35, "desc": "通用百科知识图谱"},
        {"name": "领域知识图谱", "est": 40, "desc": "医疗、金融、法律等垂直领域"},
        {"name": "知识管理", "est": 19, "desc": "个人/团队知识管理工具"}
    ]},
    "AI工具/人工智能/写作助手": {"count": 90, "dimension": "写作场景", "subs": [
        {"name": "通用写作助手", "est": 35, "desc": "Grammarly、QuillBot等通用写作工具"},
        {"name": "长文本创作", "est": 30, "desc": "文章、博客、故事写作助手"},
        {"name": "营销文案", "est": 25, "desc": "广告文案、营销内容生成"}
    ]},
    "AI工具/人工智能/聊天对话": {"count": 88, "dimension": "应用领域", "subs": [
        {"name": "通用聊天助手", "est": 40, "desc": "ChatGPT、Claude等通用对话AI"},
        {"name": "客服聊天机器人", "est": 30, "desc": "客服自动化、问答机器人"},
        {"name": "角色/社交聊天", "est": 18, "desc": "角色扮演、社交聊天AI"}
    ]},
    "AI工具/人工智能/语音识别": {"count": 88, "dimension": "应用场景", "subs": [
        {"name": "语音转文本", "est": 40, "desc": "语音识别、听写工具"},
        {"name": "实时字幕", "est": 28, "desc": "实时字幕生成、翻译"},
        {"name": "语音助手", "est": 20, "desc": "智能语音助手、语音控制"}
    ]},
    "AI工具/人工智能/摘要生成": {"count": 88, "dimension": "内容类型", "subs": [
        {"name": "文档摘要", "est": 35, "desc": "长文档自动摘要"},
        {"name": "新闻摘要", "est": 28, "desc": "新闻聚合和摘要"},
        {"name": "会议/视频摘要", "est": 25, "desc": "会议记录、视频内容摘要"}
    ]},
    "AI工具/人工智能/推荐系统": {"count": 86, "dimension": "推荐领域", "subs": [
        {"name": "内容推荐", "est": 35, "desc": "新闻、文章、内容推荐引擎"},
        {"name": "商品推荐", "est": 30, "desc": "电商推荐系统"},
        {"name": "多媒体推荐", "est": 21, "desc": "音乐、视频、图像推荐"}
    ]},
    "AI工具/人工智能/翻译服务": {"count": 86, "dimension": "翻译类型", "subs": [
        {"name": "文本翻译", "est": 40, "desc": "文本机器翻译服务"},
        {"name": "语音翻译", "est": 25, "desc": "语音实时翻译"},
        {"name": "文档翻译", "est": 21, "desc": "文档整篇翻译工具"}
    ]},
    "AI工具/人工智能/情感分析": {"count": 86, "dimension": "分析对象", "subs": [
        {"name": "文本情感分析", "est": 45, "desc": "文本情感倾向分析"},
        {"name": "社交监听", "est": 25, "desc": "社交媒体情感监控"},
        {"name": "客户反馈分析", "est": 16, "desc": "客户评价、反馈分析"}
    ]},
    "AI工具/人工智能/预测分析": {"count": 86, "dimension": "预测领域", "subs": [
        {"name": "销售预测", "est": 28, "desc": "销售趋势预测"},
        {"name": "金融预测", "est": 30, "desc": "股票、市场预测"},
        {"name": "需求预测", "est": 28, "desc": "需求预测、库存优化"}
    ]},
    "AI工具/人工智能/自动化流程": {"count": 86, "dimension": "自动化场景", "subs": [
        {"name": "工作流自动化", "est": 35, "desc": "Zapier、IFTTT等工作流自动化"},
        {"name": "业务流程自动化", "est": 30, "desc": "RPA、业务流程自动化"},
        {"name": "智能助手自动化", "est": 21, "desc": "AI驱动的自动任务执行"}
    ]},
    "AI工具/人工智能/产品图生成": {"count": 65, "dimension": "生成类型", "subs": [
        {"name": "电商产品图", "est": 35, "desc": "电商产品场景图生成"},
        {"name": "营销素材生成", "est": 30, "desc": "营销广告图生成"}
    ]},
    "AI工具/人工智能/文生图": {"count": 59, "dimension": "模型与风格", "subs": [
        {"name": "风格化生成", "est": 30, "desc": "艺术风格、创意图像生成"},
        {"name": "写实生成", "est": 29, "desc": "照片级真实感图像生成"}
    ]},
    "AI工具/人工智能/图生图": {"count": 59, "dimension": "转换类型", "subs": [
        {"name": "风格迁移", "est": 25, "desc": "艺术风格迁移"},
        {"name": "图像编辑", "est": 20, "desc": "智能图像编辑、修改"},
        {"name": "图像增强", "est": 14, "desc": "图像增强、优化"}
    ]},
    "AI工具/人工智能/图像修复": {"count": 59, "dimension": "修复类型", "subs": [
        {"name": "老照片修复", "est": 25, "desc": "老照片修复、着色"},
        {"name": "图像去瑕疵", "est": 20, "desc": "去除水印、瑕疵修复"},
        {"name": "超分辨率", "est": 14, "desc": "图像放大、清晰化"}
    ]},
    "AI工具/人工智能/图像扩展": {"count": 59, "dimension": "扩展功能", "subs": [
        {"name": "外扩扩展", "est": 35, "desc": "图像外扩、outpainting"},
        {"name": "智能裁剪", "est": 24, "desc": "智能裁剪、重构"}
    ]},
    "AI工具/人工智能/风格迁移": {"count": 59, "dimension": "艺术风格", "subs": [
        {"name": "绘画风格", "est": 30, "desc": "油画、水彩等绘画风格"},
        {"name": "设计风格", "est": 29, "desc": "平面、设计风格迁移"}
    ]},
    "AI工具/人工智能/超分辨率": {"count": 59, "dimension": "应用领域", "subs": [
        {"name": "通用超分", "est": 30, "desc": "通用图像超分辨率"},
        {"name": "视频超分", "est": 29, "desc": "视频超分辨率、画质增强"}
    ]},
    "AI工具/人工智能/背景移除": {"count": 59, "dimension": "对象类型", "subs": [
        {"name": "人像抠图", "est": 35, "desc": "人像背景移除"},
        {"name": "物体抠图", "est": 24, "desc": "通用物体背景移除"}
    ]},
    "AI工具/人工智能/人脸编辑": {"count": 59, "dimension": "编辑功能", "subs": [
        {"name": "美颜美妆", "est": 30, "desc": "美颜、化妆效果"},
        {"name": "人脸编辑", "est": 29, "desc": "换脸、年龄变换等"}
    ]},
    "AI工具/人工智能/3D生成": {"count": 59, "dimension": "生成方式", "subs": [
        {"name": "文生3D", "est": 30, "desc": "文本生成3D模型"},
        {"name": "图生3D", "est": 29, "desc": "图像生成3D模型"}
    ]},
    "AI工具/人工智能/色彩调整": {"count": 58, "dimension": "调整类型", "subs": [
        {"name": "自动调色", "est": 30, "desc": "智能色彩校正、调色"},
        {"name": "色彩风格化", "est": 28, "desc": "色彩滤镜、风格化"}
    ]},
    "AI工具/人工智能/图像增强": {"count": 58, "dimension": "增强目标", "subs": [
        {"name": "画质增强", "est": 35, "desc": "去噪、锐化、增强"},
        {"name": "低质修复", "est": 23, "desc": "修复模糊、低质量图像"}
    ]},
    "AI工具/人工智能/草图转图": {"count": 58, "dimension": "草图类型", "subs": [
        {"name": "线稿上色", "est": 30, "desc": "线稿自动上色"},
        {"name": "草图精绘", "est": 28, "desc": "草图转精细图像"}
    ]},
    "AI工具/人工智能/场景生成": {"count": 58, "dimension": "场景类型", "subs": [
        {"name": "风景生成", "est": 30, "desc": "自然风景生成"},
        {"name": "城市/建筑生成", "est": 28, "desc": "城市景观、建筑生成"}
    ]},
    "AI工具/人工智能/动漫风格": {"count": 58, "dimension": "风格细分", "subs": [
        {"name": "日漫风格", "est": 28, "desc": "日本动漫风格"},
        {"name": "美漫/其他", "est": 30, "desc": "美式卡通等其他风格"}
    ]},
    "AI工具/人工智能/综合平台": {"count": 30, "dimension": "平台定位", "subs": [
        {"name": "多模态AI平台", "est": 20, "desc": "集成多种AI能力的综合平台"},
        {"name": "垂直AI平台", "est": 10, "desc": "特定行业AI解决方案平台"}
    ]},
    "AI工具/人工智能/音频生成": {"count": 27, "dimension": "生成类型", "subs": [
        {"name": "语音合成", "est": 15, "desc": "TTS语音合成"},
        {"name": "音乐生成", "est": 12, "desc": "AI音乐、作曲工具"}
    ]},
    "AI工具/人工智能/AI视频分析": {"count": 1, "dimension": "NA", "subs": [
        {"name": "AI视频分析", "est": 1, "desc": "视频内容分析工具"}
    ]}
}

# 效率办公类拆分
efficiency_categories_detail = {
    "效率办公/协作工具": {"count": 69, "dimension": "协作类型", "subs": [
        {"name": "项目管理", "est": 28, "desc": "Trello、Asana等项目管理"},
        {"name": "团队协作", "est": 25, "desc": "Slack、Teams等团队沟通"},
        {"name": "知识库协作", "est": 16, "desc": "Notion、Confluence等知识库"}
    ]},
    "效率办公/博客管理": {"count": 65, "dimension": "博客类型", "subs": [
        {"name": "博客平台", "est": 35, "desc": "WordPress、Medium等博客平台"},
        {"name": "博客工具", "est": 30, "desc": "博客编辑、管理工具"}
    ]},
    "效率办公/剧本创作": {"count": 59, "dimension": "创作类型", "subs": [
        {"name": "影视剧本", "est": 30, "desc": "电影、电视剧剧本工具"},
        {"name": "游戏剧本", "est": 29, "desc": "游戏剧情、对话创作工具"}
    ]},
    "效率办公/社交媒体": {"count": 59, "dimension": "平台功能", "subs": [
        {"name": "社交媒体管理", "est": 35, "desc": "多平台管理、发布工具"},
        {"name": "社交分析", "est": 24, "desc": "社交媒体数据分析"}
    ]},
    "效率办公/总结摘要": {"count": 59, "dimension": "内容类型", "subs": [
        {"name": "文档摘要", "est": 35, "desc": "文档自动总结"},
        {"name": "会议摘要", "est": 24, "desc": "会议记录、纪要生成"}
    ]},
    "效率办公/内容写作": {"count": 58, "dimension": "写作场景", "subs": [
        {"name": "博客写作", "est": 30, "desc": "博客文章写作助手"},
        {"name": "技术文档", "est": 28, "desc": "技术文档写作工具"}
    ]},
    "效率办公/文案优化": {"count": 58, "dimension": "优化方向", "subs": [
        {"name": "文案润色", "est": 30, "desc": "文案润色、优化"},
        {"name": "SEO优化", "est": 28, "desc": "SEO文案优化工具"}
    ]},
    "效率办公/AI写作": {"count": 58, "dimension": "写作类型", "subs": [
        {"name": "AI写作助手", "est": 35, "desc": "通用AI写作工具"},
        {"name": "专业写作", "est": 23, "desc": "特定领域AI写作"}
    ]},
    "效率办公/诗歌创作": {"count": 58, "dimension": "创作类型", "subs": [
        {"name": "诗歌生成", "est": 35, "desc": "自动诗歌创作"},
        {"name": "文学创作", "est": 23, "desc": "文学类内容创作"}
    ]},
    "效率办公/营销文案": {"count": 58, "dimension": "营销场景", "subs": [
        {"name": "广告文案", "est": 30, "desc": "广告文案生成"},
        {"name": "营销内容", "est": 28, "desc": "营销邮件、推送文案"}
    ]},
    "效率办公/技术写作": {"count": 58, "dimension": "文档类型", "subs": [
        {"name": "API文档", "est": 30, "desc": "API文档自动生成"},
        {"name": "技术手册", "est": 28, "desc": "技术手册、指南编写"}
    ]},
    "效率办公/邮件写作": {"count": 57, "dimension": "邮件类型", "subs": [
        {"name": "邮件草稿", "est": 30, "desc": "邮件内容生成"},
        {"name": "邮件回复", "est": 27, "desc": "智能邮件回复建议"}
    ]},
    "效率办公/创意激发": {"count": 57, "dimension": "创意类型", "subs": [
        {"name": "创意生成", "est": 30, "desc": "头脑风暴、创意生成"},
        {"name": "Ideas生成", "est": 27, "desc": "各类Idea生成工具"}
    ]},
    "效率办公/标题生成": {"count": 57, "dimension": "内容类型", "subs": [
        {"name": "文章标题", "est": 35, "desc": "文章标题优化生成"},
        {"name": "广告标题", "est": 22, "desc": "广告标题、标语生成"}
    ]},
    "效率办公/改写重述": {"count": 57, "dimension": "改写目的", "subs": [
        {"name": "内容重写", "est": 35, "desc": "文章重写、改写"},
        {"name": "风格转换", "est": 22, "desc": "文风转换、风格化改写"}
    ]},
    "效率办公/故事生成": {"count": 57, "dimension": "故事类型", "subs": [
        {"name": "短篇故事", "est": 30, "desc": "短篇小说、故事生成"},
        {"name": "长篇小说", "est": 27, "desc": "长篇小说辅助创作"}
    ]}
}

# 多媒体/设计/系统工具类拆分（这些相对独立，可以适当简化）
multimedia_detail = {
    "多媒体/视频娱乐/音乐教程": {"count": 13, "dimension": "音乐类型", "subs": [
        {"name": "乐器教程", "est": 8, "desc": "乐器学习教程"},
        {"name": "音乐理论", "est": 5, "desc": "音乐理论、作曲教程"}
    ]},
    "多媒体/视频娱乐/国内视频": {"count": 21, "dimension": "视频类型", "subs": [
        {"name": "长视频平台", "est": 12, "desc": "B站、优酷等长视频平台"},
        {"name": "短视频平台", "est": 9, "desc": "抖音、快手等短视频"}
    ]},
    "多媒体/视频娱乐/国外视频": {"count": 24, "dimension": "视频类型", "subs": [
        {"name": "视频分享", "est": 14, "desc": "YouTube等视频分享"},
        {"name": "视频课程", "est": 10, "desc": "在线教育视频平台"}
    ]},
    "设计工具/UI设计工具": {"count": 125, "dimension": "设计功能", "subs": [  # 已在上面详细处理
        {"name": "原型设计", "est": 30, "desc": "Figma、Sketch等原型工具"},
        {"name": "UI设计工具", "est": 32, "desc": "高保真界面设计工具"},
        {"name": "设计协作", "est": 25, "desc": "设计协作与交付平台"},
        {"name": "设计系统", "est": 20, "desc": "设计系统管理工具"},
        {"name": "交互设计", "est": 18, "desc": "交互动效设计工具"}
    ]},
    "设计工具/资源/矢量图标": {"count": 21, "dimension": "资源类型", "subs": [
        {"name": "图标库", "est": 12, "desc": "图标资源库"},
        {"name": "图标工具", "est": 9, "desc": "图标编辑、生成工具"}
    ]},
    "系统工具/实用工具/其他工具": {"count": 35, "dimension": "工具类型", "subs": [
        {"name": "系统优化", "est": 18, "desc": "系统清理、优化工具"},
        {"name": "实用小工具", "est": 17, "desc": "各类实用小工具集合"}
    ]},
    "系统工具/实用工具/网络工具": {"count": 8, "dimension": "NA", "subs": [  # <50，不处理
        {"name": "网络工具", "est": 8, "desc": "网络诊断、测速等工具"}
    ]},
    "设计工具/资源/图库照片": {"count": 20, "dimension": "资源类型", "subs": [
        {"name": "免费图库", "est": 12, "desc": "免费图片资源站"},
        {"name": "付费图库", "est": 8, "desc": "付费高质量图库"}
    ]},
    "设计工具/资源/UI套件": {"count": 20, "dimension": "资源类型", "subs": [
        {"name": "UI Kit", "est": 12, "desc": "UI组件套件"},
        {"name": "界面模板", "est": 8, "desc": "界面设计模板"}
    ]},
    "设计工具/资源/字体资源": {"count": 20, "dimension": "资源类型", "subs": [
        {"name": "字体下载", "est": 12, "desc": "字体文件下载站"},
        {"name": "在线字体", "est": 8, "desc": "在线字体服务"}
    ]},
    "设计工具/资源/PPT模板": {"count": 20, "dimension": "模板类型", "subs": [
        {"name": "PPT模板", "est": 12, "desc": "PowerPoint模板资源"},
        {"name": "演示文稿", "est": 8, "desc": "Keynote等演示文稿模板"}
    ]},
    "设计工具/资源/设计素材": {"count": 20, "dimension": "素材类型", "subs": [
        {"name": "设计素材", "est": 12, "desc": "通用设计素材"},
        {"name": "样机素材", "est": 8, "desc": "样机、Mockup素材"}
    ]},
    "设计工具/资源/配色方案": {"count": 19, "dimension": "配色类型", "subs": [
        {"name": "配色方案", "est": 12, "desc": "配色方案、调色板"},
        {"name": "色彩工具", "est": 7, "desc": "色彩生成、提取工具"}
    ]},
    "设计工具/资源/设计灵感": {"count": 19, "dimension": "灵感类型", "subs": [
        {"name": "作品集", "est": 12, "desc": "设计师作品展示"},
        {"name": "灵感平台", "est": 7, "desc": "设计灵感收集平台"}
    ]},
    "设计工具/资源/3D模型": {"count": 19, "dimension": "模型类型", "subs": [
        {"name": "3D模型库", "est": 12, "desc": "3D模型资源下载"},
        {"name": "AR/VR资源", "est": 7, "desc": "AR/VR专用3D资源"}
    ]},
    "设计工具/资源/样机模板": {"count": 19, "dimension": "模板类型", "subs": [
        {"name": "样机模板", "est": 12, "desc": "设备样机模板"},
        {"name": "展示模板", "est": 7, "desc": "作品展示模板"}
    ]},
    "设计工具/资源/图标资源": {"count": 19, "dimension": "资源类型", "subs": [
        {"name": "图标资源", "est": 12, "desc": "各类图标资源"},
        {"name": "插画资源", "est": 7, "desc": "插画素材资源"}
    ]},
    "设计工具/资源/插画资源": {"count": 19, "dimension": "插画类型", "subs": [
        {"name": "插画库", "est": 12, "desc": "插画素材库"},
        {"name": "插画生成", "est": 7, "desc": "AI插画生成工具"}
    ]},
    "设计工具/资源/纹理贴图": {"count": 19, "dimension": "纹理类型", "subs": [
        {"name": "纹理贴图", "est": 12, "desc": "材质纹理资源"},
        {"name": "背景图案", "est": 7, "desc": "背景纹理、图案"}
    ]},
    "设计工具/资源/背景图案": {"count": 19, "dimension": "图案类型", "subs": [
        {"name": "背景素材", "est": 12, "desc": "背景图案资源"},
        {"name": "纹理资源", "est": 7, "desc": "纹理、图案素材"}
    ]},
    "设计工具/资源/设计资源包": {"count": 19, "dimension": "资源包类型", "subs": [
        {"name": "资源包", "est": 12, "desc": "综合设计资源包"},
        {"name": "素材合集", "est": 7, "desc": "素材合集、套装"}
    ]},
}

# 学术科研类拆分
academic_detail = {
    "学术科研/论文检索": {"count": 18, "dimension": "检索类型", "subs": [
        {"name": "学术搜索引擎", "est": 10, "desc": "Google Scholar等学术搜索"},
        {"name": "期刊检索", "est": 8, "desc": "期刊论文检索平台"}
    ]},
    "学术科研/学术搜索": {"count": 18, "dimension": "搜索领域", "subs": [
        {"name": "综合学术搜索", "est": 10, "desc": "跨学科学术搜索"},
        {"name": "专业领域搜索", "est": 8, "desc": "特定领域学术搜索"}
    ]},
    "学术科研/数据集平台": {"count": 18, "dimension": "数据领域", "subs": [
        {"name": "通用数据集", "est": 10, "desc": "多领域数据集平台"},
        {"name": "专域数据集", "est": 8, "desc": "特定领域数据集"}
    ]},
    "学术科研/学术期刊": {"count": 18, "dimension": "学科领域", "subs": [
        {"name": "综合期刊", "est": 10, "desc": "跨学科期刊平台"},
        {"name": "专业期刊", "est": 8, "desc": "单学科顶级期刊"}
    ]},
    "学术科研/学术会议": {"count": 18, "dimension": "会议类型", "subs": [
        {"name": "会议平台", "est": 10, "desc": "学术会议信息平台"},
        {"name": "会议服务", "est": 8, "desc": "会议投稿、评审服务"}
    ]},
    "学术科研/研究工具": {"count": 18, "dimension": "工具类型", "subs": [
        {"name": "研究管理", "est": 10, "desc": "研究项目管理工具"},
        {"name": "实验工具", "est": 8, "desc": "实验设计、数据收集工具"}
    ]},
    "学术科研/学术社交": {"count": 18, "dimension": "社交类型", "subs": [
        {"name": "学术网络", "est": 10, "desc": "ResearchGate等学术社交网络"},
        {"name": "合作平台", "est": 8, "desc": "学术合作、交流平台"}
    ]},
    "学术科研/引文管理": {"count": 18, "dimension": "工具类型", "subs": [
        {"name": "引文管理", "est": 10, "desc": "EndNote、Zotero等管理工具"},
        {"name": "引用检测", "est": 8, "desc": "查重、引用检测工具"}
    ]},
    "学术科研/学术写作": {"count": 17, "dimension": "写作类型", "subs": [
        {"name": "论文写作", "est": 10, "desc": "学术论文写作助手"},
        {"name": "投稿辅助", "est": 7, "desc": "期刊投稿辅助工具"}
    ]},
    "学术科研/实验室管理": {"count": 17, "dimension": "管理功能", "subs": [
        {"name": "实验管理", "est": 10, "desc": "实验数据、流程管理"},
        {"name": "设备管理", "est": 7, "desc": "实验室设备管理"}
    ]},
    "学术科研/课程资料": {"count": 17, "dimension": "学科类型", "subs": [
        {"name": "课程资料库", "est": 10, "desc": "大学课程资料库"},
        {"name": "课件资源", "est": 7, "desc": "课件、讲义分享"}
    ]},
    "学术科研/开放课程": {"count": 17, "dimension": "课程类型", "subs": [
        {"name": "MOOC平台", "est": 10, "desc": "大规模开放课程"},
        {"name": "公开课", "est": 7, "desc": "高校公开课资源"}
    ]},
    "学术科研/学术地图": {"count": 17, "dimension": "地图类型", "subs": [
        {"name": "知识图谱", "est": 10, "desc": "学术知识图谱"},
        {"name": "研究地图", "est": 7, "desc": "研究领域地图工具"}
    ]},
    "学术科研/研究助理": {"count": 17, "dimension": "助理类型", "subs": [
        {"name": "AI研究助理", "est": 10, "desc": "AI驱动的学术研究助手"},
        {"name": "文献管理", "est": 7, "desc": "文献管理、阅读工具"}
    ]},
    "学术科研/学术委员会": {"count": 17, "dimension": "NA", "subs": [
        {"name": "学术委员会", "est": 17, "desc": "学术委员会相关服务"}
    ]},
}

# 其它需要拆分的超容类（<100的）
remaining_over_capacity = [
    ("效率办公/协作工具", 69),
    ("效率办公/博客管理", 65),
    ("AI工具/人工智能/产品图生成", 65),
    ("效率办公/剧本创作", 59),
    ("效率办公/总结摘要", 59),
    ("效率办公/社交媒体", 59),
    ("AI工具/人工智能/3D生成", 59),
    ("AI工具/人工智能/人脸编辑", 59),
    ("AI工具/人工智能/图像修复", 59),
    ("AI工具/人工智能/图像扩展", 59),
    ("AI工具/人工智能/图生图", 59),
    ("AI工具/人工智能/文生图", 59),
    ("AI工具/人工智能/背景移除", 59),
    ("AI工具/人工智能/超分辨率", 59),
    ("AI工具/人工智能/风格迁移", 59),
    ("效率办公/内容写作", 58),
    ("效率办公/文案优化", 58),
    ("效率办公/AI写作", 58),
    ("效率办公/诗歌创作", 58),
    ("效率办公/营销文案", 58),
    ("AI工具/人工智能/动漫风格", 58),
    ("AI工具/人工智能/图像增强", 58),
    ("AI工具/人工智能/场景生成", 58),
    ("AI工具/人工智能/色彩调整", 58),
    ("AI工具/人工智能/草图转图", 58),
    ("效率办公/技术写作", 58),
]

# 现在构建完整的拆分计划
for plan in [github_plan, data_analysis_plan, video_tutorial_plan, code_assistant_plan,
             video_gen_plan, image_recognition_plan, ui_design_plan, file_tools_plan]:
    split_plan["split_categories"].append(plan)

# 添加AI类详细拆分
for cat_name, details in ai_categories_detail.items():
    plan = {
        "original_name": cat_name,
        "current_count": details["count"],
        "split_dimension": details["dimension"],
        "complexity": "low" if details["count"] < 30 else "medium",
        "rationale": f"按{details['dimension']}进行细分",
        "sub_categories": details["subs"],
        "total_sub_count": details["count"]
    }
    split_plan["split_categories"].append(plan)

# 添加效率办公类详细拆分
for cat_name, details in efficiency_categories_detail.items():
    plan = {
        "original_name": cat_name,
        "current_count": details["count"],
        "split_dimension": details["dimension"],
        "complexity": "low" if details["count"] <= 30 else "medium",
        "rationale": f"按{details['dimension']}进行细分",
        "sub_categories": details["subs"],
        "total_sub_count": details["count"]
    }
    split_plan["split_categories"].append(plan)

# 添加多媒体/设计类详细拆分
for cat_name, details in multimedia_detail.items():
    plan = {
        "original_name": cat_name,
        "current_count": details["count"],
        "split_dimension": details["dimension"],
        "complexity": "low" if details["count"] < 30 else "medium",
        "rationale": f"按{details['dimension']}进行细分",
        "sub_categories": details["subs"],
        "total_sub_count": details["count"]
    }
    split_plan["split_categories"].append(plan)

# 添加学术科研类详细拆分
for cat_name, details in academic_detail.items():
    plan = {
        "original_name": cat_name,
        "current_count": details["count"],
        "split_dimension": details["dimension"],
        "complexity": "low" if details["count"] < 30 else "medium",
        "rationale": f"按{details['dimension']}进行细分",
        "sub_categories": details["subs"],
        "total_sub_count": details["count"]
    }
    split_plan["split_categories"].append(plan)

# 添加剩余未处理的小型超容类（直接拆分为2-3个子类）
remaining_small = [c for c in remaining_over_capacity if c[0] not in
                   {p['original_name'] for p in split_plan['split_categories']}]

for cat_name, count in remaining_small:
    # 自动生成2-3个子类
    if count > 80:
        sub_count = 3
    elif count > 60:
        sub_count = 3
    else:
        sub_count = 2

    avg = count // sub_count
    subs = []
    for i in range(sub_count):
        remaining = count - sum(s['estimated_count'] for s in subs)
        if i == sub_count - 1:
            est = remaining
        else:
            est = avg + (count % sub_count if i == 0 else 0)
        subs.append({
            "name": f"{cat_name.split('/')[-1]}子类{i+1}",
            "estimated_count": est,
            "description": f"{cat_name}的细分类别{i+1}"
        })

    plan = {
        "original_name": cat_name,
        "current_count": count,
        "split_dimension": "通用细分",
        "complexity": "low",
        "rationale": f"将{count}个站点拆分为{sub_count}个均衡子类",
        "sub_categories": subs,
        "total_sub_count": count
    }
    split_plan["split_categories"].append(plan)

# 保存JSON
output_path = '/home/yoli/GitHub/web_nav_v2/plans/over_capacity_split_plan.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(split_plan, f, ensure_ascii=False, indent=2)

print(f"拆分计划已生成: {output_path}")
print(f"总计处理超容分类: {len(split_plan['split_categories'])} 个")
print()

# 打印摘要
print("="*80)
print("超容分类拆分计划摘要")
print("="*80)

for i, cat_plan in enumerate(split_plan['split_categories'], 1):
    original = cat_plan['original_name']
    current = cat_plan['current_count']
    subs = cat_plan['sub_categories']
    complexity = cat_plan['complexity']
    avg = current // len(subs) if subs else 0
    print(f"{i:2d}. {original} [{complexity}]")
    print(f"    当前: {current} → 拆分为 {len(subs)} 个子类 (目标: 10-50/类)")
    for sub in subs[:3]:  # 只显示前3个子类
        print(f"      - {sub['name']}: ~{sub['estimated_count']} sites")
    if len(subs) > 3:
        print(f"      ... 还有 {len(subs)-3} 个子类")
    print()
