
AI Category Migration Strategy - V15

PROBLEM DIAGNOSIS:
==================
AI tools category (AI工具/人工智能) has 329 sites, but only ~1 is a real AI tool.
Root cause: Category import mis-tagged many generic tech resources as "AI".

Current breakdown:
- KEEP (legitimate AI): 1 site
- PURGE (obvious junk): 115 sites (YouTube, SVGs, Wikipedia assets)
- REVIEW (needs re-categorization): 213 sites

REVIEW sites analysis (domain distribution):
- awesome-selfhosted.net (3) - self-hosted software directory
- aws.amazon.com (3) - cloud services
- ceph.com (3) - storage infrastructure
- woodpecker-ci.org (2) - CI/CD
- interviewing.io (2) - interview practice
- pomerium.io (2) - zero-trust network
- cs.yale.edu (2) - university course
- factor.io (2) - data platform
- goauthentik.io (2) - identity management
- msgpack.org (2) - serialization format
- sensu.io (2) - monitoring
- creativecommons.org (2) - licensing
- dokku.com (2) - PaaS
- mahout.apache.org (2) - Apache project
- sourceforge.net (2) - software hosting
- fossil-scm.org (2) - version control
- linuxcontainers.org (2) - containers
- ecyrd.com (2) - software
- airbyte.io (2) - data integration
- Plus 190 more single-occurrence domains

REVIEW SITE CATEGORIZATION:
==========================
These 213 REVIEW sites should be RE-CATEGORIZED (not purged) - they're legitimate
tech resources but in wrong category. Map them to correct categories:

Domain Pattern -> Target Category Mapping:
1. *.edu, *.ac.*, courses, lectures, tutorials
   -> 学术科研/教材 OR 开发工具/文档资源
2. github.com, gitlab.com, gitea.com, selfhosted.net
   -> 开发工具/平台开源/GitHub 或相应子类
3. ci/cd, jenkins, woodpecker, drone, circleci, travis
   -> 开发工具/CI/CD服务
4. cloud providers (aws, gcp, azure, oraclecloud, digitalocean)
   -> 开发工具/云开发平台
5. infrastructure (ceph, dokku, kubernetes, docker)
   -> 系统工具/服务器管理
6. documentation (readthedocs, docs., manual, guide)
   -> 开发工具/文档资源
7. monitoring/logging (sensu, prometheus, grafana)
   -> 开发工具/监控告警
8. databases (mongodb, postgresql, mysql)
   -> 开发工具/数据库
9. security/auth (pomerium, authentik, keycloak)
   -> 系统工具/网络安全
10. serialization/format libraries (msgpack, protocolbuffers)
    -> 开发工具/库
11. archiving (archive.org, backup systems)
    -> 系统工具/备份工具
12. interview practice (interviewing.io)
    -> 效率办公/面试技巧 OR 开发工具/在线工具
13. graphs/diagrams (kroki, plantuml, excalidraw)
    -> 设计工具/流程图生成
14. Other (single-use domains) - need individual review

IMPLEMENTATION PLAN:
====================
Phase 1: Apply AUTO-PURGE (123 sites) - SAFE, clear junk
  - This reduces AI from 329 → 206
  - Immediate balance improvement

Phase 2: Smart Re-categorization of REVIEW sites (205 sites)
  - Use domain-based mapping rules
  - Batch move to appropriate categories
  - Will reduce AI to ~50-70 sites

Phase 3: Final AI category split
  - After cleanup, AI category will be <100 sites
  - May not need further split if under 50
  - If still >50, split into subcategories like:
    * AI工具/人工智能/LLM平台
    * AI工具/人工智能/图像生成
    * AI工具/人工智能/代码助手
    * etc.

EXPECTED OUTCOME:
=================
Initial state: AI category = 329 sites (329 > 50 limit)
After Phase 1 purge: 206 sites
After Phase 2 migration: ~55-65 sites
After Phase 3 (split if needed): each subcategory 15-25 sites

Balance impact:
- Overfilled categories reduced by 1 (AI no longer overfilled)
- Underfilled categories naturally filled as migrated sites join appropriate small classes
- Projected balance degree: 30-40% (significant improvement from 18%)

NEXT STEPS:
===========
1. Execute Phase 1: Run purge_ai_category.py with --force
2. Execute Phase 2: Run migrate_ai_review_sites.py with dry-run first
3. Verify: recalibrate balance_check.py
4. Document changes in V15 progress report
