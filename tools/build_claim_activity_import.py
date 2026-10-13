"""Build an editable CodeArts-style claim-review activity import package.

The package is generated locally from the team's original member-2 import
template. It is intended for CodeArts import and manual refinement, not a
claim that CodeArts has validated or exported the resulting diagram.
"""

from __future__ import annotations

import argparse
import io
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from build_codearts_remaining import DiagramBuilder, read_export, write_export


def source_diagram_id(path: Path) -> str:
    with zipfile.ZipFile(path) as outer:
        data_name = next(name for name in outer.namelist() if name.endswith("2_data.zip"))
        with zipfile.ZipFile(io.BytesIO(outer.read(data_name))) as inner:
            diagrams = json.loads(inner.read("2_data/4_diagram/0/diagrams.json"))
    if len(diagrams) != 1:
        raise ValueError("Expected one activity diagram in the member-2 template")
    return diagrams[0]["uuid"]


def build(template: dict) -> DiagramBuilder:
    b = DiagramBuilder("门户认领审核活动图", "activity", template, 1520, 1680)
    applicant = b.add_partition("申请人", 30, 35, 410, 1560)
    system = b.add_partition("系统", 460, 35, 510, 1560)
    admin = b.add_partition("审核管理员", 990, 35, 440, 1560)

    start = b.add_simple_node("initial", 145, 55, applicant)
    submit = b.add_action("选择目标门户，提交本人声明和证明", applicant, 55, 110, 290)
    validate = b.add_action("校验登录、材料完整性、目标状态", system, 90, 110, 310)
    valid = b.add_decision("可受理？", system, 220, 205)
    invalid = b.add_action("返回缺失项或不合法原因；不创建申请", system, 90, 280, 310)
    end_invalid = b.add_simple_node("final", 225, 360, system)
    duplicate = b.add_decision("本人已有进行中申请？", system, 220, 390)
    existing = b.add_action("返回原申请和状态；不重复创建", system, 90, 470, 310)
    end_existing = b.add_simple_node("final", 225, 550, system)
    create = b.add_action("创建待审核申请；记录材料版本和冲突提示", system, 90, 575, 310)
    review = b.add_action("核验证据、目标授权和冲突提示", admin, 65, 575, 310)
    more = b.add_decision("需补充材料？", admin, 185, 670)
    ask_more = b.add_action("记录补充要求；申请转待补充", system, 90, 700, 310)
    supplement = b.add_action("查看要求并补交本人材料", applicant, 55, 700, 290)
    supp_valid = b.add_decision("补充有效且未过期？", system, 220, 795)
    supp_error = b.add_action("反馈问题；保持待补充并保留历史", system, 90, 870, 310)
    resubmit = b.add_action("保留历史材料；原申请转待审核", system, 90, 950, 310)
    decision = b.add_decision("审核决定？", admin, 185, 950)
    reject = b.add_action("填写驳回理由", admin, 65, 1040, 310)
    reject_check = b.add_decision("权限、版本和理由有效？", system, 220, 1130)
    rejected = b.add_action("转已驳回；不授予权限；审计并通知", system, 90, 1210, 310)
    end_rejected = b.add_simple_node("final", 225, 1295, system)
    conflict = b.add_decision("冲突已解决？", admin, 185, 1130)
    manual = b.add_action("人工核验争议；原授权保持不变", admin, 65, 1210, 310)
    conflict_pending = b.add_action("仍有争议：保持待审核，不授予新权限", system, 90, 1320, 310)
    end_conflict = b.add_simple_node("final", 175, 1500, applicant)
    approve_check = b.add_decision("权限、版本及授权复验通过？", system, 220, 1400)
    stale = b.add_action("拒绝过时决定；原申请和授权不变", admin, 65, 1450, 310)
    approved = b.add_action("原子登记已通过并授予目标门户权限；审计通知", system, 90, 1520, 360)
    end_approved = b.add_simple_node("final", 455, 1530, system)

    flows = [
        (start, submit, ""), (submit, validate, ""), (validate, valid, ""),
        (valid, invalid, "否"), (invalid, end_invalid, ""),
        (valid, duplicate, "是"), (duplicate, existing, "是"),
        (existing, end_existing, ""), (duplicate, create, "否"),
        (create, review, ""), (review, more, ""),
        (more, ask_more, "是"), (ask_more, supplement, ""),
        (supplement, supp_valid, ""), (supp_valid, supp_error, "否"),
        (supp_error, end_conflict, "本轮结束"),
        (supp_valid, resubmit, "是"), (resubmit, review, "原申请重审"),
        (more, decision, "否"),
        (decision, reject, "驳回"), (reject, reject_check, ""),
        (reject_check, rejected, "是"), (rejected, end_rejected, ""),
        (reject_check, stale, "否"),
        (decision, conflict, "拟通过"),
        (conflict, manual, "否"), (manual, conflict_pending, "未解决"),
        (conflict_pending, end_conflict, ""),
        (conflict, approve_check, "是或无冲突"),
        (approve_check, stale, "否"), (stale, end_conflict, ""),
        (approve_check, approved, "是"), (approved, end_approved, ""),
    ]
    for source, target, label in flows:
        b.add_line(source, target, "control", label)
    return b


def validate_export(path: Path) -> dict:
    with zipfile.ZipFile(path) as outer:
        root = outer.namelist()[0].split("/", 1)[0]
        define = json.loads(outer.read(f"{root}/define.json"))
        import hashlib
        meta = outer.read(f"{root}/1_meta.zip")
        data = outer.read(f"{root}/2_data.zip")
        assert hashlib.sha512(meta).hexdigest() == define["meta_data_file_hex"]
        assert hashlib.sha512(data).hexdigest() == define["data_file_hex"]
        with zipfile.ZipFile(io.BytesIO(data)) as inner:
            diagrams = json.loads(inner.read("2_data/4_diagram/0/diagrams.json"))
            elements = json.loads(inner.read("2_data/2_element/0/element.json"))
            lines = json.loads(inner.read("2_data/5_line/0/t_line.json"))
            assert len(diagrams) == 1
            xml = inner.read(f"2_data/4_diagram/0/{diagrams[0]['uuid']}.xml")
            graph = ET.fromstring(xml)
            ids = [node.get("id") for node in graph.iter() if node.get("id")]
            cell_ids = set(ids)
            assert len(ids) == len(cell_ids)
            assert all(line["source"] in cell_ids and line["target"] in cell_ids for line in lines)
            assert "\ufffd" not in xml.decode("utf-8")
            return {"diagram": diagrams[0]["name"], "elements": len(elements), "flows": len(lines)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("template", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    template = read_export(args.template, source_diagram_id(args.template))
    diagram = build(template)
    write_export(args.output, "OvO_claim_activity_refinement", [diagram], template["meta"])
    print(json.dumps(validate_export(args.output), ensure_ascii=False))


if __name__ == "__main__":
    main()
