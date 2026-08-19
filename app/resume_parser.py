from __future__ import annotations

import base64
import re
import zlib
import zipfile
from io import BytesIO
from xml.etree import ElementTree as ET


MAX_RESUME_BYTES = 10 * 1024 * 1024


def _docx_text(data: bytes) -> str:
    with zipfile.ZipFile(BytesIO(data)) as archive:
        xml = archive.read("word/document.xml")
    root = ET.fromstring(xml)
    return "\n".join(
        "".join(node.text or "" for node in paragraph.iter() if node.tag.endswith("}t"))
        for paragraph in root.iter()
        if paragraph.tag.endswith("}p")
    ).strip()


def _pdf_text(data: bytes) -> str:
    chunks: list[str] = []
    for match in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        stream = match.group(1)
        try:
            stream = zlib.decompress(stream)
        except zlib.error:
            pass
        for value in re.findall(rb"\((.*?)(?<!\\)\)", stream, re.S):
            value = value.replace(rb"\\(", b"(").replace(rb"\\)", b")").replace(rb"\\n", b"\n")
            chunks.append(value.decode("utf-8", "ignore"))
    return "\n".join(chunks).strip()


def extract_resume_text(filename: str, data: bytes) -> str:
    if len(data) > MAX_RESUME_BYTES:
        raise ValueError("resume_file_too_large")
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix == "docx":
        text = _docx_text(data)
    elif suffix == "pdf":
        text = _pdf_text(data)
    else:
        raise ValueError("unsupported_resume_format")
    if not text:
        raise ValueError("resume_text_not_extracted")
    return text[:100_000]


def extract_candidate_profile(text: str) -> dict:
    """Produce a reviewable candidate profile; it is not treated as user intent."""
    degree = next((value for value in ("博士", "硕士", "本科", "Master", "Bachelor", "PhD") if value.lower() in text.lower()), None)
    years = re.findall(r"20\d{2}", text)
    skill_vocab = [
        "Python", "Java", "C++", "Go", "SQL", "机器学习", "深度学习", "算法", "数据分析",
        "JavaScript", "React", "Linux", "Docker", "PyTorch", "TensorFlow",
    ]
    skills = [skill for skill in skill_vocab if skill.lower() in text.lower()]
    return {
        "education": degree,
        "graduation_year_candidates": sorted(set(years)),
        "skills": skills,
        "evidence_text_length": len(text),
        "needs_user_confirmation": True,
        "intent_fields": {
            "target_roles": [],
            "adjacent_roles": [],
            "target_companies": [],
            "excluded_roles": [],
        },
    }


def parse_resume_base64(filename: str, encoded: str) -> dict:
    try:
        data = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise ValueError("invalid_resume_base64") from exc
    text = extract_resume_text(filename, data)
    return {"filename": filename, "profile": extract_candidate_profile(text), "text_preview": text[:2000]}
