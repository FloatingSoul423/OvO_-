"""Keep the eight required table dictionaries aligned with the design DDL."""
from pathlib import Path
import re

ROOT = Path(__file__).parent
DDL = ROOT / "02-数据库模型-可御风雪可燃冰" / "02-核心表DDL-可御风雪可燃冰.sql"
DOC = ROOT / "01-数据库设计说明书-可御风雪可燃冰.md"
CORE = [
    ("scholar", "学者"), ("organization", "机构"), ("work", "学术成果"),
    ("work_scholar", "成果学者关系"), ("domain", "领域"),
    ("claim_application", "认领申请"), ("collection_task", "采集任务"),
    ("audit_log", "审计日志"),
]
MEANING = {
    "scholar_id": "平台学者稳定标识", "organization_id": "机构稳定标识", "display_name": "公开姓名",
    "aliases_json": "公开别名集合", "biography": "公开简介", "identity_status": "身份判定状态",
    "public_status": "当前公开资格", "data_nature": "真实、模拟或混合", "version": "对象乐观锁版本",
    "created_at": "创建时间（UTC）", "updated_at": "更新或检查时间（UTC）", "name": "名称",
    "normalized_name": "用于候选匹配的规范名称", "source_scope": "名称适用来源或作用域",
    "work_id": "成果实体稳定标识", "work_type": "论文、专利、项目或获奖", "title": "成果标题",
    "abstract_text": "公开摘要", "publication_year": "按类型定义的筛选年份", "date_precision": "来源日期精度",
    "identifier_kind": "稳定标识类别", "identifier_scope": "标识命名空间", "identifier_norm": "规范化标识",
    "type_details": "按成果类型校验的扩展字段", "relation_id": "关系稳定标识",
    "role_code": "参与角色", "author_order": "作者或参与者顺序", "organization_at_work_id": "成果发生时机构",
    "confirmation_status": "归属确认与争议状态", "evidence_record_id": "归属证据来源记录",
    "domain_id": "领域稳定标识", "parent_id": "父领域；根领域为空", "sort_order": "同级展示顺序",
    "active": "是否启用", "claim_id": "申请稳定标识", "applicant_account_id": "申请人账号",
    "target_scholar_id": "目标学者档案", "declaration_text": "本人声明",
    "evidence_object_keys": "受控证明 OBS 对象引用", "state": "业务状态",
    "review_reason": "审核决定或补充原因", "reviewer_account_id": "审核员账号",
    "submitted_at": "申请提交时间（UTC）", "decided_at": "最终决定时间（UTC）",
    "task_id": "采集任务稳定标识", "source_id": "获准数据来源", "created_by": "任务创建人",
    "mode_code": "增量或全量方式", "parameters_json": "受控采集参数摘要",
    "checkpoint_json": "可恢复检查点", "processed_count": "已处理记录数",
    "success_count": "成功记录数", "failure_count": "失败记录数", "retry_count": "重试次数",
    "failure_reason": "最近失败原因", "lease_owner": "当前 worker 租约持有者",
    "lease_until": "租约截止时间（UTC）", "started_at": "最近开始时间（UTC）",
    "ended_at": "结束时间（UTC）", "audit_id": "审计事件稳定标识",
    "actor_account_id": "操作者账号；系统事件可空", "action_code": "操作类别",
    "object_type": "目标对象类别", "object_id": "目标对象标识",
    "before_summary": "变更前最小摘要（脱敏）", "after_summary": "变更后最小摘要（脱敏）",
    "reason": "操作原因", "outcome": "成功、拒绝或失败",
    "happened_at": "发生时间（UTC）", "correlation_id": "跨步骤关联号",
}

sql = DDL.read_text(encoding="utf-8")
tables = dict(re.findall(r"CREATE TABLE (\w+) \((.*?)\) ENGINE=InnoDB", sql, re.S))
assert all(name in tables for name, _ in CORE)
out = ["## 附录 A 八类核心表字段字典", "", "本附录逐列列出类型、空值与主要约束；完整可执行语法和支撑表见同版 DDL。`PK` 为主键，`FK` 为外键；`CHECK` 约束在目标 MySQL 8.0.16+ 执行。索引条目给出字段顺序，后续需在目标数据量下用 EXPLAIN 验证。", ""]
for idx, (name, chinese) in enumerate(CORE, 1):
    body = tables[name]
    lines = [x.strip().rstrip(",") for x in body.splitlines() if x.strip()]
    pk = set()
    fk = {}
    unique = {}
    checks = []
    indexes = []
    for line in lines:
        m = re.match(r"PRIMARY KEY \(([^)]+)\)", line)
        if m: pk.update(x.strip() for x in m.group(1).split(","))
        m = re.match(r"CONSTRAINT \w+ FOREIGN KEY \(([^)]+)\) REFERENCES (\w+)\(([^)]+)\)", line)
        if m: fk[m.group(1)] = f"FK→{m.group(2)}.{m.group(3)}"
        m = re.match(r"UNIQUE KEY (\w+) \(([^)]+)\)", line)
        if m:
            indexes.append(f"唯一 `{m.group(1)}`：{m.group(2)}")
            for col in m.group(2).split(","): unique.setdefault(col.strip(), []).append("唯一键成员")
        m = re.match(r"KEY (\w+) \(([^)]+)\)", line)
        if m: indexes.append(f"普通 `{m.group(1)}`：{m.group(2)}")
        m = re.match(r"CONSTRAINT (ck_\w+) CHECK \((.+)\)", line)
        if m: checks.append(f"`{m.group(1)}`：`{m.group(2)}`")
    if name == "work_scholar":
        fk["evidence_record_id"] = "FK→source_record.record_id（后置 ALTER）"
    out.extend([f"### A.{idx} {chinese} `{name}`", "", f"表 {4+idx} {chinese}表字段设计", "", "|字段|类型|空值与约束|语义|", "|---|---|---|---|"])
    for line in lines:
        m = re.match(r"(\w+)\s+([A-Z]+(?:\([^)]*\))?)\s+(.*)", line)
        if not m or m.group(1) in {"CONSTRAINT", "UNIQUE", "PRIMARY", "KEY"}: continue
        col, typ, rest = m.groups()
        not_null = "NOT NULL" in rest or "PRIMARY KEY" in rest or col in pk
        flags = ["非空" if not_null else "可空"]
        if "PRIMARY KEY" in rest or col in pk: flags.append("PK")
        if col in fk: flags.append(fk[col])
        flags.extend(unique.get(col, []))
        default = re.search(r"DEFAULT\s+([^\s]+)", rest)
        if default: flags.append(f"默认 {default.group(1)}")
        out.append(f"|`{col}`|`{typ}`|{'；'.join(flags)}|{MEANING.get(col, '按字段名记录的业务值')}|")
    out.extend(["", "**索引。** " + ("；".join(indexes) if indexes else "主键索引；无额外索引。"), ""])
    if checks: out.extend(["**检查约束。** " + "；".join(checks), ""])

start = "<!-- DATA DICTIONARY START -->"
end = "<!-- DATA DICTIONARY END -->"
text = DOC.read_text(encoding="utf-8")
if start not in text:
    text = text.rstrip() + "\n\n" + start + "\n" + end + "\n"
text = text[:text.index(start)] + start + "\n" + "\n".join(out).rstrip() + "\n" + end + text[text.index(end)+len(end):]
DOC.write_text(text, encoding="utf-8")
print(f"updated {DOC} with {len(CORE)} core tables")
