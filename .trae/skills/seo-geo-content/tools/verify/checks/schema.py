"""checklist #7 / #7b：JSON-LD Schema 建议齐全。"""

from __future__ import annotations

import re

from .common import CheckResult, Document


def check(doc: Document, rule: dict, shared: dict) -> list[CheckResult]:
    must = set(rule.get("must_include", []))
    if "schema_suggestion" not in must:
        return []

    if doc.platform == "landing_page":
        required = shared.get("schema_landing", [])
        check_id = "7"
    else:
        required = shared.get("schema_blog_required", [])
        check_id = "7b"

    actual_types = set(re.findall(r'"@type"\s*:\s*"([A-Za-z]+)"', doc.raw))
    missing = [t for t in required if t not in actual_types]
    status = "PASS" if not missing else "FAIL"
    return [
        CheckResult(
            id=check_id,
            platform=doc.platform,
            item="Schema 建议",
            status=status,
            expected=f"必含 {required}",
            actual=f"发现 {sorted(actual_types)}",
            evidence=f"缺：{missing}" if missing else "全部命中",
        )
    ]
