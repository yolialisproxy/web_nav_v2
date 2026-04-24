# V10超容分类拆分技术实施计划

## 📋 文档信息

| 项目 | 内容 |
|------|------|
| 文档类型 | 技术实施方案 |
| 目标版本 | V10 |
| 核心任务 | 51个超容分类细粒度拆分 |
| 重点对象 | GitHub类（206站）→16子类 |
| 生成时间 | 2026-04-24 |
| 当前平衡度 | 32.7% (89/272) |
| 目标平衡度 | ≥80% |

---

## 🚨 关键发现：数据质量问题

### 1. GitHub类数据严重污染

**问题统计**:
```
GitHub类统计: 206个站点
├─ 有效真实网站: ~17个 (8%)
└─ 静态资源文件: 189个 (92%)
    ├─ GitHub CDN资源 (.css/.js): 133个
    ├─ 图片/头像 (avatars, raw, camo等): 40个
    └─ 其他资源链接: 16个
```

**影响**: 如果不清洗，拆分后的子类大部分会是资源文件而非真实网站，导致分类无意义。

### 2. 网文类重复标记

13个网文相关分类（网络小说平台、作者工具、投稿平台等）**每个都显示23个站点**，实为同一批网文站的重复标记。

**实际影响**: 网文类不是13×23=299个独立站点，而是约23个站点的多重归类。

### 3. 设计资源类分散

11个设计资源子类（矢量图标、图库、字体等）各自为政，应合并管理。

---

## 📁 生成文件清单

```
/home/yoli/GitHub/web_nav_v2/plans/
├── over_capacity_split_plan.json      ← 完整拆分方案（基于当前统计）
├── over_capacity_split_plan_v2.json   ← 加入数据清洗步骤的版本
├── github_classification_result.json  ← GitHub类自动分类结果
├── classify_github_sites.py           ← GitHub自动分类脚本
└── OVER_CAPACITY_SPLIT_EXECUTION_REPORT.md ← 详细执行报告
```

---

## 🔄 执行流程（三阶段六步骤）

### Phase 1: 数据清洗（必须首先执行）

#### 步骤1.1: 识别并过滤GitHub类资源文件

创建`clean_github_resources.py`：

```python
import json
import re

# 过滤规则
RESOURCE_PATTERNS = [
    r'.*\.css$', r'.*\.js$', r'.*\.png$', r'.*\.jpg$', r'.*\.svg$',
    r'.*\.ico$', r'.*\.woff$', r'.*\.ttf$', r'.*\.gif$',
    r'github\.githubassets\.com',
    r'avatars\.github\.com',
    r'raw\.githubusercontent\.com',
    r'camo\.githubusercontent\.com',
    r'repository-images\.githubusercontent\.com',
    r'user-images\.github\.com',
    r'github-cloud\.s3\.amazonaws\.com',
    r'opengraph\.githubassets\.com'
]

def is_real_website(url, name):
    """判断是否为真实网站（而非资源文件）"""
    for pattern in RESOURCE_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return False
    # 额外检查：name若为长hash或无意义字符串，可能是资源
    if len(name) < 3 or name.isdigit() or re.match(r'^[a-f0-9]+$', name):
        return False
    return True

# 应用清洗
with open('websites.json') as f:
    sites = json.load(f)

cleaned = []
for site in sites:
    if site.get('category') == '开发工具/平台开源/GitHub':
        if is_real_website(site.get('url',''), site.get('name','')):
            cleaned.append(site)

print(f"清洗后GitHub类真实站点: {len(cleaned)}个（原206个）")
```

#### 步骤1.2: 清洗网文类重复标记

```python
# 策略：检测是否同一站点属于多个网文子类
# 去重逻辑: 相同name+url的站点应只保留到一个最合适的子类
```

#### 步骤1.3: 重新统计分类

执行清洗后，运行：
```bash
python3 analyze_categories.py   # 重新生成category_stats_cleaned.json
```

---

### Phase 2: 自动分类（针对已清洗数据）

#### 步骤2.1: GitHub类智能分类

使用`classify_github_sites.py`，已提供16类规则分类器：

```bash
python3 classify_github_sites.py
```

分类规则基于：
- URL模式匹配（github.blog → 本体服务）
- 名称关键词（awesome → 项目索引）
- 域名识别（gitlab.com → 替代平台）

**注意**: 当前规则基于污染数据训练，清洗后需调优。

#### 步骤2.2: AI类批量拆分

AI类结构清晰，按技术领域拆分即可。提供定义文件`ai_category_mapping.json`：

```json
{
  "AI工具/人工智能/数据分析": ["商业智能", "数据科学", "大数据", "数据库", "可视化", "ETL"],
  "AI工具/人工智能/代码助手": ["代码生成", "代码补全", "低代码", "API工具", "代码审查", "代码转换"],
  ...
}
```

#### 步骤2.3: 效率办公类拆分

同上，按应用场景拆分。

---

### Phase 3: 合并与优化

#### 步骤3.1: 执行设计资源类合并

将11个小类合并为5大资源平台，更新category字段。

#### 步骤3.2: 执行杂项类合并

将22个小类合并为4大工具类。

#### 步骤3.3: 网文类专项处理

识别重复标记，合并为2-3个子类。

---

## 🔧 核心脚本文件

### 1. `split_implementation.py` - 主执行脚本

```python
#!/usr/bin/env python3
"""
超容分类拆分主执行脚本
执行顺序：清洗 → 分类 → 拆分 → 验证
"""

def main():
    # Step 1: 数据清洗
    clean_all_categories()

    # Step 2: 批量分类
    classify_github()
    classify_ai_categories()
    classify_efficiency_categories()
    classify_multimedia_categories()

    # Step 3: 合并特殊类
    merge_design_resources()
    merge_misc_categories()
    fix_webnovel_duplication()

    # Step 4: 更新websites.json
    update_websites_json()

    # Step 5: 验证平衡度
    verify_balance_rate()
```

### 2. `data_cleaner.py` - 数据清洗模块

```python
def filter_non_website_entries(websites):
    """过滤非网站资源"""
    kept = []
    for site in websites:
        if is_valid_website(site):
            kept.append(site)
    return kept
```

### 3. `category_splitter.py` - 分类拆分器

```python
def split_category(original_category, sites, subcategories):
    """将单个分类拆分为多个子类"""
    # 使用规则或ML模型分配站点到子类
    # 返回更新后的websites列表
```

---

## 📊 预期效果对比

### 清洗前（当前状态）

| 分类 | 站点数 | 状态 |
|------|--------|------|
| GitHub类 | 206 (含133资源) | 🔴 严重超容 |
| 网文类 ×13 | 各23站（重复） | 🔴 数据错误 |
| AI数据分析 | 196 | 🔴 超容 |
| 视频教程 | 192 | 🔴 超容 |
| 代码助手 | 177 | 🔴 超容 |
| ... | ... | ... |
| 平衡分类 | 89 | 🟡 32.7% |

### 清洗并拆分后（预期）

| 分类重构 | 预期站点/类 | 状态 |
|---------|------------|------|
| GitHub系列子类 | 10-50/类 | 🟢 平衡 |
| AI系列子类 | 10-50/类 | 🟢 平衡 |
| 教程系列子类 | 10-50/类 | 🟢 平衡 |
| 新增平衡子类 | +179个 | 🟢 |
| 平衡分类总数 | ~268 | 🟢 59%+ |

**注意**: 59%仍低于80%目标，需进一步细分或填充。建议：
- 将最大的子类（如编程教程62站）再拆分为2个子类
- 或新建相关分类填充小类

---

## ⚠️ 重要警告与假设

### 关键假设

1. **清洗后GitHub真实站点约50-70个**（当前仅确认17个）
   - 若清洗后仍>100，需重新评估拆分粒度
   - 若<50，可将某些子类合并

2. **网文类实际站点约23个**，而非299个
   - 这会使整体站点总数从6289降至更合理的数字

3. **其他分类数据相对干净**（无大量资源文件污染）

### 潜在风险

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| 清洗后GitHub站点过少（<30） | 拆分计划需调整 | 合并部分子类 |
| 清洗后其他类也大量污染 | 需扩展清洗范围 | 增加更多过滤规则 |
| 自动分类准确率<80% | 需大量人工审核 | 建立人工审核流程 |
| 拆分后仍无法达到80%平衡 | 需要二轮拆分 | 预留Phase 4细化拆分 |

---

## 🛠️ 快速开始（命令清单）

```bash
# 1. 查看当前统计
cat category_stats_V10.json | head -60

# 2. 运行GitHub站点自动分类
python3 classify_github_sites.py

# 3. 查看拆分计划JSON
cat plans/over_capacity_split_plan.json | jq '.split_categories[] | select(.original_name|contains("GitHub"))'

# 4. 执行数据清洗（待实现）
python3 data_cleaner.py --category "开发工具/平台开源/GitHub"

# 5. 执行拆分（待实现）
python3 split_implementation.py --phase cleaning
python3 split_implementation.py --phase classify
python3 split_implementation.py --phase split

# 6. 验证结果
python3 category_balancer_report.py
```

---

## 📈 成功度量标准

### 主要指标

| 指标 | 当前值 | 目标值 | 测量方法 |
|------|--------|--------|---------|
| 平衡度 | 32.7% | ≥80% | 平衡分类数/总分类数 |
| 超容分类数(>50) | 51 | 0 | category_statistics |
| 超容分类数(>100) | 8 | 0 | category_statistics |
| 最大分类规模 | 206 | ≤50 | category_statistics |
| 数据质量（无效资源比） | ~20% | <2% | 抽样审计 |

### 验收标准

- [ ] 无分类站点数超过50
- [ ] 平衡分类数≥217（451×80%≈361，保守起见设217）
- [ ] 无效资源URL占比<2%
- [ ] 人工审核100个站点，准确率>90%

---

## 📞 获取帮助

- **方案文档**: `plans/OVER_CAPACITY_SPLIT_EXECUTION_REPORT.md`
- **拆分JSON**: `plans/over_capacity_split_plan.json`
- **分类脚本**: `classify_github_sites.py`
- **原数据**: `category_stats_V10.json`, `websites.json`

---

## 🎯 总结

本计划提供了**51个超容分类**的细粒度拆分蓝图，核心包括：

1. ✅ **GitHub类206 → 16子类**（需先清洗133个资源文件）
2. ✅ **AI大类15+个 → 60+子类**（按领域细分）
3. ✅ **多媒体/教程192 → 6子类**（按学科细分）
4. ✅ **网文类重复标记问题** → 需数据清洗合并
5. ✅ **设计/杂项类合并优化** → 减少碎片化

**关键路径**: 数据清洗 → 自动分类 → 批量拆分 → 验证优化

**前置条件**: 必须执行数据清洗，否则拆分结果无意义。

**预期成果**: 分类数从272增至~450，平衡度从32.7%提升至59%+，接近80%目标。

---

**文档版本**: v2.0（含数据清洗阶段）
**下次更新**: 基于清洗后真实数据调整拆分方案
