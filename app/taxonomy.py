from __future__ import annotations

import re


ROLE_RULES = [
    ("algorithm_ai", ["算法", "人工智能", "机器学习", "深度学习", "computer vision", "nlp", "algorithm", "machine learning", "ai"]),
    ("software_rnd", ["后端", "前端", "软件", "开发", "研发", "java", "python", "golang", "c++", "backend", "frontend", "developer"]),
    ("hardware", ["硬件", "芯片", "嵌入式", "电子", "电气", "射频", "hardware", "embedded"]),
    ("testing_quality", ["测试", "质量", "qa", "quality", "test engineer"]),
    ("data", ["数据分析", "数据科学", "数据工程", "商业分析", "data analyst", "data science", "data engineer"]),
    ("product", ["产品经理", "产品", "product manager", "product" ]),
    ("operations", ["运营", "operation", "项目管理", "项目经理"]),
    ("sales", ["销售", "售前", "商务", "客户成功", "sales", "business development"]),
    ("marketing", ["市场", "品牌", "公关", "marketing", "brand"]),
    ("design", ["设计", "交互", "视觉", "ui", "ux", "design"]),
    ("supply_chain", ["供应链", "采购", "物流", "计划", "supply chain", "procurement"]),
    ("manufacturing", ["制造", "工艺", "生产", "质量工程", "manufacturing", "process"]),
    ("functional", ["人力", "财务", "法务", "行政", "审计", "hr", "finance", "legal"]),
]


def classify_job(title: str | None, category: str | None = None, description: str | None = None) -> tuple[str | None, float, list[str]]:
    # A long description often mentions adjacent technologies (for example,
    # an HR or operations role may mention AI tools).  Resolve the concrete
    # title first, then the controlled category, and use description only as a
    # fallback.  This prevents incidental keywords from changing the role
    # family shown to users or used by recommendations.
    title_text = str(title or "").lower()
    category_text = str(category or "").lower()
    description_text = str(description or "").lower()

    def _match(text: str) -> tuple[str | None, float, list[str]]:
        for family, keywords in ROLE_RULES:
            hits = [keyword for keyword in keywords if keyword.lower() in text]
            if hits:
                confidence = min(0.98, 0.62 + 0.1 * len(hits))
                return family, confidence, hits[:5]
        return None, 0.0, []

    family, confidence, evidence = _match(title_text)
    if family:
        return family, confidence, evidence

    category_family = {
        "算法/ai": "algorithm_ai",
        "软件研发": "software_rnd",
        "硬件研发": "hardware",
        "测试/质量": "testing_quality",
        "数据": "data",
        "产品": "product",
        "运营": "operations",
        "市场/销售": "sales",
        "设计": "design",
        "供应链/采购": "supply_chain",
        "制造/工艺": "manufacturing",
        "职能": "functional",
    }
    if category_text in category_family:
        return category_family[category_text], 0.9, [category_text]

    family, confidence, evidence = _match(description_text)
    if family:
        return family, confidence, evidence

    return None, 0.0, []
