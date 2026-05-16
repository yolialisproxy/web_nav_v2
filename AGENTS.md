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
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost)

| 阶段 | 主题 | Commit | 时间 |
|---|---|---|---|
|| Phase 23 | 游戏版块 9 款 | `4999418` | 2026-05 |
|| Phase 24 | SEO 分级 + 标签云 + 预渲染 | `26f4771` | 2026-05-15 |
|| Phase 25 | 列表视图 · 统一缓存 · 结构补全 | `5a9ffc1` | 2026-05-16 |

*本手册由 Phase 系统持续维护，根据工作进展更新。*
