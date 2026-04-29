# skill-update 技能完整分析报告

**分析时间**: 2026-04-27
**技能版本**: v6.0 Enhanced
**技能路径**: `/home/yoli/.hermes/skills/skill-update/`

---

## 📋 一句话定义

**读取任务说明 → 条件执行引擎 → 智能诊断-修复-重试闭环 → 多级验证 → 详细执行报告 → 清理 → 安装激活 → 实践经验沉淀**

skill-update 是一个"元技能"(Meta-Skill)：专门用于更新和升级其他技能（包括自己）的通用父技能。

---

## 🎯 六大核心能力详解

### 1. 🔍 分析策划能力极强

**SkillState 状态诊断器** (`scripts/skill_state.py`)
- 深度解析 SKILL.md 的 YAML frontmatter 和正文内容
- 提取所有字段（triggers, depends, entrypoint, scripts 等）
- 支持条件检查（`check_condition()`）
- 统计列表项数量（`count_field_items()`）
- 输出完整的技能状态字典

**任务说明模板系统** (`TASK_TEMPLATES.yaml` - 待完善)
- 为每个标准步骤预定义详细任务模板
- 包含：任务目标、具体工作清单、工作方式、验收标准、约束条件、执行要求
- 支持变量替换（`<TARGET_SKILL>` 占位符）
- 可扩展的7步标准流程模板

**智能诊断** (`diagnose_skill()` 函数)
```python
# 诊断逻辑：
1. 检查 action 的 check 前置条件（shell 命令）
2. 根据 action type 判断当前状态是否满足
3. 输出待执行 actions 列表 + 诊断原因
```

---

### 2. 🔄 自适应能力极强

#### 条件执行引擎 (`run_enhanced.py`)

**智能跳过机制**：
- 每个 action 可带 `check` 字段（shell 命令）
- 执行前运行 `check`，返回0（条件满足）则跳过
- 避免重复执行已满足的条件

**动态模板展开**：
```python
# composite action → 展开为多个原子操作
composite: { template: "step1_improve", ... }
↓ 展开
atomic actions: [append_field, ensure_count, set_if_missing, ...]
```

**验证强度自适应** (`expected_state` 部分):
- 根据 risk_level 选择验证策略
- LOW: 文件存在 + 基本语法
- MEDIUM: 完整性 + 基本功能
- FULL: skill-improver + agent-verification + 功能测试
- CRITICAL: FULL + independent-referee + mandatory-verification

**失败策略自适应** (`on_failure` 字段):
- `rollback_and_abort`: 核心配置错误，立即回滚中止（步骤1,3,6,7）
- `warn_only`: 非关键优化，记录警告继续（步骤2,5）
- `diagnose_and_continue`: 绑定验证失败，诊断后跳过（步骤4）
- `retry_with_fix`: 可自动修复的临时错误，重试并尝试修复

**重试策略** (`retry_policy` 字段):
```yaml
retry_policy:
  max_attempts: 3              # 最大重试次数
  retry_condition: "error_id in ['SUBAGENT_PATH_NOT_FOUND']"
  backoff_seconds: 5           # 重试间隔（指数退避）
```

---

### 3. 📦 版本管理能力极强

#### 检查点与自动回滚

**检查点创建** (`action_executor.py::create_checkpoint()`):
```python
# 首次修改前自动创建备份
.checkpoints/skill.md.YYYYMMDD_HHMMSS.bak
```
- 存储位置：`.checkpoints/` 子目录
- 保留策略：最多5个，旧自动清理
- 内容：SKILL.md + scripts/ 目录（tar.gz）

**回滚机制** (`rollback_manager.py`):
- 自动回滚：HIGH 风险步骤失败时触发
- 手动回滚：`rollback_to_latest()` 恢复到最新检查点
- 回滚失败处理：从 skill-improver 备份恢复

#### 历史追踪与预测 (`scripts/history_tracker.py`, `predictive_planner.py`)

**历史数据库** (`~/.hermes/skills/.hermes-history.db`):
```sql
executions(
  skill, action_id, action_type,
  start_ts, end_ts, duration_sec,
  cpu_percent, memory_mb, success, error_msg
)
statistics(
  skill, action_type,
  avg_duration, std_dev, success_rate, sample_count
)
```

**预测维度**:
1. **ETA 预测**: 历史平均耗时 + 2σ 缓冲
2. **失败风险**: 基于历史失败率 × 关键路径权重
3. **并发推荐**: I/O密集型占比>50%时可翻倍并发
4. **瓶颈识别**: 累计耗时>10s的 action 类型标记为瓶颈

#### 依赖图 DAG 调度 (`scripts/dag_scheduler.py`)

**功能**:
- 扫描所有 SKILL.md 的 `depends` 字段
- 构建依赖 DAG（有向无环图）
- 拓扑排序确定安全执行顺序
- 自动分组可并行任务
- 检测循环依赖并给出修复建议

**算法**: Kahn + DFS，复杂度 O(V+E)

**增量调度**: 仅重算受影响子图，避免全量重算

---

### 4. 🐛 纠错能力极强

#### 错误模式库 (`scripts/error-patterns.json`)

包含7种常见错误模式：

| 错误ID | 名称 | 严重性 | 自动修复 |
|-------|------|--------|---------|
| `SUBAGENT_PATH_NOT_FOUND` | 子技能路径解析失败 | HIGH | ✅ |
| `MISSING_ENTRYPOINT` | 缺少入口脚本（run.sh） | HIGH | ✅ |
| `EXECUTION_FAILED` | 子技能执行失败 | MEDIUM | ❌ |
| `VERIFICATION_MISMATCH` | 验证结果与执行不一致 | HIGH | ❌ |
| `CHECKPOINT_CREATION_FAILED` | 检查点创建失败 | MEDIUM | ❌ |
| `REFEREE_DISAGREED` | 独立裁判否决 | HIGH | ❌ |
| `ROLLBACK_FAILED` | 回滚失败 | CRITICAL | ❌ |
| `CORRUPTED_FRONTMATTER_PREFIX` | SKILL.md文件头损坏 | HIGH | ✅ |

**自动诊断流程**:
```
执行失败 → diagnose_failure() 查询 error-patterns.json
          ↓
        输出：错误ID、错误类型、严重性、修复步骤
          ↓
    auto_fixable? ──是──→ attempt_auto_fix() → 重试执行
          ↓ 否
        输出 fix_suggestions → 等待人工干预
```

#### 已知 BUG 及修复

**BUG 1: skill-update v6.0 路径解析错误 (2026-04-26)**
- 问题: `_resolve_skill_path()` 忽略传入的 `skill_dir` 参数
- 修复: 优先使用传入参数，回退到任务文件父目录

**BUG 2: ActionExecutor 的 check 条件逻辑反转 (2026-04-26)**
- 问题: `if not self._check_condition()` 导致判断完全颠倒
- 修复: 改为 `if self._check_condition()`，条件满足时跳过

**BUG 3: YAML 格式错误 (2026-04-26)**
- 问题: `where: after_field: triggers` YAML 解析失败
- 修复: 值加引号 `where: "after_field: triggers"`

**BUG 4: 模板与具体技能不匹配 (2026-04-26)**
- 问题: 通用模板的 trigger 列表与技能实际语义不符
- 修复: 方案A（推荐）- 创建完全定制化的任务文件

---

### 5. 🧹 清理垃圾能力极强

#### cleanup-manager 子技能

**清理范围**:
1. 临时代码和文档（`.checkpoints/` 旧备份）
2. 无用代码和文档（占位符 `TBD`, `TODO`, `待定义`）
3. 多余代码和文档（重复的 trigger, 废弃的脚本）
4. SKILL.md 中的内联代码（应移至 scripts/ 目录）
5. 旧版本代码、旧版本定时任务
6. 多余的备份文件（超过5个的自动清理）
7. debug 日志、测试文件残留

**清理原则** (来自 skill-optimizer):
- 永远先注释，后删除
- 每次只修改不超过10%内容
- 创建3份独立备份
- 优化前后大小对比、行数对比
- 必须在独立裁判审核后删除

---

### 6. ⚙️ 原子操作执行器 (`scripts/action_executor.py`)

#### 6种原子操作类型

| 类型 | 用途 | 修改目标 | 示例 |
|-----|------|---------|------|
| `append_field` | 追加字段 | SKILL.md | 在 `depends:` 后追加 `scripts:` 列表 |
| `ensure_count` | 确保数量 | SKILL.md | 补齐 triggers 到9项 |
| `set_if_missing` | 缺失时设置 | SKILL.md | 设置 entrypoint: run.sh |
| `ensure_line` | 条件性添加行 | 系统命令 | `chmod +x run.sh` |
| `delete_lines` | 删除匹配行 | SKILL.md | 删除所有 `TBD` 占位符 |
| `replace_text` | 精确文本替换 | SKILL.md | `# -*- coding: gbk -*-` → `utf-8` |
| `create_file` | 创建文件 | 文件系统 | 创建 scripts/verify.py |
| `run_shell` | 执行 shell | 系统命令 | `git add SKILL.md` |

#### 执行流程

```
前置检查(check) → 创建检查点 → 执行原子操作 → 后置断言验证
    ↓              ↓              ↓               ↓
条件满足?   首次修改前备份  类型分发        expected 列表
  ├─是→ 跳过     .checkpoints/  append_field  每个 shell 命令
  └─否→ 执行     skill.md.XXX  ensure_count  returncode==0?
```

#### 前置检查的特殊处理

`check` 字段是 **shell 命令**，返回0表示条件满足：
```yaml
- id: chmod_run_sh
  type: ensure_line
  check: 'test -x run.sh'      # run.sh 是否可执行?
  value: 'chmod +x run.sh'     # 不可执行则执行此命令
  expected:
    - 'test -x run.sh'         # 验证是否成功
```

**注意**: check 仅检查 frontmatter 部分（第一个 `---` 到第二个 `---` 之间）

---

## 🏗️ 完整架构图

```
┌──────────────────────────────────────────────────────────┐
│          skill-update v6.0 Enhanced 父技能                │
│  职责：调度 + 诊断 + 报告 + 清理（不直接干活）             │
└───────────────┬───────────────────────┬──────────────────┘
                │                       │
     task.yaml │                       │ 子技能调用
                ▼                       ▼
    ┌─────────────────┐    ┌─────────────────────────────┐
    │  Conditional    │    │     7个专用子技能            │
    │ Workflow Engine │    │  (每个负责一个标准步骤)        │
    │  - run_enhanced │    ├─────────────────────────────┤
    │  - 任务加载      │    │ 1. skill-improver          │
    │  - 条件分支评估  │    │    → 完善技能配置           │
    │  - 重试回路管理  │    │    → 补齐9个triggers        │
    │  - 诊断-修复-重试│    │    → 添加depends字段        │
    │  - 报告生成      │    │    → 验证scripts字段        │
    └────────┬────────┘    ├─────────────────────────────┤
             │              │ 2. skill-optimizer         │
             │              │    → 优化技能               │
             │              │    → 删除占位符             │
             │              │    → 修正编码               │
             │              │    → 添加最佳实践            │
             │              ├─────────────────────────────┤
             │              │ 3. code-implementer        │
             │              │    → 补充scripts/目录       │
             │              │    → 创建run.sh             │
             │              │    → 设置可执行权限          │
             │              ├─────────────────────────────┤
             │              │ 4. binding-manager         │
             │              │    → 建立depends关联        │
             │              │    → 验证绑定可用性          │
             │              ├─────────────────────────────┤
             │              │ 5. cleanup-manager         │
             │              │    → 清理临时文件           │
             │              │    → 删除无用代码           │
             │              │    → 移除旧版本备份          │
             │              ├─────────────────────────────┤
             │              │ 6. activation-manager       │
             │              │    → 安装技能               │
             │              │    → 激活技能               │
             │              │    → 设置定时任务            │
             │              ├─────────────────────────────┤
             │              │ 7. final-reviewer          │
             │              │    → 独立裁判验证            │
             │              │    → agent-verification     │
             │              │    → mandatory-verification │
             │              └─────────────────────────────┘
             │
    ┌────────▼────────┐
    │  核心组件库       │
    ├─────────────────┤
    │ task_parser_v6  │ ← YAML → Action 对象
    │ skill_state     │ ← SKILL.md 状态诊断
    │ action_executor │ ← 6种原子操作执行
    │ config_manager  │ ← 热重载配置
    │ dag_scheduler   │ ← 依赖图拓扑排序
    │ lib.sh          │ ← 共享bash函数
    └─────────────────┘
```

---

## 📊 七步标准流程（不可调整顺序）

```
┌─────────────┬──────────────────────────────────────────────────┐
│  步骤        │  负责子技能      │  核心任务                         │
├─────────────┼──────────────────────────────────────────────────┤
│  Step 1     │  skill-improver │  完善技能配置                      │
│             │                 │  • 补齐 triggers 到 9 项            │
│             │                 │  • 添加 depends 字段                │
│             │                 │  • 补全 scripts 列表（.py/.sh）     │
│             │                 │  • 设置 entrypoint: run.sh          │
│             │                 │  • 添加 verification 标记           │
├─────────────┼──────────────────────────────────────────────────┤
│  Step 2     │  skill-optimizer│  优化技能结构                      │
│             │                 │  • 删除 TODO/TBD 占位符            │
│             │                 │  • 修正编码为 UTF-8                 │
│             │                 │  • 规范化 Markdown 排版            │
│             │                 │  • 补充最佳实践说明                 │
│             │                 │  • 移除 SKILL.md 中的内联代码       │
├─────────────┼──────────────────────────────────────────────────┤
│  Step 3     │  code-implementer│ 完善功能代码                      │
│             │                 │  • 确保 scripts/ 目录存在          │
│             │                 │  • 创建缺失的 .py/.sh 脚本         │
│             │                 │  • 设置脚本可执行权限 (chmod +x)   │
│             │                 │  • 验证脚本语法正确性               │
├─────────────┼──────────────────────────────────────────────────┤
│  Step 4     │  binding-manager │ 建立关联绑定                      │
│             │                 │  • depends 字段声明子技能依赖       │
│             │                 │  • 验证子技能路径有效              │
│             │                 │  • 确保 run.sh 可调用              │
│             │                 │  • 父子技能双向绑定                │
├─────────────┼──────────────────────────────────────────────────┤
│  Step 5     │  cleanup-manager │ 清理收尾                          │
│             │                 │  • 删除临时文件、中间文件           │
│             │                 │  • 清理旧版本脚本、旧备份           │
│             │                 │  • 移除 .checkpoints 超过5个       │
│             │                 │  • 清理 debug 日志                 │
├─────────────┼──────────────────────────────────────────────────┤
│  Step 6     │  activation-manager│ 安装激活                         │
│             │                 │  • 设置脚本权限（所有 .sh/.py）    │
│             │                 │  • 创建 .installed 标记文件        │
│             │                 │  • 注册到技能系统（如有）          │
│             │                 │  • 配置 cron/systemd 定时任务      │
├─────────────┼──────────────────────────────────────────────────┤
│  Step 7     │  final-reviewer  │ 最终审核（CRITICAL）              │
│             │                 │  • skill-improver 验证             │
│             │                 │  • agent-verification 集成验证      │
│             │                 │  • independent-referee 完全隔离验证 │
│             │                 │  • mandatory-verification 系统钩子  │
│             │                 │  • 生成最终报告 JSON               │
└─────────────┴──────────────────────────────────────────────────┘

⚠️  铁律：跳过任何一步 = 任务未完成
⚠️  铁律：调整步骤顺序 = 任务未完成
✅  必须：完整执行7步后才可宣称"完成"
```

---

## 🔧 原子操作详解（6种类型）

### 1. append_field - 追加字段

**用途**: 在 SKILL.md 指定位置插入多行内容

**必需字段**:
- `field`: 字段名（`triggers`, `depends`, `scripts` 等）
- `value`: 完整内容（支持多行 YAML 块）
- `where`: 插入位置
  - `end_of_file`: 文件末尾
  - `after_field: entrypoint`: 在 `entrypoint:` 行后
  - `before_field: entrypoint`: 在 `entrypoint:` 行前
  - `line: 42`: 第42行后（基于1）

**示例**:
```yaml
- id: add_depends
  type: append_field
  field: depends
  value: |
    depends:
      - nav-core
      - nav-data
      - binding-manager
  where: after_field: triggers
  expected:
    - "grep -q '^depends:' SKILL.md"
    - "grep -A2 '^depends:' SKILL.md | grep -q 'nav-core'"
```

**关键实现细节** (`action_executor.py::_append_field`):
```python
if where.startswith('after_field:'):
    after_field = where.split(':', 1)[1].strip()  # ⚠️ strip() 关键
    for i, line in enumerate(lines):
        if re.match(rf'^{after_field}:', line):
            insert_idx = i + 1
            # 跳过缩进行（字段现有内容）
            while insert_idx < len(lines) and lines[insert_idx].startswith(' '):
                insert_idx += 1
            break
    if insert_idx is None:
        insert_idx = len(lines)  # fallback 到末尾
```

---

### 2. ensure_count - 确保列表项数量

**用途**: 统计 YAML 列表字段项数，不足则追加新项

**必需字段**:
- `field`: 字段名（`triggers`, `scripts` 等）
- `count`: 期望最小数量
- `template`: 新项模板，`{n}` 替换为序号

**示例**:
```yaml
- id: ensure_9_triggers
  type: ensure_count
  field: triggers
  count: 9
  template: "  - {n}: 待定义"
  expected:
    - "grep -c '^- ' SKILL.md | grep -q '^9$'"
```

**执行逻辑**:
1. 查找字段行 (`field:`)
2. 统计后续缩进行的 `- ` 列表项
3. 当前项数 < count: 生成 `count - current` 个新项，插入到字段内容之后
4. 当前项数 >= count: 跳过（返回 True）

---

### 3. set_if_missing - 缺失时设置

**用途**: 字段不存在时才设置值（幂等操作）

**支持格式**:
- 单行: `field: value` → `[f"{field}: {value_lines[0]}"]`
- 多行: `field:` + 缩进内容 → `[f"{field}: {val0}", *rest_lines]`

**示例**:
```yaml
- id: set_entrypoint
  type: set_if_missing
  field: entrypoint
  value: run.sh
  expected:
    - "grep -q '^entrypoint: run.sh' SKILL.md"
```

---

### 4. ensure_line - 条件性添加行（系统命令）

⚠️ **注意**: 此操作**可能执行系统命令**（如 `chmod`），**不修改 SKILL.md**

**必需字段**:
- `check`: shell 条件命令（返回0=已满足，则跳过）
- `value`: 要执行的命令（`chmod +x`, `git add` 等）

**示例**:
```yaml
- id: chmod_run_sh
  type: ensure_line
  check: 'test -x run.sh'        # run.sh 是否已可执行?
  value: 'chmod +x run.sh'       # 否 → 执行赋权
  expected:
    - 'test -x run.sh'           # 验证成功
```

**执行流程**:
```
1. 执行 check 命令
   ├─ 返回0（条件满足）→ 跳过，直接验证 expected
   └─ 返回非0 → 执行 value 命令 → 验证 expected
```

---

### 5. delete_lines - 删除匹配行

**必需字段**:
- `pattern`: 正则表达式（逐行 `re.match`，从行首匹配）

**示例**:
```yaml
- id: remove_todos
  type: delete_lines
  pattern: ".*TODO.*"
  expected:
    - "! grep -q 'TODO' SKILL.md"
```

---

### 6. replace_text - 精确文本替换

**必需字段**:
- `old`: 要替换的旧文本（子串匹配）
- `new`: 新文本
- `count`（可选）: 0=全部替换, N=替换前N处

**示例**:
```yaml
- id: fix_encoding
  type: replace_text
  old: "# -*- coding: gbk -*-"
  new: "# -*- coding: utf-8 -*-"
  expected:
    - "grep -q 'utf-8' SKILL.md"
```

---

## 📄 任务文件格式 (task_v6.yaml)

```yaml
# ─────────────────────────────────────────────────────────────
# 必需字段
# ─────────────────────────────────────────────────────────────
skill: <目标技能名>                    # 如: skill-improver
objective: <一句话描述任务目标>       # 如: 完善基础配置

# ─────────────────────────────────────────────────────────────
# 动作清单（有序数组，按顺序执行）
# ─────────────────────────────────────────────────────────────
actions:
  - id: <唯一标识符，snake_case>
    type: <append_field|ensure_count|set_if_missing|
           ensure_line|delete_lines|replace_text|create_file|run_shell>
    description: <人类可读描述，必需>

    # ── append_field 专用 ──
    field: <字段名>                    # triggers / depends / scripts
    value: |                          # 多行内容
      字段内容...
    where: <end_of_file|after_field: X|line: N>

    # ── ensure_count 专用 ──
    count: <最小数量>                  # 如: 9
    template: "  - {n}: 待定义"       # {n} 自动替换为序号

    # ── set_if_missing 专用 ──
    value: <单行或多行内容>

    # ── ensure_line 专用 ──
    check: '<shell 条件命令>'          # test -x run.sh
    value: '<shell 执行命令>'          # chmod +x run.sh

    # ── delete_lines / replace_text 专用 ──
    pattern: <正则表达式>              # delete_lines 用
    old: <旧文本>                      # replace_text 用
    new: <新文本>                      # replace_text 用
    count: <替换次数，0=全部>           # replace_text 可选

    # ── create_file 专用 ──
    path: <相对路径>                   # 如: scripts/verify.py
    content: |                        # 文件内容
      #!/usr/bin/env python3
      ...
    mode: "755"                       # 权限（可选，自动检测shebang）

    # ── run_shell 专用 ──
    command: <shell 命令>              # 如: git add SKILL.md

    # ── 所有类型通用 ──
    check: <shell 条件，满足则跳过>     # 可选
    expected:                         # 必需：至少1条断言
      - "shell command returns 0"
      - "file_exists: path"
      - "file_executable: path"
      - "dir_exists: path"
      - "file_contains: path:pattern"
    fix_action: <失败时自动修复动作>    # 可选，引用 error-patterns

    # ── 执行控制（可选） ──
    on_failure: <rollback_and_abort|warn_only|
                 diagnose_and_continue|retry_with_fix>
    retry_policy:
      max_attempts: 3
      retry_condition: "error_id in [...]"
      backoff_seconds: 5
    skip_condition: "<shell 条件>"     # 满足则跳过此action

# ─────────────────────────────────────────────────────────────
# 期望的最终状态（用于最终验证）
# ─────────────────────────────────────────────────────────────
expected_state:
  triggers_count: 9                   # triggers 列表至少9项
  depends_present: true               # depends 字段是否存在
  scripts_has_py: true                # scripts 包含 .py 文件
  run_sh_executable: true             # run.sh 是否可执行
  installed_marker_exists: true       # .installed 标记文件
  no_debug_logs: true                 # 无 debug 日志残留
  no_test_files: true                 # 无测试文件残留
  version: "v8.1"                     # 版本号包含

# ─────────────────────────────────────────────────────────────
# 可选字段
# ─────────────────────────────────────────────────────────────
description: |
  详细的任务说明（可多行）
  【任务目标】
  【具体工作清单】
  【工作方式】
  【注意事项】

dry_run: false                       # 仅用于人类阅读，不影响执行
```

---

## 🎯 使用方式

### 方式1：使用模板快速开始

```bash
cd /home/yoli/.hermes/skills/skill-update

# 执行步骤1：完善技能（通过 skill-improver）
python3 run_enhanced.py skill-improver TASK_TEMPLATES.yaml::step1_improve

# 执行步骤2：优化技能（通过 skill-optimizer）
python3 run_enhanced.py skill-optimizer TASK_TEMPLATES.yaml::step2_optimize

# 逐步执行所有7步（推荐）
for step in step1_improve step2_optimize step3_implement \
            step4_binding step5_cleanup step6_activation step7_final_review; do
    echo "=== 执行 $step ==="
    python3 run_enhanced.py $(echo $step | cut -d'_' -f1) \
        TASK_TEMPLATES.yaml::$step || break
done
```

### 方式2：自定义任务文件

```bash
# 1. 复制模板
cp TASK_TEMPLATES.yaml my_update.yaml

# 2. 编辑替换 <TARGET_SKILL> 为实际技能名
vim my_update.yaml

# 3. 预览模式（不修改）
python3 run_enhanced.py --dry-run my-skill my_update.yaml

# 4. 实际执行
python3 run_enhanced.py my-skill my_update.yaml

# 5. 自动确认模式（cron 友好）
python3 run_enhanced.py --no-prompt my-skill my_update.yaml
```

### 方式3：交互式执行

```bash
# 直接调用父技能
python3 run_enhanced.py /path/to/skill /path/to/task.yaml

# 输出示例:
[INFO] ℹ️  skill-update v6.0 Enhanced 启动
[INFO] ℹ️  目标技能: skill-improver
[INFO] ℹ️  任务文件: TASK_TEMPLATES.yaml

📋 任务摘要:
  目标技能: skill-improver
  任务: 完善基础配置
  总 actions: 13 → 待执行: 12

执行这些操作？(y/N): y

[ACTION] ▶️  步骤 1/12: ensure_9_triggers
  前置检查: triggers 字段存在，但数量不足（当前 6 项）
  执行: ensure_count(triggers, 9)
  修改完成 (+3 行)
  验证断言 1: grep -q '^triggers:' SKILL.md ✅
  验证断言 2: grep -c '^- ' SKILL.md | grep -q '^9$' ✅

[SUCCESS] ✅ 步骤 1/12 完成

📊 执行摘要:
  总 actions: 13
  执行: 12
  跳过: 1
  成功: 12
  失败: 0
  验证: 10 通过 / 0 失败
  耗时: 45.23秒

[SUCCESS] ✅ 🎉 任务完成！所有 actions 成功
```

---

## 🔍 诊断-修复-验证完整闭环

### 自动诊断流程 (`error-patterns.json`)

```python
执行失败
    ↓
diagnose_failure() 查询 error-patterns.json
    ↓
输出: 错误ID、错误类型、严重性、修复步骤
    ↓
    ┌─────────────┴─────────────┐
    │                           │
auto_fixable=true      auto_fixable=false
    │                           │
    ↓                           ↓
attempt_auto_fix()     输出 fix_suggestions
    │                           │
    ↓                           ↓
重试执行              等待人工干预
```

### 验证失败处理

```
VERIFICATION_MISMATCH
    ↓
1. 检查验证失败的详细输出
2. 检查生成文件的内容和格式
3. 验证文件权限和所有权
4. 检查文件编码（必须是 UTF-8）
    ↓
用户手动修复
    ↓
重新运行验证
```

---

## 📈 三层验证管道

### 阶段1 - skill-improver 验证
- 文件存在检查
- 备份文件创建
- 编码验证（UTF-8）

### 阶段2 - agent-verification 集成
```python
from my_agent.verification import quick_verify
ok, summary = quick_verify(task_id, files, commands)
# 自动检查：文件存在、大小、UTF-8、最后3行铁证
```

### 阶段3 - independent-referee 审查
```bash
skill run independent-referee "技能 [xxx] 是否已完全就绪？"
# 裁判完全隔离，不知道前因后果，只做纯验证
```

### 阶段4 - mandatory-verification 钩子
- 系统级强制验证（透明触发）
- 任何宣称"完成"前必须通过

**验证强度决策表**:

| 风险等级 | 判定条件 | 验证强度 | 触发阶段 |
|---------|---------|---------|---------|
| LOW | 单文件、只读、临时文件 | BASIC | 阶段1 |
| MEDIUM | 多文件、配置、有失败历史 | STANDARD | 阶段1+2 |
| HIGH | 生产部署、核心架构、安全相关 | FULL | 阶段1+2+3 |
| CRITICAL | 最终审核（步骤7） | CRITICAL | 阶段1+2+3+4 |

---

## 🛡️ 父技能职责铁律

### ❌ 绝对禁止：父技能直接操作文件系统

**错误示范**:
```python
# ❌ 父技能自己读取/写入 SKILL.md
with open(skill_dir / "SKILL.md") as f:
    content = f.read()
# ... 修改 ...
with open(...) as f:
    f.write(modified)
```

**正确示范**:
```bash
# ✅ 父技能只调度，具体工作交给子技能
skill run skill-improver --task-file step1.yaml
skill run skill-optimizer --task-file step2.yaml
```

**修复方法**（来自 skill-improver BUG 记录）:
1. 优先使用子技能完成具体任务执行
2. 父角色永远不替代子技能干活
3. 父技能可以传递任务说明、参数、约束
4. 新任务无法用现有子技能完成 → 创建新子技能

---

## 🔗 子技能智能路由

### 多级路径搜索 (`resolve_subagent_path()`)

```python
搜索顺序:
1. 标准路径: /home/yoli/.hermes/skills/<subagent>
2. 本地嵌套: /home/yoli/.hermes/skills/<parent>/<subagent>
3. 历史备份: /home/yoli/.hermes/skills/.backup/update-skill/20260423115410/<subagent>
4. 全局搜索: find /home/yoli/.hermes/skills -name "<subagent>"

⚠️  铁律: 父技能永远不硬编码子技能路径，必须动态解析
```

### 子技能清单（7个）

```
skill-update/
├── activation-manager/    # 步骤6：安装激活
├── binding-manager/       # 步骤4：建立关联
├── cleanup-manager/       # 步骤5：清理收尾
├── code-implementer/      # 步骤3：完善代码
├── final-reviewer/        # 步骤7：最终审核
├── skill-improver/        # 步骤1：完善技能
└── skill-optimizer/       # 步骤2：优化技能
```

**每个子技能包含**:
- `SKILL.md` - 安全规范（完善/优化 的黄金规则）
- `run_enhanced.py` - 条件执行引擎（复用父技能逻辑）
- `action_executor.py` - 原子操作执行器（共享）
- `skill_state.py` - 状态诊断器（共享）
- `task_parser.py` - 任务解析器（简化版）
- `run.sh` - 入口脚本
- `scripts/` - 功能脚本（各子技能独立）

---

## 📊 核心统计数据

| 指标 | 数值 |
|-----|------|
| 总子技能数 | 7 个 |
| 原子操作类型 | 8 种 |
| 错误模式库条目 | 8 种 |
| 验证强度等级 | 4 级 |
| 失败策略类型 | 4 种 |
| 已知 BUG 修复 | 5 个 |
| 代码文件数 | 26 个 |
| SKILL.md 行数 | 1,274 行 |
| 版本历史 | v1.0 → v6.0 Enhanced |

---

## ⚡ 性能与监控

### 配置文件 (`config_manager.py`)

```yaml
# ~/.hermes/config.yaml
log_level: "INFO"            # 日志级别
max_workers: 4               # 最大并发工作线程
retry_attempts: 3            # 默认重试次数
retry_delay: 2               # 重试间隔（秒）
checkpoint_enabled: true     # 启用检查点
prediction_enabled: true     # 启用预测规划
```

**热重载支持**: 修改 config.yaml 自动生效（检查 mtime）

### 结构化日志 (`scripts/structured_logger.py`)

每条日志包含:
```
[LEVEL] 符号 消息
  额外字段: extra_data (JSON)
```

**日志示例**:
```
[INFO] ℹ️  步骤 1/5: ensure_triggers_count
[ACTION] ▶️  Action: s1_ensure_9_triggers (ensure_count)
[SUCCESS] ✅  验证断言 1: grep -q '^triggers:' SKILL.md
```

### 执行报告（JSON）

```json
{
  "skill": "skill-improver",
  "task_objective": "完善基础配置",
  "timestamp": "2026-04-26T12:00:00+08:00",
  "total_actions": 13,
  "executed": 12,
  "skipped": 1,
  "duration_seconds": 45.23,
  "modifications": [
    {"id": "s1_ensure_9_triggers", "type": "ensure_count", "success": true},
    ...
  ],
  "verification": {"passed": 10, "failed": 0}
}
```

保存位置: `skill_dir/reports/self_upgrade_YYYYMMDD_HHMMSS.json`

---

## 🎓 实践经验总结

### 经验1: 任务说明强制传递（v2.0 核心发现）

**问题**: 所有脚本都是不可用脚本，因为执行阶段的参数都没有附带详细任务说明

**修复**: 父技能必须为每个步骤生成详细任务说明，写入临时文件，传递文件路径作为 `$2` 参数。子技能必须接收 `$TASK_FILE` 参数并读取，验证完整性，严格按照任务说明执行。

**铁律**:
> 所有技能中的所有代码，只要与完成任务有关，在执行之前，必须有一个参数是用来传达详细的任务说明。如果代码中没有这样的参数，以后所有的执行都等于是乱执行，不是真正按任务说明来执行任务。

### 经验2: 父技能职责只调度不代劳（v2.0）

**错误**: 父技能直接操作文件系统，代替子技能干活

**正确**: 父技能唯一操作是 `skill run 子技能名`，传递参数、校验结果、处理错误，但绝不直接操作目标技能的文件系统。

### 经验3: 技能完成度的最终标准

> 你可以不知道这个技能的任何细节，不需要看文档，不需要记住路径，只需要输入 `skill run 技能名`，它就可以完全正确地工作。如果还做不到这一点，不管文档写的多么完美，不管方案是怎么策划，它就还是没完成。

### 经验4: 反幻觉定律

> 所有写在文档里的计划、接口、流程图、设计，全部都是幻觉。只有当你看到磁盘上真实存在的、可以运行的、已经设置了可执行权限的代码的时候，它才是真的完成了。只要代码还没有写出来，不管文档写的多么漂亮，不管计划多么完美，它就是0%完成，就是不存在。

### 经验5: 完善 ≠ 修改

**真正的完善**:
- 原来的100%完全原封不动，一个字都不碰
- 只在旁边、后面追加新内容
- 原来所有入口、调用、行为100%继续正常工作
- 只是多了一些新的可能、新的路径、新的处理
- 永远不会因为完善导致原来正常工作的东西坏了

**错误示范**:
- ❌ 清空原有内容然后宣称完善完成
- ❌ 只改第一行然后宣称完善完成
- ❌ 没有实际修改就宣称完善完成
- ❌ 修改后不验证就宣称完成

---

## 🔮 未来规划（TODO）

- [ ] 集成 predictive_planner 到 execution_engine_v8（作为前置阶段）
- [ ] 写入 config.yaml 的 prediction 段到执行报告
- [ ] 性能监控器 performance_monitor.py 采样资源数据并写入 execution 记录
- [ ] 历史数据不足时自动降级为默认估值
- [ ] 可视化报表（HTML）：趋势图、热力图、瓶颈分析
- [ ] TASK_TEMPLATES.yaml 完整实现（当前缺失）
- [ ] 创建 skill-update2 目录（v8.0 升级版本）

---

## 💡 核心设计原则

### 1. 向下兼容第一
- 输入和输出接口向下兼容
- 具体实现可以改变，接口保持不变

### 2. 零幻觉交付
- 只有磁盘上真实存在的、可运行的、有可执行权限的代码才算完成
- 文档、计划、流程图都是0%完成

### 3. 安全第一
- 永远先备份，后修改
- 修改前后文件大小对比（优化必须变大）
- 独立裁判验证（完善者不能审核自己）
- 可1秒内完整回滚

### 4. 原子性
- 每个 action 必须是独立、可验证的原子操作
- 失败自动回滚到检查点
- 不完成全部7步=任务未完成

### 5. 自描述任务
- 每个任务文件必须包含详细任务说明
- 子技能无需猜测用户意图
- 验收标准必须可测量

---

## 📁 目录结构

```
~/.hermes/skills/skill-update/
├── SKILL.md                        # 主技能文档（48KB, 1274行）
├── run.sh → scripts/run.sh         # 入口符号链接
├── .installed                      # 安装标记
├── .activated                      # 激活标记
├── .gitlab-ci.yml                  # CI/CD 流水线
├── Jenkinsfile                     # Jenkins 配置
├── reports/                        # 执行报告目录
│   └── self_upgrade_*.json
├── tasks/                          # 任务文件目录（当前为空）
│   └── (待创建 TASK_TEMPLATES.yaml)
├── scripts/                        # 核心脚本集合
│   ├── run_enhanced.py             # 主引擎（条件执行）
│   ├── run.py                      # 旧版本兼容
│   ├── task_parser_v6.py           # v6任务解析器
│   ├── task_parser.py              # 旧版本解析器
│   ├── action_executor.py          # 原子操作执行器
│   ├── skill_state.py              # 状态诊断器
│   ├── config_manager.py           # 配置管理器（热重载）
│   ├── dag_scheduler.py            # 依赖图调度
│   ├── template_engine.py          # 模板引擎（待完善）
│   ├── execution_engine.py         # 执行引擎v8（待集成）
│   ├── verify_five_stages.py       # 五阶段验证（待集成）
│   ├── lib.sh                      # 共享bash函数
│   ├── error-patterns.json         # 错误模式库
│   ├── history_tracker.py          # 历史追踪（v8预测模块）
│   ├── dependency_graph.py         # 依赖图构建（v8预测模块）
│   ├── predictive_planner.py       # 预测规划器（v8预测模块）
│   ├── performance_monitor.py      # 性能监控v2（待完善）
│   ├── rollback_manager.py         # 回滚管理器
│   ├── step_validator.py           # 步骤验证器
│   ├── structured_logger.py        # 结构化日志
│   ├── delta_detector.py           # 差异检测
│   ├── ci_integration.py           # CI/CD集成
│   ├── verify_self.sh              # 自验证脚本
│   ├── upgrade_subskills.py        # 子技能升级脚本
│   └── cron_hourly.sh              # 定时任务
├── activation-manager/             # 子技能：安装激活
│   ├── SKILL.md
│   ├── run.sh
│   ├── run_enhanced.py
│   ├── action_executor.py
│   ├── skill_state.py
│   ├── task_parser.py
│   └── scripts/
├── binding-manager/                # 子技能：建立关联
├── cleanup-manager/                # 子技能：清理收尾
├── code-implementer/               # 子技能：完善代码
├── final-reviewer/                 # 子技能：最终审核
├── skill-improver/                 # 子技能：完善技能
├── skill-optimizer/                # 子技能：优化技能
└── TASK_TEMPLATES.yaml             # ⚠️ 缺失文件（待创建）
```

---

## 🚨 已知限制与待办

### 缺失组件

1. **TASK_TEMPLATES.yaml 不存在**
   - 当前 `tasks/` 目录为空
   - SKILL.md 中多次引用但未实现
   - 需要创建标准7步模板文件

2. **预测模块未集成**
   - `history_tracker.py`, `dependency_graph.py`, `predictive_planner.py` 存在但未接入主流程
   - 计划在 v8.0/v8.1 集成（已在 skill-update2 规划中）

3. **五阶段验证未完成**
   - `verify_five_stages.py` 存在但未调用
   - 需与 final-reviewer 深度集成

4. **性能监控 v2.0 未实现**
   - `performance_monitor.py` 存在但未采样
   - 需写入 execution 记录

5. **监控仪表板未实现**
   - `log_to_dashboard()` 仅设计预留
   - 需集成数据库 + 实时面板

6. **skill-update2 目录不存在**
   - v8.0 升级计划已制定
   - 但实际目录未创建（可能仍在规划阶段）

---

## 📝 总结

skill-update 是一个高度工程化、具备自省和自修复能力的**元技能系统**。它的核心价值在于：

1. **标准化**: 将技能更新过程标准化为7步流水线
2. **安全化**: 检查点、回滚、备份、独立裁判多重保障
3. **自动化**: 条件执行、诊断修复、重试回路减少人工干预
4. **可观测**: 详细日志、JSON报告、历史追踪、性能监控
5. **可扩展**: 模板系统、插件化子技能、配置外置

**当前状态**: v6.0 Enhanced 已稳定运行，但部分 v8.0 规划功能（预测、五阶段验证）尚未集成，TASK_TEMPLATES.yaml 需要补充完整。

---

**报告生成时间**: 2026-04-27
**分析依据**: SKILL.md + 26个脚本文件 + 7个子技能目录结构
