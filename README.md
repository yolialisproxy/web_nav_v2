# 🗺️ 啃魂导航 (Kunhunav)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

一个面向开发者的智能导航站，聚合 AI、编程、设计、工具等 3100+ 优质资源，支持智能搜索、标签筛选、收藏功能，配备小游戏娱乐模块。

## 🚀 功能总览

| 功能 | 说明 |
|---|---|
| **智能搜索** | Trie 前缀索引，毫秒级模糊匹配，支持名称/URL/描述/标签多维检索 |
| **标签系统** | 动态从站点数据构建标签索引，点击标签即时筛选，标签云可视化 |
| **分类导航** | 三级分类体系（分类→子分类→叶子），侧边栏折叠/展开 |
| **收藏功能** | 本地 Storage 持久化，支持收藏夹管理 |
| **视图切换** | 🎨 网格视图 / 📋 列表视图 / 📂 分类视图，偏好自动缓存 |
| **本地缓存** | LocalForage 增强离线体验，站点数据 24h/标签 1h/UI 状态 7d |
| **游戏版块** | 9 款内置小游戏，Canvas 2D 引擎，存档/音效/难度系统 |
| **SEO 优化** | 结构化数据(JSON-LD)、Sitemap(3107 URLs)、robots、Open Graph |
| **无障碍** | ARIA 标签、键盘导航、语义化 HTML、骨架屏 |

## 🎮 游戏中心（9款）

| 游戏 | 类型 | 快捷键/操作 |
|---|---|---|
| 🃏 纸牌接龙 | 经典 | 鼠标点击 |
| 🟩 俄罗斯方块 | 经典 | ←→ 移动，↑ 旋转，↓ 加速，Space 硬降 |
| ⚫ 围棋 | 策略 | 鼠标点击落子 |
| ♟️ 象棋 | 策略 | 鼠标拖拽棋子 |
| 🀄 麻将 | 经典 | 鼠标点击选牌/打牌 |
| ⚔️ 武侠世界 | RPG | W/A/S/D 移动，空格攻击 |
| 💕 恋爱大富翁 | 养成+大富翁 | 掷骰子+卡牌决策 |
| 🔢 2048 | 益智 | ←↑→↓ 滑动 |
| ⚫ 五子棋 | 策略 | 鼠标点击落子 |

## 📁 项目结构

```
web_nav_v2/
├── index.html                    # 入口 HTML（SPA 架构）
├── sitemap.xml                   # 自动生成的 Sitemap
├── robots.txt                    # 爬虫规则
├── manifest.json                 # PWA 配置
├── assets/
│   ├── css/
│   │   ├── core.css              # 核心变量 + 骨架屏
│   │   └── app.css               # 全局样式 + 游戏样式
│   └── js/
│       ├── state.js              # 全局状态机 + 标签系统 + 缓存层
│       ├── data.js               # 数据管理（fetch + 索引构建）
│       ├── search.js             # 搜索引擎（Trie）
│       ├── render.js             # 渲染引擎（视图路由、网格、列表、分类、游戏）
│       ├── app.js                # 事件绑定 + Hash 路由 + 应用生命周期
│       ├── schema.js             # 数据架构定义
│       ├── toast.js              # 弹窗通知
│       ├── core-vitals.js        # 核心性能指标
│       ├── favorite.js           # 收藏功能核心逻辑
│       ├── favourite-ui-bootstrap.js  # 收藏 UI 初始化
│       ├── game-utils.js         # 游戏公共工具（存档、音效）
│       ├── game-hub.js           # 游戏大厅管理 + 全屏容器
│       ├── performance-monitor.js    # 性能监控
│       ├── tags.js               # ⚠️ DEPRECATED（已合并到 state.js）
│       └── monetization.js       # 广告位管理
│       └── games/                # 游戏模块
│           ├── game-engine.js    # 通用游戏引擎基类
│           ├── solitaire.js      # 🃏 纸牌
│           ├── tetris.js         # 🟩 俄罗斯方块
│           ├── go.js             # ⚫ 围棋
│           ├── chess.js          # ♟️ 象棋
│           ├── mahjong.js        # 🀄 麻将
│           ├── wuxia.js          # ⚔️ 武侠世界
│           ├── dating.js         # 💕 恋爱大富翁
│           ├── 2048.js           # 🔢 2048
│           └── gomoku.js         # ⚫ 五子棋
└── data/
    └── tag_index.json            # 标签索引（静态）
```

## ⌨️ 快捷键

| 快捷键 | 功能 |
|---|---|
| `/` | 聚焦搜索框 |
| `Ctrl+K` | 聚焦搜索（Mac: `Cmd+K`） |
| `Ctrl+/` | 切换侧边栏（Mac: `Cmd+/`） |
| `Esc` | 关闭搜索/游戏/弹窗 |

## 📐 架构说明

### SPA 路由
基于 URL Hash 实现单页路由：
- `/#games` — 游戏大厅
- `/#game=solitaire` — 直接启动纸牌
- `/#category=...&sub=...` — 分类导航

### 状态管理
`state.js` 是唯一真理源，采用发布-订阅模式：
- `state.set('key', value)` — 设置状态并自动触发渲染 + 缓存
- `state.get('key')` — 读取状态
- `state.subscribe(cb)` — 订阅状态变更

### 缓存策略
| 数据类型 | 缓存键 | TTL | 后端 |
|---|---|---|---|
| 站点数据 | `nav_sites_v1` | 24h | LocalForage |
| 标签索引 | `nav_tags_v1` | 1h | LocalForage |
| 侧边栏状态 | `nav_sidebar_v1` | 7d | LocalForage |
| 主题/视图 | `nav_theme_v1` | ∞ | LocalForage |

> LocalForage 不可用时自动降级到 `localStorage`。

## 🚢 部署

### 本地开发
```bash
# 不需要构建，直接打开（部分功能需要 HTTP 服务）
python3 -m http.server 8080
# 或
npx serve .
```

### GitHub Pages
仓库设置 → Pages → Source: `main branch` → `/ (root)`

### 自建服务器
任何静态文件服务器均可（Nginx/Apache/Caddy），无需后端。

## 📝 开发指南

### 添加新游戏
1. 在 `assets/js/games/` 创建游戏文件，实现 `GameEngine` 子类
2. 在 `game-hub.js` 的 `games` 对象中注册
3. 游戏自动出现在大厅，无需其他配置

### 添加新特性
1. 在 `state.js` 的 `_state` 中声明新字段
2. 在 `renderView()` 中添加渲染分支
3. 在 `app.js` 的 `init()` 中绑定事件

### 调试
```javascript
// 查看状态
console.log(state._state);
// 查看缓存
localStorage.getItem('localforage.nav_sites_v1')
// 清除缓存
state.clearCache()
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。重构相关的设计决策记录在 `docs/adr/` 目录下。

## 📜 许可证

MIT License