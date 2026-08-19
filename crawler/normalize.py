from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin


TITLE_KEYS = [
    "title", "jobtitle", "job_title", "positionname", "position_name",
    "jobname", "job_name", "JobAdName", "name", "position"
]
CITY_KEYS = [
    "city", "location", "workplace", "work_place", "worklocation",
    "work_location", "address", "workcity", "work_city", "LocNames"
]
NATURE_KEYS = [
    "jobtype", "job_type", "nature", "jobnature", "job_nature",
    "employmenttype", "employment_type", "recruitmenttype", "recruitment_type", "Kind"
]
CATEGORY_KEYS = [
    "category", "jobcategory", "job_category", "function", "functionname",
    "jobfamily", "job_family", "positioncategory", "ClassificationOne"
]
DEGREE_KEYS = [
    "degree", "education", "educationlevel", "education_level",
    "academic", "qualification", "Degree"
]
DESC_KEYS = [
    "description", "jobdescription", "job_description", "content",
    "responsibility", "responsibilities", "duty", "duties", "Duty", "desc"
]
REQ_KEYS = [
    "requirements", "requirement", "qualification", "qualifications",
    "jobrequirement", "job_requirement", "Require", "request", "condition"
]
URL_KEYS = [
    "applyurl", "apply_url", "detailurl", "detail_url", "joburl", "job_url",
    "JobAdUrl", "url", "link", "href"
]
ID_KEYS = [
    "id", "jobid", "job_id", "positionid", "position_id",
    "recruitmentid", "JobAdId",
]
DATE_KEYS = [
    "publishedat", "published_at", "publishdate", "publish_date",
    "createdat", "created_at", "updatedat", "updated_at", "date"
]

JOB_NATURE_FULL_TIME = "全职"
JOB_NATURE_INTERNSHIP = "实习"
JOB_NATURE_VALUES = {JOB_NATURE_FULL_TIME, JOB_NATURE_INTERNSHIP}

CATEGORY_VALUES = {
    "算法/AI", "软件研发", "硬件研发", "测试/质量", "数据", "产品", "运营",
    "设计", "市场/销售", "制造/工艺", "供应链/采购", "职能", "其他",
}

DEGREE_VALUES = {"未注明", "大专及以上", "本科及以上", "硕士及以上", "博士"}


def normalize_job_nature(raw_nature: str | None, title: str = "", description: str = "") -> str | None:
    """Collapse source labels to the product's only two recruitment types."""
    text = " ".join(str(value or "") for value in (raw_nature, title, description)).lower()
    internship_tokens = ("实习", "实习生", "intern", "internship")
    full_time_tokens = (
        "全职", "正式", "校招", "校园招聘", "应届", "graduate", "new grad", "full-time", "full time"
    )
    excluded_tokens = ("社招", "社会招聘", "experienced hire", "兼职", "part-time", "外包", "劳务")
    if any(token in text for token in excluded_tokens) and not any(token in text for token in internship_tokens):
        return None
    if any(token in text for token in internship_tokens):
        return JOB_NATURE_INTERNSHIP
    if any(token in text for token in full_time_tokens):
        return JOB_NATURE_FULL_TIME
    return None


def normalize_degree(raw_degree: str | None, requirements: str = "") -> str:
    text = " ".join(str(value or "") for value in (raw_degree, requirements)).lower()
    if any(token in text for token in ("博士", "ph.d", "phd")):
        return "博士"
    if any(token in text for token in ("硕士", "研究生", "master", "mba")):
        return "硕士及以上"
    if any(token in text for token in ("本科", "学士", "bachelor", "undergraduate")):
        return "本科及以上"
    if any(token in text for token in ("大专", "专科", "associate")):
        return "大专及以上"
    return "未注明"


def normalize_category(raw_category: str | None, title: str = "", description: str = "") -> str:
    raw = str(raw_category or "").strip()
    # Human-resources and recruiting titles can contain "AI" or "数据" in
    # the business description. Prefer the explicit role title so a role such
    # as "AI Talent Partner（招聘与运营）" is not classified as an algorithm
    # position merely because its title contains the token "AI".
    title_text = str(title or "").lower()
    if any(token in title_text for token in ("招聘", "人才", "talent partner", "human resources", "hrbp")):
        return "职能"
    if raw in CATEGORY_VALUES:
        return raw
    text = " ".join(str(value or "") for value in (raw, title, description)).lower()
    rules = (
        ("算法/AI", ("算法", "机器学习", "深度学习", "人工智能", "ai", "nlp", "cv")),
        ("软件研发", ("软件", "开发", "后端", "前端", "java", "python", "c++", "golang")),
        ("硬件研发", ("硬件", "芯片", "嵌入式", "电子", "电气")),
        ("测试/质量", ("测试", "质量", "qa")),
        ("数据", ("数据分析", "数据科学", "数据工程", "bi")),
        ("产品", ("产品经理", "产品运营", "产品")),
        ("运营", ("运营", "用户运营", "内容运营")),
        ("设计", ("设计", "ui", "ux", "视觉")),
        ("市场/销售", ("市场", "销售", "商务", "品牌")),
        ("制造/工艺", ("制造", "工艺", "生产")),
        ("供应链/采购", ("供应链", "采购", "物流")),
        ("职能", ("人力", "hr", "财务", "法务", "行政", "战略")),
    )
    for category, tokens in rules:
        if any(token in text for token in tokens):
            return category
    return "其他"


def normalize_city(value: str | None) -> str | None:
    if not value:
        return None
    text = str(value).replace("工作地点：", "").replace("工作地点:", "").strip()
    values = []
    for item in re.split(r"[/|,，、;；]+", text):
        item = item.strip()
        if item and item not in values:
            values.append(item)
    return " / ".join(values) or None


def _flatten_keys(d: dict[str, Any]) -> dict[str, Any]:
    return {re.sub(r"[^a-z0-9_]", "", str(k).lower()): v for k, v in d.items()}


def _pick(d: dict[str, Any], keys: list[str]):
    flat = _flatten_keys(d)
    normalized = [re.sub(r"[^a-z0-9_]", "", k.lower()) for k in keys]
    for key in normalized:
        if key in flat and flat[key] not in (None, "", [], {}):
            value = flat[key]
            if isinstance(value, (str, int, float)):
                return str(value).strip()
            if isinstance(value, list):
                return " / ".join(str(x) for x in value if x not in (None, ""))
            if isinstance(value, dict):
                for sub in ("name", "label", "value", "text"):
                    if sub in value:
                        return str(value[sub]).strip()
    return None


def looks_like_job(d: dict[str, Any]) -> bool:
    title = _pick(d, TITLE_KEYS)
    if not title or len(title) > 160:
        return False
    # Avoid common navigation objects.
    bad = {"首页", "home", "login", "登录", "关于我们", "about us"}
    if title.strip().lower() in bad:
        return False
    signals = sum(bool(_pick(d, ks)) for ks in [CITY_KEYS, NATURE_KEYS, CATEGORY_KEYS, DESC_KEYS, REQ_KEYS, URL_KEYS, ID_KEYS])
    return signals >= 1


def find_job_dicts(obj: Any, max_items: int = 5000) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    seen: set[str] = set()

    def walk(x: Any, depth: int = 0):
        if len(found) >= max_items or depth > 10:
            return
        if isinstance(x, dict):
            if looks_like_job(x):
                sig = json.dumps(x, ensure_ascii=False, sort_keys=True, default=str)
                digest = hashlib.sha1(sig.encode("utf-8", "ignore")).hexdigest()
                if digest not in seen:
                    seen.add(digest)
                    found.append(x)
            for value in x.values():
                if isinstance(value, (dict, list)):
                    walk(value, depth + 1)
        elif isinstance(x, list):
            for value in x[:2000]:
                walk(value, depth + 1)

    walk(obj)
    return found


def infer_category(title: str, raw_category: str | None = None) -> str | None:
    if raw_category:
        return raw_category
    rules = [
        ("算法/AI", ["算法", "机器学习", "深度学习", "ai", "大模型", "cv", "nlp"]),
        ("软件研发", ["开发", "后端", "前端", "客户端", "软件", "java", "c++", "golang", "python"]),
        ("硬件研发", ["硬件", "芯片", "嵌入式", "电气", "电子", "射频", "结构"]),
        ("产品", ["产品经理", "产品运营"]),
        ("数据", ["数据分析", "数据科学", "数据工程", "bi"]),
        ("测试/质量", ["测试", "质量", "qa"]),
        ("制造/工艺", ["制造", "工艺", "生产"]),
        ("供应链/采购", ["供应链", "采购", "物流"]),
        ("市场/销售", ["市场", "销售", "商务", "品牌"]),
        ("设计", ["设计", "ui", "ux", "视觉"]),
        ("职能", ["人力", "hr", "财务", "法务", "行政", "战略"]),
    ]
    low = title.lower()
    for category, keywords in rules:
        if any(k.lower() in low for k in keywords):
            return category
    return None


def _object_name(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, dict):
        for key in ("i18n_name", "name", "zh_cn", "label", "value"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
    return None


def _normalize_xiaomi_job(
    raw: dict[str, Any], source: dict[str, Any]
) -> dict[str, Any] | None:
    job_id = str(raw.get("id") or "").strip()
    title = _object_name(raw.get("title"))
    if not job_id or not title:
        return None

    city_items = raw.get("city_list") or raw.get("city_info_list_for_delivery") or []
    cities = []
    for item in city_items if isinstance(city_items, list) else []:
        name = _object_name(item)
        if name and name not in cities:
            cities.append(name)

    recruit_type = raw.get("recruit_type") or {}
    recruit_names = []
    for item in (recruit_type.get("parent"), recruit_type):
        name = _object_name(item)
        if name and name not in recruit_names:
            recruit_names.append(name)

    category = _object_name(raw.get("job_function")) or _object_name(
        raw.get("job_category")
    )
    job_info = raw.get("job_post_info") or {}
    degree = _object_name(job_info.get("required_degree"))

    combined_text = " ".join(
        str(value or "")
        for value in (title, raw.get("description"), raw.get("requirement"))
    )
    year_match = re.search(r"(20\d{2})\s*届", combined_text)
    short_year_match = re.search(r"(?<!\d)(\d{2})\s*届", combined_text)
    if year_match:
        graduate_year = year_match.group(1)
    elif short_year_match:
        graduate_year = f"20{short_year_match.group(1)}"
    else:
        graduate_year = None

    published_at = raw.get("publish_time")
    if isinstance(published_at, (int, float)):
        published_at = datetime.fromtimestamp(
            published_at / 1000, tz=timezone.utc
        ).isoformat()
    elif published_at is not None:
        published_at = str(published_at)

    base_url = source["url"].rstrip("/")
    apply_url = f"{base_url}/position/{job_id}/detail"
    requirements = raw.get("requirement")
    description = raw.get("description")
    canonical = {
        "company": source["company"],
        "title": title[:160],
        "city": normalize_city(" / ".join(cities) or None),
        "job_nature": normalize_job_nature(" / ".join(recruit_names), title, str(description or "")),
        "category": normalize_category(category, title, str(description or "")),
        "degree": normalize_degree(degree, str(requirements or "")),
        "graduate_year": graduate_year,
        "requirements": requirements,
        "description": description,
        "apply_url": apply_url,
        "source_url": source["url"],
        "source_job_id": job_id,
        "published_at": published_at,
    }
    digest_src = "|".join(
        str(canonical.get(key) or "")
        for key in (
            "company",
            "title",
            "city",
            "job_nature",
            "source_job_id",
            "apply_url",
        )
    )
    canonical["content_hash"] = hashlib.sha256(
        digest_src.encode("utf-8", "ignore")
    ).hexdigest()
    canonical["source_id"] = source["id"]
    canonical["raw"] = raw
    return canonical


def normalize_job(raw: dict[str, Any], source: dict[str, Any]) -> dict[str, Any] | None:
    if source.get("mode") == "xiaomi_jobs_browser":
        return _normalize_xiaomi_job(raw, source)

    title = _pick(raw, TITLE_KEYS)
    if not title:
        return None

    apply_url = _pick(raw, URL_KEYS)
    if apply_url:
        apply_url = urljoin(source["url"], apply_url)

    city = normalize_city(_pick(raw, CITY_KEYS))
    nature = _pick(raw, NATURE_KEYS)
    raw_category = _pick(raw, CATEGORY_KEYS)
    description = _pick(raw, DESC_KEYS)
    requirements = _pick(raw, REQ_KEYS)
    job_nature = normalize_job_nature(nature, title, " ".join(filter(None, (description, requirements))))
    category = normalize_category(raw_category, title, " ".join(filter(None, (description, requirements))))
    degree = normalize_degree(_pick(raw, DEGREE_KEYS), requirements or "")
    source_job_id = _pick(raw, ID_KEYS)
    published_at = _pick(raw, DATE_KEYS)

    # Conservative campus filter: the source URL itself is already a campus page.
    if source.get("campus_only") and nature:
        low = nature.lower()
        # Keep internships and graduate roles; drop clear social-hire labels.
        if any(x in low for x in ["社招", "social", "experienced"]) and not any(
            x in low for x in ["校园", "校招", "应届", "实习", "campus", "graduate", "intern"]
        ):
            return None

    canonical = {
        "company": source["company"],
        "title": title[:160],
        "city": city,
        "job_nature": job_nature,
        "category": category,
        "degree": degree,
        "graduate_year": None,
        "requirements": requirements,
        "description": description,
        "apply_url": apply_url or source["url"],
        "source_url": source["url"],
        "source_job_id": source_job_id,
        "published_at": published_at,
    }
    digest_src = "|".join(
        str(canonical.get(k) or "")
        for k in ("company", "title", "city", "job_nature", "source_job_id", "apply_url")
    )
    canonical["content_hash"] = hashlib.sha256(digest_src.encode("utf-8", "ignore")).hexdigest()
    canonical["source_id"] = source["id"]
    canonical["raw"] = raw
    return canonical
