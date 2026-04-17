# AGENT.MD - WebNav V2 项目核心规范

## 项目概述

- **目标**：构建9,000个高质量导航站点，实现99.9%+链接有效率、100%分类平衡（每小类12-30个站点）、100%内容补全
- **当前状态**（2026-04-17）：
  - 站点总数：8,753/9,000（97.25%）
  - 内容补全率：77.6%（1,456/1,876）
  - 链接有效率：98.7%（23个失效链接）
  - 分类平衡度：97%（3个小类未达标）
- **核心流程**： `数据清理 → 内容补全 → 链接验证 → SEO优化 → 健康报告` 自动闭环运行，每60秒循环检测，达标后自动终止

## 🔒 禁止触碰（绝对红线）

1. **配置文件**

   - ❌ 禁止直接修改 `config.yaml` 中的 `token`、`密钥`、`密码` 字段
   - ❌ 禁止整块覆盖配置块，必须单行 `patch` 修改
   - ✅ 修改后必须重启主进程（`hermes restart`）

2. **数据文件**

   - ❌ 禁止生成新文件名/版本号/中间文件（如 `websites_v2.json`）

   - ❌ 禁止直接写入 `websites.json`，必须通过 `webnav-data-sanitizer` 等工具原子写入

   - ✅ 所有修改必须：

     ```bash
     read_file → 内存校验 → 原子写入 → 自动备份（.bak）
     ```

3. **路径规范**

   - ❌ 禁止硬编码 `~/.hermes/` 或 `/home/yoli/` 路径
   - ✅ 必须使用 `get_hermes_home()` 或 `PROJECT_ROOT` 变量
   - ❌ 禁止在代码中使用 `Path.home()`，必须通过环境变量获取

4. **工具使用**

   - ❌ 禁止用 `terminal` 执行 `cat`/`grep`/`ls`/`sed`
   - ✅ 必须使用：
     - `read_file` 替代 `cat`
     - `search_files` 替代 `grep`/`find`
     - `patch` 替代 `sed`/`awk`
     - `write_file` 替代 `echo`/`cat heredoc`

## 📜 代码规范

1. **基础原则**

   - ✅ 批量任务必须用后台脚本（`nohup`/`cronjob`），智能体仅负责发起/验收
   - ✅ 所有任务必须实现：
     - 幂等性（重复执行结果一致）
     - PID锁保护（`/tmp/lock_task_[name].pid`）
     - SLO超时终止（P0≤30s, P1≤3min, P2≤10min）

2. **Python规范**

   - ✅ 使用标准库（`json`/`subprocess`/`os`），避免第三方依赖

   - ✅ 工具调用必须捕获异常：

     ```python
     try:
         result = terminal(command="curl -I -m 5 https://example.com")
         if result["exit_code"] != 0:
             raise Exception(f"URL检查失败: {result['output']}")
     except Exception as e:
         log_error(e)
     ```

   - ❌ 禁止直接操作文件系统（必须通过 `read_file`/`write_file`）

3. **技能开发**

   - ✅ 每个技能必须包含：

     - 验证步骤（`three-layer-verification`）
     - 错误恢复机制（`recover-corrupted-json-data`）
     - 证明输出（完整路径+文件尾部3行+时间戳）

   - ✅ 技能文件结构：

     ```
     skills/webnav-xxx/
       SKILL.md # 主规范
       scripts/ # 执行脚本
       templates/ # 报告模板
       references/ # 质量标准文档
     ```

## 🔍 验证方式（强制执行）

1. **执行证明机制**

   - 每次操作必须输出：

     ```
     ✅ 完整绝对路径: /home/yoli/GitHub/web_nav_v2/reports/health_report.html
     📄 文件尾部3行: <tr><td>失效链接</td><td>23</td><td>98.7%</td></tr>
     <tr><td>分类平衡度</td><td>97%</td><td>99.5%</td></tr>
     <tr><td>内容补全率</td><td>77.6%</td><td>100%</td></tr>
     ⏱️ 时间戳: 2026-04-17 20:05:17 UTC
     ```

2. **三层验证流水线**

   | 验证层      | 工具                         | 检查内容              |
   | -------- | -------------------------- | ----------------- |
   | **执行层**  | `skill_run site-validator` | 链接有效性、JSON格式校验    |
   | **控制台层** | `browser_console`          | JS错误、API响应码、控制台警告 |
   | **视觉层**  | `browser_visual_check`     | 页面渲染、布局、交互功能      |

3. **关键指标验证**

   - **链接有效率**：

     ```bash
     curl -I -m 5 https://example.com | grep "HTTP/2 200"
     ```

   - **分类平衡**：

     ```bash
     skill_run category-report | awk '/小类/{print $2}' | grep -E '^(1[2-9]|[2-9][0-9])$'
     ```

   - **内容补全**：

     ```bash
     jq 'map(select(.name != null and .desc != null)) | length' data/enriched_websites.json
     ```

4. **灾难恢复流程**

   - 当发现 `enrichment_state.json` 缺失时：

     ```bash
     skill_run webnav-data-sanitizer --repair_state
     ```

   - 当 `websites.json` 损坏时：

     ```bash
     skill_run recover-corrupted-json-data --backup_path "data/websites.json.bak"
     ```

> 📌 **终极铁律**：
> **所有宣称完成的操作，必须同时输出完整绝对路径、文件尾部3行原文、时间戳**
> 没有证明 = 没有做。
> （来源：https://dev.to/mrlinuncut/ai-execution-hallucination-when-your-agent-says-done-and-does-nothing-35g6）