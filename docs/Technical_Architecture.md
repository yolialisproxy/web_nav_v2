# Technical Architecture Specification (Technical_Architecture.md)
Version: 1.0
Project: WebNav V2

---

## 1. 设计原则
✅ **零依赖**：不使用任何外部框架（无 React、无 Vue、无 JQuery）。仅使用原生 JavaScript / CSS / HTML。最终构建产物 < 100KB。
✅ **无构建步骤**：不需要 npm、webpack、vite。直接在浏览器运行，修改即生效。
✅ **GitHub Pages 原生兼容**：所有路径使用相对路径，无需任何配置。
✅ **可审计**：任何人都可以直接阅读源代码，没有编译后的黑盒代码。

---

## 2. 文件结构

### 2.1 最终目录树
```
web_nav_v2/
├── index.html              # 唯一 HTML 入口
├── assets/
│   ├── css/
│   │   ├── core.css        # 核心重置、主题变量、布局
│   │   ├── components.css  # 组件样式
│   │   └── responsive.css  # 响应式断点
│   └── js/
│       ├── state.js        # 全局状态机
│       ├── data.js         # 数据加载与索引
│       ├── render.js       # DOM 渲染逻辑
│       ├── search.js       # 搜索引擎
│       └── app.js          # 入口与事件绑定
├── data/
│   └── websites.json       # 唯一数据文件
└── docs/                   # 所有规格文档
```

> ✅ 总共 8 个源文件。没有额外的配置文件。没有隐藏的魔法。

---

## 3. CSS 架构

### 3.1 CSS 变量系统
单一真实源。所有视觉属性全部通过变量定义：
```css
:root {
  --sidebar-width: 280px;
  --sidebar-collapsed-width: 64px;
  --card-radius: 8px;
  --transition-duration: 150ms;
  --color-primary: #7c3aed;
  --color-bg: #ffffff;
  --color-text: #111827;
}

[data-theme="dark"] {
  --color-bg: #111827;
  --color-text: #f9fafb;
}
```

> ✅ 主题切换不需要重新渲染任何 DOM。仅修改根节点的 `data-theme` 属性，所有样式自动过渡。

### 3.2 布局原则
- 使用 `grid` 作为主布局系统
- 侧边栏使用 `position: sticky`
- 所有间距使用 4px 网格系统
- 禁止使用固定高度，禁止硬编码像素值

---

## 4. JavaScript 架构

### 4.1 模块边界划分
| 模块 | 职责 | 允许依赖 | 禁止依赖 |
|---|---|---|---|
| `state.js` | 全局状态管理，状态变更通知 | 无 | 所有其他模块 |
| `data.js` | 数据加载，索引构建，查询 | `state.js` | `render.js` |
| `search.js` | 模糊搜索，评分排序 | `data.js` | 所有其他模块 |
| `render.js` | DOM 渲染，模板生成 | `state.js`, `data.js` | 直接修改状态 |
| `app.js` | 事件绑定，路由处理，模块初始化 | 所有模块 | 无 |

> ✅ 循环依赖为零。数据流永远是单向的：`State → Data → Render → DOM`

### 4.2 状态机实现
```javascript
class State {
  set(key, value) {
    this._state[key] = value
    this._subscribers.forEach(cb => cb(this._state))
  }

  subscribe(callback) {
    this._subscribers.push(callback)
  }
}
```

> ✅ 仅 30 行代码。没有副作用。没有中间件。100% 可预测。

---

## 5. 路径处理规范

### 5.1 绝对禁止
❌ 禁止使用 `/assets/xxx` 开头的绝对路径
❌ 禁止使用 `window.location.origin`
❌ 禁止假设网站部署在根路径

### 5.2 强制规则
✅ 所有资源引用使用相对路径：`./assets/`
✅ 所有内部锚点使用 `#` 哈希路由
✅ 动态创建的链接全部使用相对路径
✅ 不修改 `base href`

> 这是唯一可以在 GitHub Pages、Vercel、Netlify、任何子路径下零修改部署的方案。

---

## 6. 错误恢复机制
1.  数据加载失败：显示友好提示，提供重试按钮
2.  单条数据损坏：自动跳过该条目，不影响其他内容渲染
3.  脚本执行异常：优雅降级到基础浏览模式
4.  LocalStorage 损坏：自动重置为默认值，不崩溃

> ✅ 任何单点故障都不会导致整个页面白屏。
