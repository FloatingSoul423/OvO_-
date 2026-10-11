"""Reproducible structural checks for the V0.2 SRS specification layer."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

from build_srs_details import CRITICAL


ROOT = Path(__file__).resolve().parents[1]
SRS = ROOT / "docs" / "srs"
MODULES = SRS / "modules"
DETAILS = MODULES / "detailed"

OVERVIEWS = [
    MODULES / "01-search-and-portal.md",
    MODULES / "02-account-claim-maintenance.md",
    MODULES / "03-collection-governance.md",
    MODULES / "04-analytics-admin-innovation.md",
    MODULES / "nonfunctional.md",
]
DETAIL_FILES = [
    DETAILS / "01-search-and-portal-detailed.md",
    DETAILS / "02-account-claim-maintenance-detailed.md",
    DETAILS / "03-collection-governance-detailed.md",
    DETAILS / "04-analytics-admin-innovation-detailed.md",
    DETAILS / "nonfunctional-detailed.md",
]
NORMATIVE = [
    SRS / "OvO-SRS-Draft.md",
    SRS / "traceability-matrix.md",
    SRS / "use-case-specifications.md",
    SRS / "cross-cutting-matrices.md",
    *OVERVIEWS,
    *DETAIL_FILES,
]

REQ = re.compile(r"(?:FR\d{2}|IN01|NF\d{2})-S\d{2}")
DETAIL_HEADING = re.compile(r"^## ((?:FR\d{2}|IN01|NF\d{2})-S\d{2}) ", re.M)
AC_DEFINITION = re.compile(r"^- (?:\*\*)?(AC-((?:FR\d{2}|IN01|NF\d{2})-S\d{2})-\d{2})", re.M)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    for path in NORMATIVE:
        if not path.is_file():
            fail(f"missing normative file: {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if re.match(r"^(?:https?://|#)", target):
                continue
            local_target = target.split("#", 1)[0]
            if local_target and not (path.parent / local_target).resolve().exists():
                fail(f"broken local link in {path.relative_to(ROOT)}: {target}")

    overview_ids = set()
    for path in OVERVIEWS:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("|"):
                first = line.strip().strip("|").split("|", 1)[0].strip()
                if REQ.fullmatch(first):
                    overview_ids.add(first)

    detail_ids = []
    detail_text = "\n".join(path.read_text(encoding="utf-8") for path in DETAIL_FILES)
    detail_ids.extend(DETAIL_HEADING.findall(detail_text))
    if len(detail_ids) != 124 or len(set(detail_ids)) != 124:
        fail(f"expected 124 unique detail headings, got {len(detail_ids)}/{len(set(detail_ids))}")
    if set(detail_ids) != overview_ids:
        fail(f"overview/detail ID mismatch: missing={sorted(overview_ids-set(detail_ids))}, extra={sorted(set(detail_ids)-overview_ids)}")

    functional = [item for item in detail_ids if not item.startswith("NF")]
    nonfunctional = [item for item in detail_ids if item.startswith("NF")]
    if len(functional) != 107 or len(nonfunctional) != 17:
        fail(f"expected 107 function/innovation and 17 NF, got {len(functional)} and {len(nonfunctional)}")

    for field in [
        "| 需求描述 |", "| 前置条件 |", "| 触发条件 |", "| 输入/业务数据 |",
        "| 输出/可观察结果 |", "| 状态变化 |", "| 权限规则 |", "| 业务规则 |",
        "| 备选流程 |", "| 异常流程 |", "### 主成功流程", "### 验收条件", "### 关联项",
    ]:
        count = detail_text.count(field)
        if count != 124:
            fail(f"field {field!r} expected 124 occurrences, got {count}")

    definition_text = "\n".join(path.read_text(encoding="utf-8") for path in [*OVERVIEWS, *DETAIL_FILES])
    definitions = AC_DEFINITION.findall(definition_text)
    ac_ids = [item[0] for item in definitions]
    if len(ac_ids) != len(set(ac_ids)):
        duplicates = [item for item, count in Counter(ac_ids).items() if count > 1]
        fail(f"duplicate AC definitions: {duplicates}")
    by_req = defaultdict(list)
    for ac_id, req_id in definitions:
        by_req[req_id].append(ac_id)
    missing_ac = sorted(set(detail_ids) - set(by_req))
    if missing_ac:
        fail(f"requirements without AC definition: {missing_ac}")
    excessive_ac = sorted((req_id, len(items)) for req_id, items in by_req.items() if len(items) > 3)
    if excessive_ac:
        fail(f"requirements with more than three ACs: {excessive_ac}")
    bad_critical = sorted((req_id, len(by_req[req_id])) for req_id in CRITICAL if len(by_req[req_id]) not in {2, 3})
    if bad_critical:
        fail(f"critical requirements must have two or three ACs: {bad_critical}")

    uc_text = (SRS / "use-case-specifications.md").read_text(encoding="utf-8")
    use_cases = re.findall(r"^## (UC-\d{2}) ", uc_text, re.M)
    expected_uc = [f"UC-{index:02d}" for index in range(1, 16)]
    if use_cases != expected_uc:
        fail(f"use-case sections are not exactly UC-01..UC-15: {use_cases}")

    matrix_text = (SRS / "cross-cutting-matrices.md").read_text(encoding="utf-8")
    for heading in ["## 1. 权限矩阵", "## 2. 状态登记表", "## 3. 业务规则适用矩阵"]:
        if heading not in matrix_text:
            fail(f"missing matrix section: {heading}")
    for number in range(1, 21):
        if f"BR-{number:02d}" not in matrix_text:
            fail(f"BR-{number:02d} absent from cross-cutting matrix")

    physical_lines = 0
    nonblank_lines = 0
    nonspace_chars = 0
    han_chars = 0
    for path in NORMATIVE:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        physical_lines += len(lines)
        nonblank_lines += sum(bool(line.strip()) for line in lines)
        nonspace_chars += len(re.sub(r"\s", "", text))
        han_chars += len(re.findall(r"[\u3400-\u9fff]", text))

    print("PASS: SRS V0.2 structural quality checks")
    print(f"normative_files={len(NORMATIVE)}")
    print(f"physical_lines={physical_lines}")
    print(f"nonblank_lines={nonblank_lines}")
    print(f"nonspace_chars={nonspace_chars}")
    print(f"han_chars={han_chars}")
    print(f"detailed_requirements={len(detail_ids)} (function_innovation={len(functional)}, nf={len(nonfunctional)})")
    print(f"unique_ac_definitions={len(ac_ids)}")
    print(f"use_case_specifications={len(use_cases)}")


if __name__ == "__main__":
    main()
