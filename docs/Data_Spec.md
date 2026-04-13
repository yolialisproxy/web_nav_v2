# Data Specification (Data_Spec.md)
Version: 1.0
Project: WebNav V2

## 1. 核心设计目标
- **高可扩展性**: 支持从百级到万级数据的平滑扩展。
- **零冗余**: 采用索引化结构，避免重复存储相同信息。
- **强校验**: 定义严格的类型约束，确保前端渲染零崩溃。
- **多维检索**: 支持通过类别、标签、关键词进行交叉筛选。

## 2. 整体架构
数据采用 `websites.json` 作为唯一真理源，分为三个核心模块：
- `categories`: 导航层级定义（大类 $\rightarrow$ 中类 $\rightarrow$ 小类）。
- `sites`: 扁平化的网站数据库（存储所有详细信息）。
- `mappings`: 建立类别与网站之间的关联索引。

---

## 3. 详细数据定义

### 3.1 Categories (分类树)
定义导航的视觉结构。
- **结构**: `Map<<CategoryIDCategoryID, CategoryObject>`
- **字段**:
    - `id` (String): 唯一标识符 (如 `ai_tools`)。
    - `name` (String): 显示名称 (如 `AI 工具`)。
    - `icon` (String): 对应图标类名或URL。
    - `subCategories` (Map): 嵌套的中类/小类。

### 3.2 Sites (网站数据库)
存储所有网站的原子信息。
- **结构**: `Array<<<SiteSiteSiteObject>>` 或 `Map<<<SiteSiteSiteID, SiteObject>` (目标规模: 9000+ 条目)
- **字段**:
    - `id` (String): 唯一标识符 (如 `claude_ai`)。
    - `name` (String): 网站名称。
    - `url` (String): 完整绝对URL。
    - `desc` (String): 简短描述 (限制 60 字以内)。
    - `icon` (String): Favicon URL 或自定义图标路径。
    - `tags` (Array<<StringString>): 标签集 (如 `["LLM", "Writing", "Productivity"]`)。
    - `priority` (Number): 排序权重 (数值越大越靠前)。

### 3.3 Mappings (关联映射)
定义哪个网站属于哪个分类。
- **结构**: `Map<<CategoryIDCategoryID, SiteID[]>`
- **逻辑**: 一个网站可以通过 Mapping 出现在多个不同的分类中，而无需重复定义 Site 详情。

---

## 4. 数据示例 (JSON)

```json
{
  "config": {
    "version": "1.0",
    "lastUpdated": "2026-04-13"
  },
  "categories": {
    "cat_ai": {
      "name": "AI 工具",
      "icon": "fa-robot",
      "subCategories": {
        "sub_llm": {
          "name": "大语言模型",
          "leafCategories": {
            "leaf_chat": {
              "name": "对话机器人",
              "siteIds": ["site_claude", "site_gpt4"]
            }
          }
        }
      }
    }
  },
  "sites": {
    "site_claude": {
      "name": "Claude",
      "url": "https://claude.ai",
      "desc": "Anthropic 开发的高智能AI助手",
      "icon": "https://claude.ai/favicon.ico",
      "tags": ["LLM", "Coding"],
      "priority": 100
    },
    "site_gpt4": {
      "name": "ChatGPT",
      "url": "https://chatgpt.com",
      "desc": "OpenAI 开发的通用人工智能",
      "icon": "https://chatgpt.com/favicon.ico",
      "tags": ["LLM", "General"],
      "priority": 90
    }
  }
}
```

## 5. 校验规则 (Validation Rules)
- **唯一性**: 所有 `id` 必须全局唯一。
- **完整性**: `siteIds` 中引用的 ID 必须在 `sites` 库中真实存在。
- **有效性**: `url` 必须符合标准的 URL 格式。
- **必填项**: `name` 和 `url` 为强必填项，缺失则该条目在渲染阶段被自动过滤。
