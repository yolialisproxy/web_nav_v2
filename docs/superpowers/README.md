# Superpowers – Hermes Agent 技能适配

## 源项目

**[obra/superpowers](https://github.com/obra/superpowers)** — 187k+ Stars 的 Agentic 软件开发工作流框架

## 适配说明

原项目为 Claude Code / Cursor / Codex 等平台设计的插件。现已转换为 **Hermes Agent** 兼容的技能格式，放置在 `~/.hermes/skills/` 目录下。

### 转换原则
- 严格遵循 cross-platform-skill-standard v1.0 前置元数据规范（仅 `name/description/license`）
- 保留全部原始内容和结构
- 补充关联技能链，便于 Hermes 自动发现和调用
- 新增 2 个 technique 级子技能（`condition-based-waiting`、`root-cause-tracing`）

### 技能清单 (17 个)

| 类型 | 技能 | 说明 |
|------|------|------|
| 🔷 入口 | `superpowers` | 框架总览，完整依赖图 |
| 🔷 入口 | `using-superpowers` | 安装 + 工作流概览 |
| 🟢 设计 | `brainstorming` | Socratic 设计流程 |
| 🟢 设计 | `using-git-worktrees` | 隔离工作区 |
| 🟢 计划 | `writing-plans` | TDD 级别任务拆解 |
| 🔵 执行 | `subagent-driven-development` | 双阶段评审子代理 |
| 🔵 执行 | `executing-plans` | 批量执行 + 人机检查点 |
| 🔵 编码 | `test-driven-development` | RED-GREEN-REFACTOR |
| 🔴 调试 | `systematic-debugging` | 4 阶段根因分析 |
| 🔴 调试 | `dispatching-parallel-agents` | 并行独立调查 |
| 🔴 调试 | `condition-based-waiting` | 替代任意超时 |
| 🔴 调试 | `root-cause-tracing` | 调用栈回溯 |
| 🟡 验证 | `verification-before-completion` | 证据优先原则 |
| 🟡 评审 | `requesting-code-review` | 结构化代码评审 |
| 🟡 评审 | `receiving-code-review` | 回应评审反馈 |
| 🟠 收尾 | `finishing-a-development-branch` | 测试→选项→清理 |
| 🔵 元技能 | `writing-skills` | TDD 编写技能 |

### 啃魂导航 V2 的使用方式

项目中的 `docs/superpowers/plans/2026-04-18-webnav-v2-implementation.md` 已经引用了 `superpowers:subagent-driven-development`。现在可以：

```
brainstorming → writing-plans → subagent-driven-development
                                  ├─ Task 1: 基础页面骨架
                                  ├─ Task 2: 搜索栏与导航
                                  ├─ Task 3: 分类网格视图
                                  ├─ Task 4: 侧边栏
                                  ├─ Task 5: 网站卡片列表
                                  ├─ Task 6: 动画与优化
                                  └─ Task 7: 验收测试
```