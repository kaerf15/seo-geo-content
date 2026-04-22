"""checklist #6：文首/文末标注更新日期 or dateModified。"""

from __future__ import annotations

import re

from .common import CheckResult, Document


def check(doc: Document, rule: dict) -> list[CheckResult]:
    must = set(rule.get("must_include", []))
    if "update_date" not in must:
        return []

    head = doc.raw[:1000]
    tail = doc.raw[-1500:]
    patterns = [
        r"最近更新[\s：:]*\d{4}-\d{2}-\d{2}",
        r"更新日期[\s：:]*\d{4}-\d{2}-\d{2}",
        r"Last updated[\s:]*\d{4}-\d{2}-\d{2}",
        r"Updated[\s:]*\d{4}-\d{2}-\d{2}",
        r'"dateModified"\s*:\s*"\d{4}-\d{2}-\d{2}"',
    ]
    evidence = None
    for p in patterns:
        m = re.search(p, head) or re.search(p, tail)
        if m:
            evidence = m.group(0)
            break

    status = "PASS" if evidence else "FAIL"
    return [
        CheckResult(
            id="6",
            platform=doc.platform,
            item="更新日期信号",
            status=status,
            expected="文首/文末含 '最近更新'/'Last updated'/dateModified + YYYY-MM-DD",
            actual="命中" if evidence else "未命中",
            evidence=evidence or "",
        )
    ]
