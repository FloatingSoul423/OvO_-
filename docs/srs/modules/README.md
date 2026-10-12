# 模块 SRS

本目录保存四个功能域和横切非功能需求。当前为V0.3提交评审稿，模块文件只保留编号索引，完整行为与AC只在详细分册定义。

当前文件：

- [01-search-and-portal.md](01-search-and-portal.md)：FR01～FR03；
- [02-account-claim-maintenance.md](02-account-claim-maintenance.md)：FR04～FR07；
- [03-collection-governance.md](03-collection-governance.md)：FR08～FR10、FR15～FR16；
- [04-analytics-admin-innovation.md](04-analytics-admin-innovation.md)：FR11～FR14、IN01；
- [nonfunctional.md](nonfunctional.md)：NF01～NF08。

逐条完整规格位于 [detailed/](detailed/)：107条功能/创新和17条非功能均有独立场景、输入输出、状态、权限规则、验收和关联。场景内容维护在tools/srs_cases.py，排版工具为 [../../../tools/build_srs_review.py](../../../tools/build_srs_review.py)，不再通过父需求通用流程扩写。

文件范围可按最终人员分工调整，但 FR/IN/NF 编号必须唯一，不得在多个模块中重新定义不同语义。系统总入口与公共规则见 [../OvO-SRS-Draft.md](../OvO-SRS-Draft.md)，独立用例规约见 [../use-case-specifications.md](../use-case-specifications.md)，横切矩阵见 [../cross-cutting-matrices.md](../cross-cutting-matrices.md)，追踪矩阵见 [../traceability-matrix.md](../traceability-matrix.md)。
