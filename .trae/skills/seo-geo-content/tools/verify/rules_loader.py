"""加载 SSOT 文件：platform_rules.yaml / checklist.yaml / channels.yaml / authority.txt。

设计要点：
- 只依赖 PyYAML；不引入任何 markdown/schema 解析库，保持轻量
- `platform_rules.yaml` 的 `{ref: shared.xxx}` 在加载期一次性展开，后续 check 模块拿到纯数字/列表
- `channels.yaml` 提供 slug→rule_key 映射，供 verify.py 解析非标准文件名（如 `quora.md` → 用 `zhihu` 规则）
- `authority` 支持合并外部追加片段（供 report.md §3 的行业白名单真正生效）
"""

from __future__ import annotations

import pathlib
import re
from typing import Any

import yaml


class RulesLoadError(Exception):
    pass


def _resolve(value: Any, shared: dict) -> Any:
    """递归把形如 {'ref': 'shared.faq'} 替换成 shared 段里的实际值。"""
    if isinstance(value, dict):
        if "ref" in value and isinstance(value["ref"], str):
            path = value["ref"].split(".")
            # 仅支持 shared.xxx.yyy 这种前缀
            if path[0] != "shared":
                raise RulesLoadError(f"不支持的 ref 前缀：{value['ref']}")
            cursor: Any = shared
            for key in path[1:]:
                if not isinstance(cursor, dict) or key not in cursor:
                    raise RulesLoadError(f"ref 路径无效：{value['ref']}")
                cursor = cursor[key]
            return _resolve(cursor, shared)
        return {k: _resolve(v, shared) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve(v, shared) for v in value]
    return value


def load_rules(rules_path: pathlib.Path) -> dict:
    if not rules_path.exists():
        raise RulesLoadError(f"找不到规则文件：{rules_path}")
    raw = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "shared" not in raw:
        raise RulesLoadError("platform_rules.yaml 结构异常：缺少 shared 段")
    shared = raw["shared"]
    resolved = {"shared": shared}
    for key, value in raw.items():
        if key == "shared":
            continue
        resolved[key] = _resolve(value, shared)
    return resolved


def load_authority(
    authority_path: pathlib.Path,
    extra_fragments: list[str] | None = None,
) -> list[str]:
    """加载权威白名单。

    - 主体来自 `rules/authority.txt`（团队共识，低频维护）
    - `extra_fragments` 允许本任务追加（典型来源：`report.md §3` 的行业专属白名单）
      —— 这堵住了原设计里"report §3 追加但门禁不认"的裂缝
    """
    if not authority_path.exists():
        raise RulesLoadError(f"找不到权威白名单：{authority_path}")
    fragments: list[str] = []
    for line in authority_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        fragments.append(stripped.lower())
    for frag in extra_fragments or []:
        f = frag.strip().lower()
        if f and f not in fragments:
            fragments.append(f)
    return fragments


_URL_HOST_RE = re.compile(r"^(?:https?://)?([^/\s]+)", re.I)


def parse_authority_from_report(report_text: str) -> list[str]:
    """从 report.md §3 追加段落里抽行业专属白名单片段。

    解析策略：
    - 定位 H2 "## 3." 开头的节（容忍标题后带任意文字）
    - 提取 `^\\s*-\\s+(.+)$` 的 bullet；过滤空占位
    - 若是 URL 取 host；否则原样作为"片段"（支持 `.gov` / `mckinsey.com` 这种裸片段）
    """
    section_match = re.search(
        r"##\s*3\.[^\n]*\n(.*?)(?:^##\s|\Z)",
        report_text,
        flags=re.S | re.M,
    )
    if not section_match:
        return []
    body = section_match.group(1)
    fragments: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^\s*-\s+(.+?)\s*$", line)
        if not m:
            continue
        raw = m.group(1).strip()
        # 跳过占位符（单个 `-`、包含 "此处" / "追加" 等模板关键词的示例行）
        if not raw or raw in ("-", "（略）", "..."):
            continue
        if raw.startswith(">"):
            continue
        # 如果是完整 URL / 域名，取 host
        host_m = _URL_HOST_RE.match(raw)
        if host_m:
            host = host_m.group(1).strip().rstrip("/").lower()
            if host:
                fragments.append(host)
            continue
        fragments.append(raw.lower())
    return fragments


def load_channels_slug_map(channels_path: pathlib.Path) -> dict[str, str]:
    """从 channels.yaml 读出 slug → rule_key 映射。

    用途：verify.py 看到 `quora.md` / `bilibili.md` / `twitter.md` 这种**非 rule_key**
    的落盘文件名时，按映射找到该平台的硬规则段。
    - 缺 `slug` 或 `rule_key` 的条目会被跳过（例如暂无骨架的 Reddit / Product Hunt）
    - 不存在 channels.yaml 时返回空 dict（退化为"只接受文件名 == rule_key"）
    """
    if not channels_path.exists():
        return {}
    raw = yaml.safe_load(channels_path.read_text(encoding="utf-8")) or {}
    platforms = raw.get("platforms", []) or []
    mapping: dict[str, str] = {}
    for p in platforms:
        slug = p.get("slug")
        rule_key = p.get("rule_key")
        if not slug or not rule_key:
            continue
        mapping[str(slug)] = str(rule_key)
    return mapping


def load_checklist(checklist_path: pathlib.Path) -> dict:
    """加载 checklist.yaml（SSOT #2）。

    返回原始 dict；消费方按需取 `checks` 与每条的 `covered_must_include` 字段。
    """
    if not checklist_path.exists():
        raise RulesLoadError(f"找不到 checklist：{checklist_path}")
    raw = yaml.safe_load(checklist_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "checks" not in raw:
        raise RulesLoadError("checklist.yaml 结构异常：缺少 checks 段")
    return raw


def covered_must_include_items(checklist: dict) -> set[str]:
    """从 checklist.yaml 汇总"已由独立 check 模块覆盖"的 must_include item 名。

    下游用法（must_include.py）：对这些 item 一律跳过，避免与独立 check 重复判定。
    这是"must_include 去双重维护"的 SSOT 来源。
    """
    covered: set[str] = set()
    for c in checklist.get("checks", []) or []:
        for item in c.get("covered_must_include", []) or []:
            covered.add(str(item))
    return covered
