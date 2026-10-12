from __future__ import annotations

import argparse
import copy
import hashlib
import html
import io
import json
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


USER = "8fbf2804c4374f148be86ed6d7ef4fd5"
NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def uid() -> str:
    return uuid.uuid4().hex


def read_export(path: Path, diagram_uuid: str) -> dict:
    with zipfile.ZipFile(path) as outer:
        root = outer.namelist()[0].split("/", 1)[0]
        meta = outer.read(f"{root}/1_meta.zip")
        data = outer.read(f"{root}/2_data.zip")
    with zipfile.ZipFile(io.BytesIO(data)) as inner:
        packages = json.loads(inner.read("2_data/1_package/0/package.json"))
        diagrams = json.loads(inner.read("2_data/4_diagram/0/diagrams.json"))
        elements = json.loads(inner.read("2_data/2_element/0/element.json"))
        lines = json.loads(inner.read("2_data/5_line/0/t_line.json"))
        diagram = next(d for d in diagrams if d["uuid"] == diagram_uuid)
        package = next(p for p in packages if p["uuid"] == diagram["packageuuid"])
        xml_name = f"2_data/4_diagram/0/{diagram_uuid}.xml"
        xml = inner.read(xml_name)
    return {
        "meta": meta,
        "package": package,
        "diagram": diagram,
        "elements": [e for e in elements if e.get("diagram_uuid") == diagram_uuid],
        "lines": [l for l in lines if l.get("diagram_uuid") == diagram_uuid],
        "xml": xml,
    }


def json_bytes(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")


def zip_bytes(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


class DiagramBuilder:
    def __init__(self, name: str, kind: str, template: dict, width: int, height: int):
        self.name = name
        self.kind = kind
        self.template = template
        self.package_uuid = uid()
        self.diagram_uuid = uid()
        self.width = width
        self.height = height
        self.elements: list[dict] = []
        self.lines: list[dict] = []
        self.cells: list[ET.Element] = []

        self.package = copy.deepcopy(template["package"])
        self.package.update({
            "uuid": self.package_uuid,
            "name": name,
            "create_time": NOW,
            "update_time": NOW,
            "create_user": USER,
            "update_user": USER,
            "parent_packageuuid": "",
            "path": "",
            "sequence": 0,
        })
        self.diagram = copy.deepcopy(template["diagram"])
        self.diagram.update({
            "uuid": self.diagram_uuid,
            "packageuuid": self.package_uuid,
            "name": name,
            "description": "OvO SRS V0.3 对应 UML 图",
            "create_time": NOW,
            "update_time": NOW,
            "create_user": USER,
            "update_user": USER,
            "path": json.dumps({"type": "Package", "uuid": self.package_uuid}, ensure_ascii=False, separators=(",", ":")),
            "sequence": 0,
        })

    def _prototype(self, type_name: str) -> dict:
        return copy.deepcopy(next(e for e in self.template["elements"] if e.get("type") == type_name))

    def _line_prototype(self, stereotype: str) -> dict:
        candidates = [l for l in self.template["lines"] if (l.get("stereotype") or "").lower() == stereotype.lower()]
        if not candidates:
            candidates = self.template["lines"]
        return copy.deepcopy(candidates[0])

    def add_element(self, type_name: str, stereotype: str, name: str, x: int, y: int,
                    width: int, height: int, parent: str = "1", style: str | None = None) -> str:
        record = self._prototype(type_name)
        element_id = uid()
        chosen_style = style or record.get("style") or ""
        display = html.escape(name).replace("\n", "<br>")
        label = f'<div id="CELL_NAME" style="max-width: {width}px; word-wrap: break-word;margin: 0 auto;">{display}</div>'
        obj = ET.Element("object", {
            "showMemberProperty": "true",
            "pureName": name,
            "id": element_id,
            "type": type_name,
            "stereotype": stereotype,
            "cellDefineName": name,
            "label": label,
        })
        cell = ET.SubElement(obj, "mxCell", {
            "style": chosen_style,
            "vertex": "1",
            "parent": parent,
        })
        ET.SubElement(cell, "mxGeometry", {
            "x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"
        })
        xml_text = ET.tostring(obj, encoding="unicode", short_empty_elements=True)
        record.update({
            "diagram_uuid": self.diagram_uuid,
            "element_data": xml_text,
            "element_id": element_id,
            "height": str(height),
            "parent_element": parent,
            "stereotype": stereotype,
            "style": chosen_style,
            "type": type_name,
            "value": label,
            "vertex": "1",
            "width": str(width),
            "x": str(x),
            "y": str(y),
            "uuid": element_id,
            "parentuuid": self.package_uuid,
            "name": name,
            "path": json.dumps({"type": "Package", "uuid": self.package_uuid}, ensure_ascii=False, separators=(",", ":")),
            "origin_cell_id": element_id,
            "create_time": NOW,
            "update_time": NOW,
            "create_user": USER,
            "update_user": USER,
            "sequence": len(self.elements),
        })
        self.elements.append(record)
        self.cells.append(obj)
        return element_id

    def add_actor(self, name: str, x: int, y: int) -> str:
        return self.add_element("Actor", "Actor", name, x, y, 70, 95)

    def add_usecase(self, name: str, x: int, y: int, width: int = 190, height: int = 72) -> str:
        return self.add_element("UseCase", "UseCase", name, x, y, width, height)

    def add_partition(self, name: str, x: int, y: int, width: int, height: int) -> str:
        return self.add_element("VerticalPartition", "Partition", name, x, y, width, height)

    def add_action(self, name: str, parent: str, x: int, y: int, width: int = 230, height: int = 58) -> str:
        return self.add_element("Action", "Action", name, x, y, width, height, parent)

    def add_decision(self, name: str, parent: str, x: int, y: int) -> str:
        return self.add_element("Decision", "Decision", name, x, y, 46, 46, parent)

    def add_state(self, name: str, x: int, y: int, width: int = 180, height: int = 72) -> str:
        return self.add_element("State", "State", name, x, y, width, height)

    def add_boundary(self, name: str, x: int, y: int, width: int, height: int) -> str:
        cid = uid()
        cell = ET.Element("mxCell", {
            "id": cid,
            "value": html.escape(name),
            "style": "swimlane;html=1;startSize=34;rounded=1;strokeColor=#808080;fillColor=#F5F5F5;fontStyle=1;fontSize=14;whiteSpace=wrap;",
            "vertex": "1", "parent": "1",
        })
        ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"})
        self.cells.append(cell)
        return cid

    def add_text(self, text: str, x: int, y: int, width: int, height: int, note: bool = False) -> str:
        cid = uid()
        value = html.escape(text).replace("\n", "<br>")
        style = "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;fontSize=14;fontStyle=1;"
        if note:
            style = "shape=note;html=1;whiteSpace=wrap;strokeColor=#808080;fillColor=#FFF2CC;fontSize=12;align=left;verticalAlign=middle;spacing=8;"
        cell = ET.Element("mxCell", {"id": cid, "value": value, "style": style, "vertex": "1", "parent": "1"})
        ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"})
        self.cells.append(cell)
        return cid

    def add_simple_node(self, kind: str, x: int, y: int, parent: str = "1") -> str:
        cid = uid()
        if kind == "initial":
            style = "ellipse;html=1;aspect=fixed;fillColor=#000000;strokeColor=#000000;"
            width = height = 26
        else:
            style = "ellipse;html=1;aspect=fixed;shape=doubleEllipse;fillColor=#000000;strokeColor=#000000;margin=4;"
            width = height = 30
        cell = ET.Element("mxCell", {"id": cid, "value": "", "style": style, "vertex": "1", "parent": parent})
        ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"})
        self.cells.append(cell)
        return cid

    def add_line(self, source: str, target: str, kind: str = "association", label: str = "") -> str:
        stereotypes = {
            "association": "default edge",
            "include": "Include",
            "extend": "Extend",
            "control": "Control Flow",
            "transition": "Transition",
        }
        requested = stereotypes[kind]
        record = self._line_prototype(requested)
        line_id = uid()
        if kind == "association":
            style = "shape=connector;labelBackgroundColor=none;endArrow=classic;fontSize=12;fontFamily=Helvetica;align=center;verticalAlign=bottom;rounded=1;strokeColor=#000000;fontColor=#333333;html=1;edgeStyle=orthogonalEdgeStyle;jumpStyle=arc;jumpSize=14;fillColor=#FFE6CC;whiteSpace=nowrap;"
        elif kind in ("include", "extend"):
            style = "edgeStyle=orthogonalEdgeStyle;shape=connector;rounded=1;jumpStyle=arc;jumpSize=14;html=1;strokeColor=#000000;fontFamily=Helvetica;fontSize=12;fontColor=#333333;whiteSpace=nowrap;verticalAlign=bottom;endArrow=open;startArrow=none;endSize=6;endFill=0;dashed=1;"
        else:
            style = "edgeStyle=orthogonalEdgeStyle;shape=connector;rounded=1;jumpStyle=arc;jumpSize=14;html=1;strokeColor=#000000;fontFamily=Helvetica;fontSize=12;fontColor=#333333;whiteSpace=nowrap;verticalAlign=bottom;endArrow=open;startArrow=none;endSize=6;endFill=0;dashed=0;"
        prefix = ""
        if kind == "include":
            prefix = "&lt;&lt;include&gt;&gt; "
        elif kind == "extend":
            prefix = "&lt;&lt;extend&gt;&gt; "
        value = f'<div id="CELL_NAME" style="max-width: initial; word-wrap: break-word;margin: 0 auto;">{prefix}{html.escape(label)}</div>'
        obj = ET.Element("object", {
            "pureName": label,
            "showMemberProperty": "true",
            "id": line_id,
            "type": requested if kind != "association" else "default edge",
            "stereotype": requested,
            "label": value,
        })
        cell = ET.SubElement(obj, "mxCell", {
            "style": style, "edge": "1", "parent": "1", "source": source, "target": target
        })
        geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
        ET.SubElement(geometry, "Array", {"as": "points"})
        xml_text = ET.tostring(obj, encoding="unicode", short_empty_elements=True)
        record.update({
            "line_data": xml_text,
            "diagram_uuid": self.diagram_uuid,
            "source": source,
            "target": target,
            "stereotype": requested,
            "style": style,
            "type": requested if kind != "association" else "default edge",
            "value": value,
            "uuid": line_id,
            "create_time": NOW,
            "update_time": NOW,
            "create_user": USER,
            "update_user": USER,
            "parent_link": "1",
            "sequence": len(self.lines),
        })
        self.lines.append(record)
        self.cells.append(obj)
        return line_id

    def xml_bytes(self) -> bytes:
        root = ET.Element("mxGraphModel", {
            "dx": "1422", "dy": "794", "grid": "1", "gridSize": "10", "guides": "1",
            "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1",
            "pageScale": "1", "pageWidth": str(self.width), "pageHeight": str(self.height),
            "math": "0", "shadow": "0",
        })
        graph_root = ET.SubElement(root, "root")
        ET.SubElement(graph_root, "mxCell", {"id": "0"})
        ET.SubElement(graph_root, "mxCell", {"id": "1", "parent": "0"})
        for cell in self.cells:
            graph_root.append(cell)
        return ET.tostring(root, encoding="utf-8", xml_declaration=True, short_empty_elements=True)


def overall_usecase(t: dict) -> DiagramBuilder:
    b = DiagramBuilder("系统总体用例图", "usecase", t, 1900, 1120)
    b.add_boundary("OvO 学术成果分享平台", 190, 45, 1480, 990)
    visitor = b.add_actor("访客", 35, 170)
    user = b.add_actor("登录用户", 35, 430)
    manager = b.add_actor("门户管理者", 35, 720)
    admin = b.add_actor("管理员", 1770, 410)
    external = b.add_actor("外部数据来源", 1770, 765)

    uc01 = b.add_usecase("UC-01\n检索成果与学者", 245, 120)
    uc02 = b.add_usecase("UC-02\n查看成果详情与来源", 475, 120)
    uc03 = b.add_usecase("UC-03\n查看学者门户", 705, 120)
    uc11 = b.add_usecase("UC-11\n查看统计与机构排名", 935, 120)
    uc12 = b.add_usecase("UC-12\n查看专家合作网络", 1165, 120)
    uc13 = b.add_usecase("UC-13\n查看领域热点", 1395, 120)
    uc15 = b.add_usecase("UC-15\n探索合作关系", 1165, 235)

    uc04 = b.add_usecase("UC-04\n管理账号与访问权限", 250, 385)
    uc05 = b.add_usecase("UC-05\n提交并跟踪门户认领", 500, 385)
    uc07 = b.add_usecase("UC-07\n维护学者门户", 500, 610)
    uc08 = b.add_usecase("UC-08\n确认、补录与纠正成果", 740, 610)

    uc06 = b.add_usecase("UC-06\n审核门户认领", 1270, 385)
    uc09 = b.add_usecase("UC-09\n管理采集任务", 1030, 760)
    uc10 = b.add_usecase("UC-10\n治理成果与学者关系", 1270, 760)
    uc14 = b.add_usecase("UC-14\n管理后台与审计", 1270, 565)

    for target in (uc01, uc02, uc03, uc11, uc12, uc13, uc15):
        b.add_line(visitor, target)
    for target in (uc04, uc05):
        b.add_line(user, target)
    for target in (uc07, uc08):
        b.add_line(manager, target)
    for target in (uc06, uc09, uc10, uc14):
        b.add_line(admin, target)
    b.add_line(external, uc09)
    b.add_line(external, uc10)
    b.add_line(uc03, uc05, "extend", "未认领且用户发起申请")
    b.add_line(uc05, uc04, "include", "受保护操作鉴权")
    b.add_line(uc07, uc04, "include", "对象级授权校验")
    b.add_line(uc08, uc04, "include", "对象级授权校验")
    b.add_line(uc09, uc10, "include", "采集后进入治理")
    b.add_line(uc12, uc15, "extend", "按机构/领域扩展探索")
    b.add_text("公开检索与分析", 245, 75, 450, 30)
    b.add_text("账号、认领与门户维护", 245, 335, 520, 30)
    b.add_text("采集、治理与后台管理", 1025, 710, 520, 30)
    return b


def claim_activity(t: dict) -> DiagramBuilder:
    b = DiagramBuilder("门户认领审核活动图", "activity", t, 1450, 1450)
    user_lane = b.add_partition("登录用户 / 申请人", 40, 45, 390, 1320)
    sys_lane = b.add_partition("系统", 450, 45, 430, 1320)
    admin_lane = b.add_partition("管理员", 900, 45, 390, 1320)
    start = b.add_simple_node("initial", 175, 55, user_lane)
    submit = b.add_action("选择目标学者档案，填写本人声明\n并提交必要证明", user_lane, 70, 115)
    validate = b.add_action("校验登录、目标、必填项、\n材料格式与本人声明", sys_lane, 95, 115)
    valid = b.add_decision("完整合法？", sys_lane, 185, 205)
    invalid = b.add_action("返回具体问题；不创建申请，\n不授予门户权限", sys_lane, 95, 275)
    end_invalid = b.add_simple_node("final", 200, 360, sys_lane)
    duplicate = b.add_decision("已有进行中申请？", sys_lane, 185, 385)
    existing = b.add_action("返回已有申请及当前状态", user_lane, 70, 405)
    end_existing = b.add_simple_node("final", 175, 490, user_lane)
    conflict = b.add_action("检查已有授权并登记冲突提示；\n原授权保持不变", sys_lane, 95, 480)
    pending = b.add_action("创建申请并置为“待审核”；\n通知申请人并进入审核队列", sys_lane, 95, 575)
    review = b.add_action("查看申请、受控证据摘要与冲突；\n核验证据并填写理由", admin_lane, 75, 575)
    need_more = b.add_decision("证据不足？", admin_lane, 165, 675)
    set_supp = b.add_action("置为“待补充”，记录要求并通知", sys_lane, 95, 690)
    supplement = b.add_action("补充认领材料", user_lane, 70, 690)
    validate_supp = b.add_action("校验补充内容", sys_lane, 95, 780)
    supp_ok = b.add_decision("补充合格？", sys_lane, 185, 865)
    approve_decision = b.add_decision("拟通过？", admin_lane, 165, 800)
    reject = b.add_action("置为“已驳回”，记录理由；\n不授予权限并通知申请人", sys_lane, 95, 1090)
    end_reject = b.add_simple_node("final", 200, 1180, sys_lane)
    conflict_decision = b.add_decision("有未解决冲突？", admin_lane, 165, 895)
    manual = b.add_action("人工处理冲突", admin_lane, 75, 975)
    conflict_ok = b.add_decision("冲突已解决？", admin_lane, 165, 1060)
    keep_pending = b.add_action("保持“待审核”；原授权不变，\n反馈冲突仍需处理", sys_lane, 95, 990)
    final_check = b.add_action("再次校验管理员权限、\n申请版本与目标授权", sys_lane, 95, 900)
    final_ok = b.add_decision("最终校验通过？", sys_lane, 185, 1190)
    approve = b.add_action("原子登记“已通过”并授予\n目标门户权限；记录审计并通知", sys_lane, 95, 1260)
    end_success = b.add_simple_node("final", 330, 1275, sys_lane)

    for s, d, label in [
        (start, submit, ""), (submit, validate, ""), (validate, valid, ""),
        (valid, invalid, "否"), (invalid, end_invalid, ""), (valid, duplicate, "是"),
        (duplicate, existing, "是"), (existing, end_existing, ""), (duplicate, conflict, "否"),
        (conflict, pending, ""), (pending, review, ""), (review, need_more, ""),
        (need_more, set_supp, "是"), (set_supp, supplement, ""), (supplement, validate_supp, ""),
        (validate_supp, supp_ok, ""), (supp_ok, set_supp, "否：保持待补充"),
        (supp_ok, pending, "是：回到待审核"), (need_more, approve_decision, "否"),
        (approve_decision, reject, "否：驳回"), (reject, end_reject, ""),
        (approve_decision, conflict_decision, "是"), (conflict_decision, manual, "是"),
        (manual, conflict_ok, ""), (conflict_ok, keep_pending, "否"),
        (conflict_decision, final_check, "否"), (conflict_ok, final_check, "是"),
        (final_check, final_ok, ""), (final_ok, reject, "否：拒绝覆盖"),
        (final_ok, approve, "是"), (approve, end_success, ""),
    ]:
        b.add_line(s, d, "control", label)
    b.add_text("待补充不得直接进入终态；认领通过与授予目标门户权限是同一成功结果。\n冲突未解决不得通过；材料只对申请人和对应审核管理员可见。", 455, 1375, 800, 60, note=True)
    return b


def claim_state(t: dict) -> DiagramBuilder:
    b = DiagramBuilder("认领申请状态图", "state", t, 1200, 780)
    start = b.add_simple_node("initial", 75, 300)
    pending = b.add_state("待审核", 205, 280)
    supplement = b.add_state("待补充", 205, 500)
    approved = b.add_state("已通过", 650, 170)
    rejected = b.add_state("已驳回", 650, 440)
    end_ok = b.add_simple_node("final", 1010, 190)
    end_no = b.add_simple_node("final", 1010, 460)
    b.add_line(start, pending, "transition", "完整申请提交成功")
    b.add_line(pending, supplement, "transition", "证据不足 / 管理员要求补充")
    b.add_line(supplement, pending, "transition", "申请人补充且校验通过")
    b.add_line(pending, approved, "transition", "核验通过 [权限/版本有效且无未解决冲突] / 授权并审计")
    b.add_line(pending, rejected, "transition", "管理员驳回 / 记录理由且不授权")
    b.add_line(approved, end_ok, "transition")
    b.add_line(rejected, end_no, "transition")
    b.add_text("禁止跳转：待补充 → 已通过/已驳回；终态 → 既有申请状态；\n存在未解决冲突时，待审核 → 已通过。重新申请必须另建记录。", 250, 650, 700, 68, note=True)
    b.add_text("认领申请状态与门户“未认领/已认领”摘要是不同业务对象。", 300, 735, 620, 30)
    return b


def collection_state(t: dict) -> DiagramBuilder:
    b = DiagramBuilder("数据采集任务状态图", "state", t, 1400, 900)
    start = b.add_simple_node("initial", 60, 350)
    pending = b.add_state("待执行", 175, 330)
    running = b.add_state("运行中", 470, 330)
    success = b.add_state("成功", 825, 135)
    failed = b.add_state("失败", 825, 330)
    retry = b.add_state("重试", 825, 525)
    stopped = b.add_state("已停止", 825, 720)
    end_success = b.add_simple_node("final", 1200, 155)
    end_stopped = b.add_simple_node("final", 1200, 740)
    for s, d, label in [
        (start, pending, "创建任务且配置校验通过"),
        (pending, running, "管理员启动 / 建立执行上下文"),
        (running, success, "全部处理完成 / 保存摘要与检查点"),
        (running, failed, "来源不可用或处理失败 / 记录原因与范围"),
        (running, stopped, "管理员停止 / 保留已成功数据和恢复上下文"),
        (failed, retry, "管理员重试 [失败可恢复]"),
        (retry, running, "校验通过 / 从安全检查点恢复"),
        (retry, failed, "恢复校验失败或来源仍不可用"),
        (success, end_success, ""), (stopped, end_stopped, ""),
    ]:
        b.add_line(s, d, "transition", label)
    b.add_text("禁止跳转：待执行 → 成功；失败 → 成功；已停止 → 运行中；成功 → 运行中。\n重试必须经过“重试”状态并重新校验；重复输入按幂等规则处理。", 340, 805, 760, 68, note=True)
    return b


def collection_usecase(t: dict) -> DiagramBuilder:
    b = DiagramBuilder("采集与成果治理局部用例图", "usecase", t, 1780, 1120)
    b.add_boundary("OvO：采集、治理、更新与来源追踪（FR08～FR10、FR15～FR16）", 200, 45, 1370, 1000)
    admin = b.add_actor("管理员", 40, 390)
    source = b.add_actor("外部数据来源", 1645, 400)
    manager = b.add_actor("门户管理者", 40, 790)

    register = b.add_usecase("登记并维护\n获准数据来源", 260, 120)
    create = b.add_usecase("创建并配置采集任务", 510, 120)
    operate = b.add_usecase("启动、停止与重试任务", 760, 120)
    inspect = b.add_usecase("查看任务进度、摘要\n失败原因与历史", 1010, 120)

    collect = b.add_usecase("采集四类成果并保留\n原始值、来源与游标", 1330, 250, 205)
    validate = b.add_usecase("校验并规范化字段", 1070, 360)
    dedup = b.add_usecase("识别重复成果与\n版本关系候选", 800, 360)
    detect = b.add_usecase("识别新增、未变化、\n变更和来源失效", 530, 360)
    trace = b.add_usecase("追踪来源、时间、\n使用范围与数据性质", 260, 360)

    identity = b.add_usecase("生成学者身份与\n成果关系候选", 800, 590)
    queue = b.add_usecase("将不确定或冲突项\n送入人工核验队列", 1070, 590)
    govern = b.add_usecase("批准合并、拒绝候选、\n拆分或改归属", 1070, 785)
    audit = b.add_usecase("记录证据、前后值、\n理由和操作者", 800, 785)
    propagate = b.add_usecase("传播生效结果到详情、\n门户、检索与统计", 530, 785)
    personal = b.add_usecase("提交成果确认、补录、\n纠错或解除本人关系", 260, 785)

    for target in (register, create, operate, inspect, queue, govern, audit):
        b.add_line(admin, target)
    b.add_line(source, collect)
    b.add_line(source, trace)
    b.add_line(manager, personal)
    b.add_line(create, register, "include", "来源必须已登记并获准")
    b.add_line(operate, inspect, "include", "任务状态与历史可查询")
    b.add_line(collect, validate, "include")
    b.add_line(validate, dedup, "include")
    b.add_line(validate, detect, "include")
    b.add_line(collect, trace, "include")
    b.add_line(dedup, identity, "include")
    b.add_line(dedup, queue, "extend", "证据不足或冲突")
    b.add_line(identity, queue, "extend", "同名或归属证据不足")
    b.add_line(queue, govern, "include")
    b.add_line(govern, audit, "include")
    b.add_line(govern, propagate, "include", "决定生效后")
    b.add_line(personal, queue, "extend", "补录、争议、共享字段或解除关系")
    b.add_text("规则边界：仅标题相似或仅姓名相同不得直接合并；自动更新不得覆盖人工确认值。\n解除个人关系不删除成果实体、来源记录或其他参与者关系；全部生效结果必须可追源。", 400, 955, 900, 62, note=True)
    return b


def make_data_zip(builders: list[DiagramBuilder]) -> bytes:
    files: dict[str, bytes] = {
        "2_data/1_package/0/package.json": json_bytes([b.package for b in builders]),
        "2_data/2_element/0/element.json": json_bytes([e for b in builders for e in b.elements]),
        "2_data/4_diagram/0/diagrams.json": json_bytes([b.diagram for b in builders]),
        "2_data/5_line/0/t_line.json": json_bytes([l for b in builders for l in b.lines]),
    }
    for b in builders:
        files[f"2_data/4_diagram/0/{b.diagram_uuid}.xml"] = b.xml_bytes()
    return zip_bytes(files)


def write_export(path: Path, root_name: str, builders: list[DiagramBuilder], meta: bytes) -> None:
    data = make_data_zip(builders)
    define = {
        "format_version": 1.0,
        "source_project_space_iuid": uid(),
        "source_project_branch_uuid": "",
        "source_env": "codeArts",
        "meta_data_file": "1_meta.zip",
        "meta_data_file_hex": hashlib.sha512(meta).hexdigest(),
        "data_file": "2_data.zip",
        "data_file_hex": hashlib.sha512(data).hexdigest(),
        "create_time": NOW,
        "create_user": USER,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"{root_name}/define.json", json_bytes(define))
        archive.writestr(f"{root_name}/1_meta.zip", meta)
        archive.writestr(f"{root_name}/2_data.zip", data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--usecase-template", type=Path, required=True)
    parser.add_argument("--activity-template", type=Path, required=True)
    parser.add_argument("--state-template", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    usecase = read_export(args.usecase_template, "766ce4414c3d42a5b1ec03c2336760d7")
    activity = read_export(args.activity_template, "93c3638f6cbf479a9468d02d9291fe22")
    state = read_export(args.state_template, "448565b7c725463c960486b2b219c373")
    diagrams = [
        ("member1_overall_usecase", overall_usecase(usecase), usecase["meta"]),
        ("member2_claim_activity", claim_activity(activity), activity["meta"]),
        ("member3_claim_state", claim_state(state), state["meta"]),
        ("member3_collection_state", collection_state(state), state["meta"]),
        ("member5_collection_governance_usecase", collection_usecase(usecase), usecase["meta"]),
    ]
    outputs = []
    for slug, builder, meta in diagrams:
        out = args.output_dir / f"OvO_{slug}_codearts_20261012.zip"
        write_export(out, f"OvO_{slug}_master_20261012", [builder], meta)
        outputs.append(out)
    combined = args.output_dir / "OvO_remaining_five_diagrams_codearts_20261012.zip"
    write_export(combined, "OvO_remaining_five_diagrams_master_20261012", [b for _, b, _ in diagrams], usecase["meta"])
    outputs.append(combined)
    print(json.dumps({"outputs": [str(p) for p in outputs], "diagram_names": [b.name for _, b, _ in diagrams]}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
