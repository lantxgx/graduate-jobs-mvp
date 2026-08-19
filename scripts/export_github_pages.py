"""Export the current active-job snapshot for the GitHub Pages demo."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
sys.path.insert(0, str(ROOT))

from app.db import connect, init_db
PUBLIC_FIELDS = (
    "id", "company", "title", "city", "job_nature", "category", "degree",
    "graduate_year", "requirements", "description", "apply_url", "source_url",
    "published_at", "first_seen_at", "last_seen_at", "last_changed_at", "job_family",
)


def main() -> None:
    init_db()
    columns = ", ".join(PUBLIC_FIELDS)
    with connect() as conn:
        rows = [
            dict(row)
            for row in conn.execute(
                f"SELECT {columns} FROM jobs WHERE status='active' ORDER BY last_seen_at DESC, id DESC"
            ).fetchall()
        ]
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "jobs.json").write_text(
        json.dumps({"exported_at": rows[0]["last_seen_at"] if rows else None, "items": rows}, ensure_ascii=False),
        encoding="utf-8",
    )
    shutil.copy2(ROOT / "static" / "styles.css", DOCS / "styles.css")
    print(f"Exported {len(rows)} active jobs to {DOCS / 'jobs.json'}")


if __name__ == "__main__":
    main()
