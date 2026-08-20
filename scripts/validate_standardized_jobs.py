"""Validate the complete standardized company export without extra packages."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


REQUIRED = ("record_version", "source_id", "source_job_id", "company", "title", "work_locations",
            "location_hierarchy", "location_status", "job_function", "job_nature", "degree", "major_requirements",
            "responsibilities", "qualifications", "apply_url", "source_url", "status", "evidence")


def validate(path: Path) -> tuple[int, list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    jobs = [job for company in payload.get("companies", []) for job in company.get("jobs", [])]
    for index, job in enumerate(jobs):
        missing = [field for field in REQUIRED if field not in job]
        if missing:
            errors.append(f"job[{index}] missing: {','.join(missing)}")
            continue
        for field in ("apply_url", "source_url"):
            parsed = urlparse(str(job[field]))
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                errors.append(f"job[{index}] invalid {field}")
        if job["job_nature"] not in {"全职", "实习"}:
            errors.append(f"job[{index}] invalid job_nature")
        if len(job["work_locations"]) != len(job["location_hierarchy"]):
            errors.append(f"job[{index}] location arrays differ")
        if job["location_status"] == "stated" and not job["work_locations"]:
            errors.append(f"job[{index}] stated location is empty")
        if len(set(job["major_requirements"])) != len(job["major_requirements"]):
            errors.append(f"job[{index}] duplicate major")
    return len(jobs), errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="data/standardized/companies-all.json")
    args = parser.parse_args()
    count, errors = validate(Path(args.path))
    if errors:
        print(json.dumps({"jobs": count, "errors": errors[:20]}, ensure_ascii=False))
        raise SystemExit(1)
    print(json.dumps({"jobs": count, "errors": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
