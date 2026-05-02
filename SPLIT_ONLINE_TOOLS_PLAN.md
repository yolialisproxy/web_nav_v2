
V15 Phase 3: 拆分 "其他/杂项/在线工具" 完整执行脚本

RATIONALE:
==========
- 当前: 其他/杂项/在线工具 = 445 sites (超容395)
- 目标: 拆解到 <=50
- 策略: 迁移到合适的欠容分类 + 创建必要子类

SOURCES:
- 148个可直接匹配到现有分类 (通过规则)
- 285个疑难站点 → 根据关键词映射到最合适的欠容类

TARGET MAPPING (prioritize underfilled):
- 学术科研/在线课程 (+81): coursera, udacity, khanacademy…
- 开发工具/文档资源 (+26): docs, gitbook, tech blogs…
- 开发工具/平台开源 (+11): open source projects
- 效率办公/团队协作 (+6): slack, discord pattern matches
- And more…

EXECUTION PLAN:
1. Backup websites.json
2. Re-categorize 148 rule-matched sites
3. Distribute 285 leftover sites to best-fit underfilled categories
4. Atomic write
5. Verify: online_tools < 50, and gap reduction