"""checklist #11：所有数字/结论可在 facts.md 追溯（或已标'暂无'）。

由于全自动追溯会高误报，这里实现半自动：
- 抽取每个 deliverable 中的"具体数字短语"（如 '12 年' / '95% 良品率' / '$1.2M'）
- 在 facts.md 里做字符串包含查找
- 命中则 PASS，未命中则 FAIL（Agent 需检查是否为'暂无'已确认）
"""

from __future__ import annotations

import pathlib
import re

from .common import CheckResult, Document


NUMBER_PHRASE = re.compile(
    r"(\d+(?:[\.,]\d+)?\s*(?:%|％|年|月|日|周|天|小时|分钟|秒|万|千|百|亿|美元|元|欧|英镑|USD|CNY|MOQ|%|pcs|件|单|人|客户))",
    re.I,
)


def check(docs: list[Document], facts_path: pathlib.Path | None) -> list[CheckResult]:
    if facts_path is None or not facts_path.exists():
        return [
            CheckResult(
                id="11",
                platform="__global__",
                item="事实锚定",
                status="SKIP",
                expected="每个数字/结论可在 facts.md 追溯",
                actual="未找到 facts.md（Agent 请手动核对）",
            )
        ]

    facts_text = facts_path.read_text(encoding="utf-8")
    results: list[CheckResult] = []

    for doc in docs:
        phrases = set(NUMBER_PHRASE.findall(doc.raw))
        missing: list[str] = []
        for phrase in phrases:
            normalized = phrase.replace(" ", "")
            if normalized not in facts_text.replace(" ", "") and phrase not in facts_text:
                missing.append(phrase)
        status = "PASS" if not missing else "FAIL"
        results.append(
            CheckResult(
                id="11",
                platform=doc.platform,
                item="事实锚定（数字短语可回溯）",
                status=status,
                expected="所有具体数字短语在 .workspace/facts.md 中可找到（或用户已确认为'暂无'）",
                actual=f"deliverable 数字短语 {len(phrases)} 条；未追溯 {len(missing)} 条",
                evidence="未追溯样本：" + "、".join(missing[:3]) if missing else "全部命中",
            )
        )
    return results
