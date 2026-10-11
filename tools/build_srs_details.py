"""Expand the reviewed SRS overview tables into full per-subrequirement specifications.

The compact module files remain the human-readable overview. This generator produces
the detailed, field-complete layer and keeps repeated context centralized by domain.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRS = ROOT / "docs" / "srs"
MODULES = SRS / "modules"
DETAILS = MODULES / "detailed"


def meta(mode, actors, related, pre, trigger, data, result, state, permission, rules, uc, nf, objects, diagram):
    return {
        "mode": mode,
        "actors": actors,
        "related": related,
        "pre": pre,
        "trigger": trigger,
        "data": data,
        "result": result,
        "state": state,
        "permission": permission,
        "rules": rules,
        "uc": uc,
        "nf": nf,
        "objects": objects,
        "diagram": diagram,
    }


META = {
    "FR01": meta("read", "访客", "无", "平台存在可公开检索的数据；查询条件可被解析", "访客提交关键词、筛选、排序或分页操作", "关键词、检索范围、类型、年份、领域、机构、数据性质、排序及分页", "与条件一致的去重结果、总量、分页和明确反馈", "不改变业务对象状态", "公开能力无需登录；只返回公开版本", "BR-01、BR-12、BR-14、BR-17", "UC-01", "NF01、NF02、NF04", "Achievement、Scholar、Organization、Field", "DGM-USECASE-01"),
    "FR02": meta("read", "访客", "无", "目标成果实体存在且允许公开", "访客打开成果详情或来源入口", "成果标识、公共字段、类型专属字段、参与关系、来源及版本证据", "当前公开详情、来源、更新时间、数据性质及可用导航", "不改变成果状态；仅记录访问不属于本期需求", "访客不能查看待审版本和内部治理证据", "BR-01、BR-05、BR-07、BR-17、BR-19", "UC-02", "NF01、NF03、NF04、NF06", "Achievement、SourceRecord、ScholarAchievementRelation", "DGM-USECASE-01"),
    "FR03": meta("read", "访客", "登录用户（仅认领入口）", "目标学者档案存在且未限制公开", "访客打开学者门户或筛选门户成果", "学者标识、公开简介、机构、领域、认领状态、成果关系和筛选条件", "门户公开版本、分类成果、收录范围和关系状态说明", "不改变档案或认领状态", "公开浏览无需登录；管理操作须另行授权", "BR-01、BR-02、BR-03、BR-05、BR-09、BR-19", "UC-03", "NF01、NF03、NF05、NF06", "Scholar、Achievement、ScholarAchievementRelation", "DGM-USECASE-01"),
    "FR04": meta("write", "访客、登录用户", "管理员", "账号输入满足最小要求；受保护操作具有可验证登录状态", "用户注册、登录、退出或发起受保护操作", "账号标识、凭据、账号状态、角色、目标对象和操作类型", "账号操作结果、登录状态或明确的拒绝原因", "账号可由未注册变为有效；登录状态建立/失效；停用不删除档案", "每次受保护操作同时校验角色和对象级授权", "BR-02、BR-03、BR-18", "UC-04", "NF01、NF03、NF06", "UserAccount、Authorization、AuditLog", "DGM-USECASE-01"),
    "FR05": meta("review", "登录用户、管理员", "门户管理者（已有授权冲突时）", "用户已登录且目标学者档案存在", "用户提交/补充认领申请或管理员作出审核决定", "目标档案、本人声明、必要证明、申请状态、审核意见和冲突信息", "可查询的申请状态、决定原因及通过后的对象级授权", "申请在待审核、待补充、已通过、已驳回间合法转移；门户授权仅在通过后新增", "材料仅申请人和审核管理员可见；冲突不自动转移授权", "BR-01、BR-03、BR-04、BR-18、BR-19", "UC-05、UC-06", "NF01、NF03、NF05、NF06", "ClaimRequest、Scholar、PortalAuthorization、AuditLog", "DGM-USECASE-01、DGM-ACTIVITY-01、DGM-STATE-02"),
    "FR06": meta("review", "门户管理者", "管理员", "用户对目标门户具有有效对象级授权", "门户管理者提交信息或展示设置变更", "门户标识、当前公开版本、修改字段、展示设置、提交原因和版本信息", "直接生效或待审的变更结果、当前公开版本和处理记录", "公开版本仅在允许直接生效或审核通过后变化", "仅目标门户管理者可提交；重要公开字段按规则审核", "BR-03、BR-05、BR-18", "UC-07", "NF01、NF03、NF05、NF06", "Scholar、PortalProfile、ChangeRequest、AuditLog", "DGM-USECASE-01"),
    "FR07": meta("review", "门户管理者、管理员", "系统", "用户对目标门户具有授权；成果或来源可识别", "用户确认候选、补录已有成果或提交纠错", "门户、成果、关系、操作类型、来源证据、修改内容和理由", "确认/补录/纠错申请状态及审核通过后的公开结果", "成果关系或公开字段仅在规则允许或审核通过后改变", "本人只能处理自身门户关系；共享成果和他人关系受保护", "BR-03、BR-05、BR-06、BR-07、BR-08、BR-09、BR-10、BR-18、BR-19", "UC-08", "NF01、NF03、NF04、NF05、NF06", "Achievement、ScholarAchievementRelation、ChangeRequest、SourceRecord", "DGM-USECASE-01"),
    "FR08": meta("ingest", "管理员", "外部数据来源、系统", "来源已登记且使用条件允许；管理员具备采集权限", "管理员创建、启动、停止或重试采集任务", "来源、数据类型、采集范围、输入标识、调度参数和任务控制命令", "任务状态、进度、处理摘要、失败原因和历史记录", "任务在待执行、运行中、成功、失败、重试、已停止间合法转移", "只有采集管理员可控制任务；不得绕过来源访问控制", "BR-07、BR-11、BR-18", "UC-09", "NF03、NF04、NF07", "DataSource、CollectionTask、SourceRecord、AuditLog", "DGM-USECASE-01、DGM-STATE-01"),
    "FR09": meta("ingest", "系统、管理员", "无", "存在待处理来源记录；规则版本可识别", "系统处理记录或管理员处置候选/异常", "原始记录、规范化值、稳定标识、标题、时间、参与者、类型和来源证据", "新建、合并、版本关联、候选、异常或人工处置结果及证据链", "来源记录由待处理进入已处理/待核验；成果可合并或经审计拆分", "自动规则不得越过人工核验边界；管理员决定须留痕", "BR-07、BR-08、BR-10、BR-12、BR-18", "UC-10", "NF04、NF05、NF07、NF08", "SourceRecord、Achievement、DedupCandidate、VersionRelation、AuditLog", "DGM-USECASE-01"),
    "FR10": meta("ingest", "系统、管理员", "外部数据来源", "来源已有历史记录或版本游标；本次结果可识别", "定时/人工更新开始或管理员恢复失败批次", "来源记录、历史版本、变更差异、人工值保护标记和恢复检查点", "新增/未变/变更/删除声明分类、处理结果和传播状态", "来源版本和公开版本按审核规则变化；失败批次可恢复", "管理员可查看和恢复；自动更新不能覆盖人工结果", "BR-05、BR-07、BR-10、BR-18", "UC-09", "NF04、NF05、NF07、NF08", "SourceRecord、UpdateBatch、ChangeRequest、AuditLog", "DGM-USECASE-01、DGM-STATE-01"),
    "FR11": meta("analysis", "访客", "系统", "存在已生效且满足统计条件的数据；统计口径可披露", "访客选择统计主题、范围或筛选条件", "成果类型、年份、领域、机构、数据性质、统计版本和筛选条件", "分布、机构分类排名、口径、更新时间和可复核范围", "不改变业务对象；统计版本可由旧版更新为新版", "公开统计只使用允许公开且满足口径的数据", "BR-12、BR-13、BR-14、BR-16、BR-17", "UC-11", "NF01、NF02、NF04、NF05", "Achievement、Organization、Field、MetricSnapshot", "DGM-USECASE-01"),
    "FR12": meta("analysis", "访客", "系统", "公开论文作者关系已生效且学者身份可区分", "访客选择学者或合作网络范围", "学者、共同论文、领域/机构范围、关系强度口径和网络规模限制", "带论文证据的节点、边、强度说明和可导航对象", "不改变关系；网络视图随已生效关系更新", "只展示公开学者与公开论文证据", "BR-09、BR-12、BR-15、BR-16、BR-17", "UC-12", "NF01、NF02、NF04、NF05", "Scholar、Paper、CoauthorRelation、MetricSnapshot", "DGM-USECASE-01"),
    "FR13": meta("analysis", "访客", "系统", "所选领域和时间窗口内存在可统计字段", "访客选择领域、时间窗口或热点指标", "领域、时间范围、关键词/主题、归一规则、数据性质和统计版本", "热点排名/趋势、指标解释、数据范围、更新时间和不足提示", "不改变成果；热点快照可更新", "仅公开聚合结果；指标不得解释为质量认证", "BR-12、BR-14、BR-16、BR-17", "UC-13", "NF01、NF02、NF04、NF05", "Achievement、Field、TopicTerm、MetricSnapshot", "DGM-USECASE-01"),
    "FR14": meta("review", "管理员", "系统", "管理员已登录并具有目标管理能力", "管理员进入工作台、筛选队列或处理对象", "任务、异常、申请、关系、分类、账号、来源配置、处理意见和版本", "待办摘要、处理结果、失败反馈和可查询审计", "对应业务对象按其状态机变化；审计记录追加且不可被普通操作覆盖", "非管理员及无对应权限者拒绝；敏感材料受控", "BR-01、BR-03、BR-04、BR-05、BR-18、BR-19", "UC-06、UC-10、UC-14", "NF01、NF03、NF04、NF05、NF06、NF07、NF08", "AdminQueue、AuditLog、UserAccount、ClaimRequest、ChangeRequest", "DGM-USECASE-01"),
    "FR15": meta("review", "系统、管理员", "相关门户管理者", "存在学者候选、外部身份线索或成果参与者记录", "系统进行身份匹配或相关人员请求核验/纠正", "姓名/别名、机构、外部标识、领域、合作者、成果角色、顺序和证据", "同一/不同/待核验判定、带证据的成果关系及传播结果", "候选可转为确认/排除；误合并可拆分；公开关系仅在生效后变化", "自动规则证据不足时不得决定；人工纠正须审计", "BR-02、BR-03、BR-04、BR-05、BR-06、BR-09、BR-18、BR-19", "UC-08、UC-10", "NF03、NF04、NF05、NF06、NF07、NF08", "Scholar、IdentityCandidate、ScholarAchievementRelation、AuditLog", "DGM-USECASE-01"),
    "FR16": meta("ingest", "系统、管理员、访客", "外部数据来源", "数据来自获准来源或明确标识的模拟数据", "四类记录进入平台或用户查看其来源与类型字段", "成果类型、公共/专属字段、来源、时间、数据性质和去重计数", "四类可查询成果、完整来源追踪、数据性质和可复核总量", "来源记录进入已收录/异常；来源不可用不删除历史成果", "管理员管理来源；访客只查看公开字段", "BR-07、BR-12、BR-17", "UC-02、UC-09、UC-10", "NF01、NF04、NF05、NF06、NF07、NF08", "Achievement、Paper、Patent、Project、Award、SourceRecord", "DGM-USECASE-01、DGM-STATE-01"),
    "IN01": meta("analysis", "访客", "系统", "两名目标学者可公开且已消歧；合作关系已生效", "访客筛选网络或提交两学者路径查询", "起点、终点、领域、机构、共同论文图和路径展示范围", "最短合作路径、逐跳论文证据、无路径/节点异常反馈", "不改变合作关系；结果随已生效关系更新", "仅使用公开共同论文；创新功能不阻断基础功能", "BR-13、BR-15、BR-16、BR-17、BR-20", "UC-15", "NF01、NF02、NF04、NF05", "Scholar、Paper、CoauthorRelation、PathResult", "DGM-USECASE-01"),
}


NF_META = {
    "NF01": meta("nf", "访客及所有交互角色", "系统", "适用功能可访问", "用户执行公开或受保护交互", "交互步骤、状态和表单输入", "可理解、可继续操作的反馈", "不规定业务状态变化", "受保护操作仍须鉴权", "BR-01、BR-03", "适用 UC", "NF01", "用户界面状态", "无"),
    "NF02": meta("nf", "性能测试人员", "系统", "测试目标、环境、数据量和查询集已经记录", "执行固定负载测试", "数据规模、并发、查询集、预热、时长和硬件", "P95、错误率及完整测试记录", "不改变业务状态", "仅授权测试环境执行", "待评审性能目标", "UC-01、UC-11～UC-15", "NF02", "PerformanceTestResult", "无"),
    "NF03": meta("nf", "所有角色", "安全测试人员", "角色、对象授权和受控材料样例已准备", "访问受保护对象或执行受保护操作", "身份、角色、目标对象、操作和材料", "允许或拒绝结果及安全审计摘要", "授权状态按业务审核变化", "角色与对象级授权必须同时满足", "BR-01、BR-03、BR-18", "UC-04～UC-10、UC-14", "NF03", "Authorization、AuditLog", "无"),
    "NF04": meta("nf", "管理员、访客", "系统", "来源中断、失败任务或备份样例可复现", "发生依赖故障、恢复任务或执行恢复核验", "历史数据、任务检查点、备份范围和失败信息", "持续可浏览、可恢复且不重复的结果", "失败任务可进入重试；业务数据按恢复点还原", "恢复操作限管理员", "BR-07、BR-10、BR-11", "UC-02、UC-09", "NF04", "CollectionTask、BackupSet、SourceRecord", "DGM-STATE-01"),
    "NF05": meta("nf", "系统、管理员", "测试人员", "存在可生效的审核或更新样例", "业务变更生效并开始一致性检查", "变更标识、各视图版本、时间戳和审计信息", "一致视图或明确的未同步/失败提示", "变更由待审到生效并传播", "审计数据受控", "BR-05、BR-10、BR-18", "UC-07～UC-15", "NF05", "ChangeRequest、AuditLog、IndexView、MetricSnapshot", "无"),
    "NF06": meta("nf", "所有角色", "数据管理员", "数据字段和材料分类已明确", "数据采集、展示、审核材料访问或清理", "字段分类、公开范围、保留条件和数据性质", "最小化采集、受控访问、按规则清理和明确标识", "材料可由有效转为到期/已清理", "敏感信息仅最小授权访问", "BR-01、BR-17", "UC-02～UC-10、UC-14", "NF06", "SensitiveData、ClaimEvidence、SourceRecord", "无"),
    "NF07": meta("nf", "维护人员、管理员", "新成员", "文档、配置和来源样例可用", "新增/停用来源或定位失败", "来源配置、运行记录、故障信息和维护文档", "不改变用户语义的来源变更和可执行说明", "来源可启用/停用；用户业务对象不随之删除", "配置仅管理员维护", "BR-07、BR-10", "UC-09、UC-14", "NF07", "DataSource、MaintenanceDocument", "无"),
    "NF08": meta("nf", "开发与测试人员", "评审人员", "进入实现阶段且核心模块/需求映射已确定", "执行测试、检查或追踪抽查", "需求、SPEC、代码变更、测试、覆盖率和流水线证据", "可复核的覆盖率、测试结果和端到端追踪", "不定义业务状态", "工程证据按团队权限维护", "规范驱动开发与课程工程要求", "全部核心 UC", "NF08", "TraceLink、TestResult、PipelineEvidence", "无"),
}


INPUTS = [
    ("01-search-and-portal.md", "01-search-and-portal-detailed.md", "详细规格一：检索、成果详情与学者门户"),
    ("02-account-claim-maintenance.md", "02-account-claim-maintenance-detailed.md", "详细规格二：账号、认领与维护"),
    ("03-collection-governance.md", "03-collection-governance-detailed.md", "详细规格三：采集、治理、更新与追踪"),
    ("04-analytics-admin-innovation.md", "04-analytics-admin-innovation-detailed.md", "详细规格四：统计、管理与合作探索"),
    ("nonfunctional.md", "nonfunctional-detailed.md", "详细规格五：非功能需求"),
]

CRITICAL = {
    "FR01-S01", "FR01-S02", "FR02-S03", "FR03-S04", "FR04-S03",
    "FR05-S04", "FR05-S05", "FR05-S06", "FR07-S05", "FR07-S06",
    "FR08-S04", "FR08-S06", "FR09-S03", "FR09-S04", "FR09-S08",
    "FR10-S04", "FR10-S05", "FR10-S06", "FR11-S03", "FR11-S05",
    "FR12-S02", "FR12-S03", "FR13-S05", "FR14-S05", "FR14-S06",
    "FR15-S02", "FR15-S07", "FR15-S08", "FR16-S04", "FR16-S05",
    "IN01-S03", "IN01-S04", "IN01-S05", "NF02-S01", "NF03-S02",
    "NF04-S01", "NF05-S01", "NF06-S01", "NF08-S01",
}


def existing_ac_max():
    """Reserve AC numbers already used by the compact overview layer."""
    maxima = {}
    pattern = re.compile(r"AC-((?:FR|NF)\d{2}|IN01-S\d{2}|(?:FR|NF)\d{2}-S\d{2})-(\d{2})")
    for source_name, _, _ in INPUTS:
        text = (MODULES / source_name).read_text(encoding="utf-8")
        for requirement, number in pattern.findall(text):
            maxima[requirement] = max(maxima.get(requirement, 0), int(number))
    return maxima


EXISTING_AC_MAX = existing_ac_max()


def parse_rows(path: Path):
    rows = []
    pattern = re.compile(r"^(FR\d{2}|IN01|NF\d{2})-S\d{2}$")
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in raw.strip().strip("|").split("|")]
        if len(cells) >= 2 and pattern.match(cells[0]):
            rows.append((cells[0], re.sub(r"\s+", " ", cells[1]).rstrip("。")))
    return rows


def flow(meta, title):
    mode = meta["mode"]
    if mode == "read":
        return [
            f"参与者进入对应功能并提出“{title}”请求。",
            "系统校验目标对象的公开状态与输入条件。",
            f"系统依据适用业务规则读取当前有效数据，执行“{title}”。",
            "系统对结果去重并附带必要的范围、状态或来源说明。",
            "系统返回可观察结果；无匹配数据时进入备选流程。",
        ]
    if mode == "analysis":
        return [
            f"参与者选择分析对象和范围，发起“{title}”。",
            "系统校验范围、时间窗口、数据性质和统计版本。",
            "系统按已声明口径筛选已生效数据并执行聚合或关系计算。",
            f"系统生成“{title}”结果，同时附带口径、范围、更新时间和证据入口。",
            "参与者查看结果或调整条件重新计算。",
        ]
    if mode == "ingest":
        return [
            f"管理员或系统发起“{title}”。",
            "系统检查来源条件、权限、输入标识和当前处理状态。",
            "系统校验输入并保留原始值、来源和处理上下文。",
            f"系统按照业务规则执行“{title}”，区分成功、候选、异常或失败。",
            "系统保存结果、证据链和可恢复信息，必要时更新业务状态。",
            "系统返回处理摘要；管理员可定位失败或待核验项。",
        ]
    if mode == "review":
        return [
            f"有权限的参与者发起“{title}”并提交必要信息。",
            "系统校验身份、对象级授权、对象当前版本和输入完整性。",
            "系统展示当前公开值、申请值及适用证据，避免隐式覆盖。",
            f"系统或管理员按规则处理“{title}”，产生明确决定。",
            "仅满足生效条件的结果更新公开业务状态；其他结果保持原状态。",
            "系统记录操作者、时间、原因、前后值并反馈处理结果。",
        ]
    if mode == "nf":
        return [
            f"评审人员准备与“{title}”对应的可复现实验或检查样例。",
            "记录前置环境、数据范围、角色、操作步骤和预期结果。",
            f"执行“{title}”验证，采集可观察结果和失败证据。",
            "将实际结果与验收条件比较，不以未执行或局部结果代替通过。",
            "保存结论、限制和需要改进的事项。",
        ]
    return [
        f"参与者发起“{title}”。",
        "系统校验身份、权限、输入完整性和当前状态。",
        f"系统执行“{title}”并产生明确结果。",
        "系统保存必要状态与审计信息并向参与者反馈。",
    ]


def alternative(meta):
    return {
        "read": ["A1：没有匹配数据时返回空结果及调整条件入口，不把空结果描述为系统失败。", "A2：部分字段未知时显示未知/来源未提供，不推测补全。"],
        "analysis": ["A1：样本不足时显示不足说明和当前范围，不生成误导性排名或路径。", "A2：存在多种展示结果时采用已声明的确定规则，并允许收窄范围。"],
        "ingest": ["A1：证据不足或存在冲突时进入候选/异常队列，不强制自动决定。", "A2：重复输入按幂等规则处理，保留本次任务记录但不重复创建业务实体。"],
        "review": ["A1：需要补充或重新核验时保持当前公开结果，记录待办和原因。", "A2：申请被驳回时不改变原业务授权或公开版本，并向申请人返回原因。"],
        "nf": ["A1：环境或样例不满足前置条件时结论记为未执行/不可判定，不记为通过。", "A2：仅部分场景通过时分别记录，不用平均结果掩盖失败项。"],
        "write": ["A1：输入可修正时指出具体字段并保留其他合法内容。", "A2：操作无需改变业务状态时只返回结果，不创建虚假状态。"],
    }[meta["mode"]]


def exceptions(meta):
    common = [
        "E1：输入无效、对象不存在或状态不允许时拒绝操作，指出可修正原因。",
        "E2：依赖失败或处理超时时返回失败/未完成状态，不伪装成无结果或成功。",
        "E3：并发版本已变化时不覆盖新结果，要求刷新后重新判断。",
    ]
    if meta["mode"] in {"write", "review", "ingest"}:
        common.append("E4：权限不足时拒绝操作，业务数据保持不变，并记录必要的安全或审计摘要。")
    return common


def acceptance(req_id, title, meta):
    actor = meta["actors"].split("、")[0]
    first_pre = meta["pre"].split("；")[0]
    first_number = EXISTING_AC_MAX.get(req_id, 0) + 1
    items = [
        f"AC-{req_id}-{first_number:02d}：Given {first_pre}，When {actor}执行本条操作，Then 可观察结果必须满足“{title}”，并返回“{meta['result']}”中与本条相关的结果；不满足该行为即判定失败。"
    ]
    if req_id in CRITICAL:
        second_number = first_number + 1
        if meta["mode"] == "analysis":
            items.append(f"AC-{req_id}-{second_number:02d}：Given 固定且可手工核对的数据样例，When 重复执行“{title}”，Then 结果应符合已声明口径，并显示范围、证据或更新时间。")
        elif meta["mode"] == "ingest":
            items.append(f"AC-{req_id}-{second_number:02d}：Given 同一输入被重复处理或执行中断后重试，When 再次执行“{title}”，Then 不得产生重复业务实体，失败与恢复范围应可追踪。")
        elif meta["mode"] in {"write", "review"}:
            items.append(f"AC-{req_id}-{second_number:02d}：Given 操作者无目标对象权限或对象版本已变化，When 尝试执行“{title}”，Then 系统应拒绝覆盖，保持原业务结果并给出可理解原因。")
        elif meta["mode"] == "nf":
            items.append(f"AC-{req_id}-{second_number:02d}：Given 验证环境或证据不满足约定条件，When 评审本条要求，Then 结论必须标记为未执行或不通过，不得宣称已经满足。")
        else:
            items.append(f"AC-{req_id}-{second_number:02d}：Given 目标数据不存在、不可公开或输入边界无效，When 执行“{title}”，Then 系统应给出明确反馈且不得泄露受控信息或伪造结果。")
    return items


def render_requirement(req_id, title, meta):
    parent = req_id.split("-S")[0]
    alternate_text = " ".join(alternative(meta))
    exception_text = " ".join(exceptions(meta))
    lines = [
        f"## {req_id} {title}",
        "",
        f"- **父需求/优先级：** {parent} / {'Innovation' if parent == 'IN01' else ('Non-functional' if parent.startswith('NF') else 'Must')}",
        f"- **主要/相关参与者：** {meta['actors']} / {meta['related']}",
        "",
        "### 规格字段",
        "",
        "| 字段 | 规格 |",
        "|---|---|",
        f"| 需求描述 | 系统应满足以下要求：{title}；遵守本分册公共上下文和 {meta['rules']}，不得通过未声明的实现假设改变需求语义。 |",
        f"| 前置条件 | {meta['pre']}；适用规则、公开范围和当前版本可识别。 |",
        f"| 触发条件 | {meta['trigger']}，且本条能力被调用。 |",
        f"| 输入/业务数据 | {meta['data']}；当前对象版本、数据公开范围和适用规则版本。 |",
        f"| 输出/可观察结果 | {meta['result']}；失败、无结果、待处理或权限不足须与成功明确区分。 |",
        f"| 状态变化 | {meta['state']}；无状态变化时保持原状态，不创建伪状态。 |",
        f"| 权限规则 | {meta['permission']}；界面隐藏不替代角色和对象级鉴权。 |",
        f"| 业务规则 | {meta['rules']}；冲突时进入评审，不在本条私自重定义。 |",
        f"| 备选流程 | {alternate_text} |",
        f"| 异常流程 | {exception_text} |",
        "",
        "### 主成功流程",
        "",
    ]
    lines.extend(f"{i}. {step}" for i, step in enumerate(flow(meta, title), 1))
    lines += ["", "### 验收条件", ""]
    lines.extend(f"- {x}" for x in acceptance(req_id, title, meta))
    lines += [
        "",
        "### 关联项",
        "",
        f"- **用例：** {meta['uc']}；**非功能需求：** {meta['nf']}；**数据对象：** {meta['objects']}；**关联图：** {meta['diagram']}（图模任务完成后核对）。",
        "",
    ]
    return lines


def generate_detail(source_name, output_name, title):
    rows = parse_rows(MODULES / source_name)
    lines = [
        f"# {title}",
        "",
        "> 状态：V0.2 Draft｜生成依据：V1.9、模块概览和公共规则｜所有条目须经人工评审后冻结",
        "",
        "## 公共说明",
        "",
        "本分册逐条采用统一 SRS 模板。为避免重复，术语、参与者定义、BR-01～BR-20 和 UC 注册表以 `../../OvO-SRS-Draft.md` 为公共真源；每条仍显式给出适用角色、条件、流程、数据、状态、权限、规则、验收与关联项。实现技术不属于本分册。",
        "",
        f"本分册共包含 **{len(rows)}** 条子需求。",
        "",
    ]
    for req_id, req_title in rows:
        parent = req_id.split("-S")[0]
        item_meta = NF_META[parent] if parent.startswith("NF") else META[parent]
        lines.extend(render_requirement(req_id, req_title, item_meta))
    output = DETAILS / output_name
    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return output, len(rows)


def main():
    DETAILS.mkdir(parents=True, exist_ok=True)
    total = 0
    for source, output, title in INPUTS:
        path, count = generate_detail(source, output, title)
        total += count
        print(f"generated {path.relative_to(ROOT)}: {count} requirements")
    print(f"total detailed requirements: {total}")


if __name__ == "__main__":
    main()
