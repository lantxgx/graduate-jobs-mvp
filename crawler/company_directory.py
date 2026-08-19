from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from xml.etree import ElementTree as ET

from app.db import connect, init_db


DEFAULT_WORKBOOK = Path(
    "outputs/019fe088-133d-7612-8425-8d152dbf8426/official_campus_career_sites.xlsx"
)
NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PACKAGE_REL = "http://schemas.openxmlformats.org/package/2006/relationships"


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _column_index(cell_ref: str) -> int:
    letters = re.match(r"[A-Z]+", cell_ref.upper())
    if not letters:
        return 0
    value = 0
    for char in letters.group(0):
        value = value * 26 + ord(char) - ord("A") + 1
    return value - 1


def _cell_value(cell: ET.Element, shared_strings: list[str]):
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.iter() if _local_name(node.tag) == "t")
    value_node = next((node for node in cell if _local_name(node.tag) == "v"), None)
    if value_node is None:
        return ""
    value = value_node.text or ""
    if cell_type == "s":
        return shared_strings[int(value)]
    if cell_type == "b":
        return value == "1"
    return value


def read_xlsx_sheet(path: Path, sheet_name: str) -> list[list[str]]:
    with zipfile.ZipFile(path) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root:
                shared_strings.append(
                    "".join(node.text or "" for node in item.iter() if _local_name(node.tag) == "t")
                )

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels
            if rel.attrib.get("Type", "").endswith("/worksheet")
        }
        sheet_target = None
        for sheet in workbook.iter():
            if _local_name(sheet.tag) == "sheet" and sheet.attrib.get("name") == sheet_name:
                sheet_target = targets.get(sheet.attrib.get(f"{{{NS_REL}}}id"))
                break
        if not sheet_target:
            raise ValueError(f"Worksheet not found: {sheet_name}")
        sheet_path = sheet_target.lstrip("/")
        if not sheet_path.startswith("xl/"):
            sheet_path = "xl/" + sheet_path
        root = ET.fromstring(archive.read(sheet_path))
        rows: list[list[str]] = []
        for row in root.iter():
            if _local_name(row.tag) != "row":
                continue
            cells: dict[int, str] = {}
            for cell in row:
                if _local_name(cell.tag) != "c":
                    continue
                cells[_column_index(cell.attrib.get("r", "A1"))] = _cell_value(cell, shared_strings)
            width = max(cells.keys(), default=-1) + 1
            rows.append([cells.get(index, "") for index in range(width)])
        return rows


def normalize_url(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    parts = urlsplit(value)
    if not parts.scheme or not parts.netloc:
        return value.rstrip("/")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), parts.query, ""))


def _first_main_site_url(notes: str) -> str:
    match = re.search(r"主站\s+(https?://[^\s，。；]+)", notes or "")
    return match.group(1).rstrip("/\u3002") if match else ""


def _map_official_status(value: str) -> str:
    if value.startswith("A-"):
        return "confirmed"
    if value.startswith("B-"):
        return "candidate"
    if value.startswith("C-"):
        return "unverified"
    if value.startswith("D-"):
        return "excluded"
    return "unverified"


def _map_access_status(value: str) -> str:
    if value == "可访问":
        return "reachable"
    if value in {"访问失败", "HTTP 404"}:
        return "access_error"
    if "验证码" in value or "拒绝" in value:
        return "blocked"
    return "unknown"


def _map_integration_status(official: str, suggestion: str) -> str:
    if official == "excluded" or "第三方" in suggestion or "寻找企业官网" in suggestion:
        return "excluded" if official == "excluded" else "paused"
    if "小样本" in suggestion:
        return "analyzing"
    if "复核" in suggestion or "补充" in suggestion or "检查" in suggestion:
        return "analyzing"
    return "not_integrated"


def _quality_and_priority(official: str, access: str, ats_type: str) -> tuple[str, int]:
    """Derive conservative quality and integration order from recorded evidence."""
    if official == "excluded" or access in {"access_error", "blocked"}:
        return "blocked", 4
    if official == "confirmed" and access == "reachable":
        return "high", 0
    if official == "candidate" and access == "reachable":
        return "medium", 1 if ats_type in {"feishu", "beisen", "moka"} else 2
    if access == "reachable":
        return "low", 3
    return "low", 4


def _map_ats(value: str) -> str:
    if "飞书" in value:
        return "feishu"
    if "北森" in value or "智联" in value:
        return "beisen"
    if "Moka" in value or "moka" in value:
        return "moka"
    if "自建" in value:
        return "self_hosted"
    if "中华英才" in value:
        return "other"
    return "unknown"


def normalize_directory_rows(rows: list[list[str]]) -> list[dict]:
    if not rows:
        raise ValueError("入口目录没有数据")
    headers = [str(value).strip() for value in rows[0]]
    required = ["企业", "校招入口URL", "招聘系统", "官方性等级", "可访问性"]
    missing = [header for header in required if header not in headers]
    if missing:
        raise ValueError(f"入口目录缺少必要列: {', '.join(missing)}")
    index = {header: headers.index(header) for header in headers}

    def value(row: list[str], header: str) -> str:
        position = index.get(header)
        return str(row[position]).strip() if position is not None and position < len(row) else ""

    normalized: list[dict] = []
    seen_urls: set[str] = set()
    for row_number, row in enumerate(rows[1:], start=5):
        company = value(row, "企业")
        original_url = value(row, "校招入口URL")
        url = normalize_url(original_url)
        if not company and not url:
            continue
        if not company or not url:
            raise ValueError(f"入口目录第 {row_number} 行缺少企业或 URL")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        access_status = _map_access_status(value(row, "可访问性"))
        ats_type = _map_ats(value(row, "招聘系统"))
        quality_level, integration_priority = _quality_and_priority(
            _map_official_status(value(row, "官方性等级")), access_status, ats_type
        )
        official_status = _map_official_status(value(row, "官方性等级"))
        suggestion = value(row, "接入建议")
        notes = value(row, "备注/错误")
        final_url = normalize_url(value(row, "最终URL"))
        main_url = _first_main_site_url(notes)
        raw = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
        source_key = "source-" + hashlib.sha1(f"{company}|{url}".encode("utf-8")).hexdigest()[:16]
        normalized.append(
            {
                "source_key": source_key,
                "company": company,
                "brand_name": company,
                "official_website": main_url or None,
                "official_domain": urlsplit(main_url).netloc.lower() if main_url else None,
                "source_name": value(row, "页面标题") or f"{company}校招",
                "url": url,
                "final_url": final_url or url,
                "domain": value(row, "域名"),
                "recruitment_scope": "mixed" if "实习" in (value(row, "覆盖届次") + notes) else "campus",
                "ats_type": ats_type,
                "official_status": official_status,
                "access_status": access_status,
                "integration_status": _map_integration_status(official_status, suggestion),
                "evidence_url": main_url or value(row, "候选来源").splitlines()[0],
                "discovery_source": value(row, "候选来源"),
                "covered_cohorts": value(row, "覆盖届次"),
                "source_category": value(row, "行业/来源分类"),
                "http_status": int(value(row, "HTTP状态")) if value(row, "HTTP状态").isdigit() else None,
                "page_title": value(row, "页面标题"),
                "last_verified_at": value(row, "验证日期") or None,
                "notes": json.dumps({"suggestion": suggestion, "error_or_note": notes}, ensure_ascii=False),
                "raw_json": json.dumps(raw, ensure_ascii=False),
                "enabled": 0 if official_status == "excluded" else 1,
                "quality_level": quality_level,
                "integration_priority": integration_priority,
            }
        )
    return normalized


def _upsert_rows(records: list[dict]) -> dict:
    init_db()
    created_companies = updated_companies = created_sources = updated_sources = 0
    with connect() as conn:
        for record in records:
            company_row = conn.execute(
                "SELECT id FROM companies WHERE canonical_name=?", (record["company"],)
            ).fetchone()
            if company_row:
                company_id = company_row["id"]
                conn.execute(
                    "UPDATE companies SET brand_name=?, official_website=?, official_domain=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (record["brand_name"], record["official_website"], record["official_domain"], company_id),
                )
                updated_companies += 1
            else:
                cursor = conn.execute(
                    "INSERT INTO companies(canonical_name, brand_name, official_website, official_domain) VALUES (?, ?, ?, ?)",
                    (record["company"], record["brand_name"], record["official_website"], record["official_domain"]),
                )
                company_id = cursor.lastrowid
                created_companies += 1

            existing = conn.execute(
                "SELECT id FROM career_sources WHERE source_key=?", (record["source_key"],)
            ).fetchone()
            values = (
                company_id, record["source_name"], record["url"], record["final_url"], record["domain"],
                record["recruitment_scope"], record["ats_type"], record["official_status"], record["access_status"],
                record["integration_status"], record["evidence_url"], record["discovery_source"], record["covered_cohorts"],
                record["source_category"], record["http_status"], record["page_title"], record["last_verified_at"],
                record["notes"], record["raw_json"], record["enabled"], record["quality_level"],
                record["integration_priority"], record["source_key"],
            )
            if existing:
                conn.execute(
                    """UPDATE career_sources SET company_id=?, source_name=?, url=?, final_url=?, domain=?,
                       recruitment_scope=?, ats_type=?, official_status=?, access_status=?, integration_status=?,
                       evidence_url=?, discovery_source=?, covered_cohorts=?, source_category=?, http_status=?,
                       page_title=?, last_verified_at=?, notes=?, raw_json=?, enabled=?, quality_level=?,
                       integration_priority=?, updated_at=CURRENT_TIMESTAMP
                       WHERE source_key=?""",
                    values,
                )
                updated_sources += 1
            else:
                conn.execute(
                    """INSERT INTO career_sources(company_id, source_name, url, final_url, domain, recruitment_scope,
                       ats_type, official_status, access_status, integration_status, evidence_url, discovery_source,
                       covered_cohorts, source_category, http_status, page_title, last_verified_at, notes, raw_json,
                       enabled, quality_level, integration_priority, source_key) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    values,
                )
                created_sources += 1
    return {
        "companies_created": created_companies,
        "companies_updated": updated_companies,
        "sources_created": created_sources,
        "sources_updated": updated_sources,
        "records": len(records),
    }


def import_directory(workbook_path: Path, dry_run: bool = False) -> dict:
    rows = read_xlsx_sheet(workbook_path, "入口目录")
    # The reader omits completely empty XML rows; in this workbook the title,
    # instruction, and header occupy the first three logical rows.
    records = normalize_directory_rows(rows[2:])
    summary = {
        "workbook": str(workbook_path),
        "dry_run": dry_run,
        "records": len(records),
        "excluded": sum(record["official_status"] == "excluded" for record in records),
        "by_ats_type": {},
        "by_quality_level": {},
        "by_integration_priority": {},
    }
    for record in records:
        summary["by_ats_type"][record["ats_type"]] = summary["by_ats_type"].get(record["ats_type"], 0) + 1
        summary["by_quality_level"][record["quality_level"]] = summary["by_quality_level"].get(record["quality_level"], 0) + 1
        priority = str(record["integration_priority"])
        summary["by_integration_priority"][priority] = summary["by_integration_priority"].get(priority, 0) + 1
    if not dry_run:
        summary.update(_upsert_rows(records))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(json.dumps(import_directory(args.workbook, args.dry_run), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
