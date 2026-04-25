"""checklist #4：权威引用数量命中 shared.authority_citations_min。"""

from __future__ import annotations

from .common import CheckResult, Document, is_authority_link


def check(doc: Document, rule: dict, shared: dict, authority_fragments: list[str]) -> list[CheckResult]:
    must = set(rule.get("must_include", []))
    if "at_least_one_authority_citation" not in must:
        return []

    min_required = rule.get("thresholds", {}).get("authority_citations_min") or shared.get("authority_citations_min")
    if isinstance(min_required, dict):  # 未解引用兜底
        min_required = shared["authority_citations_min"]

    hits: list[tuple[str, str]] = [
        (text, url) for text, url in doc.links if is_authority_link(url, authority_fragments)
    ]
    status = "PASS" if len(hits) >= min_required else "FAIL"
    return [
        CheckResult(
            id="4",
            platform=doc.platform,
            item="权威引用",
            status=status,
            expected=f"≥ {min_required}（命中 rules/authority.txt）",
            actual=str(len(hits)),
            evidence="；".join(url for _, url in hits[:3]),
        )
    ]
