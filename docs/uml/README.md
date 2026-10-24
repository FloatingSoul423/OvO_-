# UML 图模清单与规范

## 当前必需图

| 建议编号 | 图 | 关键覆盖 |
| --- | --- | --- |
| DGM-USECASE-01 | [系统总体用例图](overall-usecase/DGM-USECASE-01-overall.puml) | 采集管理、门户认领、认领审核、检索查看、统计分析、成果管理及参与者关系 |
| DGM-ACTIVITY-01 | [门户认领审核活动图](claim-activity/DGM-ACTIVITY-01-claim-review.puml) | 提交→验证→审核→补充/通过/驳回→授权与记录 |
| DGM-STATE-01 | [数据采集任务状态图](collection-state/DGM-STATE-01-collection-task.puml) | 待执行、运行中、成功、失败、重试、已停止 |
| DGM-STATE-02 | [认领申请状态图](claim-state/DGM-STATE-02-claim-application.puml) | 待审核、待补充、已通过、已驳回 |

## 局部展开图

| 图号 | 图 | 覆盖 |
| --- | --- | --- |
| DGM-USECASE-02 | [账号与门户管理局部用例图](account-portal/DGM-USECASE-02-account-portal-management.puml) | FR04～FR07、UC-04～UC-08；注册登录、门户认领与审核、门户维护、成果关系维护 |
| DGM-USECASE-03 | [采集与成果治理局部用例图](collection-governance/DGM-USECASE-03-collection-governance.puml) | FR08～FR10、FR15～FR16；采集任务、来源追踪、清洗去重与人工核验 |
| DGM-USECASE-04 | [成果治理与身份消歧局部用例图](governance-identity/DGM-USECASE-04-governance-disambiguation.puml) | 成员 D 补充图；FR09、FR15、UC-08、UC-10 |
| DGM-ACTIVITY-02 | [学者身份与成果归属核验活动图](governance-identity/DGM-ACTIVITY-02-identity-attribution.puml) | 成员 D 补充图；身份候选、人工核验、归属与公开视图同步 |
| DGM-ACTIVITY-03 | [成果清洗与去重治理活动图](governance-cleaning/DGM-ACTIVITY-03-cleaning-dedup.puml) | 成员 D 补充图；字段校验、去重候选、人工合并/拆分及审计 |

成员 D 的 [原始 XMI](codearts/member-d/D_成果治理与身份消歧.xmi)包含两张治理活动图和一张局部用例图；上述三张 PlantUML 图是依据该 XMI 与 SRS 形成的可追踪重绘稿，并非 CodeArts 同次导出，仍需成员复核。它们不能替代必需的门户认领审核活动图。

## 成员图稿

| 图号 | 图稿 | 当前状态 |
| --- | --- | --- |
| DGM-STATE-01 | [数据采集任务状态图](collection-state/README.md) | sxh 已提交原始 CodeArts SVG/PNG，以及按 SRS 补齐的 PlantUML 图源与导出图；CodeArts 原图待同步微调 |
| DGM-STATE-02 | [认领申请状态图](claim-state/README.md) | sxh 已提交 CodeArts XMI、原始导入包，以及按 SRS 补齐的 PlantUML 图源与导出图；CodeArts 状态迁移标注待同步 |
| DGM-USECASE-01 | [系统总体用例图 XMI](codearts/member1/系统总体用例图.xmi) | 成员 1 原件保留；PlantUML 与 SVG/PNG 已补齐。XMI 中两处自指 `extend` 需回 CodeArts 核对关系方向 |
| DGM-USECASE-03 | [采集与成果治理局部用例图 XMI](codearts/member5/采集与成果治理局部用例图.xmi) | 成员 5 原件和截图保留；PlantUML 与 SVG/PNG 已补齐。XMI 中三处自指 `extend` 待核对 |
| DGM-USECASE-02 | [账号与门户管理局部用例图](account-portal/DGM-USECASE-02-account-portal-management.puml) | 成员 4 的 XMI、PlantUML 与 SVG/PNG 已归档 |
| DGM-ACTIVITY-01 | [门户认领审核活动图](claim-activity/README.md) | PlantUML 与 SVG/PNG 已归档；待精修 ZIP 尚未经 CodeArts 导入验证与成员审核 |

[CodeArts 原始导入包清单](codearts/README.md)汇总小组提供的六份基础 ZIP，并区分可导入 ZIP 与 XMI 导出。

## 文件与工具

- 共 9 张 `.puml` 图源均已通过 PlantUML 语法检查，并导出同名 SVG/PNG；SVG/PNG 是本地图源的渲染结果，不冒充 CodeArts 导出；
- 各模块图和导出文件放在同一主题目录，导出图进入 `generated/`；
- 课程提交时另保留 CodeArts Modeling 源文件和导出图；
- PlantUML 与 CodeArts 两套图必须使用相同术语、状态、守卫条件和业务规则；
- 不提交截图拼贴代替图源。

本轮渲染使用 PlantUML 1.2026.8：`java -jar plantuml.jar -charset UTF-8 -tsvg -o generated <图源.puml>`，PNG 将 `-tsvg` 换为 `-tpng`。成员需在 CodeArts 核对原始 XMI 的连线方向、活动图守卫及图文一致性，再重新导出课程最终版。上述状态不等于教师或小组已验收。

认领申请状态与学者门户“未认领/已认领”状态属于不同业务对象，不得混成一个状态机。

## 需求分析作业 3 新增图

|图号|图|负责人|当前状态|
|---|---|---|---|
|DGA-SEQUENCE-01|[数据采集入库时序图](sequence-collection-ingestion/README.md)|宋显涵|PlantUML 图源、SVG/PNG、追踪说明及 CodeArts 精修检查表已完成；CodeArts 平台源文件与正式导出图待完成|

