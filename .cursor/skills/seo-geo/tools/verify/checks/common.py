"""check 模块共用的数据类型与 Markdown 轻量解析器。

保持零外部依赖（除 PyYAML，已在 rules_loader 里用），纯正则切块足以覆盖本仓库模板。
"""

from __future__ import annotations

import dataclasses
import re
from typing import Iterable


@dataclasses.dataclass
class CheckResult:
    id: str               # 对应 SKILL.md checklist 的编号，如 "1"、"8b"
    platform: str         # "landing_page" / "xiaohongshu" / "__report__" / "__global__"
    item: str             # 人话标题
    status: str           # PASS / FAIL / SKIP
    expected: str         # 规则口径（阈值 + 字段名）
    actual: str           # 实测值
    evidence: str = ""    # 命中段落 / 链接摘要

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class Document:
    """解析过的 Markdown 文档轻量视图。"""

    platform: str
    path: str
    raw: str

    @property
    def chinese_chars(self) -> int:
        """中文字符数（含常用符号中的汉字区）。"""
        return len(re.findall(r"[\u4e00-\u9fff]", self.raw))

    @property
    def english_words(self) -> int:
        """英文词数（用空白分词 + 过滤）。"""
        en_only = re.sub(r"[\u4e00-\u9fff]", " ", self.raw)
        en_only = re.sub(r"`{1,3}.*?`{1,3}", " ", en_only, flags=re.S)
        tokens = re.findall(r"[A-Za-z][A-Za-z\-']+", en_only)
        return len(tokens)

    @property
    def effective_length(self) -> int:
        """取中文字符与英文词数的较大值——自适应中英混合文档。"""
        return max(self.chinese_chars, self.english_words)

    @property
    def headings(self) -> list[tuple[int, str]]:
        """返回 [(level, text), ...]，忽略代码块内的 '#'。"""
        out: list[tuple[int, str]] = []
        in_fence = False
        for line in self.raw.splitlines():
            if line.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
            if m:
                out.append((len(m.group(1)), m.group(2)))
        return out

    @property
    def paragraphs(self) -> list[str]:
        """按空行切成段落；剥离标题/代码块/HTML 块；保留引用正文（不保留 '>' 前缀）。"""
        text = self.raw
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", "", text)
        blocks = re.split(r"\n\s*\n", text)
        cleaned: list[str] = []
        for block in blocks:
            lines = [ln for ln in block.splitlines() if not re.match(r"^#{1,6}\s", ln)]
            if not lines:
                continue
            text_block = "\n".join(lines).strip()
            if not text_block:
                continue
            cleaned.append(text_block)
        return cleaned

    def body_paragraphs(self) -> list[str]:
        """与 paragraphs 同，但剔除引用块（> 开头行）与纯元信息段。"""
        out: list[str] = []
        for block in self.paragraphs:
            non_quote = [ln for ln in block.splitlines() if not ln.lstrip().startswith(">")]
            if not non_quote:
                continue
            joined = "\n".join(non_quote).strip()
            if not joined:
                continue
            # 过滤形如 "- 发布日期：..." 这样的元信息 bullet
            if all(re.match(r"^[-*]\s", ln) for ln in non_quote if ln.strip()):
                continue
            out.append(joined)
        return out

    @property
    def links(self) -> list[tuple[str, str]]:
        """抽取所有 [text](url) 形式的 markdown 链接。"""
        return re.findall(r"\[([^\]]+)\]\(([^)]+)\)", self.raw)

    def section_after(self, heading_patterns: Iterable[str]) -> str | None:
        """返回第一个匹配某 heading 正则之后的节内容（到下一个同级或更高级 heading 为止）。"""
        lines = self.raw.splitlines()
        idx = -1
        matched_level = 0
        for i, line in enumerate(lines):
            m = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
            if m and any(re.search(p, m.group(2), re.I) for p in heading_patterns):
                idx = i
                matched_level = len(m.group(1))
                break
        if idx < 0:
            return None
        out: list[str] = []
        for line in lines[idx + 1 :]:
            m = re.match(r"^(#{1,6})\s+", line)
            if m and len(m.group(1)) <= matched_level:
                break
            out.append(line)
        return "\n".join(out).strip()


QUESTION_CN = ("？", "?", "如何", "为什么", "是什么", "怎么", "怎样", "哪些", "多少", "能不能", "要不要", "该不该", "值不值", "对不对")
QUESTION_EN_PREFIX = ("how", "why", "what", "when", "where", "which", "who", "can", "should", "do", "does", "is", "are", "will", "would")


def is_question_heading(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    for kw in QUESTION_CN:
        if kw in stripped:
            return True
    first_word = re.split(r"\s+", stripped)[0].lower().rstrip(":")
    return first_word in QUESTION_EN_PREFIX


def has_number(text: str) -> bool:
    """段落内是否含有"具体数字"——排除 markdown 语法自带的 1. / 2. 编号干扰。"""
    cleaned = re.sub(r"^\s*\d+[\.\)]\s", "", text, flags=re.M)
    cleaned = re.sub(r"^\s*[-*]\s", "", cleaned, flags=re.M)
    return bool(re.search(r"\d", cleaned))


def is_authority_link(url: str, fragments: list[str]) -> bool:
    u = url.lower()
    return any(frag in u for frag in fragments)
