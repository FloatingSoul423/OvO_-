# 模块 SRS

本目录保存四个功能域和横切非功能需求的 SRS。当前为 V0.2 Draft，已经建立完整基线覆盖，但尚未完成组内签认。

当前文件：

- [01-search-and-portal.md](01-search-and-portal.md)：FR01～FR03；
- [02-account-claim-maintenance.md](02-account-claim-maintenance.md)：FR04～FR07；
- [03-collection-governance.md](03-collection-governance.md)：FR08～FR10、FR15～FR16；
- [04-analytics-admin-innovation.md](04-analytics-admin-innovation.md)：FR11～FR14、IN01；
- [nonfunctional.md](nonfunctional.md)：NF01～NF08。

上述五个文件是模块概览。逐条完整规格位于 [detailed/](detailed/)：107 条功能/创新子需求和 17 条非功能子需求均套用统一模板，包含输入、输出、状态变化、权限/规则、唯一验收条件和关联项。生成工具为 [../../../tools/build_srs_details.py](../../../tools/build_srs_details.py)。

文件范围可按最终人员分工调整，但 FR/IN/NF 编号必须唯一，不得在多个模块中重新定义不同语义。系统总入口与公共规则见 [../OvO-SRS-Draft.md](../OvO-SRS-Draft.md)，独立用例规约见 [../use-case-specifications.md](../use-case-specifications.md)，横切矩阵见 [../cross-cutting-matrices.md](../cross-cutting-matrices.md)，追踪矩阵见 [../traceability-matrix.md](../traceability-matrix.md)。
