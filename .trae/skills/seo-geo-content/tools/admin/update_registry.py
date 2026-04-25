#!/usr/bin/env python3
"""维护 seo-geo-content 的渠道表与权威来源白名单。

设计目标：
- 用户说白话，Agent 可以把白话交给本脚本解析；
- 脚本负责安全更新 rules/channels.yaml 与 rules/authority.txt；
- 默认做去重、规范化与最小推断，不要求用户手动改文件。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from dataclasses import dataclass
from typing import Any

import yaml

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent.parent
CHANNELS_PATH = SKILL_ROOT / "rules" / "channels.yaml"
AUTHORITY_PATH = SKILL_ROOT / "rules" / "authority.txt"
AUTHORITY_ALIASES_PATH = SKILL_ROOT / "rules" / "authority_aliases.yaml"
PLATFORM_RULES_PATH = SKILL_ROOT / "rules" / "platform_rules.yaml"
EVAL_RUBRIC_PATH = SKILL_ROOT / "rules" / "eval_rubric.yaml"
CONTENT_PLATFORMS_DIR = SKILL_ROOT / "content" / "platforms"

CHANNELS_HEADER = """# 渠道矩阵（最小配置）
# 只负责路由，不负责讲道理。
# `landing_page` 不在这里；它是核心资产类型，由 Agent 按目标决定是否生成。
# 若用户提出新增平台，应由本 skill 直接维护本文件与相关模板/规则，而不是要求用户手动添加。
#
# 字段：
# - slug: 落盘文件名
# - aliases: 可选别名列表，供白话识别
# - rule_key: 对应平台模板；null = 可推荐但默认不直接生成
# - maturity:
#   - full: 可推荐，可直接生成
#   - partial: 可推荐，生成后需人工复核
#   - advisory: 只建议，不默认生成
# 模板状态不落盘；由脚本根据模板/规则/评估资产自动推导"""

AUTHORITY_HEADER = """# 权威来源域名/片段白名单（团队共识）
# 用途：供 SKILL.md 的上线前自检 checklist 判定"权威来源引用"是否达标
# 每行一个域名或片段（无需 https://），以 # 开头为注释
#
# 维护建议：
# - 国家/政府/高校：.gov / .edu
# - 标准组织：w3.org / ietf.org / iso.org
# - 学术出版：doi.org / nature.com / ieee.org / acm.org
# - 行业权威媒体/机构：按你的行业补充
# - 若用户提出新增行业权威来源，优先由本 skill 直接维护本文件，而不是要求用户手动编辑"""

MATURITY_VALUES = {"full", "partial", "advisory"}


@dataclass
class Action:
    action: str
    payload: dict[str, Any]
    reason: str


def _load_channels() -> dict[str, Any]:
    raw = yaml.safe_load(CHANNELS_PATH.read_text(encoding="utf-8")) or {}
    data = {
        "version": raw.get("version", 1),
        "platforms": raw.get("platforms", []) or [],
    }
    data["platforms"] = [_hydrate_channel(p) for p in data["platforms"]]
    return data


def _load_yaml(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_platform_rules() -> dict[str, Any]:
    return _load_yaml(PLATFORM_RULES_PATH)


def _load_eval_rubric() -> dict[str, Any]:
    return _load_yaml(EVAL_RUBRIC_PATH)


def _load_authority_aliases() -> dict[str, str]:
    data = _load_yaml(AUTHORITY_ALIASES_PATH)
    raw = data.get("aliases", {}) if isinstance(data, dict) else {}
    return {str(k).lower(): _normalize_authority(str(v)) for k, v in raw.items()}


def _save_channels(data: dict[str, Any]) -> None:
    body = yaml.safe_dump(
        {
            "version": data.get("version", 1),
            "platforms": [_dehydrate_channel(p) for p in data.get("platforms", [])],
        },
        allow_unicode=True,
        sort_keys=False,
    )
    CHANNELS_PATH.write_text(CHANNELS_HEADER + "\n\n" + body, encoding="utf-8")


def _load_authority() -> list[str]:
    values: list[str] = []
    for line in AUTHORITY_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or (not line.strip() and not values):
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        values.append(stripped)
    return values


def _save_authority(values: list[str]) -> None:
    unique = []
    seen = set()
    for value in values:
        norm = _normalize_authority(value)
        if norm and norm not in seen:
            unique.append(norm)
            seen.add(norm)
    AUTHORITY_PATH.write_text(
        AUTHORITY_HEADER + "\n\n" + "\n".join(unique) + "\n",
        encoding="utf-8",
    )


def _normalize_authority(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"^https?://", "", text)
    text = text.rstrip("/")
    return text


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _platform_aliases(channel: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for item in [channel.get("name"), channel.get("slug"), *(channel.get("aliases") or [])]:
        if item:
            values.append(str(item).strip())
    return values


def _find_platform(text: str) -> dict[str, Any] | None:
    lowered = text.lower()
    best: dict[str, Any] | None = None
    best_len = -1
    for channel in list_channels():
        for alias in _platform_aliases(channel):
            alias_lower = alias.lower()
            if alias_lower in lowered and len(alias_lower) > best_len:
                best = channel
                best_len = len(alias_lower)
    return best


def _find_platform_by_name(name: str) -> dict[str, Any] | None:
    lowered = name.strip().lower()
    for channel in list_channels():
        for alias in _platform_aliases(channel):
            if alias.lower() == lowered:
                return channel
    return None


def _find_authority(text: str) -> str | None:
    domain = re.search(r"(?:https?://)?([a-z0-9.-]+\.[a-z]{2,})", text, flags=re.I)
    if domain:
        return _normalize_authority(domain.group(1))
    lowered = text.lower()
    for alias, canonical in _load_authority_aliases().items():
        if alias in lowered:
            return canonical
    return None


def _infer_slug(name: str) -> str:
    existing = _find_platform_by_name(name)
    if existing:
        return str(existing["slug"])
    ascii_name = _slugify(name)
    if not ascii_name:
        raise ValueError(f"无法从平台名推断 slug：{name}")
    return ascii_name


def _has_native_assets(rule_key: str) -> bool:
    if not rule_key:
        return False
    template_exists = (CONTENT_PLATFORMS_DIR / f"{rule_key}.md").exists()
    has_platform_rule = rule_key in _load_platform_rules()
    rubric = _load_eval_rubric().get("platform_dimensions", {})
    has_eval_dimension = rule_key in rubric
    return template_exists and has_platform_rule and has_eval_dimension


def _infer_template_mode(slug: str, rule_key: str | None) -> str:
    if rule_key is None:
        return "none"
    if slug == rule_key and _has_native_assets(rule_key):
        return "native"
    return "reuse"


def _hydrate_channel(channel: dict[str, Any]) -> dict[str, Any]:
    hydrated = dict(channel)
    hydrated["template_mode"] = _infer_template_mode(hydrated["slug"], hydrated.get("rule_key"))
    return hydrated


def _dehydrate_channel(channel: dict[str, Any]) -> dict[str, Any]:
    raw = dict(channel)
    raw.pop("template_mode", None)
    return raw


def _infer_rule_key(
    name: str,
    summary: str = "",
    content_types: list[str] | None = None,
    languages: list[str] | None = None,
) -> str | None:
    del summary  # 当前兜底不再依赖描述文本猜平台
    existing = _find_platform_by_name(name)
    if existing:
        return existing.get("rule_key")
    slug = _slugify(name)
    if slug and _has_native_assets(slug):
        return slug
    kinds = {str(v).lower() for v in (content_types or [])}
    langs = {str(v).lower() for v in (languages or [])}
    if "short_video" in kinds:
        return "short_video"
    if "thread" in kinds or "insight" in kinds:
        return "twitter_thread"
    if "faq" in kinds and ("comparison" in kinds or "howto" in kinds):
        return "zhihu" if "zh" in langs else "quora"
    if "report" in kinds and "case_study" in kinds and "en" in langs:
        return "medium"
    return "own_blog"


def _infer_maturity(rule_key: str | None) -> str:
    return "advisory" if rule_key is None else "partial"


def list_channels() -> list[dict[str, Any]]:
    data = _load_channels()
    return data.get("platforms", [])


def list_authority() -> list[str]:
    values = _load_authority()
    return [_normalize_authority(v) for v in values]


def add_authority(value: str, dry_run: bool = False) -> dict[str, Any]:
    values = _load_authority()
    normalized = _normalize_authority(value)
    exists = normalized in {_normalize_authority(v) for v in values}
    result = {"action": "add_authority", "value": normalized, "status": "exists" if exists else "added"}
    if not exists and not dry_run:
        values.append(normalized)
        _save_authority(values)
    return result


def add_channel(channel: dict[str, Any], dry_run: bool = False) -> dict[str, Any]:
    data = _load_channels()
    platforms = data.setdefault("platforms", [])
    slug = channel["slug"]
    existing = next((p for p in platforms if p.get("slug") == slug or p.get("name") == channel["name"]), None)
    if existing:
        if "aliases" not in channel and existing.get("aliases"):
            channel["aliases"] = existing.get("aliases")
        existing.update(channel)
        channel = _hydrate_channel(existing)
        existing.clear()
        existing.update(channel)
        status = "updated"
    else:
        channel = _hydrate_channel(channel)
        platforms.append(channel)
        status = "added"
    if not dry_run:
        _save_channels(data)
    return {"action": "add_channel", "status": status, "channel": channel}


def update_channel(slug: str, updates: dict[str, Any], dry_run: bool = False) -> dict[str, Any]:
    data = _load_channels()
    platform = next((p for p in data.get("platforms", []) if p.get("slug") == slug), None)
    if platform is None:
        raise ValueError(f"未找到渠道 slug：{slug}")
    platform.update({k: v for k, v in updates.items() if v is not None})
    if "maturity" in updates and updates["maturity"] not in MATURITY_VALUES:
        raise ValueError(f"非法 maturity：{updates['maturity']}")
    platform.update(_hydrate_channel(platform))
    if not dry_run:
        _save_channels(data)
    return {"action": "update_channel", "status": "updated", "channel": platform}


def build_channel_payload(args: argparse.Namespace) -> dict[str, Any]:
    preset = (_find_platform_by_name(args.name) or {}).copy()
    canonical_name = str(preset.get("name") or args.name)
    payload = {
        "name": canonical_name,
        "slug": args.slug or preset.get("slug") or _infer_slug(args.name),
        "rule_key": args.rule_key if args.rule_key != "__auto__" else None,
        "maturity": args.maturity or preset.get("maturity"),
        "regions": args.regions or preset.get("regions") or ["GLOBAL"],
        "languages": args.languages or preset.get("languages") or ["en"],
        "goals": args.goals or preset.get("goals") or ["brand"],
        "content_types": args.content_types or preset.get("content_types") or ["howto"],
        "summary": args.summary or preset.get("summary") or "",
    }
    if preset.get("aliases"):
        payload["aliases"] = preset.get("aliases")
    if args.rule_key is None:
        payload["rule_key"] = preset.get("rule_key")
        if payload["rule_key"] is None and payload["maturity"] != "advisory":
            payload["rule_key"] = _infer_rule_key(
                payload["name"],
                payload["summary"],
                payload["content_types"],
                payload["languages"],
            )
    if payload["maturity"] is None:
        payload["maturity"] = _infer_maturity(payload["rule_key"])
    if payload["maturity"] not in MATURITY_VALUES:
        raise ValueError(f"非法 maturity：{payload['maturity']}")
    if payload["rule_key"] is not None and not isinstance(payload["rule_key"], str):
        raise ValueError("rule_key 必须是字符串或留空")
    return payload


def parse_request(text: str) -> Action:
    lowered = text.lower()
    if any(key in text for key in ["白名单", "权威", "可信来源"]) or "authority" in lowered:
        value = _find_authority(text)
        if not value:
            raise ValueError("未能从白话请求中识别权威来源，请直接给域名或名称。")
        return Action("add_authority", {"value": value}, "识别为白名单维护请求")

    platform = _find_platform(text)
    if platform:
        if any(key in text for key in ["只建议", "不直接生成", "先别直接生成"]):
            payload = {"slug": platform["slug"], "maturity": "advisory"}
            return Action("update_channel", payload, "识别为渠道成熟度调整请求")
        if any(key in text for key in ["人工复核", "先部分支持", "partial"]):
            payload = {"slug": platform["slug"], "maturity": "partial"}
            return Action("update_channel", payload, "识别为渠道成熟度调整请求")
        return Action("add_channel", platform.copy(), "识别为新增或启用渠道请求")

    raise ValueError("未能从白话请求中识别动作，请改用结构化子命令。")


def _print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="维护 seo-geo-content 的渠道表与白名单")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list_channels = sub.add_parser("list-channels", help="查看当前渠道表")
    p_list_channels.add_argument("--json", action="store_true")

    p_list_authority = sub.add_parser("list-authority", help="查看当前白名单")
    p_list_authority.add_argument("--json", action="store_true")

    p_add_authority = sub.add_parser("add-authority", help="新增权威来源")
    p_add_authority.add_argument("value")
    p_add_authority.add_argument("--dry-run", action="store_true")

    p_add_channel = sub.add_parser("add-channel", help="新增或更新渠道")
    p_add_channel.add_argument("--name", required=True)
    p_add_channel.add_argument("--slug")
    p_add_channel.add_argument("--rule-key")
    p_add_channel.add_argument("--maturity")
    p_add_channel.add_argument("--regions", nargs="*")
    p_add_channel.add_argument("--languages", nargs="*")
    p_add_channel.add_argument("--goals", nargs="*")
    p_add_channel.add_argument("--content-types", nargs="*")
    p_add_channel.add_argument("--summary")
    p_add_channel.add_argument("--dry-run", action="store_true")

    p_update_channel = sub.add_parser("update-channel", help="更新渠道字段")
    p_update_channel.add_argument("--slug", required=True)
    p_update_channel.add_argument("--rule-key")
    p_update_channel.add_argument("--maturity")
    p_update_channel.add_argument("--summary")
    p_update_channel.add_argument("--dry-run", action="store_true")

    p_apply_request = sub.add_parser("apply-request", help="解析白话请求并执行")
    p_apply_request.add_argument("--text", required=True)
    p_apply_request.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)

    try:
        if args.command == "list-channels":
            data = list_channels()
            _print_json(data) if args.json else print("\n".join(f"{p['name']} ({p['slug']})" for p in data))
            return 0

        if args.command == "list-authority":
            data = list_authority()
            _print_json(data) if args.json else print("\n".join(data))
            return 0

        if args.command == "add-authority":
            _print_json(add_authority(args.value, dry_run=args.dry_run))
            return 0

        if args.command == "add-channel":
            payload = build_channel_payload(args)
            _print_json(add_channel(payload, dry_run=args.dry_run))
            return 0

        if args.command == "update-channel":
            updates = {"rule_key": args.rule_key, "maturity": args.maturity, "summary": args.summary}
            _print_json(update_channel(args.slug, updates, dry_run=args.dry_run))
            return 0

        if args.command == "apply-request":
            action = parse_request(args.text)
            if action.action == "add_authority":
                result = add_authority(action.payload["value"], dry_run=args.dry_run)
            elif action.action == "add_channel":
                result = add_channel(action.payload, dry_run=args.dry_run)
            elif action.action == "update_channel":
                result = update_channel(action.payload["slug"], action.payload, dry_run=args.dry_run)
            else:
                raise ValueError(f"不支持的动作：{action.action}")
            result["reason"] = action.reason
            _print_json(result)
            return 0

    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
