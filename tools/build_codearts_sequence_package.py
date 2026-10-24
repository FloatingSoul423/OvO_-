"""Build the OvO data-collection sequence diagram as a CodeArts import package.

The builder deliberately starts from a real CodeArts Modeling export so the
metadata, mxGraph styles, and archive hierarchy remain compatible with the
course tool.  It then keeps only the sequence diagram and rewrites the model
names to the approved OvO terminology.

Usage:
    python tools/build_codearts_sequence_package.py TEMPLATE.zip OUTPUT.zip
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


SEQUENCE_DIAGRAM_UUID = "80a8edadd14b48d9a8129888d515a10c"

LIFELINE_NAMES = {
    "9a5d9a91729246739d76eb882aca1b3a": "管理员/调度器",
    "cf807acc9b8f4385f33bc17f419d50de": "采集任务服务",
    "1683669a448a4fd49a278ee598e50799": "清洗与去重服务",
    "bc59471107b1427cbfc04438d60d7bff": "成果存储与索引",
    "4843dd65d77c455fc08d40863df13c02": "来源适配器",
    "f86408648dbe47d387cf8f9bdd44b8b7": "外部数据来源",
    "27064ae8f7284b77d276251b4289fa58": "人工核验队列",
}

MESSAGE_NAMES = {
    "55df94bb2a6f4679b6b94afc00b0029d": "1. 创建并启动采集任务",
    "39186596aace464eb4d1c6cc447c1808": "2. 返回任务编号与初始状态",
    "df141a245e404031d74856e2ebcffbc8": "3. 请求拉取下一批数据",
    "55a207da80624854a0d1cfe76cda1c9b": "4. 请求增量数据",
    "8b43786730d54189f3ce24fed677daf1": "5. 拉取来源数据批次",
    "87a6ca44395c45c1bc888cf83b451fae": "6. 提交批次进行清洗去重",
    "f002a36cff6b4adac0b6c9a557ede1aa": "7. 返回标准化结果",
    "3434e33bc39d4b7f89e8b2a73c28ac29": "8. 校验来源元数据",
    "96fbeec3eff64c4182fdefc731143a73": "9. 请求持久化本批次",
    "457daa1431e24ec9b7272545c8bc891d": "10. 生成成果变更集",
    "c6c069d1272b4f21cc710121ec144b35": "11. 查询重复成果与身份候选",
    "9d147922afd64e07d6afad59bb1cb53a": "12. 返回可入库结果",
    "89620f9c648f4f1196224728900ca03a": "13. 提交入库并更新检查点",
    "1c02f9e97c724f33daf295f41ed777c8": "14. 写入成果或待核验项",
    "71751efaf99c4449e0e84ed356e9845c": "15. 更新来源游标与索引",
    "e75ef85d12554a1ae4de9c3f3b6b2dd0": "16. 发送疑似冲突候选",
    "7b0177f2ffbb4a3bfcb29768d88c3ee9": "17. 加入人工核验队列",
}


def json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")


def zip_bytes(files: dict[str, bytes]) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, payload in sorted(files.items()):
            archive.writestr(name, payload)
    return stream.getvalue()


def rename_xml_object(obj: ET.Element, new_name: str) -> None:
    old_name = obj.attrib.get("pureName", "")
    obj.set("pureName", new_name)
    if "cellDefineName" in obj.attrib:
        obj.set("cellDefineName", new_name)
    if "label" in obj.attrib:
        obj.set("label", obj.attrib["label"].replace(old_name, new_name))


def replace_record_name(record: dict, old_name: str, new_name: str) -> None:
    for key in ("name", "value", "element_data", "line_data"):
        value = record.get(key)
        if isinstance(value, str):
            record[key] = value.replace(old_name, new_name)


def build(template: Path, output: Path) -> None:
    with zipfile.ZipFile(template) as outer:
        meta_member = next(name for name in outer.namelist() if name.endswith("1_meta.zip"))
        data_member = next(name for name in outer.namelist() if name.endswith("2_data.zip"))
        define_member = next(name for name in outer.namelist() if name.endswith("define.json"))
        meta_payload = outer.read(meta_member)
        data_payload = outer.read(data_member)
        define = json.loads(outer.read(define_member).decode("utf-8"))

    with zipfile.ZipFile(io.BytesIO(data_payload)) as data_archive:
        files = {
            name: data_archive.read(name)
            for name in data_archive.namelist()
            if not name.endswith("/")
        }

    diagram_json_name = next(name for name in files if name.endswith("diagrams.json"))
    package_json_name = next(name for name in files if name.endswith("package.json"))
    element_json_name = next(name for name in files if name.endswith("element.json"))
    line_json_name = next(name for name in files if name.endswith("t_line.json"))
    diagram_xml_name = next(
        name for name in files if name.endswith(f"{SEQUENCE_DIAGRAM_UUID}.xml")
    )

    diagrams = json.loads(files[diagram_json_name].decode("utf-8"))
    diagram = next(item for item in diagrams if item["uuid"] == SEQUENCE_DIAGRAM_UUID)
    sequence_package_uuid = diagram["packageuuid"]
    diagram["name"] = "DGA-SEQUENCE-01 数据采集入库时序图"
    diagram["description"] = (
        "覆盖采集任务启动、增量拉取、清洗去重、成果入库、检查点更新与人工核验。"
    )
    diagram["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    diagrams = [diagram]

    packages = json.loads(files[package_json_name].decode("utf-8"))
    package = next(item for item in packages if item["uuid"] == sequence_package_uuid)
    old_package_name = package["name"]
    package["name"] = "OvO-数据采集入库"
    package["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    root = ET.fromstring(files[diagram_xml_name])
    old_names: dict[str, str] = {}
    rename_map = {**LIFELINE_NAMES, **MESSAGE_NAMES}
    for obj in root.iter("object"):
        object_id = obj.attrib.get("id", "")
        if object_id in rename_map:
            old_names[object_id] = obj.attrib.get("pureName", "")
            rename_xml_object(obj, rename_map[object_id])
        elif obj.attrib.get("type") == "Fragment" and obj.attrib.get("pureName") == "moreitem":
            old_names[object_id] = "moreitem"
            rename_map[object_id] = "loop [仍有待处理数据]"
            rename_xml_object(obj, rename_map[object_id])

    xml_payload = ET.tostring(root, encoding="utf-8", xml_declaration=False)

    elements = json.loads(files[element_json_name].decode("utf-8"))
    kept_elements = []
    for record in elements:
        if record.get("diagram_uuid") == SEQUENCE_DIAGRAM_UUID:
            kept_elements.append(record)
        elif record.get("uuid") == sequence_package_uuid:
            kept_elements.append(record)
            replace_record_name(record, old_package_name, package["name"])
            record["name"] = package["name"]
    for record in kept_elements:
        object_id = record.get("uuid") or record.get("element_id")
        if object_id in rename_map:
            replace_record_name(record, old_names.get(object_id, ""), rename_map[object_id])
            record["name"] = rename_map[object_id]

    lines = json.loads(files[line_json_name].decode("utf-8"))
    kept_lines = [
        record for record in lines if record.get("diagram_uuid") == SEQUENCE_DIAGRAM_UUID
    ]
    for record in kept_lines:
        object_id = record.get("uuid")
        if object_id in rename_map:
            replace_record_name(record, old_names.get(object_id, ""), rename_map[object_id])
            record["name"] = rename_map[object_id]

    new_data_files = {
        diagram_json_name: json_bytes(diagrams),
        package_json_name: json_bytes([package]),
        element_json_name: json_bytes(kept_elements),
        line_json_name: json_bytes(kept_lines),
        diagram_xml_name: xml_payload,
    }
    new_data_payload = zip_bytes(new_data_files)

    now = datetime.now()
    root_name = f"OvO_collection_sequence_master_{now.strftime('%Y%m%d%H%M%S')}"
    define["source_project_space_iuid"] = uuid.uuid4().hex
    define["source_project_branch_uuid"] = ""
    define["create_time"] = now.strftime("%Y-%m-%d %H:%M:%S")
    define["meta_data_file"] = "1_meta.zip"
    define["data_file"] = "2_data.zip"
    define["meta_data_file_hex"] = hashlib.sha512(meta_payload).hexdigest()
    define["data_file_hex"] = hashlib.sha512(new_data_payload).hexdigest()

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"{root_name}/define.json", json_bytes(define))
        archive.writestr(f"{root_name}/1_meta.zip", meta_payload)
        archive.writestr(f"{root_name}/2_data.zip", new_data_payload)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: build_codearts_sequence_package.py TEMPLATE.zip OUTPUT.zip")
    build(Path(sys.argv[1]), Path(sys.argv[2]))


if __name__ == "__main__":
    main()
