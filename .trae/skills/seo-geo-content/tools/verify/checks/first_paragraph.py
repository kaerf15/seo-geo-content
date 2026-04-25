"""checklist #1：首段直答字数命中 first_paragraph_direct_answer。"""

from __future__ import annotations

import re

from .common import CheckResult, Document


def check(doc: Document, rule: dict, shared: dict) -> list[CheckResult]:
    thresholds = rule.get("thresholds", {})
    if "first_paragraph_direct_answer" not in thresholds and "first_paragraph_direct_answer" not in shared:
        return []

    cfg = thresholds.get("first_paragraph_direct_answer") or shared.get("first_paragraph_direct_answer")
    min_chars = cfg.get("min_chars")
    max_chars = cfg.get("max_chars")

    section = doc.section_after([r"首段直答", r"direct\s+answer"])
    if section is None:
        body = doc.body_paragraphs()
        first = body[0] if body else ""
    else:
        first = ""
        for block in re.split(r"\n\s*\n", section):
            lines = [ln for ln in block.splitlines() if not ln.lstrip().startswith(">")]
            text = "\n".join(lines).strip()
            if text:
                first = text
                break

    actual_zh = len(re.findall(r"[\u4e00-\u9fff]", first))
    actual_en = len(re.findall(r"[A-Za-z][A-Za-z\-']*", first))
    actual = max(actual_zh, actual_en)
    status = "PASS" if min_chars <= actual <= max_chars else "FAIL"

    return [
        CheckResult(
            id="1",
            platform=doc.platform,
            item="首段直答",
            status=status,
            expected=f"{min_chars}–{max_chars}（按 shared.first_paragraph_direct_answer）",
            actual=f"{actual}（中文 {actual_zh} / 英文 {actual_en}）",
            evidence=first[:80].replace("\n", " ") + ("..." if len(first) > 80 else ""),
        )
    ]
