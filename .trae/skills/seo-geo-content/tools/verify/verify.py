#!/usr/bin/env python3
"""seo-geo-content 内部质检入口。

用法（从项目根运行）：
    python .trae/skills/seo-geo-content/tools/verify/verify.py <task_slug>             # 跑某任务
    python .trae/skills/seo-geo-content/tools/verify/verify.py --self-check            # 脚本自检（无需任务）
    python .trae/skills/seo-geo-content/tools/verify/verify.py <task_slug> --json-only # 只输出 JSON 到 workspace

产出（写入项目根的 output/<task>/.workspace/）：
- verify_report.json：结构化结果，机器读
- verify_report.md  ：渲染好的 Markdown 片段，供 report.md §4.1 直接 include

stdout 同时打印人类可读摘要。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

# 目录锚点：
#   SCRIPT_DIR  = .../.trae/skills/seo-geo-content/tools/verify
#   SKILL_ROOT  = .../.trae/skills/seo-geo-content           （skill 自包含的根，含 content/rules/tools）
#   PROJECT_ROOT = 项目根（含 output/ 的目录；相对 SKILL_ROOT 往上 3 层：seo-geo/../../..）
# 注意：`output/` 留在项目根，不进 skill——skill 是跨任务复用的；output 是任务专属。
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent.parent
PROJECT_ROOT = SKILL_ROOT.parent.parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from rules_loader import (  # noqa: E402
    covered_must_include_items,
    load_authority,
    load_channels_slug_map,
    load_checklist,
    load_rules,
    parse_authority_from_report,
)
from checks.common import CheckResult, Document  # noqa: E402
from checks import (  # noqa: E402
    authority as chk_authority,
    facts_trace as chk_facts_trace,
    faq as chk_faq,
    first_paragraph as chk_first_paragraph,
    headings_ratio as chk_headings_ratio,
    must_include as chk_must_include,
    numeric_citation as chk_numeric_citation,
    schema as chk_schema,
    update_date as chk_update_date,
    word_count as chk_word_count,
)


RULES_PATH = SKILL_ROOT / "rules" / "platform_rules.yaml"
AUTHORITY_PATH = SKILL_ROOT / "rules" / "authority.txt"
CHANNELS_PATH = SKILL_ROOT / "rules" / "channels.yaml"
CHECKLIST_PATH = SKILL_ROOT / "rules" / "checklist.yaml"


def _resolve_rule_key(filename_stem: str, rules: dict, slug_map: dict[str, str]) -> str | None:
    """把落盘文件名 stem 解析为 platform_rules.yaml 的规则段 key。

    优先级：
    1. stem 直接命中 rules → 返回 stem（默认场景，如 `xiaohongshu.md` / `landing_page.md`）
    2. 在 channels.yaml 的 slug→rule_key 映射里找（如 `quora.md` → `zhihu`）
    3. 都没找到 → 返回 None，调用方打 SKIP
    """
    if filename_stem in rules:
        return filename_stem
    mapped = slug_map.get(filename_stem)
    if mapped and mapped in rules:
        return mapped
    return None


def _count_queries_in_report(report_text: str) -> int | None:
    section = re.search(
        r"^##\s+.*?(目标查询集合|重点查询|重点主题).*?\n(.*?)(?:^##\s|\Z)",
        report_text,
        flags=re.S | re.M,
    )
    if not section:
        return None
    body = section.group(2)
    items = re.findall(r"^\s*(?:\d+\.\s+|-\s+)\S", body, flags=re.M)
    return len(items)


def run(task_slug: str, json_only: bool = False) -> dict:
    task_dir = PROJECT_ROOT / "output" / task_slug
    content_dir = task_dir / "deliverables" / "content"
    report_path = task_dir / "deliverables" / "report.md"
    facts_path = task_dir / ".workspace" / "facts.md"

    if not content_dir.exists():
        raise SystemExit(f"找不到 deliverables 目录：{content_dir}")

    rules = load_rules(RULES_PATH)
    shared = rules["shared"]
    slug_map = load_channels_slug_map(CHANNELS_PATH)
    checklist = load_checklist(CHECKLIST_PATH)
    covered_items = covered_must_include_items(checklist)

    # 先读 report.md（若存在）——既用于 §3 追加权威片段，也用于 §2 查询集合计数
    report_text: str | None = None
    if report_path.exists():
        report_text = report_path.read_text(encoding="utf-8")
    extra_authority = parse_authority_from_report(report_text) if report_text else []
    authority_fragments = load_authority(AUTHORITY_PATH, extra_fragments=extra_authority)

    md_files = sorted(content_dir.glob("*.md"))
    if not md_files:
        raise SystemExit(f"{content_dir} 下没有 .md 文件")

    all_results: list[CheckResult] = []
    docs: list[Document] = []

    for md in md_files:
        stem = pathlib.Path(md.name).stem
        rule_key = _resolve_rule_key(stem, rules, slug_map)
        if rule_key is None:
            all_results.append(
                CheckResult(
                    id="0",
                    platform=stem,
                    item="未知平台",
                    status="SKIP",
                    expected=f"stem={stem} 在 platform_rules.yaml 存在，或在 channels.yaml 有 slug→rule_key 映射",
                    actual="未找到",
                )
            )
            continue
        rule = rules[rule_key]
        # platform 字段在结果里用**落盘 slug**，方便 Agent 回查具体文件；
        # 规则段 key 可能不同（fallback 场景），放到 expected 里提示
        doc_platform = stem
        doc = Document(platform=doc_platform, path=str(md), raw=md.read_text(encoding="utf-8"))
        docs.append(doc)

        all_results += chk_word_count.check(doc, rule)
        all_results += chk_first_paragraph.check(doc, rule, shared)
        all_results += chk_headings_ratio.check(doc, rule)
        all_results += chk_faq.check(doc, rule)
        all_results += chk_authority.check(doc, rule, shared, authority_fragments)
        all_results += chk_numeric_citation.check(doc, rule, shared)
        all_results += chk_update_date.check(doc, rule)
        all_results += chk_schema.check(doc, rule, shared)
        all_results += chk_must_include.check(doc, rule, covered_items)

    if report_text is not None:
        queries_n = _count_queries_in_report(report_text)
        min_required = shared.get("target_queries_in_report_min", 10)
        if queries_n is None:
            all_results.append(
                CheckResult(
                    id="10",
                    platform="__report__",
                    item="report.md 查询跟踪项",
                    status="SKIP",
                    expected="存在“目标查询集合”或“重点查询/主题”章节",
                    actual="未找到对应章节",
                )
            )
        else:
            all_results.append(
                CheckResult(
                    id="10",
                    platform="__report__",
                    item="report.md 查询跟踪项",
                    status="PASS" if queries_n >= min_required else "FAIL",
                    expected=f"条数 ≥ {min_required}",
                    actual=str(queries_n),
                )
            )
    else:
        all_results.append(
            CheckResult(
                id="10",
                platform="__report__",
                item="report.md 查询跟踪项",
                status="SKIP",
                expected="report.md 存在",
                actual="未找到 report.md",
            )
        )

    all_results += chk_facts_trace.check(docs, facts_path)

    summary = _summarize(all_results, task_slug)
    if not json_only:
        _print_human(summary)

    workspace = task_dir / ".workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "verify_report.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (workspace / "verify_report.md").write_text(
        _render_markdown(summary), encoding="utf-8"
    )

    return summary


def _render_markdown(summary: dict) -> str:
    """把 summary 渲染成 Markdown，供 Agent 按需贴到报告或工作记录。

    设计原则：
    - 输出只包含"逐条结果"的表格，顶部一句话摘要
    - 按 platform 分组；每组一张小表
    """
    totals = summary["totals"]
    gate = "PASS" if summary["gate_pass"] else "FAIL"
    lines: list[str] = []
    lines.append(f"> 门禁：**{gate}**  |  PASS {totals['PASS']}  FAIL {totals['FAIL']}  SKIP {totals['SKIP']}")
    lines.append("")

    by_platform: dict[str, list[dict]] = {}
    for c in summary["checks"]:
        by_platform.setdefault(c["platform"], []).append(c)

    status_icon = {"PASS": "✓", "FAIL": "✗", "SKIP": "·"}
    for platform, items in by_platform.items():
        label = {
            "__report__": "report.md 全局项",
            "__global__": "全局项",
        }.get(platform, platform)
        lines.append(f"#### {label}")
        lines.append("")
        lines.append("| # | 项 | 结果 | 判定口径 | 实测值 |")
        lines.append("|---|---|---|---|---|")
        for c in items:
            icon = status_icon.get(c["status"], "?")
            expected = c["expected"].replace("|", "\\|")
            actual = c["actual"].replace("|", "\\|")
            item = c["item"].replace("|", "\\|")
            lines.append(
                f"| {c['id']} | {item} | {icon} {c['status']} | {expected} | {actual} |"
            )
        lines.append("")

    if not summary["gate_pass"]:
        lines.append("> ⚠️ 存在 FAIL，不得宣告交付；回 Step 3 改稿后重跑。")
    else:
        lines.append("> ⇒ 门禁 PASS：可作为内部质检记录留档。")
    lines.append("")
    return "\n".join(lines)


def _summarize(results: list[CheckResult], task_slug: str) -> dict[str, Any]:
    by_status = {"PASS": 0, "FAIL": 0, "SKIP": 0}
    for r in results:
        by_status[r.status] = by_status.get(r.status, 0) + 1

    return {
        "task": task_slug,
        "totals": by_status,
        "gate_pass": by_status["FAIL"] == 0,
        "checks": [r.as_dict() for r in results],
    }


def _print_human(summary: dict) -> None:
    totals = summary["totals"]
    print(f"\n=== seo-geo-content verify | task: {summary['task']} ===")
    print(f"PASS {totals['PASS']}  FAIL {totals['FAIL']}  SKIP {totals['SKIP']}\n")

    by_platform: dict[str, list[dict]] = {}
    for c in summary["checks"]:
        by_platform.setdefault(c["platform"], []).append(c)

    for platform, items in by_platform.items():
        print(f"--- {platform} ---")
        for c in items:
            mark = {"PASS": "✓", "FAIL": "✗", "SKIP": "·"}[c["status"]]
            print(f"  {mark} [#{c['id']}] {c['item']}")
            print(f"      expected: {c['expected']}")
            print(f"      actual:   {c['actual']}")
            if c.get("evidence"):
                print(f"      evidence: {c['evidence']}")
        print()

    if summary["gate_pass"]:
        print("⇒ 门禁 PASS：可作为内部质检记录留档")
    else:
        print("⇒ 门禁 FAIL：回 Step 3 修改后重跑")


def self_check() -> int:
    """不依赖任何任务目录，做两件事：
    1. **SSOT 元校验**：channels.yaml 的 rule_key / checklist.yaml 的 covered_must_include
       所指向的字段必须在对应 SSOT 里真实存在（"三份 SSOT 自一致"体检）
    2. **规则执行冒烟**：对一份应当通过的示例文本跑全部 check 模块，确认无接口回归
    """
    print("== verify.py self-check ==")
    errors: list[str] = []
    try:
        rules = load_rules(RULES_PATH)
        authority = load_authority(AUTHORITY_PATH)
        slug_map = load_channels_slug_map(CHANNELS_PATH)
        checklist = load_checklist(CHECKLIST_PATH)
        covered_items = covered_must_include_items(checklist)
    except Exception as e:
        print(f"加载规则失败：{e}")
        return 1

    print(f"规则平台数：{len(rules) - 1}（{', '.join(k for k in rules if k != 'shared')}）")
    print(f"权威域名片段数：{len(authority)}")
    print(f"channels slug→rule_key 映射条目数：{len(slug_map)}")
    print(f"checklist covered_must_include 条目数：{len(covered_items)}")

    # --- 元校验 1：channels.yaml 的 rule_key 必须在 platform_rules.yaml 存在
    for slug, rk in slug_map.items():
        if rk not in rules:
            errors.append(f"[channels.yaml] slug={slug} 的 rule_key={rk} 在 platform_rules.yaml 中不存在")

    # --- 元校验 2：checklist.yaml 的 covered_must_include 所列 item 至少
    #              在某个 platform 的 must_include 里出现过
    all_must_include: set[str] = set()
    for key, val in rules.items():
        if key == "shared" or not isinstance(val, dict):
            continue
        for item in val.get("must_include", []) or []:
            all_must_include.add(str(item))
    for item in covered_items:
        if item not in all_must_include:
            errors.append(
                f"[checklist.yaml] covered_must_include={item} 未出现在任何 platform 的 must_include 列表中"
            )

    # --- 元校验 3：checklist.yaml 每条 check 的 verifier 如果以模块名形式给出，
    #              必须能在 checks/ 下找到（忽略形如 "(inline in verify.py)" 的内联判定）
    known_verifiers = {
        "authority", "facts_trace", "faq", "first_paragraph", "headings_ratio",
        "must_include", "numeric_citation", "schema", "update_date", "word_count",
    }
    for c in checklist.get("checks", []) or []:
        verifier = c.get("verifier")
        if not verifier or verifier.startswith("("):  # 内联或 null
            continue
        if verifier not in known_verifiers:
            errors.append(f"[checklist.yaml] id={c.get('id')} 的 verifier={verifier} 不在 checks/ 模块列表中")

    if errors:
        print("\n⚠️ SSOT 元校验发现问题：")
        for e in errors:
            print(f"  - {e}")
    else:
        print("\n✓ SSOT 元校验通过（channels / checklist / platform_rules 互相自洽）")

    long_body = "这是一段用于自检的补充说明，强调适用场景、操作边界、风险控制和结果判断，并保持表达清楚可被抽取。"
    faq_a1 = "这是一个足够完整的回答，用来解释概念边界和适用场景，便于用户直接理解。"
    faq_a2 = "通常先完成基础发布，再观察一到两周反馈，然后根据数据补 FAQ、证据段和对比内容。"
    faq_a3 = "费用受范围和复杂度影响，一般要结合目标市场、内容长度和证据材料一起评估。"
    faq_a4 = "建议先做核心页面，再按平台特性改写分发内容，这样承接和复用效率更高。"
    faq_a5 = "主要风险是证据不充分或承诺过度，所以数字、案例和结论都要给清楚出处。"

    sample = Document(
        platform="landing_page",
        path="<memory>",
        raw=(
            "# 示例标题\n\n"
            "> 副标题\n\n"
            "- 最近更新：2026-04-22\n\n"
            "## 首段直答\n\n"
            "这是面向真实用户的直接回答段落，清楚说明方案价值、适用场景、交付边界、行动建议与下一步动作安排。\n\n"
            "## 为什么重要？\n\n[ISO](https://iso.org) 报告显示 85% 的企业\n\n"
            f"{long_body * 10}\n\n"
            "## 如何做？\n\n1. 第一步\n2. 第二步\n\n"
            f"{long_body * 7}\n\n"
            "## 适合谁？\n\n"
            f"{long_body * 6}\n\n"
            "## 如何评估效果？\n\n"
            f"{long_body * 6}\n\n"
            "## FAQ\n\n"
            f"### Q1. 什么是这件事？\nA. {faq_a1}\n\n"
            f"### Q2. 多久见效？\nA. {faq_a2}\n\n"
            f"### Q3. 费用？\nA. {faq_a3}\n\n"
            f"### Q4. 渠道？\nA. {faq_a4}\n\n"
            f"### Q5. 风险？\nA. {faq_a5}\n\n"
            "## 下一步\n\n"
            "- 立即咨询：填写表单\n"
            "- 获取资料：下载方案说明\n\n"
            '<script type="application/ld+json">{"@type":"Organization"}</script>\n'
            '<script type="application/ld+json">{"@type":"Article","dateModified":"2026-04-22"}</script>\n'
            '<script type="application/ld+json">{"@type":"FAQPage"}</script>\n'
        ),
    )

    shared = rules["shared"]
    rule = rules["landing_page"]

    all_results = []
    all_results += chk_word_count.check(sample, rule)
    all_results += chk_first_paragraph.check(sample, rule, shared)
    all_results += chk_headings_ratio.check(sample, rule)
    all_results += chk_faq.check(sample, rule)
    all_results += chk_authority.check(sample, rule, shared, authority)
    all_results += chk_numeric_citation.check(sample, rule, shared)
    all_results += chk_update_date.check(sample, rule)
    all_results += chk_schema.check(sample, rule, shared)
    all_results += chk_must_include.check(sample, rule, covered_items)

    summary = _summarize(all_results, "__self_check__")
    _print_human(summary)
    if not summary["gate_pass"]:
        print("\n⚠️ 自检样例未通过，说明检查规则或样例内容需要修正。")
    return 1 if errors or not summary["gate_pass"] else 0


def main() -> int:
    p = argparse.ArgumentParser(description="seo-geo-content 上线前自检")
    p.add_argument("task_slug", nargs="?", help="任务 slug（output/<slug>/ 目录下）")
    p.add_argument("--self-check", action="store_true", help="脚本自检（不依赖任务）")
    p.add_argument("--json-only", action="store_true", help="只输出 JSON 到 workspace，不打印人类可读摘要")
    args = p.parse_args()

    if args.self_check:
        return self_check()
    if not args.task_slug:
        p.error("必须提供 task_slug，或使用 --self-check")
    summary = run(args.task_slug, json_only=args.json_only)
    return 0 if summary["gate_pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
