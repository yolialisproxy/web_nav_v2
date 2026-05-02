# 啃魂导航 V2 - 项目上下文

## 项目概述
啃魂导航（WebNav V2）是一个智能化的网站导航和分类平台，收集、整理和展示高质量的互联网资源，涵盖 AI 工具、开发工具、设计资源、学习社区等 263 个细分领域。

## 核心架构

### 前端架构
- **入口文件**: `index.html`
- **样式系统**:
  - Tailwind CSS (CDN)
  - `assets/css/core.css` - CSS 变量和基础布局
  - `assets/css/components.css` - 组件样式（菜单、卡片、搜索）
  - `assets/css/responsive.css` - 响应式设计
  - `css/style.css` - 自定义样式覆盖
- **JavaScript 模块**:
  - `assets/js/state.js` - 全局状态机（唯一真理源）
  - `assets/js/data.js` - 数据加载与索引管理
  - `assets/js/render.js` - DOM 渲染引擎
  - `assets/js/search.js` - 搜索引擎
  - `assets/js/app.js` - 应用入口和胶水代码

### 后端架构
- **数据层**: `data/websites.json` (1.4MB, 3830+ 条目)
- **服务层**: `serve.py` - Python HTTP 服务器
- **处理脚本**: `scripts/` 目录下的 Python 数据处理工具

### 分类体系
- **层级结构**: 大类 → 中类 → 小类（三级分类）
- **分类数量**: 16 个大类, 28+ 中类, 263 个小类
- **示例**: AI工具/人工智能/综合平台, 开发工具/开发资源/框架

## 开发规范

### Git 工作流
1. 功能开发在独立分支
2. 提交前运行代码检查
3. 合并前完成测试

### 代码风格
- **JavaScript**: 使用 ES6+ 语法，const/let 替代 var
- **CSS**: 使用 CSS 变量，BEM 命名规范
- **HTML**: 语义化标签，中文注释

### 测试要求
- 所有功能变更必须通过 acceptance test
- 响应式设计测试覆盖桌面/平板/手机
- 搜索功能必须支持中文模糊匹配

## 关键接口

### 数据接口
- `GET /data/websites.json` - 获取所有网站数据
- 格式: JSON 数组，每个对象包含 name, url, description, category

### 状态接口
- `state.set(key, value)` - 设置状态
- `state.get(key)` - 获取状态
- `state.subscribe(callback)` - 订阅状态变更

### 渲染接口
- `renderSites(sites)` - 渲染站点列表
- `renderer.renderSidebar(state)` - 渲染侧边栏
- `renderer.renderView(state)` - 渲染主视图

## 已知问题与限制

1. **数据规模**: 1.4MB JSON 文件加载需要 2-3 秒
2. **搜索性能**: 模糊匹配在 3800+ 条目上可能有延迟
3. **CDN 依赖**: Tailwind 和部分图标依赖外部 CDN
4. **离线模式**: 当前版本需要网络连接

## 待办事项

- [ ] 添加本地缓存机制
- [ ] 实现数据增量更新
- [ ] 添加用户收藏功能
- [ ] 实现标签系统
- [ ] 添加网站健康检查
- [ ] 实现 PWA 支持
