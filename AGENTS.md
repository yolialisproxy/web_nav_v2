## Agent skills

### Issue tracker

Local Markdown — issues live as files in `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Bilingual labels (English + Chinese) for the five canonical roles. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout — `CONTEXT.md` + `docs/adr/` at repo root. See `docs/agents/domain.md`.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- ALWAYS read graphify-out/GRAPH_REPORT.md before reading any source files, running grep/glob searches, or answering codebase questions. The graph is your primary map of the codebase.
- IF graphify-out/wiki/index.md EXISTS, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## 待完成：

游戏版块 - 在主页菜单栏新增一个游戏版块的入口。游戏版块主要是为了增加用户对网站的粘性，所以只需要开发九个比较受大部分用户欢迎的小游戏即可，例如：纸牌、麻将、俄罗斯方块、围棋、象棋、虚拟武侠世界（武侠剧情配合杀怪升级）、虚拟现实世界（恋爱养成配合大富翁模式（一男一女、一男多女））