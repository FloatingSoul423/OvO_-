# CodeArts Modeling 原始材料清单

`import-packages/` 保存小组提供的六份原始 CodeArts 导入 ZIP，按成员编号和图名原样命名，不在仓库内重写其内容。这些是共同基础版本，不代表六张图均已完成或通过 SRS 一致性检查。

| 成员 | 基础导入包 | 对应图 |
| --- | --- | --- |
| 1 | `OvO_member1_overall_usecase_codearts_20261012.zip` | 总体用例图 |
| 2 | `OvO_member2_claim_activity_codearts_20261012.zip` | 认领审核活动图 |
| 3 | `OvO_member3_claim_state_codearts_20261012.zip` | 认领申请状态图 |
| 3 | `OvO_member3_collection_state_codearts_20261012.zip` | 采集任务状态图 |
| 4 | `OvO_member4_account_portal_codearts_20261012(1).zip` | 账号与门户管理局部用例图 |
| 5 | `OvO_member5_collection_governance_usecase_codearts_20261012.zip` | 采集与成果治理局部用例图 |

`member3/` 保存 sxh 已编辑并导出的两份 XMI，均按用户提供的原文件原样归档。XMI 可用于核对状态和迁移；若要回到华为云继续编辑，应使用对应 ZIP。最终展示图应与 SRS、PlantUML 图源及 CodeArts 模型同步，不能用此清单代替一致性检查。

## 后续成员导出（2026-10-13）

| 成员 | 已归档文件 | 备注 |
| --- | --- | --- |
| 1 | [系统总体用例图.xmi](member1/系统总体用例图.xmi) | 用户提供的 CodeArts XMI 原样保存；尚无同次导出的图片 |
| 4 | [成员4-账号与门户管理局部用例图.xmi](成员4-账号与门户管理局部用例图.xmi) | 先前已入库，另有 PlantUML 图源与 PNG |
| 5 | [采集与成果治理局部用例图.xmi](member5/采集与成果治理局部用例图.xmi) | 用户提供的 CodeArts XMI 原样保存；[截图](../collection-governance/generated/采集与成果治理局部用例图.png)仅作视觉预览 |
| D（来稿标签） | [D_成果治理与身份消歧.xmi](member-d/D_成果治理与身份消歧.xmi) | 2026-10-13 收到并原样归档；内含“学者身份与成果归属核验”“成果清洗与去重治理”两张活动图，以及“成果治理与身份消歧”局部用例图；不等同于成员 2 的门户认领审核活动图 |

成员 2 的原始基础导入 ZIP 仍原样保留。另新增 [门户认领审核活动图待精修 ZIP](member2/OvO_member2_claim_activity_refinement.zip)：基于该基础包的结构和模板在本地重建，可供 CodeArts 导入尝试；已有对应 [PlantUML 图源及预览](../claim-activity/README.md)。该 ZIP 尚未在 CodeArts 实测导入，也不是成员正式编辑后的 XMI 或华为云导出图。XMI 与 ZIP 不应视为同一交付物。上述图件仍需与 SRS 的参与者、用例关系及业务规则逐项核对。

初步 XML 检查显示：成员 1 的总体图有 2 处、成员 5 的局部图有 3 处 `extend` 的 `extendedCase` 与 `extension` 指向同一用例。原始 XMI 未改动；需回到 CodeArts 确认关系方向，并重新导出后再作为最终模型。

本地已为总体用例、采集治理局部用例及成员 D 的三张补充图编写独立的 PlantUML 重绘稿，并生成 SVG/PNG，见[图模总索引](../README.md)。重绘稿用于版本管理和评审对照，不是从 XMI 一键无损转换，更不能证明已在华为云完成导入、修正或最终导出。
