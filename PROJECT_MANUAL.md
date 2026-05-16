# 📘 啃魂导航 — 项目综合手册

> 本文档由多个核心设计文档合并而成，是啃魂导航项目的唯一权威参考。
> 最后更新：2026-05-15

---

## 1. 项目概述

**啃魂导航 (Kunhunav)** 是一个面向开发者的智能导航站，聚合 AI、编程、设计、工具等 3100+ 优质资源，支持智能搜索、标签筛选、收藏功能，配备小游戏娱乐模块。

### 核心功能
| 功能 | 说明 |
|---|---|
| **智能搜索** | Trie 前缀索引，毫秒级模糊匹配，支持名称/URL/描述/标签多维检索 |
| **标签系统** | 动态从站点数据构建标签索引，点击标签即时筛选，标签云可视化 |
| **分类导航** | 三级分类体系（分类→子分类→叶子），侧边栏折叠/展开 |
| **收藏功能** | 本地 Storage 持久化，支持收藏夹管理 |
| **视图切换** | 网格视图 / 列表视图 / 分类视图，偏好自动缓存 |
| **本地缓存** | LocalForage 增强离线体验，站点数据 24h / 标签 1h / UI 状态 7d |
| **游戏版块** | 9 款内置小游戏，Canvas 2D 引擎，存档/音效/难度系统 |
| **SEO 优化** | 结构化数据(JSON-LD)、Sitemap(3107 URLs)、robots、Open Graph |
| **无障碍** | ARIA 标签、键盘导航、语义化 HTML、骨架屏 |

### 技术栈
- **架构：** SPA（单页应用），Hash 路由
- **UI：** 纯 HTML/CSS/JS，零框架依赖
- **缓存：** LocalForage v1.10.0（IndexedDB/WebSQL/localStorage 自动降级）
- **搜索：** Trie 前缀树索引
- **游戏：** Canvas 2D + 自研 GameEngine 基类
- **PWA：** Service Worker 离线缓存 + Manifest + 安装横幅

---

## 2. 数据架构

### 2.1 数据源

- **`websites.json`** — 主数据源，3107 条站点记录，扁平结构
  - 每条包含：`name`（名称）、`url`（链接）、`icon`（图标）、`tags`（标签数组）
  - 无嵌套分类，所有分类关系通过前端 `category.js` 配置
- **`category.js`** — 分类结构配置，定义分类 → 子分类 → 叶子的三级映射
- **`data/categories.json`** — 分类元数据（图标、描述等）

### 2.2 索引构建

```
websites.json → dataManager.load()
  → sites[] 数组（主数据）
  → tagAll Set（所有标签集合）
  → categoryMap 分类索引
  → Trie 搜索索引（searchEngine.buildTrie()）
```

### 2.3 搜索架构

```
              ┌──────────────┐
 用户输入 ──→ │  Trie 索引   │ ──→ 候选集
              │  search.js   │
              └──────┬───────┘
                     │
              ┌──────▼───────┐
              │  多维过滤    │ ──→ 结果集
              │  名称/URL/   │      (tags, 分类, 收藏)
              │  描述/标签   │
              └──────┬───────┘
                     │
              ┌──────▼───────┐
              │  render.js   │ ──→ DOM 渲染
              │  分页加载    │     (每页40条)
              └──────────────┘
```

---

## 3. 状态管理

### 3.1 State 类（`state.js`）

全局唯一状态机，采用发布-订阅模式：

| 方法 | 说明 |
|---|---|
| `set(key, value)` | 设置状态，自动触发渲染 + 缓存 |
| `get(key)` | 读取状态 |
| `subscribe(cb)` | 订阅状态变更 |
| `load()` / `save()` | 数据加载/持久化入口 |
| `loadTags(dataManager)` | 加载标签索引 |
| `getActiveTags()` / `setActiveTags()` | 标签筛选 |
| `addSite(site)` / `removeSite(url)` | 收藏管理 |
| `setView(view)` | 切换视图模式 |
| `clearCache()` | 清空所有缓存 |

### 3.2 状态字段

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sites` | Array | [] | 站点数据列表 |
| `currentView` | String | 'grid' | 当前视图模式：grid/list/category/games |
| `activeTags` | Set | new Set() | 已选标签 |
| `favorites` | Set | new Set() | 收藏的 URL 集合 |
| `sidebarOpen` | Boolean | false | 侧边栏展开状态 |
| `theme` | String | 'dark' | 主题模式 |
| `tagAll` | Set | new Set() | 全局标签索引 |

### 3.3 缓存策略

||| 数据类型 | 缓存键 | TTL | 底层存储 |
|---|---|---|---|
||| 站点数据 | `nav_sites_v1` | 24h | LocalForage |
||| 标签索引 | `nav_tags_v1` | 1h | LocalForage |
||| 侧边栏状态 | `nav_sidebar_v1` | 7d | LocalForage |
||| 主题/视图 | `nav_theme_v1` | ∞ | LocalForage |
||| 音效偏好 | `gn_sound_enabled` | ∞ | localStorage |
||| 游戏存档 | `gn_game_<key>` | ∞ | localStorage |

> LocalForage 不可用时降级到 localStorage；data.js `_saveCache/_loadCache` 已统一路由到
> state._saveToCache / state.get('sites')，SPA 内站点数据唯一来源为 LocalForage `nav_sites_v1`。

### 3.4 数据质量报告（2026-05-15）

| 指标 | 数值 |
|---|---|
| 总站点数 | 3107 |
| 分类数（清洗后） | 324 |
| URL格式异常 | 0 |
| 空标题 | 0 |
| 重复URL | 0 |
| 清洗详情 | 73个"子类-X"临时编号归并到父分类，838条目修正，1个重复词修复 |

> 历史备份：`websites_backup_pre_clean.json`（清洗前快照）

---

## 4. 渲染引擎

### 4.1 视图路由

```
renderView()
  ├── 'grid'      → renderSiteGrid()     — 网格卡片视图
  ├── 'list'      → renderSitesList()    — 列表行视图
  ├── 'category'  → renderCategory()     — 分类导航视图
  └── 'games'     → renderGamesHub()     — 游戏大厅
        └── #game=<key> → GameHub.startGame(key)
```

### 4.2 渲染优化

- **分页加载**：每页 40 条，IntersectionObserver 无限滚动
- **Trie 索引**：替代全量 O(n) 遍历，搜索性能 O(m)（m = 关键词长度）
- **骨架屏**：加载状态占位，减少视觉闪烁
- **懒加载**：图片 `loading="lazy"`，视口外不渲染

---

## 5. 交互设计

### 5.1 搜索交互

| 操作 | 快捷键 |
|---|---|
| 聚焦搜索框 | `/` 或 `Ctrl+K` |
| 关闭搜索 | `Esc` |
| 切换侧边栏 | `Ctrl+/` |

### 5.2 标签交互

- 点击标签 → 添加到 activeTags → 即时筛选
- Shift + 点击 → 批量添加标签
- activeTags 为空时显示全部站点

### 5.3 收藏交互

- 点击站点卡片收藏按钮 → 切换收藏状态
- 收藏数据持久化到 localStorage
- 收藏视图可通过 filter 切换

### 5.4 视图切换

- Header 区域提供网格/列表/分类三种视图按钮
- 视图偏好自动缓存到 LocalForage

---

## 6. 游戏系统

### 6.1 架构

```
GameEngine (game-engine.js)
  ├── init() / start() / destroy()
  ├── initTouch() — 触摸事件框架
  │    ├── _onTouchStart / _onTouchMove / _onTouchEnd
  │    ├── onSwipe(dir) 回调
  │    └── onTouchTap(x,y) 回调（默认：_defaultOnTouchTap 合成鼠标事件）
  ├── save() / load() / clearSave()
  ├── _calcLevel() — 难度等级自适应
  └── score / level / state 状态管理

GameHub (game-hub.js)
  ├── 游戏注册表（games 字典）
  ├── startGame(key) — 启动游戏
  ├── closeGame() — 关闭游戏
  ├── renderContainer() — 全屏游戏 DOM 容器
  └── 游戏卡片网格渲染
```

### 6.2 游戏清单（9款）

| 游戏 | 文件 | 类型 | 特色 |
|---|---|---|---|
| 🃏 纸牌接龙 | `solitaire.js` | 经典 | 拖拽移动 + 触摸 + 音效 + 存档 |
| 🟩 俄罗斯方块 | `tetris.js` | 经典 | ←→ 移动，↑ 旋转，↓ 加速，Space 硬降 + 触控 + 音效 |
| ⚫ 围棋 | `go.js` | 策略 | 鼠标点击 + 虚着/终局 + 音效 |
| ♟️ 象棋 | `chess.js` | 策略 | 鼠标拖拽/点击 + AI对战 + 将军警告音效 |
| 🀄 麻将 | `mahjong.js` | 经典 | 点击选牌配对 + 音效反馈 + 存档 |
| ⚔️ 武侠世界 | `wuxia.js` | RPG | W/A/S/D + 空格攻击 + 音效戰鬥 + 存檔 |
| 💕 恋爱大富翁 | `dating.js` | 养成 | 掷骰子+卡牌决策 + 投电影票音效 + 存档 |
| 🔢 2048 | `2048.js` | 益智 | ←↑→↓ 滑动 + 触控手势 + 合并音效 + 存档 |
| ⚫ 五子棋 | `gomoku.js` | 策略 | 鼠标点击落子 + 悔棋 + 音效 + 存档 |

### 6.3 音效系统

- **GameUtils** 统一管理 9 组预设音效：move / rotate / flip / score / levelUp / gameOver / click / win / warning
- 游戏内通过 `GameUtils.playSfx(key)` 播放
- 音效开关支持用户自定义，偏好持久化到 localStorage
- 音效开关已集成到游戏 HUD（右下角 🔊/🔇 按钮）

### 6.4 添加新游戏

1. 在 `assets/js/games/` 创建游戏文件
2. 实现 GameEngine 子类，覆写 `init() / start() / tick() / quit()`
3. 在 `game-hub.js` 的 `games` 字典中注册（id/title/icon 即可）
4. 启动游戏自动出现在大厅

---

## 7. PWA 与离线支持

| 组件 | 说明 |
|---|---|
| **Service Worker** (`sw.js`) | Cache First 静态资源 + Network First 数据文件；版本戳 `webnav-v3-20260515` |
| **Manifest** (`manifest.json`) | standalone 模式 + 深色主题 `#0a0a0f` + 紫色主题色 `#7c3aed` + 双图标（32px/192px） |
| **安装横幅** | `beforeinstallprompt` 事件 + 自定义 UI 按钮 |
| **缓存清单** | 完整静态资源预缓存：主页 + 13 CSS + 26 JS（含 9 款游戏）+ manifest.json + favicon.ico/logo.png |
| **离线回退** | 首页 `/` + 所有静态资源服务端缓存；`websites.json` / `data/` 取失败时走缓存降级 |
| **PWA Meta 标签** | `apple-mobile-web-app-capable`, `apple-touch-icon`, `msapplication-TileColor`, `theme-color` |
| **搜索引擎索引** | `sitemap.xml` + `robots.txt`；`prerendered/` 目录存放静态 SEO 页面 |
| **触控手势** | 全站触摸优化（游戏卡片点击事件直接绑定）；无 TAP delay |


---

## 8. SEO 优化

|| **优化项** | **详情** |
||---|---|
|| **Sitemap** | 分级权重：首页 1.0 / 一级分类 0.95 / 二级 0.80-0.88；148条URL，29KB（从450KB压缩） |
|| **robots.txt** | 允许全站，排除 /data/ /backup/ /scripts/ /plans/ /reports/ 等30+非公开路径 |
|| **JSON-LD** | 单份 @graph 结构：WebSite + CollectionPage + SearchAction + EntryPoint |
|| **预渲染** | 155个分类页面，差异化 title/description，data-prerendered 标记 |
|| **标签系统** | 1029标签/padded+path全覆盖/3107站点100%覆盖/展开收起交互 |
|| **Open Graph** | og:title / og:description / og:image / og:url |
|| **Twitter Card** | summary_large_image |
|| **Canonical** | 规范链接设置 |

---

## 9. 项目结构

```
web_nav_v2/
├── index.html                    # SPA 入口
├── sitemap.xml                   # 自动生成 Sitemap
├── robots.txt                    # 爬虫规则
├── manifest.json                 # PWA 配置
├── README.md                     # 项目文档
├── PROJECT_MANUAL.md             # 本文件（综合手册）
├── assets/
│   ├── css/
│   │   ├── core.css              # CSS 变量 + 骨架屏 + 响应式
│   │   └── app.css               # 全局样式 + 游戏样式
│   └── js/
│       ├── state.js              # 全局状态机 + 标签 + 缓存层
│       ├── data.js               # 数据管理 + 索引构建
│       ├── search.js             # Trie 搜索引擎
│       ├── render.js             # 渲染引擎（视图路由）
│       ├── app.js                # 事件绑绑 + Hash 路由 + 生命周期
│       ├── schema.js             # 数据架构定义
│       ├── toast.js              # 弹窗通知
│       ├── core-vitals.js        # 核心性能指标
│       ├── favorite.js           # 收藏功能核心
│       ├── favorite-ui-bootstrap.js  # 收藏 UI 初始化
│       ├── game-utils.js         # 游戏公共工具 + 音效系统
│       ├── game-hub.js           # 游戏大厅管理
│       ├── game-engine.js        # 游戏引擎基类
│       ├── performance-monitor.js    # 性能监控
│       ├── tags.js               # ⚠️ DEPRECATED（兼容层）
│       ├── monetization.js       # 广告位管理
│       └── games/
│           ├── solitaire.js      # 🃏 纸牌
│           ├── tetris.js         # 🟩 俄罗斯方块
│           ├── go.js             # ⚫ 围棋
│           ├── chess.js          # ♟️ 象棋
│           ├── mahjong.js        # 🀄 麻将
│           ├── wuxia.js          # ⚔️ 武侠世界
│           ├── dating.js         # 💕 恋爱大富翁
│           ├── 2048.js           # 🔢 2048
│           └── gomoku.js         # ⚫ 五子棋
├── .scratch/                     # 临时工作区（不提交）
├── pages/                        # 独立页面
│   ├── site-detail.html          # 站点详情页（SPA，通过 ?name= 参数定位）
│   ├── category.html             # 分类页占位
│   └── search-results.html       # 搜索结果页占位
├── prerendered/                  # SEO预渲染快照（155个分类页面，差异化 title/description）
└── docs/
    ├── adr/                      # 设计决策记录
    ├── agents/                   # 代理系统配置
    └── superpowers/              # 超级能力规划
```

---

## 10. 开发规范

### 10.1 代码风格
- 使用 `var` 而非 `let/const`（兼容老旧浏览器）
- 方法定义使用 `原型链` 形式：`GameEngine.prototype.method = function(){}`
- 缩进统一 4 空格
- 行尾不加多余空格，空文件末尾留一个空行

### 10.2 Git 规范
- 提交信息格式：`feat(scope): 描述` / `fix(scope): 描述` / `refactor(scope): 描述`
- 中文描述，附英文标签
- 每阶段独立 commit，便于追踪

### 10.3 调试
```javascript
// 查看状态
console.log(state._state);
// 查看缓存
state.clearCache()
// 调试游戏
GameHub.startGame('tetris')
```

---

## 11. 发布与部署

### 本地开发
```bash
python3 -m http.server 8080
# 或
npx serve .
```

### GitHub Pages
仓库 Settings → Pages → Source: main branch → `/ (root)`

### 任何静态服务器
Nginx / Apache / Caddy 均可，无需后端。

---

## 12. 里程碑

| 阶段 | 主题 | Commit | 时间 |
|---|---|---|---|
| Phase 4 | 数据清洗与重构 | `51e88e0` | 2026-05 |
| Phase 5 | 标签系统统一 | `d14e605` | 2026-05 |
| Phase 6 | LocalForage 缓存 | `6034625` | 2026-05 |
| Phase 7 | 视图切换 | `0f22aee` | 2026-05 |
| Phase 8 | SEO 增强 | `fe4b0ec` | 2026-05 |
| Phase 9 | 游戏版块 MVP | `4999418` | 2026-05 |
| Phase 10 | 项目文档 | `7d8488e` | 2026-05 |
| Phase 11-12 | PWA 增强 | `0b19aa6` | 2026-05 |
| Phase 13 | 安装提示横幅 | `898dcd4` | 2026-05 |
| Phase 14 | 游戏音效与难度 | `9c4a1c9` | 2026-05 |
| Phase 15.1 | GameEngine 触摸基类 | `c311ce7` | 2026-05 |
|| Phase 15.2 | Tetris 触摸适配 | `a2180b0` | 2026-05 |
|| Phase 15.3 | Chess 触摸集成 | `b941a2b` | 2026-05 |
|| Phase 23 | 游戏版块 9 款 | `4999418` | 2026-05 |
|| Phase 24 | SEO 分级 + 标签云 + 预渲染 | `26f4771` | 2026-05-15 |
|| Phase 25 | 列表视图 · 统一缓存 · 结构补全 · 游戏回归 | `363bec3` | 2026-05-16 |

---

*本手册自动生成，后续由 Phase 系统维护更新。*