# 学术成果分享平台（本组仓库）

本仓库用于《软件系统分析与设计》课程“学术成果分享平台”项目。2026-11-18 起进入作业5构件设计阶段，旧阶段材料保留供追踪。

## 关键链接

- 协作小组仓库：[CognitaNexus](https://github.com/CognitaNexus/CognitaNexus)
- 作业5初稿：[构件设计目录](docs/component-design/README.md)
- 本组进度：[当前进度与阶段计划](docs/project-management/current-status.md)（早期记录，具体文件状态以仓库目录为准）
- 本组已完成成果：[现成调研统计报告](docs/research/学术成果分享平台现成调研统计报告.docx)

> 注意：CognitaNexus 的 README 部分内容已经过时。涉及其实际架构、目录、依赖、配置和运行方式时，应以该仓库当前文件结构、配置文件和代码为准，不根据 README 推断。

## 当前状态

- 需求阶段：本组 SRS V0.4、SPEC、需求追踪与图模保存在 `docs/srs/`、`docs/spec/`、`docs/uml/`；共同基线仍为 V1.9。
- 架构阶段：作业4材料保存在 [`docs/architecture/`](docs/architecture/README.md)，ADR 等部分决策尚待两组联合签认。
- 构件阶段：作业5数据库、UI、接口说明书和可打开源文件已形成 [`AI 辅助参考初稿`](docs/component-design/README.md)；尚未与成员在仓库外的交付比对，目标环境验证、两小组对比和签认待完成。

## 当前阶段边界

当前开展作业5构件设计与文件验证。数据库、UI 和接口均为设计稿；接口实现、部署与性能验收属于后续工作。完成状态及未决项见 [`docs/component-design/README.md`](docs/component-design/README.md)。

## 目录

```text
.
├── AGENTS.md                         # 项目级协作与阶段约束
├── CONTRIBUTING.md                   # Git 与评审约定
├── docs/
│   ├── project-management/           # 进度、计划、风险与提交检查
│   ├── research/                     # 本组需求调研成果
│   ├── requirements/                 # 需求基线入口与追溯说明
│   ├── srs/                          # SRS 总稿与模块规格
│   ├── spec/                         # 核心规则 SPEC
│   ├── uml/                          # PlantUML 图源与导出图
│   ├── architecture/                 # 作业4架构设计
│   ├── component-design/             # 作业5构件设计
│   └── reports/                      # 评审、汇报与版本记录
└── tools/                            # 可复现的文档生成工具
```

目录说明反映当前约定；判断实际状态时，以 Git 中现有文件为准。

## 近期节点

- 2026-11-18：形成作业5构件设计初稿。
- 2026-11-25 24:00 前：按课程构件设计提交要求完成两组交叉评审、目标工具验证和独立打包，以教学平台通知为准。

## 依据优先级

1. 课程任务书、课堂展示与提交要求、教师最新通知；
2. 经共同确认的 V1.9 需求基线；
3. SRS 编写与需求建模规范；
4. 调研附录、协作组文档与其他参考材料。

发生冲突时记录依据和影响，交由负责人评审，不擅自修改需求编号或业务语义。
