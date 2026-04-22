"""checklist #8 / #8b / #8c：字数 / 时长 / 条目数。

时长 / 条目数的精确判断需要结合 short_video / twitter_thread 骨架做启发式判断：
- short_video：找"分镜表"末行时间段上限；若无则标 SKIP
- twitter_thread：按 "^\\d+/" 行数统计
"""

from __future__ import annotations

import re

from .common import CheckResult, Document


def check(doc: Document, rule: dict) -> list[CheckResult]:
    results: list[CheckResult] = []

    if "word_count" in rule:
        wc = rule["word_count"]
        actual = doc.effective_length
        status = "PASS" if wc["min"] <= actual <= wc["max"] else "FAIL"
        results.append(
            CheckResult(
                id="8",
                platform=doc.platform,
                item="字数",
                status=status,
                expected=f"{wc['min']}–{wc['max']}（按 {doc.platform}.word_count；中文字符数/英文词数取大）",
                actual=str(actual),
                evidence=f"中文字符 {doc.chinese_chars} / 英文词 {doc.english_words}",
            )
        )

    if "duration_sec" in rule:
        dur = rule["duration_sec"]
        actual_sec = _parse_duration_from_shot_table(doc.raw)
        if actual_sec is None:
            results.append(
                CheckResult(
                    id="8b",
                    platform=doc.platform,
                    item="时长",
                    status="SKIP",
                    expected=f"{dur['min']}–{dur['max']}s（按 {doc.platform}.duration_sec）",
                    actual="未解析出分镜表末行时长",
                    evidence="需人工确认分镜表结构",
                )
            )
        else:
            status = "PASS" if dur["min"] <= actual_sec <= dur["max"] else "FAIL"
            results.append(
                CheckResult(
                    id="8b",
                    platform=doc.platform,
                    item="时长",
                    status=status,
                    expected=f"{dur['min']}–{dur['max']}s",
                    actual=f"{actual_sec}s",
                    evidence="从分镜表时间列末行推出",
                )
            )

    if "items" in rule:
        items = rule["items"]
        n = _count_thread_items(doc.raw)
        status = "PASS" if items["min"] <= n <= items["max"] else "FAIL"
        rec_min = items.get("recommended_min", items["min"])
        rec_max = items.get("recommended_max", items["max"])
        in_rec = rec_min <= n <= rec_max
        results.append(
            CheckResult(
                id="8c",
                platform=doc.platform,
                item="线程条目数",
                status=status,
                expected=f"硬范围 {items['min']}–{items['max']}；推荐 {rec_min}–{rec_max}",
                actual=str(n),
                evidence=f"{'在推荐区间' if in_rec else '在硬范围但超出推荐区间'}",
            )
        )

    return results


def _parse_duration_from_shot_table(raw: str) -> int | None:
    candidates = re.findall(r"(\d+)\s*[-–~]\s*(\d+)\s*s", raw)
    if not candidates:
        return None
    return max(int(e) for _, e in candidates)


def _count_thread_items(raw: str) -> int:
    return len(re.findall(r"^\s*\d+/\s", raw, flags=re.M))
