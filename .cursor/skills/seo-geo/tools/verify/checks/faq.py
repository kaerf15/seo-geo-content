"""checklist #3：FAQ 条数与单条字数命中 shared.faq。

策略：
- 定位 H2 含 "FAQ" 或 "常见问题"
- 之后的 H3 视为一条 FAQ
- 单条字数 = 该 H3 到下一个 H3 之间的正文长度（按 effective length 规则）
"""

from __future__ import annotations

import re

from .common import CheckResult, Document


def check(doc: Document, rule: dict) -> list[CheckResult]:
    thresholds = rule.get("thresholds", {})
    faq_cfg = thresholds.get("faq")
    if faq_cfg is None:
        return []

    count_min = faq_cfg["count_min"]
    count_max = faq_cfg["count_max"]
    per_item = faq_cfg["per_item"]

    section = doc.section_after([r"\bFAQ\b", r"常见问题"])
    if section is None:
        return [
            CheckResult(
                id="3",
                platform=doc.platform,
                item="FAQ",
                status="FAIL",
                expected=f"条数 {count_min}–{count_max}，单条 {per_item['min_chars']}–{per_item['max_chars']}",
                actual="未找到 FAQ 段",
            )
        ]

    items = re.split(r"^###\s+", section, flags=re.M)[1:]
    n = len(items)
    count_ok = count_min <= n <= count_max

    per_item_lens = []
    failing_items: list[str] = []
    for item_text in items:
        first_line, _, body = item_text.partition("\n")
        zh = len(re.findall(r"[\u4e00-\u9fff]", body))
        en = len(re.findall(r"[A-Za-z][A-Za-z\-']*", body))
        length = max(zh, en)
        per_item_lens.append(length)
        if not (per_item["min_chars"] <= length <= per_item["max_chars"]):
            failing_items.append(f"{first_line.strip()[:20]}(len={length})")

    per_ok = len(failing_items) == 0
    status = "PASS" if count_ok and per_ok else "FAIL"
    return [
        CheckResult(
            id="3",
            platform=doc.platform,
            item="FAQ 条数 + 单条字数",
            status=status,
            expected=f"条数 {count_min}–{count_max}；单条 {per_item['min_chars']}–{per_item['max_chars']}（effective length）",
            actual=f"条数={n}；长度列表={per_item_lens}",
            evidence="超限条：" + "、".join(failing_items[:3]) if failing_items else "全部命中",
        )
    ]
