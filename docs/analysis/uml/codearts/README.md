# CodeArts 正式模型归档

更新：2026-10-25。本目录只保存组员从华为云 CodeArts Modeling 导出的正式源文件及与其配套的导出图；`../generated/` 中同名文件仍是 PlantUML 本地预览，两者不得混称。

|模型|CodeArts 源文件|正式导出图|状态|
|---|---|---|---|
|DGA-CLASS-01 核心业务类图|`DGA-CLASS-01-core-business.xmi`|`generated/DGA-CLASS-01-core-business.png`|已归档；待组内图文一致性签认|
|DGA-SEQUENCE-03 检索请求处理时序图|`DGA-SEQUENCE-03-search-request.xmi`|`generated/DGA-SEQUENCE-03-search-request.png`|已归档；待组内图文一致性签认|

数据采集入库时序图的正式 XMI 位于 `../../../uml/sequence-collection-ingestion/codearts/DGA-SEQUENCE-01-collection-ingestion.xmi`。门户认领审核时序图当前仅有 `../DGA-SEQUENCE-02-claim-review.puml` 及本地渲染图，尚未收到 CodeArts XMI 和正式导出图。

## 核验规则

1. XMI 必须能被 XML 解析器读取，根元素为 `xmi:XMI`，模型名称与图名一致。
2. 正式导出图必须与同一版本 XMI 配套，人物、生命线、消息、类、关系、多重性和组合片段不得靠后期图片编辑补写。
3. 最终提交前由模型负责人和一名交叉复核人对照 SRS/用例逐项签认；“已归档”不等于“已验收”。
