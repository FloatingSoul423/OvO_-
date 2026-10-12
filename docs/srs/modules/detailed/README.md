# 逐条详细规格

本目录是SRS V0.3逐条规范层。tools/srs_cases.py保存每条单独编写的场景，tools/build_srs_review.py负责统一排版；尚待成员复核签认，不宣称已人工评审。公共术语、字段、状态和BR集中定义，每条引用适用项。

| 分册 | 覆盖 | 子需求数 |
|---|---|---:|
| [检索、成果详情与学者门户](01-search-and-portal-detailed.md) | FR01～FR03 | 19 |
| [账号、认领与维护](02-account-claim-maintenance-detailed.md) | FR04～FR07 | 24 |
| [采集、治理、更新与追踪](03-collection-governance-detailed.md) | FR08～FR10、FR15～FR16 | 34 |
| [统计、管理与合作探索](04-analytics-admin-innovation-detailed.md) | FR11～FR14、IN01 | 30 |
| [非功能需求](nonfunctional-detailed.md) | NF01～NF08 | 17 |

合计 124 条，其中功能/创新子需求 107 条，非功能子需求 17 条。每条均包含参与者、前置/触发、输入、输出、状态变化、权限、业务规则、主/备选/异常流程、至少一个唯一验收条件和关联项。
