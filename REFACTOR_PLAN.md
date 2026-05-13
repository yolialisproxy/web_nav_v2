# 啃魂导航 V2 — 全量重构计划

## 背景
当前项目虽然功能基本可用，但在UI/UX、性能、架构、代码质量各方面都存在严重问题，在同类导航站中排名倒数。本计划基于 Superpowers 框架（Brainstorming → Writing Plans → Executing Plans → Verification）制定。

---

## 全量诊断报告

### 一、UI/UX 问题（共15项）

| # | 严重度 | 问题 | 根因文件 |
|---|--------|------|----------|
| U1 | 🔴 | CSS变量在3个文件中分散定义，存在大量重复和冲突 | core.css + theme-modern.css + components.css |
| U2 | 🔴 | theme-modern.css 滥用 `!important`（150+处），掩盖选择器优先级问题 | theme-modern.css |
| U3 | 🔴 | tailwind.css 是手动编写的类集合，与主题系统重复 | tailwind.css |
| U4 | 🔴 | 顶栏毛玻璃效果在index.html内联样式和theme-modern.css中重复定义 | index.html + theme-modern.css |
| U5 | 🟡 | 无统一设计token系统，颜色/圆角/间距散落在各处 | 全局CSS |
| U6 | 🟡 | 卡片hover 3D倾斜效果在 theme-modern.css 中定义了两次（行383-385和行375-379冲突） | theme-modern.css |
| U7 | 🟡 | 首页index.html的header结构（毛玻璃顶栏）与pages/category.html重复 | index.html + category.html |
| U8 | 🟡 | footer区域完全缺失 | 所有页面 |
| U9 | 🟡 | 无骨架屏/加载过渡效果，体验割裂 | render.js |
| U10 | 🟡 | 图标使用emoji（🌐🤖⚙️🎨），不统一、不专业 | site-detail.html + search-results.html |
| U11 | 🟡 | 响应式布局不完善，缺少平板断点适配 | responsive.css（未读取） |
| U12 | 🟡 | 搜索覆盖层有两套独立的HTML结构（顶栏+弹窗） | index.html |
| U13 | 🟢 | 无页面过渡动画 | 所有页面 |
| U14 | 🟢 | 无暗黑/亮色模式切换UI（只有系统跟随） | state.js |
| U15 | 🟢 | 无访问量/热度可视化 | render.js |

### 二、JS架构问题（共12项）

| # | 严重度 | 问题 | 根因文件 |
|---|--------|------|----------|
| J1 | 🔴 | Trie树insert()复杂度O(n²)，对每个字符位置做后缀插入；9000+站点时索引构建极慢 | search.js:26-43 |
| J2 | 🔴 | `_scanAll()` 在query≤2时DFS遍历整个Trie，等于全量扫描，失去索引意义 | search.js:86-95 |
| J3 | 🔴 | 全局状态污染严重（`window.xxx`到处挂载），命名冲突风险 | app.js + 各模块 |
| J4 | 🔴 | SPA与MPA并存：index.html是SPA，pages/下3个页面是独立MPA，无统一路由 | index.html + pages/* |
| J5 | 🟡 | 跨页面通信断裂：各页面加载不同JS子集，全局状态无法共享 | 各页面script标签 |
| J6 | 🟡 | `favorite-ui-bootstrap.js` 调用 `favoriteManager.export()` 但该方法未定义 | favorite-ui-bootstrap.js:71 |
| J7 | 🟡 | 收藏功能有两套独立UI系统（favorite.js + favorite-ui-bootstrap.js + init-favorites.js） | 3个文件 |
| J8 | 🟡 | state.js `_notify()` 同步通知，订阅者中修改状态会导致竞态条件 | state.js:82-84 |
| J9 | 🟡 | `data.js` 标签索引和 `TagManager` 从不同数据源加载，可能不一致 | data.js + tags.js |
| J10 | 🟡 | `data.js` mappings存储冗余数据（leafId和subLevelId重复映射） | data.js:76-83 |
| J11 | 🟡 | render.js混合纯函数和DOM操作，关注点未分离 | render.js |
| J12 | 🟡 | 无错误恢复机制（localStorage损坏、JSON解析失败等） | 各模块 |

### 三、数据/性能问题（共6项）

| # | 严重度 | 问题 | 根因文件 |
|---|--------|------|----------|
| D1 | 🔴 | websites.json 1.5MB+ 未压缩，首屏加载慢 | data/ |
| D2 | 🔴 | 无虚拟滚动，45536条数据虽分页但DOM仍累积 | render.js |
| D3 | 🟡 | 数据中无id字段，由data.js动态分配，每次加载不一致 | data.js:52 |
| D4 | 🟡 | 标签数据同时存在于sites_with_tags.json、tag_index.json和websites.json中 | data/ |
| D5 | 🟡 | 无Service Worker，离线不可用 | 全局 |
| D6 | 🟡 | 无懒加载/预加载策略 | 全局 |

### 四、缺失的基础设施（共5项）

| # | 严重度 | 问题 |
|---|--------|------|
| I1 | 🔴 | 无构建工具链（Vite/webpack），无代码压缩 |
| I2 | 🔴 | 无单元测试/自动化测试 |
| I3 | 🟡 | 无Lighthouse/性能基线 |
| I4 | 🟡 | 无版本管理策略 |
| I5 | 🟡 | 无文档化API（模块间接口靠注释） |

---

## 重构优先级矩阵

```
影响面大 × 改动小 → 优先做（P0）
影响面大 × 改动大 → 分阶段做（P1）
影响面小 × 改动小 → 顺手做（P2）
影响面小 × 改动大 → 延后做（P3）
```

| 任务 | 影响面 | 改动量 | 优先级 | 阶段 |
|------|--------|--------|--------|------|
| 统一CSS变量/消除!important | 全局 | 中 | P0 | Phase 1 |
| 统一设计token系统 | 全局 | 小 | P0 | Phase 1 |
| 修复Trie搜索算法 | 搜索 | 中 | P0 | Phase 1 |
| SPA化/统一路由 | 全局 | 大 | P1 | Phase 2 |
| 虚拟滚动 | 渲染 | 中 | P1 | Phase 2 |
| 数据文件优化 | 性能 | 小 | P1 | Phase 2 |
| 统一收藏系统 | 功能 | 中 | P1 | Phase 2 |
| 骨架屏/加载状态 | 体验 | 小 | P1 | Phase 2 |
| 卡片设计统一 | UI | 中 | P2 | Phase 3 |
| Service Worker | 离线 | 中 | P2 | Phase 3 |
| 无障碍增强 | 体验 | 小 | P2 | Phase 3 |
| 测试基础设施 | 质量 | 大 | P3 | Phase 3 |

---

## 实施计划（12天）

### Phase 1：基础稳固（第1-2天）
1. **CSS变量统一**：将所有CSS变量收敛到 core.css 的 `:root` 中，建立单一设计token源
2. **删除 tailwind.css**：迁移到原生CSS变量 + 精简工具类
3. **消除 !important**：通过修复选择器特异性来消除所有 `!important`
4. **修复Trie搜索**：重写 search.js 的索引构建和搜索逻辑
5. **统一页面模板**：建立共享的 `<head>`、header、footer 模板

### Phase 2：架构升级（第3-5天）
1. **SPA化改造**：将所有pages/合并到单页应用，使用hash路由
2. **统一路由系统**：基于 state.js 建立声明式路由
3. **虚拟滚动实现**：用 IntersectionObserver 实现高效无限滚动
4. **数据优化**：压缩JSON、按需加载、数据分片
5. **统一收藏系统**：合并两套收藏UI
6. **全局错误恢复**：localStorage降级、JSON解析容错

### Phase 3：体验升华（第6-8天）
1. **统一卡片设计**：消除index.html和pages/的视觉差异
2. **骨架屏效果**：加载时的占位UI
3. **页面过渡动画**：视图切换的平滑过渡
4. **Service Worker**：离线缓存和PWA支持
5. **无障碍增强**：ARIA标签、键盘导航完善
6. **图标系统统一**：替换emoji为SVG图标

### Phase 4：功能增强（第9-11天）
1. **智能推荐**：基于浏览历史的个性化推荐
2. **浏览历史**：记录和展示最近访问
3. **统计面板**：站点数量、分类分布等数据可视化
4. **批量操作**：收藏/打开多个站点
5. **搜索增强**：拼音搜索、模糊匹配优化

### Phase 5：收尾验证（第12天）
1. **全站测试**：功能回归、兼容性测试
2. **性能审计**：Lighthouse评分提升
3. **代码清理**：移除冗余代码和注释
4. **文档更新**：README和API文档
5. **部署准备**：最终构建产物

---

## 架构原则（执行期间严格遵守）

1. **单一数据源**：每个数据项有且只有一个权威来源
2. **关注点分离**：数据获取、状态管理、UI渲染、事件处理分层
3. **渐进增强**：基础功能优先，高级体验渐进添加
4. **KISS原则**：不引入不必要的抽象
5. **无 !important**：通过合理的选择器结构避免
6. **CSS变量驱动**：所有视觉属性通过变量控制