# DGM-STATE-01 数据采集任务状态图

- [PlantUML 图源](DGM-STATE-01-collection-task.puml)及其 [SVG](generated/DGM-STATE-01-collection-task.svg)、[PNG](generated/DGM-STATE-01-collection-task.png)：按 SRS V0.3 状态登记表 2.5 补全触发条件与“待执行→已停止”迁移。导出命令需指定 `-charset UTF-8`。
- `generated/数据采集任务状态图.svg`、`.png`：成员 sxh 提供的 CodeArts 导出原图，原样保存，作为后续微调的基础版本。

原导出图未标注迁移条件，且缺少“待执行→已停止”。因此原图与当前 PlantUML 图源并非最终一致版；后续须在建模工具中同步修改并重新导出。对应的可编辑 CodeArts 源文件（XMI）此次未提供，不能把 SVG/PNG 当作建模源文件。

本成员分工中的 `DGM-STATE-02` 认领申请状态图仍待导出；仓库 `tools/build_codearts_remaining.py` 含其基础版本生成逻辑。
