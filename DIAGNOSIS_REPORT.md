# 啃魂导航 V2 — 全面诊断报告

> 生成时间: 2026-05-12
> 评估框架: Superpowers Brainstorming + Systematic Debugging

---

## 🔴 致命问题 (P0) — 同类别排名倒数的主因

### 1. 架构分裂：4套重复HTML壳
- `index.html` / `category.html` / `search-results.html` / `site-detail.html` 各自引入完全相同的CSS/JS文件
- `category.html` 缺少收藏弹窗(`#favorite-modal`)、标签云区域、搜索覆盖层
- `search-results.html` 缺少侧边栏、标签筛选、收藏功能
- 每一个"页面"都是独立的多页应用(MPA)，不是SPA

### 2. CSS严重冲突 — 6处重复定义
- `tailwind-local.css` 与 `components.css` 中重复定义了: `.menu-category`, `.category-header`, `.menu-subcategory`, `.subcategory-header`, `.subcategory-arrow`, `.menu-leaf`, `.card-grid` 等
- `.subcategory-content` 在 `responsive.css` 中有 `!important` 强制覆盖，在 `tailwind-local.css` 又有另一套规则
- `search-overlay` 相关样式在多个文件中重复出现

### 3. 搜索功能割裂
- 首页：搜索覆盖层(overlay)弹出式搜索，带Trie索引
- search-results.html：独立页面，简单的`Array.filter`线性搜索，无索引
- 两套完全不同的UI风格和交互模式
- 搜索结果页卡片用`bg-white dark:bg-gray-800`，首页用`var(--color-bg-card)`，风格不一致

## 🟠 严重问题 (P1)

### 4. 收藏功能多处断裂
- `site-detail.html` 中收藏按钮只是 `alert('收藏功能开发中...')`
- `favorite-ui-bootstrap.js` 中的 `exportFavorites()` 调用了不存在的 `favoriteManager.export()` (应为 `getAll()`)
- `init-favorites.js` 中的 `exportData()` 方法才是正确的，但 bootstrap 版本未同步
- 卡片上没有收藏按钮(只有顶栏有一个♡按钮)

### 5. 标签系统功能缺失
- `TagManager.load()` 请求 `data/tag_index.json`，但该文件不存在
- 标签筛选功能不可用，`filterByActiveTags` 永远返回原列表(因为初始化失败)
- 侧边栏标签云区域会静默失败

### 6. Favicon 404
- HTML引用 `<link rel="icon" href="favicon.ico">` 但实际文件是 `favicon.png`
- 服务器serve.py做了fallback，但直接访问favicon.ico会404

## 🟡 一般问题 (P2)

### 7. 无障碍(Accessibility)缺失
- 搜索覆盖层打开后焦点未自动聚焦到输入框
- 侧边栏切换按钮缺少 `aria-label`
- 键盘导航不完整(Tab键无法正确导航侧边栏层级)
- 缺少 `role="navigation"`, `role="main"` 等语义化标签
- 搜索覆盖层关闭后焦点未返回

### 8. 移动端体验差
- 移动端侧边栏打开时有闪烁
- 搜索框在小屏设备上被遮挡
- 没有底部导航栏

### 9. SEO完全缺失
- 没有 `meta description`
- 没有Open Graph标签
- 没有sitemap引用(虽然有sitemap.xml文件)
- canonical标签缺失

### 10. JavaScript潜在错误
- `data.js` line 58 的 `if (parts.length >= 3)` 条件在部分数据格式下可能出错
- 全局错误监听中有重复的favicon修复逻辑(app.js中已有，index.html的onerror又有)
- `state.js` 中 `set` 方法对路径的边界检查可能导致静默失败

---

## 📊 同类竞品对比差距

| 维度 | 竞品标准 | 当前状态 | 差距 |
|------|---------|---------|------|
| 加载性能 | <1s首屏 | 无骨架屏，数据全靠fetch | ❌ |
| 搜索体验 | 实时搜索+高亮+建议 | 首页有但不完整，搜索页无 | ❌ |
| 视觉一致性 | 统一设计系统 | CSS冲突，4套页面风格 | ❌ |
| 交互体验 | 流畅过渡+反馈 | 缺少加载态、空状态 | ❌ |
| 移动端 | 完整适配 | 侧边栏问题，无底部导航 | ❌ |
| 无障碍 | WCAG 2.1 AA | 几乎为零 | ❌ |
| SEO | 基础优化 | 完全缺失 | ❌ |
| 功能完整 | 收藏/标签/搜索 | 收藏断裂，标签不可用 | ❌ |

---

## 🎯 修复优先级路线图

1. **P0**: 统一为SPA架构 + CSS去重
2. **P0**: 统一搜索体验(全局Trie索引)
3. **P1**: 修复收藏功能
4. **P1**: 修复favicon和标签系统
5. **P2**: 无障碍增强
6. **P2**: SEO优化
7. **P2**: 骨架屏和加载态