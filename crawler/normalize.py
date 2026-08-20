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

MAJOR_RULES = (
    ("计算机类", ("计算机科学", "计算机技术", "计算机相关", "计算机类", "计算机专业", "计算机")),
    ("软件工程", ("软件工程",)),
    ("人工智能", ("人工智能", "机器学习", "智能科学")),
    ("模式识别", ("模式识别",)),
    ("信息工程", ("信息工程", "电子信息工程", "信息与通信工程")),
    ("通信工程", ("通信工程", "通信相关")),
    ("自动化类", ("自动化", "控制科学", "控制工程")),
    ("数学类", ("数学", "应用数学")),
    ("统计学类", ("统计学", "应用统计")),
    ("数据科学", ("数据科学", "大数据")),
    ("电子科学与技术", ("电子科学", "微电子", "集成电路")),
    ("电气工程", ("电气工程", "电气相关")),
    ("机械类", ("机械工程", "机械设计", "机械相关")),
    ("材料类", ("材料科学", "材料工程", "材料相关")),
    ("土木工程", ("土木工程",)),
    ("建筑类", ("建筑学", "建筑设计", "城乡规划")),
    ("工业工程", ("工业工程",)),
    ("化学化工类", ("化学", "化工", "应用化学")),
    ("生物医药类", ("生物", "医学", "药学")),
    ("经济学类", ("经济学", "金融学", "国际经济")),
    ("工商管理类", ("工商管理", "市场营销", "人力资源管理")),
    ("财会类", ("会计学", "财务管理", "审计学")),
    ("法学类", ("法学", "法律")),
    ("语言文学类", ("汉语言文学", "外国语言", "英语专业", "翻译专业")),
    ("新闻传播类", ("新闻学", "传播学", "广告学")),
    ("设计学类", ("视觉传达", "工业设计", "交互设计", "设计学")),
)

COUNTRY_ALIASES = {
    "中国": "中国", "china": "中国", "cn": "中国",
    "日本": "日本", "japan": "日本",
    "新加坡": "新加坡", "singapore": "新加坡",
    "英国": "英国", "uk": "英国", "united kingdom": "英国",
    "法国": "法国", "france": "法国",
    "德国": "德国", "germany": "德国",
    "马来西亚": "马来西亚", "malaysia": "马来西亚",
    "泰国": "泰国", "thailand": "泰国",
    "土耳其": "土耳其", "turkey": "土耳其",
    "巴基斯坦": "巴基斯坦", "pakistan": "巴基斯坦",
    "印度": "印度", "india": "印度",
    "阿联酋": "阿联酋", "uae": "阿联酋", "united arab emirates": "阿联酋",
    "越南": "越南", "vietnam": "越南",
    "西班牙": "西班牙", "spain": "西班牙",
    "菲律宾": "菲律宾", "philippines": "菲律宾",
    "韩国": "韩国", "south korea": "韩国", "korea": "韩国",
    "印度尼西亚": "印度尼西亚", "indonesia": "印度尼西亚",
}

INTERNATIONAL_CITY_COUNTRIES = {
    "东京": "日本", "tokyo": "日本",
    "新加坡": "新加坡", "singapore": "新加坡",
    "伦敦": "英国", "london": "英国",
    "巴黎": "法国", "paris": "法国",
    "杜塞尔多夫": "德国", "düsseldorf": "德国", "dusseldorf": "德国",
    "吉隆坡": "马来西亚", "kuala lumpur": "马来西亚",
    "曼谷": "泰国", "bangkok": "泰国",
    "伊斯坦布尔": "土耳其", "istanbul": "土耳其",
    "拉合尔": "巴基斯坦", "lahore": "巴基斯坦",
    "班加罗尔": "印度", "bangalore": "印度", "bengaluru": "印度",
    "迪拜": "阿联酋", "dubai": "阿联酋",
    "胡志明": "越南", "ho chi minh": "越南",
    "马德里": "西班牙", "madrid": "西班牙",
    "马尼拉": "菲律宾", "manila": "菲律宾",
    "首尔": "韩国", "seoul": "韩国",
    "雅加达": "印度尼西亚", "jakarta": "印度尼西亚",
}


def normalize_job_nature(raw_nature: str | None, title: str = "", description: str = "") -> str | None:
    """Collapse source labels to the product's only two recruitment types."""
    text = " ".join(str(value or "") for value in (raw_nature, title, description)).lower()
    internship_tokens = ("实习", "实习生", "intern", "internship")
    full_time_tokens = (
        "全职", "正式", "校招", "校园招聘", "应届", "graduate", "new grad", "full-time", "full time"
    )
    excluded_tokens = ("社招", "社会招聘", "experienced hire", "兼职", "part-time", "外包", "劳务")
    # A source-specific channel can explicitly identify a graduate/full-time
    # record while its requirements mention an internship or outsourcing
    # experience.  The explicit listing nature wins over incidental text.
    explicit_nature = str(raw_nature or "").lower()
    if any(token in explicit_nature for token in full_time_tokens) and not any(token in explicit_nature for token in internship_tokens):
        return JOB_NATURE_FULL_TIME
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


def normalize_location_name(value: str | None) -> str | None:
    """Normalize one evidenced location to a stable city-level filter value."""
    text = str(value or "").strip().replace("·", "-")
    if not text:
        return None
    municipality = {
        "北京市": "北京", "上海市": "上海", "天津市": "天津", "重庆市": "重庆",
        "香港特别行政区": "香港", "澳门特别行政区": "澳门",
    }
    parts = [part.strip() for part in text.split("-") if part.strip()]
    if len(parts) >= 3 and parts[-1].endswith(("区", "县")):
        candidate = parts[-2]
    elif len(parts) >= 2:
        candidate = parts[-1]
    else:
        candidate = text
    candidate = municipality.get(candidate, candidate)
    if candidate.endswith("市") and len(candidate) > 1:
        candidate = candidate[:-1]
    return candidate.strip() or None


def split_work_locations(value: str | None) -> list[str]:
    """Split a source's multi-location text into unique normalized locations."""
    result: list[str] = []
    for item in re.split(r"[/|,，、;；\n]+", str(value or "")):
        location = normalize_location_name(item)
        if location and location not in result:
            result.append(location)
    return result


def split_location_records(value: str | None) -> list[dict[str, str]]:
    """Return evidenced locations as country/province/city records."""
    raw_items = [item.strip() for item in re.split(r"[/|,，、;；\n]+", str(value or "")) if item.strip()]
    forced_country = None
    if len(raw_items) == 2 and raw_items[1].lower() in COUNTRY_ALIASES:
        forced_country = COUNTRY_ALIASES[raw_items[1].lower()]
        raw_items = raw_items[:1]
    records: list[dict[str, str]] = []
    municipalities = {"北京", "上海", "天津", "重庆"}
    for raw in raw_items:
        cleaned = raw.replace("·", "-").strip()
        parts = [part.strip() for part in cleaned.split("-") if part.strip()]
        country = forced_country or ""
        province = ""
        city = ""
        if parts and parts[0].lower() in COUNTRY_ALIASES:
            country = COUNTRY_ALIASES[parts.pop(0).lower()]
        if len(parts) >= 2 and parts[0].endswith(("省", "自治区")):
            country = country or "中国"
            province = re.sub(r"(省|壮族自治区|回族自治区|维吾尔自治区|自治区)$", "", parts[0])
            city = parts[1]
        elif len(parts) >= 2 and parts[0] in ("北京市", "上海市", "天津市", "重庆市"):
            country = country or "中国"
            province = parts[0][:-1]
            city = parts[1]
        elif parts:
            city = parts[-1]
        city = normalize_location_name(city)
        city_key = str(city or "").lower()
        if not country:
            country = INTERNATIONAL_CITY_COUNTRIES.get(city_key, "中国")
        if not province and city in municipalities:
            province = city
        if city:
            record = {"country": country, "province": province, "city": city}
            if record not in records:
                records.append(record)
    return records


def extract_major_requirements(requirements: str | None) -> list[str]:
    """Extract controlled academic majors only from explicit official evidence."""
    result: list[str] = []
    for line in re.split(r"[\r\n；;]+", str(requirements or "")):
        line = line.strip()
        if not line or not any(token in line for token in ("专业", "学科", "背景", "相关方向")):
            continue
        low = line.lower()
        for major, aliases in MAJOR_RULES:
            if any(alias.lower() in low for alias in aliases) and major not in result:
                result.append(major)
    return result


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
