"""checklist #2：H2/H3 问题式标题比例。"""

from __future__ import annotations

from .common import CheckResult, Document, is_question_heading


def check(doc: Document, rule: dict) -> list[CheckResult]:
    thresholds = rule.get("thresholds", {})
    ratio_req = thresholds.get("question_style_headings_ratio")
    if ratio_req is None:
        return []

    h23 = [t for lvl, t in doc.headings if lvl in (2, 3)]
    if not h23:
        return [
            CheckResult(
                id="2",
                platform=doc.platform,
                item="H2/H3 问题式比例",
                status="FAIL",
                expected=f"比例 ≥ {ratio_req}",
                actual="0（未找到 H2/H3）",
            )
        ]

    q_count = sum(1 for t in h23 if is_question_heading(t))
    ratio = q_count / len(h23)
    status = "PASS" if ratio >= ratio_req else "FAIL"
    return [
        CheckResult(
            id="2",
            platform=doc.platform,
            item="H2/H3 问题式比例",
            status=status,
            expected=f"比例 ≥ {ratio_req}",
            actual=f"{q_count}/{len(h23)} = {ratio:.2f}",
            evidence="；".join(h23[:3]),
        )
    ]
