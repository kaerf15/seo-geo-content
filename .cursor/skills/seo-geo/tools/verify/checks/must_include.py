"""checklist #9：逐一核对 must_include 结构块。

策略：
- 已由独立 check 模块完全覆盖的 item → 跳过（跳过表来自 checklist.yaml 的 covered_must_include 字段，**SSOT**）
- 本模块内有 heuristic 的 item → 直接判 PASS/FAIL
- 未知 id 一律 SKIP 并记录，供 Agent 人工核对
"""

from __future__ import annotations

import re

from .common import CheckResult, Document


HEADING_PATTERNS: dict[str, list[str]] = {
    "faq_section": [r"\bFAQ\b", r"常见问题"],
    "internal_cta": [r"下一步", r"询盘", r"CTA"],
    "references": [r"参考", r"引用", r"References"],
    "author_bio": [r"作者简介", r"About the author"],
    "author_note": [r"作者", r"About the author"],
    "tldr": [r"TL;DR"],
    "closing_framework_or_list": [r"framework", r"checklist", r"清单", r"框架"],
    "action_checklist": [r"行动清单", r"action\s+checklist"],
    "cta": [r"CTA", r"关注", r"咨询", r"领资料"],
    "hook_opening": [r"开头", r"hook"],
    "three_to_five_h2": [],  # 通过 H2 计数判定
}


def check(doc: Document, rule: dict, covered_items: set[str] | None = None) -> list[CheckResult]:
    """逐一核对本平台的 must_include 结构块。

    参数：
    - covered_items：由 checklist.yaml 汇总的"已由独立 check 覆盖"的 item 名集合；传 None 时退化为空集
      （跳过表的 SSOT 在 checklist.yaml；本模块不再维护硬编码跳过表）
    """
    must = rule.get("must_include", [])
    results: list[CheckResult] = []
    skip_set = covered_items or set()

    for item in must:
        if item in skip_set:
            continue

        status, actual = _judge_item(doc, rule, item)
        results.append(
            CheckResult(
                id="9",
                platform=doc.platform,
                item=f"must_include/{item}",
                status=status,
                expected=f"must_include 含 {item}",
                actual=actual,
            )
        )
    return results


def _judge_item(doc: Document, rule: dict, item: str) -> tuple[str, str]:
    t = doc.raw

    # 优先查 HEADING_PATTERNS 表（存在性型判定）
    if item in HEADING_PATTERNS and HEADING_PATTERNS[item]:
        section = doc.section_after(HEADING_PATTERNS[item])
        if section is None:
            return ("FAIL", f"未找到标题匹配 {HEADING_PATTERNS[item]} 的段")
        return ("PASS", f"找到段（长度 {len(section)} 字符）")

    if item == "hook_first_line":
        lines = [ln for ln in t.splitlines() if ln.strip()]
        for ln in lines:
            if ln.startswith("#"):
                continue
            if ln.startswith(">"):
                continue
            max_chars = rule.get("thresholds", {}).get("hook_first_line_max_chars")
            length = max(len(re.findall(r"[\u4e00-\u9fff]", ln)), len(re.findall(r"[A-Za-z][A-Za-z\-']*", ln)))
            if max_chars:
                return ("PASS" if length <= max_chars else "FAIL", f"首行 effective len={length}; 上限={max_chars}")
            return ("PASS", f"首行 {length} 字")
        return ("FAIL", "未找到非标题首行")

    if item == "numbered_list_or_checklist":
        has_num = bool(re.search(r"^\s*\d+[\.\)]\s", t, flags=re.M)) or bool(re.search(r"^\s*[-*]\s\[[ x]\]", t, flags=re.M))
        has_emoji_num = bool(re.search(r"[1-9]\ufe0f?\u20e3|\u0031\ufe0f\u20e3", t))
        return ("PASS" if has_num or has_emoji_num else "FAIL", "命中" if has_num or has_emoji_num else "未命中")

    if item == "scene_or_first_person":
        return ("PASS" if re.search(r"(我|我的|我们|I\s|I'm|my\s|we\s)", t, re.I) else "FAIL", "检测第一人称 / 场景语气")

    if item == "tags":
        cfg = rule.get("thresholds", {}).get("tags", {})
        tags = re.findall(r"#[\w\u4e00-\u9fff]+", t)
        n = len(tags)
        if cfg:
            ok = cfg["min"] <= n <= cfg["max"]
            return ("PASS" if ok else "FAIL", f"tags={n}; 需 {cfg['min']}–{cfg['max']}")
        return ("PASS" if n > 0 else "FAIL", f"tags={n}")

    if item == "hashtags":
        cfg = rule.get("thresholds", {}).get("hashtags", {})
        tags = re.findall(r"#[A-Za-z][\w]*", t)
        n = len(tags)
        if cfg:
            ok = cfg["min"] <= n <= cfg["max"]
            return ("PASS" if ok else "FAIL", f"hashtags={n}; 需 {cfg['min']}–{cfg['max']}")
        return ("PASS" if n > 0 else "FAIL", f"hashtags={n}")

    if item == "cover_brief":
        return ("PASS" if re.search(r"(封面|cover)", t, re.I) else "FAIL", "找 '封面'/'cover'")

    if item == "internal_links":
        cfg = rule.get("thresholds", {}).get("internal_links")
        if isinstance(cfg, dict):
            rel_links = [u for _, u in doc.links if not u.startswith(("http://", "https://"))]
            n = len(rel_links)
            ok = cfg["min"] <= n <= cfg["max"]
            return ("PASS" if ok else "FAIL", f"内链 {n}; 需 {cfg['min']}–{cfg['max']}")
        return ("SKIP", "thresholds.internal_links 未定义")

    if item == "three_to_five_h2":
        cfg = rule.get("thresholds", {}).get("h2_count", {})
        h2_count = sum(1 for lvl, _ in doc.headings if lvl == 2)
        ok = cfg["min"] <= h2_count <= cfg["max"] if cfg else h2_count >= 3
        return ("PASS" if ok else "FAIL", f"H2={h2_count}")

    if item == "conclusion_first":
        max_pts = rule.get("thresholds", {}).get("conclusion_first_max_points", 3)
        section = doc.section_after([r"先给结论", r"conclusion"])
        if section is None:
            return ("FAIL", "未找到'先给结论'段")
        pts = len(re.findall(r"^\s*\d+\.", section, flags=re.M))
        return ("PASS" if 1 <= pts <= max_pts else "FAIL", f"结论条数 {pts}")

    if item == "takeaway_bullets":
        cfg = rule.get("thresholds", {}).get("takeaway_bullets", {})
        section = doc.section_after([r"Takeaway"])
        if not section:
            return ("FAIL", "未找到 Takeaway 段")
        pts = len(re.findall(r"^\s*(\d+\.|[-*])\s", section, flags=re.M))
        ok = cfg["min"] <= pts <= cfg["max"] if cfg else pts > 0
        return ("PASS" if ok else "FAIL", f"takeaway={pts}")

    if item == "first_person_voice":
        has_first = bool(re.search(r"\b(I|I'm|my|we|our|we're)\b", t))
        return ("PASS" if has_first else "FAIL", "检测英文第一人称")

    if item == "data_point":
        return ("PASS" if has_number(t) else "FAIL", "全文至少 1 个具体数字")

    if item == "mini_case":
        return ("PASS" if re.search(r"(case|案例|example|例如|for instance)", t, re.I) else "FAIL", "检测 case/案例关键词")

    if item == "thread_hook":
        first = re.search(r"^\s*1/\s*(.+)$", t, flags=re.M)
        return ("PASS" if first else "FAIL", "首条 1/ 存在" if first else "缺首条钩子")

    if item == "numbered_prefix":
        lines = [ln for ln in t.splitlines() if re.match(r"^\s*\d+/\s", ln)]
        return ("PASS" if len(lines) >= 5 else "FAIL", f"N/ 前缀行数={len(lines)}")

    if item == "closing_cta":
        last = "\n".join(t.splitlines()[-10:])
        return ("PASS" if re.search(r"(关注|收藏|link|follow|subscribe|cta)", last, re.I) else "FAIL", "尾部未检出 CTA 关键词")

    if item == "at_least_one_data_point":
        return ("PASS" if has_number(t) else "FAIL", "全文至少 1 个数字")

    if item in ("hook_0_3s", "core_conclusion_3_30s", "explanation_30_70s", "cta_70_90s", "shot_table"):
        has_table = bool(re.search(r"\|\s*0[–-]", t)) or "| 0" in t
        return ("PASS" if has_table or "分镜" in t else "SKIP", "短视频结构需人工核对")

    if item in ("data_or_case_per_section",):
        return ("SKIP", "逐节判定过于启发式，交给 Agent 人工核对")

    if item == "subhead":
        return ("PASS" if re.search(r"^>\s+\S", t, flags=re.M) else "FAIL", "检测 '> 副标题' 行")

    if item == "per_section_data":
        return ("SKIP", "逐节人工核对")

    if item == "per_point_evidence":
        return ("SKIP", "逐条人工核对")

    # 注：question_style_subheadings 已在 checklist.yaml 的 #2 covered_must_include 里声明由
    # headings_ratio 覆盖，不会走到这里；保留 headings_ratio 作为唯一判定口径。

    if item == "actionable_ending":
        last = "\n".join(t.splitlines()[-30:])
        return ("PASS" if re.search(r"(清单|行动|步骤|checklist|action|steps)", last, re.I) else "FAIL", "尾部未检出清单/行动词")

    if item == "contrarian_or_insight_hook":
        first_5 = "\n".join(t.splitlines()[:30])
        return ("SKIP", f"反共识 hook 由人判定；首 30 行抽样：{first_5[:80]}...")

    return ("SKIP", f"未在判定规则表中：{item}（Agent 请人工核对）")
