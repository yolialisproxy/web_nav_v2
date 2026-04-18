# 啃魂导航网站 V2 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现完整可用的啃魂导航网站，包含分类导航、搜索、响应式布局

**Architecture:** 单页 HTML + 原生 JS + 纯 CSS，0 外部依赖，直接打开即可运行

**Tech Stack:** HTML5, CSS3, Vanilla JavaScript, JSON

---

## 任务分解

### 任务 1: 基础页面骨架与数据加载

**Files:**
- Create: `/home/yoli/GitHub/web_nav_v2/index.html`

- [ ] **Step 1: 编写基础 HTML 骨架**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>啃魂导航</title>
    <style>
        /* 基础全局样式 */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #121212; color: #e0e0e0; font-family: system-ui, -apple-system, sans-serif; }
    </style>
</head>
<body>
    <div id="app"></div>
    <script>
        // 全局应用状态
        const App = {
            data: null,
            currentCategory: null,
            searchQuery: '',

            async init() {
                // 加载数据
                const res = await fetch('./data/websites.json');
                App.data = await res.json();
                App.render();
            }
        };

        // 启动应用
        document.addEventListener('DOMContentLoaded', () => App.init());
    </script>
</body>
</html>
```

- [ ] **Step 2: 验证页面加载**

打开 `index.html`，控制台无报错，数据成功加载


### 任务 2: 顶部搜索栏与导航

- [ ] **Step 1: 实现搜索栏组件**

添加到 style:
```css
.top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 56px;
    background: #1e1e1e;
    border-bottom: 1px solid #333;
    display: flex;
    align-items: center;
    padding: 0 20px;
    z-index: 100;
}

.search-input {
    flex: 1;
    max-width: 600px;
    height: 40px;
    background: #2d2d2d;
    border: 1px solid #444;
    border-radius: 8px;
    padding: 0 16px;
    color: white;
    font-size: 16px;
}
```

- [ ] **Step 2: 实现实时搜索过滤**

添加搜索逻辑，输入时实时过滤网站列表


### 任务 3: 分类网格视图

- [ ] **Step 1: 9 大分类 3x3 网格布局**

```css
.category-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    padding: 20px;
    max-width: 1200px;
    margin: 80px auto 0;
}

.category-card {
    background: #1e1e1e;
    border: 1px solid #333;
    border-radius: 12px;
    padding: 24px;
    cursor: pointer;
    transition: all 0.2s;
}

.category-card:hover {
    border-color: #ffd700;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(255,215,0,0.1);
}
```

- [ ] **Step 2: 分类点击切换逻辑**

点击分类卡片进入该分类网站列表视图


### 任务 4: 侧边栏导航

- [ ] **Step 1: 可折叠侧边栏实现**

左侧分类树导航，支持折叠展开子分类

- [ ] **Step 2: 响应式适配移动端**

移动端侧边栏自动隐藏，滑出动画


### 任务 5: 网站卡片列表

- [ ] **Step 1: 网站卡片组件**

卡片式布局，包含网站图标、标题、描述

- [ ] **Step 2: 无限滚动加载**

分页加载优化性能


### 任务 6: 动画与细节优化

- [ ] **Step 1: 过渡动画与悬停效果**
- [ ] **Step 2: 加载状态与骨架屏**
- [ ] **Step 3: 深色主题细节优化**


### 任务 7: 完整验收测试

- [ ] **Step 1: 所有分类正确显示**
- [ ] **Step 2: 搜索功能正常**
- [ ] **Step 3: 移动端完美适配**
- [ ] **Step 4: 控制台无报错**
- [ ] **Step 5: 加载时间 < 1 秒**
