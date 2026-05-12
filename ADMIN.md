# 管理后台使用手册

## API 接口文档

### 1. 健康检查
```
GET /health
```
返回系统健康状态

### 2. 获取所有网站
```
GET /api/websites?skip=0&limit=100&category=AI工具&merged=true
```
参数:
- skip: 跳过数量 (分页用)
- limit: 返回数量 (最大1000)
- category: 按分类筛选
- merged: 按状态筛选

### 3. 获取单个网站
```
GET /api/websites/{id}
```

### 4. 创建网站
```
POST /api/websites
Content-Type: application/json

{
  "url": "https://example.com",
  "name": "示例网站",
  "description": "网站描述",
  "category": "分类名称"
}
```

### 5. 更新网站
```
PUT /api/websites/{id}
Content-Type: application/json

{
  "url": "https://example.com",
  "name": "示例网站",
  "description": "更新后的描述",
  "category": "分类名称"
}
```

### 6. 删除网站
```
DELETE /api/websites/{id}
```

### 7. 搜索网站
```
GET /api/search?q=关键词&category=分类&limit=100
```

### 8. 获取分类统计
```
GET /api/categories
```

### 9. 获取统计数据
```
GET /api/stats
```

### 10. 批量导入
```
POST /api/websites/batch
Content-Type: application/json

[
  {
    "url": "https://example1.com",
    "name": "网站1",
    "description": "描述1",
    "category": "分类1"
  },
  {
    "url": "https://example2.com",
    "name": "网站2",
    "description": "描述2",
    "category": "分类2"
  }
]
```

## 管理后台功能

### 网站管理
- 添加新网站
- 编辑网站信息
- 删除网站
- 批量导入/导出

### 分类管理
- 查看分类统计
- 调整分类结构

### 内容审核
- 审核新添加的网站
- 验证链接有效性
- 标记问题内容

### 数据统计
- 总网站数量
- 分类分布
- 审核状态统计
- 数据更新时间

## 使用说明

### 启动服务
```bash
# 使用 FastAPI
python3 api_server.py

# 或使用内置服务器
python3 serve.py
```

### 访问管理界面
```
http://localhost:8000/docs  # API文档
http://localhost:8000/health  # 健康检查
```

## 数据格式

### 网站数据结构
```json
{
  "id": 1,
  "url": "https://example.com",
  "name": "网站名称",
  "description": "网站描述",
  "category": "AI工具/人工智能/综合平台",
  "title": "网页标题",
  "_cat": "AI工具/人工智能/综合平台",
  "phase3_merged": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

## 常见问题

### 如何添加新网站？
1. 通过管理后台界面添加
2. 或使用API批量导入

### 如何更新分类？
在网站详情页面编辑分类信息

### 如何审核网站？
检查网站的可用性和内容质量，更新审核状态

## 注意事项

- 所有修改都会自动备份
- 建议定期导出数据备份
- API调用频率限制为每秒100次
