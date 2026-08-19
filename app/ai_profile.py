from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import httpx

from app.resume_parser import extract_candidate_profile


def _load_local_env() -> None:
    """Load the project .env without requiring an extra dependency."""
    env_path = Path(".env")
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_local_env()


SYSTEM_PROMPT = """你是校招简历结构化助手。只提取简历中明确出现的能力证据，不推断用户求职意愿。
请只返回一个严格的 JSON 对象，字段必须为：education（字符串或 null）、graduation_year_candidates（年份字符串数组）、skills（技能字符串数组）、projects（对象数组，每项包含 title 和 description）、experience（对象数组，每项包含 title 和 description）、uncertainties（不确定内容字符串数组）。
如果信息没有明确出现，使用 null、空数组，或把疑点放入 uncertainties。
不要生成录取概率、匹配分数、用户目标岗位、目标公司、目标城市或排除岗位；不要添加 target_roles、target_companies、target_cities、excluded_roles 等字段。"""


def _json_from_text(content: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", content, re.S)
    if not match:
        raise ValueError("ai_response_not_json")
    result = json.loads(match.group(0))
    if not isinstance(result, dict):
        raise ValueError("ai_response_not_object")
    return result


def _validate_provider_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Validate the narrow external schema and reject inferred intent."""
    list_fields = {"graduation_year_candidates", "skills", "projects", "experience", "uncertainties"}
    for field in list_fields:
        if field in profile and not isinstance(profile[field], list):
            raise ValueError(f"ai_response_invalid_field:{field}")
    forbidden_intent = {"target_roles", "adjacent_roles", "target_companies", "target_cities", "excluded_roles"}
    if forbidden_intent.intersection(profile):
        raise ValueError("ai_response_contains_job_seeking_intent")
    return profile


def analyze_resume_text(text: str, external_consent: bool = False) -> dict[str, Any]:
    provider = os.getenv("AI_PROFILE_PROVIDER", "rules").lower()
    if provider in {"rules", "local"}:
        profile = extract_candidate_profile(text)
        profile["provider"] = "local_rules"
        profile["needs_user_confirmation"] = True
        return profile
    if provider != "openai_compatible":
        raise RuntimeError("unsupported_ai_profile_provider")
    if not external_consent:
        raise PermissionError("external_ai_consent_required")

    base_url = os.getenv("AI_BASE_URL", "").rstrip("/")
    api_key = os.getenv("AI_API_KEY", "")
    model = os.getenv("AI_MODEL", "")
    if not base_url or not api_key or not model:
        raise RuntimeError("ai_provider_not_configured")
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text[:100_000]},
        ],
    }
    try:
        with httpx.Client(timeout=45) as client:
            response = client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        content = data["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        # AI is an optional enrichment layer.  A provider outage must not
        # block manual profile editing or the complete job-search channel.
        raise RuntimeError("ai_provider_request_failed") from exc
    profile = _validate_provider_profile(_json_from_text(content))
    profile["provider"] = "openai_compatible"
    profile["needs_user_confirmation"] = True
    profile["external_ai_used"] = True
    return profile
