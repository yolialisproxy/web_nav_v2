# Superpowers Hermes Agent 技能映射
> 本文件记录啃魂导航 V2 项目使用的 Superpowers 技能与 Hermes Agent 技能的映射关系。

## 当前项目状态
- 计划文档: `docs/superpowers/plans/2026-04-18-webnav-v2-implementation.md`
- 设计文档: `docs/superpowers/specs/2026-04-18-webnav-v2-design.md`
- 已转换为 17 个 Hermes Agent 技能，放置于 `~/.hermes/skills/`

## 推荐执行路径

### 阶段 1: 启动 (manual)
1. 调用 `brainstorming` 技能审查/更新设计 (设计已完成，此步可跳过)
2. 调用 `writing-plans` 审查/更新实现计划 (计划已存在，更新 checklist 状态)

### 阶段 2: 实施
3. 调用 `using-git-worktrees` 创建隔离工作区
4. 调用 `subagent-driven-development` 或 `executing-plans` 执行计划
   - 每个任务自动触发 `test-driven-development`
   - 每个任务完成后自动触发 `verification-before-completion`
   - 完成后触发 `requesting-code-review` + `receiving-code-review`

### 阶段 3: 收尾
5. 调用 `finishing-a-development-branch`
   - 选择: merge / PR / keep / discard

## 可选: 并行加速
- 若有独立的子任务 (如前端 vs 后端)，可用 `dispatching-parallel-agents` 并行处理

## 调试辅助
- 遇到问题: `systematic-debugging` → `root-cause-tracing` → `condition-based-waiting`