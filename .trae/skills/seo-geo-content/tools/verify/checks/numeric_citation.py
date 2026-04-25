"""checklist #5：含数字段落就近给出处的比例 ≥ shared.numeric_citation_ratio。

判定口径：
- 段落（body_paragraphs）里含有数字字符（排除 markdown 的 1. / 2. 列表编号）
- 视为"含数字段落"；检查段内是否有 markdown 链接
- 比例 = 有链接的数字段 / 所有数字段
"""

from __future__ import annotations

import re

from .common import CheckResult, Document, has_number


def check(doc: Document, rule: dict, shared: dict) -> list[CheckResult]:
    must = set(rule.get("must_include", []))
    if "numeric_claims_with_citation" not in must:
        return []

    ratio_req = rule.get("thresholds", {}).get("numeric_citation_ratio") or shared.get("numeric_citation_ratio")

    blocks = doc.body_paragraphs()
    numeric_blocks = [b for b in blocks if has_number(b)]
    if not numeric_blocks:
        return [
            CheckResult(
                id="5",
                platform=doc.platform,
                item="数字就近链接比例",
                status="SKIP",
                expected=f"比例 ≥ {ratio_req}",
                actual="未发现含数字段落",
            )
        ]

    with_link = sum(1 for b in numeric_blocks if re.search(r"\[[^\]]+\]\([^)]+\)", b))
    ratio = with_link / len(numeric_blocks)
    status = "PASS" if ratio >= ratio_req else "FAIL"
    return [
        CheckResult(
            id="5",
            platform=doc.platform,
            item="数字就近链接比例",
            status=status,
            expected=f"比例 ≥ {ratio_req}",
            actual=f"{with_link}/{len(numeric_blocks)} = {ratio:.2f}",
        )
    ]
